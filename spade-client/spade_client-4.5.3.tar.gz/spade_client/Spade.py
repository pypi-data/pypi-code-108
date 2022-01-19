#
# Module: Spade
#
# Description: Encapsulation the connection and communications to a SPADE server.
#

from __future__ import print_function

DEBUG_SEPARATOR = '--------'
HEADERS = {'Content-Type': 'application/xml',
           'Accept': 'application/xml'}

import sys
sys.path.append('.')

# This code is needed is pyxml if installed
pyxml=None
index = 0
for p in sys.path:
    if -1 != p.find('pyxml'):
         pyxml = p
    index += 1
if None != pyxml:
    sys.path.remove(pyxml)

import xml.etree.ElementTree as ET


def _eprint(*args, **kwargs):
    """Prints to standard error"""
    print(*args, file=sys.stderr, **kwargs)


class FatalError(Exception):
    def __init__(self, message, errorCode, response):
        self.code = errorCode
        self.message = message
        self.response = response


def _check_status(url, r, expected):
    """Checks the return status of a request to a URL

    Keyword arguments:
    url      -- the URL to which the request was made
    r        -- the response to the request
    expected -- the expected response code
    """
    if expected == r.status_code:
        return
    elif 400 == r.status_code:
        raise FatalError('Application at "' + url  + '" can not process this request as it is bad', r.status_code, r.text)
    elif 401 == r.status_code:
        raise FatalError('Not authorized to execute commands for Application at "' + url, r.status_code, r.text)
    elif 404 == r.status_code:
        raise FatalError('Application at "' + url  + '" not found', r.status_code, r.text)
    raise FatalError('Unexpected status (' + str(r.status_code) + ') returned from "' + url  + '"', r.status_code, r.text)


import os
import requests
import xml.dom.minidom

from spade_client import Display

class Spade(object):
    def __init__(self, url = 'http://localhost:8080/spade/local/report/', xml = False, cert = None, key = None, cacert = None, verify = None):
        """An Object that talks to the specified **SPADE** server.

        :param str url: the URL of the SPADE instance.
        :param bool xml: True if the raw XML exchanges should be logged.
        :param str cert: path to the file containing the client\'s x509
            certificate, (default
            ``${HOME}/.spade/client/cert/spade_client.pem``).
        :param str key: path to the file containing path to the client\'s
            private x509 key (default
            ``${HOME}/.spade/client/private/spade_client.key``).
        :param str cacert: path to the file containing one or more CA x509
            certificates, (default
            ``${HOME}/.spade/client/cert/cacert.pem``).

        The ``cert`` and ``key`` will only be used if the files
        containing them exist, otherwise they are ignored.

        The alternate ``cacert`` location is only used if the specified
        directory exists.
        """

        self.url=url
        self.debug=xml
        self.session=requests.Session()
        client_dir=os.getenv('HOME') + '/.spade/client'
        if None == cert:
            cert = client_dir + '/cert/spade_client.pem' #Client certificate
        if None == key:
            key = client_dir + '/private/spade_client.key' #Client private key
        if None == cacert:
            cacert = client_dir + '/cert/cacert.pem' #CA certificate file
        if os.path.exists(cert) and os.path.exists(key):
            self.session.cert = (cert, key)
        if os.path.exists(cacert):
            self.session.cacert = cacert
        if None != verify:
            self.session.verify = verify


    def debug_separator(self):
        _eprint(DEBUG_SEPARATOR)


    def _pretty_print(self, url, s, response = True):
        """Prints out a formatted version of the supplied XML

        :param str url: the URL to which the request was made.
        :param str s: the XML to print.
        :param bool response: True is the XML is the reponse to a request.
        """
        if self.debug:
            if None != url:
                if response:
                    _eprint('URL : Response : ' + url)
                else:
                    _eprint('URL : Request :  ' + url)
            _eprint(xml.dom.minidom.parseString(s).toprettyxml())
            self.debug_separator()


    def get_application(self):
        """:return: the application document at the URL
        :rtype: ElementTree

        :raises FatalError: if the server response in not OK. 
        """

        try:
            r = self.session.get(self.url)
            _check_status(self.url, r, 200)
            application = ET.fromstring(r.text)
            self._pretty_print(self.url, ET.tostring(application))
            return application
        except requests.exceptions.ConnectionError as e:
           raise FatalError('Unable to conenct to application at "' + self.url + '"', None, e)
           


    def application_action(self, application_action):
        """
        Executes, if found, the application action as the specified action method.
        """

        action_uri = application_action.find('uri').text
        r = self.session.post(action_uri, headers=HEADERS)
        _check_status(action_uri, r, 200)
        report = ET.fromstring(r.text)
        self._pretty_print(action_uri, ET.tostring(report))
        Display.action_result(application_action, r)


    def _get_named_resource_url(self, application, xpath, name):
        """
        Returns the URI of the application_action resource if the supplied command is an application_action's name.

        :param str xpath: the xpath to the Named Resources within a Named Resource group that contains the Named Resource.
        :param str name: the name of theresource whose URL should be returned.

        :return: the URI of a Named Resource.
        :rtype: str
        :raises FatalError: if the server response in not OK.
        """

        c = application.findall(xpath)
        for resource in c:
            if name == resource.find('name').text:
                return resource
        return None


    def execute_named_resource(self, application, xpath, name, action):
        """
        Executes, if found, the named resource as the specified action method.
        """
        resource = self._get_named_resource_url(application, xpath, name)
        if None == resource:
            return False
        action(resource)
        return True

