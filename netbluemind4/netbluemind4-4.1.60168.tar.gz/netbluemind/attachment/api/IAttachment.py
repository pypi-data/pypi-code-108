#
#  BEGIN LICENSE
#  Copyright (c) Blue Mind SAS, 2012-2016
# 
#  This file is part of BlueMind. BlueMind is a messaging and collaborative
#  solution.
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of either the GNU Affero General Public License as
#  published by the Free Software Foundation (version 3 of the License).
# 
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# 
#  See LICENSE.txt
#  END LICENSE
#
import requests
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IAttachment_VERSION = "4.1.60168"

class IAttachment(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/attachment/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def getConfiguration (self):
        postUri = "/_config";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAttachment_VERSION}, data = __encoded__);
        from netbluemind.attachment.api.Configuration import Configuration
        from netbluemind.attachment.api.Configuration import __ConfigurationSerDer__
        return self.handleResult__(__ConfigurationSerDer__(), response)
    def shareDedup (self, extension , document ):
        postUri = "/{extension}/share_dedup";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{extension}",extension);
        __data__ = serder.STREAM.encode(document)
        __encoded__ = __data__
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAttachment_VERSION}, data = __encoded__);
        from netbluemind.attachment.api.AttachedFile import AttachedFile
        from netbluemind.attachment.api.AttachedFile import __AttachedFileSerDer__
        return self.handleResult__(__AttachedFileSerDer__(), response)
    def unShare (self, url ):
        postUri = "/{url}/unshare";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{url}",url);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAttachment_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def share (self, name , document ):
        postUri = "/{name}/share";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{name}",name);
        __data__ = serder.STREAM.encode(document)
        __encoded__ = __data__
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IAttachment_VERSION}, data = __encoded__);
        from netbluemind.attachment.api.AttachedFile import AttachedFile
        from netbluemind.attachment.api.AttachedFile import __AttachedFileSerDer__
        return self.handleResult__(__AttachedFileSerDer__(), response)
