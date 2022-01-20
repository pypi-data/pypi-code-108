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

ISudoSupport_VERSION = "4.1.60168"

class ISudoSupport(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/auth/sudo_support'

    def setOwner (self, subject ):
        postUri = "/_owner";
        __data__ = None
        __encoded__ = None
        queryParams = {  'subject': subject   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : ISudoSupport_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
