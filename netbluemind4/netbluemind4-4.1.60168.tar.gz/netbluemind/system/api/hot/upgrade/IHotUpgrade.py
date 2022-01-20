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

IHotUpgrade_VERSION = "4.1.60168"

class IHotUpgrade(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/hot_upgrade'

    def progress (self):
        postUri = "/progress";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IHotUpgrade_VERSION}, data = __encoded__);
        from netbluemind.system.api.hot.upgrade.HotUpgradeProgress import HotUpgradeProgress
        from netbluemind.system.api.hot.upgrade.HotUpgradeProgress import __HotUpgradeProgressSerDer__
        return self.handleResult__(serder.ListSerDer(__HotUpgradeProgressSerDer__()), response)
    def list (self, filter ):
        postUri = "/list";
        __data__ = None
        __encoded__ = None
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskFilter import HotUpgradeTaskFilter
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskFilter import __HotUpgradeTaskFilterSerDer__
        __data__ = __HotUpgradeTaskFilterSerDer__().encode(filter)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IHotUpgrade_VERSION}, data = __encoded__);
        from netbluemind.system.api.hot.upgrade.HotUpgradeTask import HotUpgradeTask
        from netbluemind.system.api.hot.upgrade.HotUpgradeTask import __HotUpgradeTaskSerDer__
        return self.handleResult__(serder.ListSerDer(__HotUpgradeTaskSerDer__()), response)
