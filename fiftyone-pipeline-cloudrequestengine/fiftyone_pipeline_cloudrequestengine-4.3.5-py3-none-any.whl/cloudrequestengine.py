 # *********************************************************************
 # This Original Work is copyright of 51 Degrees Mobile Experts Limited.
 # Copyright 2019 51 Degrees Mobile Experts Limited, 5 Charlotte Close,
 # Caversham, Reading, Berkshire, United Kingdom RG4 7BY.
 #
 # This Original Work is licensed under the European Union Public Licence (EUPL) 
 # v.1.2 and is subject to its terms as set out below.
 #
 # If a copy of the EUPL was not distributed with this file, You can obtain
 # one at https://opensource.org/licenses/EUPL-1.2.
 #
 # The 'Compatible Licences' set out in the Appendix to the EUPL (as may be
 # amended by the European Commission) shall be deemed incompatible for
 # the purposes of the Work and the provisions of the compatibility
 # clause in Article 5 of the EUPL shall not apply.
 # 
 # If using the Work as, or as part of, a network application, by 
 # including the attribution notice(s) required under Article 5 of the EUPL
 # in the end user terms of the application under an appropriate heading, 
 # such notice(s) shall fulfill the requirements of that article.
 # ********************************************************************

from __future__ import absolute_import
from fiftyone_pipeline_core.basiclist_evidence_keyfilter import BasicListEvidenceKeyFilter
from fiftyone_pipeline_engines.engine import Engine
from fiftyone_pipeline_engines.aspectdata_dictionary import AspectDataDictionary
from .requestclient import RequestClient
from .cloudrequestexception import CloudRequestException
from .constants import Constants
import warnings
import json
import os

try:
    #python2
    from urllib import urlencode
except ImportError:
    #python3
    from urllib.parse import urlencode

# Engine that makes a call to the 51Degrees cloud service
# Returns raw JSON as a "cloud" property under "cloud" datakey

