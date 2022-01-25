import requests
import base64
import datetime
import traceback
import json

############################# DOCUMENTUM Class ##########################################
class DOCUMENTUM_API():
    """
        Documentum API class allows the user to communicate with Documentum API using python

        Prerequisites:
        -------------
            - Python > 3.7
            - Documentum access
    """

    def __init__(self, base_uri, authentication_type='Basic',
                 username=None, password=None,
                 max_attempts=1, timeout=None, verbose=False, verify=True):

        assert authentication_type in ['Basic'], 'Incorrect authentication type'

        self.base_uri = base_uri + '/dctm-rest'
        self.authentication_type = authentication_type

        self.username = username
        self.password = password

        self.max_attempts = max_attempts  # TODO: To be added to the REST calls
        self.timeout = timeout  # TODO: To be added to the REST calls
        self.verbose = verbose
        self.verify = verify
        self.session = None

        if self.username != None or self.password != None:
            self.key_64 = self.generate_base64(self.username + ':' + self.password)
        else:
            raise Exception('Username and/or password are not valid, please provide a valid username/password')

        self.authenticate()

    ################################ Core REST API Calls #################################
    ######################################################################################
    def generate_base64(self, value):
        """
            Generate base64 string

            :param value: (``string``) - String value to be converted to base64.

            :returns: (``String``) - base64 string.
        """
        return str(base64.b64encode(bytes(value, 'utf-8')), "utf-8")

    ######################################################################################
    def validate_and_return_response(self, response, message, raw=False, content=False):
        """
            Validate response by comparing it against the acceptable status codes. Returns response and status code.

            :param response: (``requests.response``) - The response from the query.
            :param message: (``string`` - optional) - Desired custom error message.
            :param raw: (``bool`` - optional) - Defines whether to return response raw format or json (default value False).
            :param content: (``bool`` - optional) - Defines whether to return response content or json (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if response.status_code in [200]:
            if raw:
                return response.raw, response.status_code
            elif content:
                return response.content, response.status_code
            else:
                return response.json(), response.status_code
        else:
            raise Exception(str(message) + str(response.status_code) + ': ' + str(response.text), \
                   response.status_code)

    ######################################################################################
    def get_request(self, url, accept=None, content_type=None, errormsg='', raw=False, content=False):
        """
            Execute get request.

            :param url: (``string``) - URL to be executed in the get request.
            :param accept: (``string`` - optional) - Request accept string (default value None).
            :param content_type: (``string`` - optional) - Request content_type string (default value None).
            :param raw: (``bool`` - optional) - Defines whether to return response raw format or json (default value False).
            :param content: (``bool`` - optional) - Defines whether to return response content or json (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        headers = {'Authorization': self.authentication_type + ' ' + self.key_64}

        if accept != None:
            headers['Accept'] = str(accept)

        if content_type != None:
            headers['content-type'] = content_type

        res = requests.get(url, headers=headers,
                           verify=self.verify)

        return self.validate_and_return_response(res, errormsg, raw=raw, content=content)

    ######################################################################################
    def authenticate(self, verbose=False):
        """
            Authenticate with Documentum using the defined authentication type used in the class constructor.

            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``tuple`` - dict or string, string) - response (json, raw or error string) and response status code.
        """

        if self.verbose or verbose:
            print('Authenticating with Documentum...')

        url = self.base_uri + '/services'
        return self.get_request(url, errormsg='Authentication error ')

    ######################################################################################
    def get_resources(self, base_url, resource_type, verbose=False):
        """
            Execute get request to get all resources.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param resource_type: (``string``) - Resource type (e.g. cabinets, folders...etc.).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``list``) - Resources found.
        """

        if self.verbose or verbose:
            print('Getting ' + str(resource_type) + '...')

        if 'cabinets' in base_url:
            base_url = base_url.replace('cabinets', 'folders')

        url = str(base_url) + '/' + str(resource_type)
        result, result_status = self.get_request(url, errormsg='Get ' + str(resource_type) + ' error ')

        if 'entries' in result:
            if len(result['entries']) > 0:
                return result['entries']
            else:
                raise Exception('No ' + str(resource_type) + ' were found')
        else:
            raise Exception('No entries in ' + str(resource_type) + ' were found')

    ######################################################################################
    def get_resource(self, base_url, resource_type, resource_name, resources=None, verbose=False):
        """
            Execute get request to get a specific resource.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param resource_type: (``string``) - Resource type (e.g. cabinets, folders...etc.).
            :param resource_name: (``string``) - Resource name.
            :param resources: (``list`` - optional) - List of all resources (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict``) - Resource found.
        """

        if self.verbose or verbose:
            print('Getting ' + str(resource_name) + ' in ' + str(resource_type) + '...')

        if resources == None:
            resources = self.get_resources(base_url, resource_type)

        for resource in resources:
            if resource_name == resource['title']:
                return resource

        raise Exception(str(resource_name) + ' was not found')

    ######################################################################################
    def get_repositories(self, verbose=False):
        """
            Execute get request to get all repositories.

            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``list``) - Repositories found.
        """

        return self.get_resources(self.base_uri, 'repositories', verbose=verbose)

    ######################################################################################
    def get_repository(self, repo_name, repos=None, verbose=False):
        """
            Execute get request to get a specific repository.

            :param repo_name: (``string``) - Repository name.
            :param repos: (``list`` - optional) - List of all repositories (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict``) - Repository found.
        """

        return self.get_resource(self.base_uri, 'repositories', repo_name, resources=repos, verbose=verbose)

    ######################################################################################
    def get_cabinets(self, base_url, verbose=False):
        """
            Execute get request to get all cabinets.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``list``) - Repositories found.
        """

        return self.get_resources(base_url, 'cabinets', verbose=verbose)

    ######################################################################################
    def get_cabinet(self, base_url, cabinet_name, cabinets=None, verbose=False):
        """
            Execute get request to get a specific cabinet.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param cabinet_name: (``string``) - Cabinet name.
            :param cabinets: (``list`` - optional) - List of all cabinets (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict``) - Cabinet found.
        """

        return self.get_resource(base_url, 'cabinets', cabinet_name, resources=cabinets, verbose=verbose)

    ######################################################################################
    def get_folders(self, base_url, verbose=False):
        """
            Execute get request to get all folders.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``list``) - Repositories found.
        """

        return self.get_resources(base_url, 'folders', verbose=verbose)

    ######################################################################################
    def get_folder(self, base_url, folder_name, folders=None, verbose=False):
        """
            Execute get request to get a specific folder.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param folder_name: (``string``) - Folder name.
            :param folders: (``list`` - optional) - List of all folders (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict``) - Folder found.
        """

        return self.get_resource(base_url, 'folders', folder_name, resources=folders, verbose=verbose)

    ######################################################################################
    def get_documents(self, base_url, verbose=False):
        """
            Execute get request to get all documents.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``list``) - Repositories found.
        """

        return self.get_resources(base_url, 'documents', verbose=verbose)

    ######################################################################################
    def get_document(self, base_url, doc_name, documents=None, verbose=False):
        """
            Execute get request to get a specific document.

            :param base_url: (``string``) - URL to be executed in the get request.
            :param doc_name: (``string``) - Document name.
            :param documents: (``list`` - optional) - List of all documents (default value None).
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict``) - Document found.
        """

        return self.get_resource(base_url, 'documents', doc_name, resources=documents, verbose=verbose)

    ######################################################################################
    def get_document_content(self, document_obj, verbose=False):
        """
            Execute get request to get the content of a specific document.

            :param document_obj: (``dict``) - Document object.
            :param verbose: (``bool`` - optional) - Print internal messages if True (default value False).

            :return: (``dict`` - dict, bytes) - Document content (properties and data).
        """

        if self.verbose or verbose:
            print('Getting ' + str(document_obj['title']) + ' contents and media...')

        url = document_obj['id'].replace('/documents/', '/objects/')
        content_url = url + '/contents/content'
        content_obj = self.get_request(content_url, errormsg='Error getting document content: ')

        media_url = url + '/content-media'
        media_obj = self.get_request(media_url, errormsg='Error getting document media: ', content=True)
        return {'properties': content_obj[0], 'data': media_obj[0]}

######################################################################################
################################### Start Script #####################################
if __name__ == '__main__':
    url = ''
    username = ''
    password = ''
    repo = ''

    startTime = datetime.datetime.now()

    ###### Program start here #######
    doc_api = DOCUMENTUM_API(url, username=username, password=password, verbose=True)

    ####### End of program ########

    endTime = datetime.datetime.now()
    elapsedTime = endTime - startTime

    print('Documentum API actions completed.....runtime: %s' % (str(elapsedTime)))