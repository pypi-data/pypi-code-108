"""

    Spirent Aion Rest client is front end for Spirent AION licensing server ReST API
    Spirent AION is checkout based licencing, contained in cloud or on-prem cluster.
    Its Multi tenant hosted site
    Supports 2.7 + to python 3+

"""


__Version__ = '0.2'
__Author__ = 'Poornima Wari'


from datetime import datetime  # we need it to create log file based on current time and date


# python3 supports urllib.parse and python2 supports urlparse
# we need this is to build the url
try:
    from urllib.parse import urlunsplit
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlunsplit
    from urlparse import urlparse


"""
    Modification history 
    ====================
    0.1 : 12/27/2021
            - Initial code
    0.2 : 01/27/2022
            - Added SSLError exception
              API will try http, in-case https fails
              Note: http needs to be enabled on AION Cluster
"""


import requests      # we need it for http session
import json          # we need it to parse json data
import logging       # we need it to create logger
import platform      # we need it to print environment - python version
import sys           # we need it to trace runtime error
import os            # we need it to create log file
import functools     # we need it to decorate the logs


# helper functions
# helps trace the runtime error
def trace_error():
    logging.error('Error: {}.{},line:{}'.format(sys.exc_info()[0], sys.exc_info()[1],
                                                sys.exc_info()[2].tb_lineno))


# get the default organization id
def get_default_id(url):
    """
        returns default organization id
    """
    url = '{}/api/iam/organizations/default'.format(url)

    # Catch the SSLError and try for http
    try:
        session = requests.Session()
        response = session.get(url)

    except requests.exceptions.SSLError as error:
        logging.warning('SSL Certificate verification failed')
        logging.warning('We will try go get the token with http')

        # parse the url
        content = urlparse(url)

        # build url with http scheme
        url = urlunsplit(('http', content.netloc, content.path, content.params, content.query))

        try:
            response = session.get(url)
        except Exception as error:
            logging.critical('Looks like http is not enable on AION {} {}'.format(content.netloc, error))
            raise

    if not response.ok:
        try:
            error_content = response.content
            response.raise_for_status()
        except Exception as error_massage:
            logging.critical('Failed to get the organization id {} {}'.format(error_massage, error_content))
            raise requests.HTTPError(error_massage, error_content)

    return response.json()['id']


# define wrapper class , we will call our function in that
def log_decorator(function):
    """
        This is to log the request and return result of the http verbs
    :param function: function object
    :return: logs the start and end results
    """

    @functools.wraps(function)
    def inner_function(*args, **kwargs):
        # log beginning of function and agrs / kwargs if any
        logging.info('Calling function {} arguments {} {}'.format(function.__name__, args, kwargs))
        try:
            # get the return value from the function
            value = function(*args, **kwargs)
            logging.info('Response of {} is {}'.format(function.__name__, value))
        except:
            # log exception in-case
            trace_error()
            raise
        return value

    return inner_function


# process the response
def process_response(raw_response):
    """
        returns raw response into json/text/content
    """
    # get the content type
    content_type = raw_response.headers.get('content-type')
    result = ''
    if 'text' in content_type:
        result = raw_response.text
    elif 'application/json' in content_type:
        result = raw_response.json()
    else:
        result = raw_response.content

    return result


