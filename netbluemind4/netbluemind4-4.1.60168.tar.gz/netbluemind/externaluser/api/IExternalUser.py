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

IExternalUser_VERSION = "4.1.60168"

class IExternalUser(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/externaluser/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def byExtId (self, extid ):
        postUri = "/byExtId/{extid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{extid}",extid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        from netbluemind.externaluser.api.ExternalUser import ExternalUser
        from netbluemind.externaluser.api.ExternalUser import __ExternalUserSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__ExternalUserSerDer__()), response)
    def update (self, uid , externalUser ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.externaluser.api.ExternalUser import ExternalUser
        from netbluemind.externaluser.api.ExternalUser import __ExternalUserSerDer__
        __data__ = __ExternalUserSerDer__().encode(externalUser)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def delete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def getComplete (self, uid ):
        postUri = "/{uid}/complete";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        from netbluemind.externaluser.api.ExternalUser import ExternalUser
        from netbluemind.externaluser.api.ExternalUser import __ExternalUserSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__ExternalUserSerDer__()), response)
    def create (self, uid , externalUser ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        from netbluemind.externaluser.api.ExternalUser import ExternalUser
        from netbluemind.externaluser.api.ExternalUser import __ExternalUserSerDer__
        __data__ = __ExternalUserSerDer__().encode(externalUser)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def memberOf (self, uid ):
        postUri = "/{uid}/groups";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        from netbluemind.group.api.Group import Group
        from netbluemind.group.api.Group import __GroupSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__GroupSerDer__())), response)
    def memberOfGroups (self, uid ):
        postUri = "/{uid}/groupUids";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.STRING), response)
    def createWithExtId (self, uid , extid , externalUser ):
        postUri = "/{uid}/{extid}/createwithextid";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        postUri = postUri.replace("{extid}",extid);
        from netbluemind.externaluser.api.ExternalUser import ExternalUser
        from netbluemind.externaluser.api.ExternalUser import __ExternalUserSerDer__
        __data__ = __ExternalUserSerDer__().encode(externalUser)
        __encoded__ = json.dumps(__data__)
        queryParams = {     };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IExternalUser_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
