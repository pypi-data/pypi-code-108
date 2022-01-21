from six.moves import urllib
import six
import os
import requests
import logging
import json
from clarus.api_config import ApiConfig
#from urllib.parse import urlencode
from six.moves.urllib.parse import urlencode

#DIRECTORY    = 'c:/clarusft/data/test/'            # where to look for data files

logger = logging.getLogger(__name__)

def ticketAction(action, **params):
    if 'CHARM_TICKET_ACTION_ABS_PATH' in os.environ:
        actionPath = os.environ['CHARM_TICKET_ACTION_ABS_PATH'] + action
        if params:
            querystring = urlencode(params)
            actionPath = actionPath + '?' + querystring
        httpresp = requests.post(actionPath)
        #httpresp = requests.post(actionPath, auth=(ApiConfig.api_key, ApiConfig.api_secret))
        if (httpresp.status_code!=200):
            raise ValueError(httpresp.text)
        else:
            return httpresp.text;
    else:
        return None

def openFile(fileName, mode='r'):
    if (os.path.isfile(fileName)) :
        return open(fileName, mode)
    if os.path.isdir(ApiConfig.resource_path):
        fileName = ApiConfig.resource_path+fileName
    return open(fileName, mode)

def list():
    if 'CHARM_RESOURCE_LIST_PATH' in os.environ:
        resourceListPath = os.environ['CHARM_RESOURCE_LIST_PATH']
        return listResources(resourceListPath);
    else:
        return listFiles();
    
def listFiles():
    if os.path.isdir(ApiConfig.resource_path):
        start = ApiConfig.resource_path
    else:
        start = '.'
    
    filedict = {}
    
    for root, subdirs, files in os.walk(start):
        reldir = os.path.relpath(root, start)
        for f in files:
            filepath = os.path.join(reldir, f)
            
            filedict[filepath] = {
                    "parsedId": {
                        "id": filepath
                    },
                    "name": f,
                    "description": None,
                    "uploaded": False,
                    "mine": False,
                    "sample": False,
                    "metadata": {
                        "DataCategory": None
                    }
                }
    return filedict

def listResources(resourceListPath):
    if resourceListPath.startswith('http'):
        return listHttpResources(resourceListPath)
    else:
        return None
    
def listHttpResources(resourceListPath):
    url = resourceListPath 
    logger.debug ('reading http resource '+url)
    r = requests.get(url)
    if r.status_code != 200:
        logger.error ('error listing http resources: '+str(r.status_code)+" " + r.text)
        return None
    else:
        return json.loads(r.text).get('files')
    
def read(fileNames, asBytes=False, readOptions=None):
    if 'CHARM_RESOURCE_PATH' in os.environ:
        resourcePath = os.environ['CHARM_RESOURCE_PATH']
        return readResources(fileNames, resourcePath, asBytes, readOptions);
    else:
        return readFiles(fileNames, asBytes);

def readFiles(fileNames, asBytes=False):
    streams = []
    
    if isinstance(fileNames, six.string_types):
        fileNameList = fileNames.split(',');
    else:
        fileNameList = fileNames
    
    for fileName in fileNameList:
        if (asBytes):
            mode = 'rb'
        else:
            mode = 'r'
            
        try:
            with openFile(fileName.strip(), mode) as f:
                streams.append(f.read())
        except IOError as error:
            logger.error("Error can't open file " + fileName)
            raise error
    return streams;

def readResources(resourceNames, resourcePath, asBytes=False, readOptions=None):
    streams = []
    
    if isinstance(resourceNames, six.string_types):
        resourceNameList = resourceNames.split(',');
    else:
        resourceNameList = resourceNames
        
    for resourceName in resourceNameList:
        resource = readResource(resourceName.strip(), resourcePath, asBytes, readOptions)
        if resource is not None:
            streams.append(resource);
        else:
            raise IOError('Cannot open resource '+resourceName)
    return streams;

def readResource(resourceName, resourcePath, asBytes=False, readOptions=None):
    if resourcePath.startswith('http'):
        return readHttpResource(resourceName, resourcePath, asBytes, readOptions)
    else:
        return None

def readHttpResource(resourceName, resourcePath, asBytes=False, readOptions=None):
    url = resourcePath + urllib.parse.quote(resourceName)
    
    if readOptions:
        querystring = urllib.parse.urlencode(readOptions, doseq=True)
        url = url+'?'+ querystring
        
    logger.debug ('reading http resource '+url)
    r = requests.get(url)
    if r.status_code != 200:
        logger.error ('error reading http resource: '+str(r.status_code)+" " + r.text)
        return None
    else:
        if (asBytes):
            return r.content
        else:
            return r.text

def write(fileName, data):
    try:
        f = openFile(fileName.strip(), 'w')
        f.write(data.text)
    except IOError as error:
        logger.error ("Error can't open file " + fileName);
        raise error