class SpirentAion:
    """
        This module is ReST Client for Spirent AION license service
        Support : HTTP-Verbs GET,PUT,POST & DELETE

        Command Syntax :

        spirentaion_object = SpirentAion(username, password, orgnization_id)
            1:	Get the Build version
                    end_point = '/lic/version'
                    spirentaion_object.get(end_point)

            2:  List Users
			        end_point = '/iam/users'
			        spirentaion_object.get(end_point)

            3:	Get application Id
			        end_point = '/inv/applications'
                    spirentaion_object.get(end_point)

            4:	License Checkout
                    end_point = '/lic/checkouts'
                    user_params = {
                        'view': 'current',
                        'orgnization_id' = 'org id provided by spirent',
                        'application_id' = 'your application id ex: stc',
                        'user_id': user_id
                    }
			        spirentaion_object.get(end_point,params=user_params)
    """

    def __init__(self, server, username, password, organization_id='', log_level='INFO', log_path=None):
        """

            Mandatory arguments :
            username = spirentaion username
            password = spirentaion password
            server = spirentaion server wth the subdomain

            Optional arguments:
            organization_id = spirent organization id (optional)
                        if not passed the rest client will get one.
            log_level = uses INFO default
            log_path = if not provided creates log folder in abspath and add .log file with current date and time

        """

        self.username = username
        self.password = password
        self.log_level = log_level
        self.log_path = log_path
        self.organization_id = organization_id

        # remove extra / , if there is one
        if server.endswith('/'):
            server = server[:-1]

        self.__url = server

        # append https
        if not server.startswith('http'):
            self.__url = 'https://' + server

        # if log path is not defined create one at abspath
        if self.log_path:
            self.log_path = os.path.join(self.log_path, 'logs')
        else:
            self.log_path = os.path.abspath('logs')

        # creating a log file with current date and time
        now = datetime.now()
        current_time_date = now.strftime('H%M%S%m%d%Y')

        # creating the log folder if it doesnt exist
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        self.log_path = os.path.expanduser(self.log_path)

        # creating log file with current time and date
        self.log_file = os.path.join(self.log_path + '/spirentaion_rest_client' + current_time_date + '.log')

        # set the log-level
        if log_level.lower() == 'debug':
            self.log_level = 'DEBUG'
        elif log_level.lower() == 'error':
            self.log_level = 'ERROR'
        elif log_level.lower() == 'critical':
            self.log_level = 'CRITICAL'
        elif log_level.lower() == 'warning':
            self.log_level = 'WARNING'
        else:
            self.log_level = 'INFO'

        # set the logger format
        logging.basicConfig(filename=self.log_file, filemode='w', level=self.log_level,
                            format='%(asctime)s %(levelname)-8s %(message)s')

        # creating logger object
        logger = logging.getLogger(self.log_file)

        # print the python version
        logging.info('Python Version :{}'.format(platform.python_version()))
        logging.info('Executing SpirentAion __init__ ')
        logging.info('Spirent Aion URL :{}'.format(self.__url))

        # suppress all deeply nested module messages, but the CRITICAL
        # get to the root and set it CRITICAL
        logging.getLogger('request').setLevel(logging.CRITICAL)

        # getting default organization id , if not passed
        if not self.organization_id:
            self.organization_id = get_default_id(self.__url)

        # Authorizing spirent aion
        logging.info('Authorizing Spirent AION with USERNAME:{} PASSWORD:{} and ORGANIZATION_ID:{}'
                     .format(self.username, self.password, self.organization_id))

        # set bearer token
        self.__beare_token = None

        # set the header
        self.__header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # set the data
        self.__data = json.dumps({
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'scope': self.organization_id
        })

        # append end point to the path
        path = '{}/api/iam/oauth2/token'.format(self.__url)

        # storing the session handle
        self.__session = requests.Session()

        # authorizing the session
        # try with https and will go for http in-case of failure
        try:
            response = self.__session.post(path, headers=self.__header, data=self.__data)

        except requests.exceptions.SSLError as error:
            logger.warning('SSL Certificate verification failed')
            logger.warning('We will try go get the token with http')

            # parse the url
            content = urlparse(path)

            # build url with http scheme
            path = urlunsplit(('http', content.netloc, content.path, content.params, content.query))
            self.__url = urlunsplit(('http', content.netloc, '', '', ''))

            try:
                response = self.__session.post(path, headers=self.__header, data=self.__data)
            except Exception as error:
                logger.critical('Looks like http is not enable on AION {} {}'.format(content.netloc, error))
                raise
        except Exception as error:
            logger.critical('Failed to authorize {}'.format(error))
            raise
        # error handling in case of failure
        if not response.ok:
            try:
                error_content = response.content
                response.raise_for_status()
            except Exception as error_massage:
                logging.critical('Failed to Authorize {} {}'.format(error_massage, error_content))
                raise requests.HTTPError(error_massage, error_content)

        if response.status_code == 200:
            logging.info('Successfully Authorized :) ')

            # extract the authentication token
            self.__bearer_token = response.json()['access_token']

            # updating bearer token
            self.__session.headers.update({'Authorization': 'Bearer {}'.format(self.__bearer_token)})

        version_api = 'https://spirentaion.com/api/lic/version'
        license_version = self.__session.get(version_api)
        logging.info("Platform Version:{}".format(license_version.json()['build_number']))

    def execute_request(self, httpverb, endpoints, **kwargs):
        """
            Execute the http method and return result
            :param http-verb: method to process
            :param endpoints: url endpoints
            :param kwargs: key values : ex data = {} or payload = {} or files = []
            :return: returns the response or the error
        """

        # append / if the endpoints doesn't starts with '/'
        if not endpoints.startswith('/'):
            endpoints = '/' + endpoints

        # append /api if the endpoints doesn't starts with '/api'
        if not endpoints.startswith('/api'):
            endpoints = '/api' + endpoints

        # add endpoints to the base url
        url = self.__url + endpoints
        payload = {}
        params = {}
        file_data = None
        raw_response = None

        # check for the payload and files in kwargs
        if len(list(kwargs.keys())) > 0:
            for key1 in kwargs.keys():
                if 'params' in key1:
                    params = kwargs[key1]
                if 'payload' in key1 or 'data' in key1:
                    # convert python object to json string
                    payload = json.dumps(kwargs[key1])
                elif 'file' in key1:
                    # in case you want to post the file
                    file_name = kwargs[key1]
                    file_data = [('mapFileFormFile', (file_name, open(file_name, 'rb'), 'application/json'))]

        # process the http verb
        if httpverb.lower() == 'get':
            raw_response = self.__session.get(url, params=params)
        elif httpverb.lower() == 'put':
            self.__session.headers.update(self.__headers)
            raw_response = self.__session.put(url, data=payload)
        elif httpverb.lower() == 'post':
            raw_response = self.__session.post(url, data=payload, files=file_data)
        elif httpverb.lower() == 'delete':
            raw_response = self.__session.delete(url)

        if not raw_response.ok:
            # ERROR handling
            try:
                raw_response.raise_for_status()
            except Exception as error_massage:
                error_content = raw_response.content
                logging.critical(str(error_massage) + ' ' + str(error_content))
                raise requests.HTTPError(error_massage, error_content)

        # process the response
        end_result = process_response(raw_response)
        return end_result

    @log_decorator
    def get(self, end_points, **kwargs):
        """
        :param end_points: end points
        :param **kwargs: key:value
        :return: result in json or text
        """
        result = self.execute_request('get', end_points, **kwargs)
        return result

    @log_decorator
    def post(self, end_points, **kwargs):
        """
        :param end_points: end point
        :param **kwargs: key:value Ex file=filename or payload=dictionary
        :return: result in json or text
        """
        result = self.execute_request('post', end_points, **kwargs)
        return result

    @log_decorator
    def put(self, end_points, **kwargs):
        """
        :param end_points: end point
        :param **kwargs: key:value Ex : payload = dictionary
        :return: result in json or text
        """
        result = self.execute_request('put', end_points, **kwargs)
        return result

    @log_decorator
    def delete(self, end_points, **kwargs):
        """
        :param end_points: end points
        :param payload: data
        :return:raw_responsejson format
        """
        result = self.execute_request('delete', end_points, **kwargs)
        return result


def main():
    # user credentials
    user = 'poornima.wari@spirent.com'
    password = '***'
    aion_server = 'sjc.spirentaion.com'

    # license server version end point
    end_points = '/lic/version'

    # creating spirentaion object
    spirentaion_object = SpirentAion(aion_server, user, password)

    # calling get method
    license_version = spirentaion_object.get(end_points)

    return license_version['build_number']

if __name__ == '__main__':
    print(main())
