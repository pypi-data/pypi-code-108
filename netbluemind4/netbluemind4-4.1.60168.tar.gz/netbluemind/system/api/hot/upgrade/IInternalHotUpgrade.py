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

IInternalHotUpgrade_VERSION = "4.1.60168"

class IInternalHotUpgrade(BaseEndpoint):
    def __init__(self, apiKey, url ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/hot_upgrade'

    def startLimited (self, maxDuration , mode ):
        postUri = "/limitedStart";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{maxDuration}",maxDuration);
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import HotUpgradeTaskExecutionMode
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import __HotUpgradeTaskExecutionModeSerDer__
        __data__ = __HotUpgradeTaskExecutionModeSerDer__().encode(mode)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInternalHotUpgrade_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def start (self, mode ):
        postUri = "/start";
        __data__ = None
        __encoded__ = None
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import HotUpgradeTaskExecutionMode
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskExecutionMode import __HotUpgradeTaskExecutionModeSerDer__
        __data__ = __HotUpgradeTaskExecutionModeSerDer__().encode(mode)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInternalHotUpgrade_VERSION}, data = __encoded__);
        from netbluemind.core.task.api.TaskRef import TaskRef
        from netbluemind.core.task.api.TaskRef import __TaskRefSerDer__
        return self.handleResult__(__TaskRefSerDer__(), response)
    def list (self, filter ):
        postUri = "/list";
        __data__ = None
        __encoded__ = None
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskFilter import HotUpgradeTaskFilter
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskFilter import __HotUpgradeTaskFilterSerDer__
        __data__ = __HotUpgradeTaskFilterSerDer__().encode(filter)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInternalHotUpgrade_VERSION}, data = __encoded__);
        from netbluemind.system.api.hot.upgrade.HotUpgradeTask import HotUpgradeTask
        from netbluemind.system.api.hot.upgrade.HotUpgradeTask import __HotUpgradeTaskSerDer__
        return self.handleResult__(serder.ListSerDer(__HotUpgradeTaskSerDer__()), response)
    def progress (self):
        postUri = "/progress";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IInternalHotUpgrade_VERSION}, data = __encoded__);
        from netbluemind.system.api.hot.upgrade.HotUpgradeProgress import HotUpgradeProgress
        from netbluemind.system.api.hot.upgrade.HotUpgradeProgress import __HotUpgradeProgressSerDer__
        return self.handleResult__(serder.ListSerDer(__HotUpgradeProgressSerDer__()), response)