class CloudRequestEngine(Engine):

    def __init__(self, settings = {}):

        """!
        Constructor for CloudRequestEngine
        
        @type settings: dict
        @param settings: Settings should contain a resource_key and optionally 
        1) a cloud_endpoint to overwrite the default baseurl 
        2) an cloud_request_origin to use when making requests

        """

        super(CloudRequestEngine, self).__init__()

        self.datakey = "cloud"

        self.properties = {
            "cloud" : {
                "type": "string",
                "description": "raw JSON from the cloud service"
            }
        }

        if not "resource_key" in settings:
            raise Exception("CloudRequestEngine needs a resource key")
        else: 
            self.resource_key = settings["resource_key"]
        
        
        if "cloud_endpoint" in settings:
            self.baseURL = settings["cloud_endpoint"]
        else:
            self.baseURL = os.environ.get(Constants.FOD_CLOUD_API_URL)
            if self.baseURL is None or (self.baseURL is not None and self.baseURL == ""):
                self.baseURL = Constants.BASE_URL_DEFAULT

        # Make sure if baseURL does not end with '/', one will be appended
        if not self.baseURL.endswith("/"):
            self.baseURL = self.baseURL + "/"
  
        if "http_client" in settings:
            self.http_client = settings["http_client"]
        else:
            self.http_client = RequestClient()

        if "cloud_request_origin" in settings:
            self.cloud_request_origin = settings["cloud_request_origin"]
        else:
            self.cloud_request_origin = None
			
        # Initialise evidencekeys and properties from the cloud service
     
        self.flow_element_properties = self.get_engine_properties()

        self.evidence_keys = self.get_evidence_keys()

        self.exclude_from_messages = True

    def get_evidence_keys(self):

        """!
        Internal function for getting evidence keys used by cloud engines
        @rtype: dict
        @return: Returns list of keys
        """
    
        evidenceKeyRequest = self.make_cloud_request('GET', self.baseURL + "evidencekeys")

        evidenceKeys = json.loads(evidenceKeyRequest)

        return evidenceKeys


    def get_evidence_key_filter(self):

        """!
        Instance of EvidenceKeyFilter based on the evidence keys fetched
        from the cloud service by the private getEvidenceKeys() method
        
        @type: BasicListEvidenceKeyFilter
        @return: Returns BasicListEvidenceKeyFilter

        """

        return BasicListEvidenceKeyFilter(self.evidence_keys)


    def get_engine_properties(self):

        """!
        Internal method to get properties for cloud engines from the cloud service
    
        @rtype: dict
        @return: Returns properties for all engines
        """

        # Get properties for all engines

        propertiesURL = self.baseURL +"accessibleProperties?" + "resource=" + self.resource_key

        properties = self.make_cloud_request('GET', propertiesURL)

        properties = json.loads(properties)

        flowElementProperties = {}

        # Change indexes to be by name
        for datakey, elementProperties in properties["Products"].items():

            flowElementProperties[datakey] = {}

            engine_properties = elementProperties["Properties"]

            for engineProperty in engine_properties:

                # Lowercase keys

                engineProperty =  {k.lower(): v for k, v in engineProperty.items()}

                flowElementProperties[datakey][engineProperty["name"]] = engineProperty
               
        return flowElementProperties

    def validate_response(self, cloudResponse, checkForErrorMessages = True):

        """!
        Validate the JSON response from the cloud service.
    
        @type: Response
        @param: Response returned from the cloud service.
        @rtype: Exception
        @return: Thrown if there are errors returned from the cloud service.
        """

        hasData = cloudResponse.text and cloudResponse.text.strip()
        messages = []

        if hasData and checkForErrorMessages:
            try:
                jsonResponse = json.loads(cloudResponse.content)
            except:
                raise CloudRequestException("Cloud request engine properties list request returned code '" + 
                    str(cloudResponse.status_code) + "' with content '" + cloudResponse.content+ "'")

            hasErrors = "errors" in jsonResponse and len(jsonResponse["errors"])
            if hasErrors:
                hasData = len(jsonResponse) > 1
            else:
                hasData = len(jsonResponse) > 0
            
            if hasErrors:
                messages.append(json.dumps(jsonResponse["errors"]))

        # If there were no errors but there was also no other data
        # in the response then add an explanation to the list of
        # messages.

        if (len(messages) == 0 and hasData == False):
            message = Constants.MESSAGE_NO_DATA_IN_RESPONSE.format(cloudResponse.url)
            messages.append(message)

        # If there were no errors returned but the response code was non
        # success then throw an exception.

        if (len(messages) == 0 and cloudResponse.status_code != 200):
            message = Constants.MESSAGE_ERROR_CODE_RETURNED.format(self.baseURL, cloudResponse.status_code, json.loads(cloudResponse.content))
            messages.append(message)

        # If there are any errors returned from the cloud service
        # then throw an exception

        headers = None
        
        if (len(messages) > 0):
            # Get the response headers.
            headers = cloudResponse.headers

        if (len(messages) > 1):
            exceptionList = [Constants.EXCEPTION_CLOUD_ERRORS_MULTIPLE]
            exceptionList = exceptionList + messages
            raise CloudRequestException(exceptionList, cloudResponse.status_code, headers)
        elif (len(messages) == 1):
            message = Constants.EXCEPTION_CLOUD_ERROR.format(messages[0])
            raise CloudRequestException(message, cloudResponse.status_code, headers)

    def make_cloud_request(self, type, url, content = None):

        """!    
        @type url: string
        @param url
        
        @rtype: dict
        @return Returns dict with data and error properties error contains any errors from the request, data contains the response
        """

        cloudResponse = self.http_client.request(type, url, content, self.cloud_request_origin)
 
        self.validate_response(cloudResponse)

        return cloudResponse.text           

    def process_internal(self, flowdata):

        """!
        Processing function for the CloudRequestEngine
        Makes a request to the cloud service with the supplied resource key
        and evidence and returns a JSON object that is then parsed by cloud engines
        placed later in the pipeline
        
        @type FlowData: FlowData
        @param FlowData: Returns a JSON object that is then parsed by cloud engines

        """
   
        url = self.baseURL + self.resource_key + ".json?"

        content = self.get_content(flowdata)

        result = self.make_cloud_request('POST', url, content)

        data = AspectDataDictionary(self, {"cloud" : result})

        flowdata.set_element_data(data)

        return

    def get_content(self, flowData):

        """!
        Generate the Content to send in the POST request. The evidence keys
        e.g. 'query.' and 'header.' have an order of precedence. These are
        added to the evidence in reverse order, if there is conflict then 
        the queryData value is overwritten. 

        'query.' evidence should take precedence over all other evidence.
        If there are evidence keys other than 'query.' that conflict then
        this is unexpected so a warning will be logged.

        @param: flowData: FlowData
        @return: Evidence Dictionary
        """

        queryData = {}

        evidence = flowData.evidence.get_all()
        print(evidence)
        # Add evidence in reverse alphabetical order, excluding special keys. 
        self.add_query_data(queryData, evidence, self.get_selected_evidence(evidence, Constants.EVIDENCE_OTHER))
        # Add cookie evidence.
        self.add_query_data(queryData, evidence, self.get_selected_evidence(evidence, Constants.EVIDENCE_COOKIE_PREFIX))
        # Add header evidence.
        self.add_query_data(queryData, evidence, self.get_selected_evidence(evidence, Constants.EVIDENCE_HTTPHEADER_PREFIX))
        # Add query evidence.
        self.add_query_data(queryData, evidence, self.get_selected_evidence(evidence, Constants.EVIDENCE_QUERY_PREFIX))
        print(queryData)
        return queryData

    def add_query_data(self, query_data, all_evidence, evidence):

        """!
        Add query data to the evidence.

        @param: query_data: The destination dictionary to add query data to.
        @param all_evidence: All evidence in the flow data. This is used to report which evidence
        keys are conflicting.
        @param evidence: Evidence to add to the query Data.
        """        

        for evidenceKey, evidenceValue in evidence.items():

            # Get the key parts
            evidenceKeyParts = evidenceKey.split(Constants.EVIDENCE_SEPERATOR)
            prefix = evidenceKeyParts[0].lower()
            suffix = evidenceKeyParts[-1].lower()

            # Check and add the evidence to the query parameters.
            if (not suffix in query_data.keys()):
                query_data[suffix] = evidenceValue
            # If the queryParameter exists already.
            else:
                # Get the conflicting pieces of evidence and then log a 
                # warning, if the evidence prefix is not query. Otherwise a
                # warning is not needed as query evidence is expected 
                # to overwrite any existing evidence with the same suffix.
                if (prefix.lower() != Constants.EVIDENCE_QUERY_PREFIX):
                    conflicts = {}
                    for key, value in all_evidence.items(): 
                        if(key.lower() != evidenceKey.lower() and suffix in key.lower()):
                            conflicts[key] = value

                    warningMessage = Constants.WARNING_MESSAGE \
                                        .format(evidenceKey, evidenceValue) 
                        
                    conflictStr = ', '.join('{}:{}'.format(key, value) \
                                for key, value in conflicts.items())
                    
                    if conflictStr:
                        warnings.warn(warningMessage + conflictStr)
                    
                # Overwrite the existing queryParameter value.
                query_data[suffix] = evidenceValue

    def get_selected_evidence(self, evidence, type):
        
        """!
        Get evidence with specified prefix.

        @param evidence: All evidence in the flow data.
        @param type: Required evidence key prefix
        """

        selected_evidence = {}

        if type == Constants.EVIDENCE_OTHER:
            for key, value in evidence.items():
                if (not self.key_has_prefix(key, Constants.EVIDENCE_QUERY_PREFIX) and \
                        not self.key_has_prefix(key, Constants.EVIDENCE_HTTPHEADER_PREFIX) and \
                            not self.key_has_prefix(key, Constants.EVIDENCE_COOKIE_PREFIX)):
                    selected_evidence[key] = value
            selected_evidence = dict(sorted(selected_evidence.items(), reverse=True))
            
        else:
            for key, value in evidence.items():
                if self.key_has_prefix(key, type):
                    selected_evidence[key] = value
            
        return selected_evidence
        
    def key_has_prefix(self, itemKey, prefix):

        """!
        Check that the key of a KeyValuePair has the given prefix.

        @param itemKey: Key to check
        @param prefix: The prefix to check for.
        @return: True if the key has the prefix.
        """

        key = itemKey.split(Constants.EVIDENCE_SEPERATOR)
        return key[0].lower() == prefix.lower()

