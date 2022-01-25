#
# Module: PSquared
#
# Description: Encapsulation the connection and communications to a Catalog server.
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
import xml.etree.ElementTree as ET

from catalog_client import Selections

class Catalog:

    def __init__(self, url, element = ['url'], xml = False, triggers = None,
                 cert = None, key = None, cacert = None, verify = None):
        """Initialize the object

        Keyword arguments:
        url      -- the URL of the Catalog instance (default 'http://localhost:8080/catalog/local/report/')
        element  -- the Tag that should be used as the element of a selection (default 'url')
        xml      -- True if the raw XML exchanges should be logged (default False)
        triggers -- a collection of secondary tags needs to create the element tag (Default None)
        """

        self.url = url
        self.debug = xml
        self.element = element
        self.session=requests.Session()
        client_dir=os.getenv('HOME') + '/.psquared/client'
        if None == cert:
            cert = client_dir + '/cert/psquare_client.pem' #Client certificate
        if None == key:
            key = client_dir + '/private/psquare_client.key' #Client private key
        if None == cacert:
            cacert = client_dir + '/private/cacert.pem' #CA certificate file
        if os.path.exists(cert) and os.path.exists(key):
            self.session.cert = (cert, key)
        if os.path.exists(cacert):
            self.session.cacert = cacert
        if None != verify:
            self.session.verify = verify
        self.triggers = triggers


    def debug_separator(self):
        _eprint(DEBUG_SEPARATOR)


    def _pretty_print(self, url, s, response = True):
        """Prints out a formatted version fo the supplied XML

        Keyword arguments:
        url      -- the URL to which the request was made
        s        -- the XML to print, in the form of a string
        response -- True is the XML is the reponse to a request (default True)
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
        """Returns the application document at the URL"""

        r = self.session.get(self.url)
        _check_status(self.url, r, 200)
        application = ET.fromstring(r.text)
        self._pretty_print(self.url, ET.tostring(application))
        return application


    def _get_named_resource_url(self, xpath, name):
        """Returns the URI of a Named Resource for the specified configuration/version.

        Arguments:
        xpath   -- the xpath to the Named Resources within a Named Resource group that contains the Named Resource.
        name    -- the Named Resource whose URL should be returned.
        """

        application = self.get_application()
        cmd = application.find(xpath + '/[name="' + name + '"]')
        if None == cmd:
            raise FatalError('This version of the Catalog server does not support the "' + name + '" command', 2, ET.tostring(application))
        return cmd.find('uri').text, application


    def get_selection(self, attachment, filter = None):
        """
        Returns the selected items from the catalog.
        """
        
        selection_url, application = self._get_named_resource_url('actions/action', 'selection')
        
        if None != filter:
            selection_url = selection_url + filter
        self._pretty_print(selection_url, ET.tostring(attachment), False)
        r = self.session.get(selection_url, data=ET.tostring(attachment), headers=HEADERS)
        _check_status(selection_url, r, 200)
        selection = ET.fromstring(r.text)
        self._pretty_print(selection_url, ET.tostring(selection))
        return selection


    def get_selection_from_file(self, file):
        tree = ET.parse(file)
        selection = tree.getroot()
        return self.get_selection(selection)


    def select(self, tag, value):
        return Selections(self, tag, value, self.element, self.triggers)

