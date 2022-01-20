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
from netbluemind.python import serder

class HotUpgradeProgress :
    def __init__( self):
        self.status = None
        self.count = None
        self.lastUpdatedAt = None
        pass

class __HotUpgradeProgressSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = HotUpgradeProgress()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import HotUpgradeTaskStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import __HotUpgradeTaskStatusSerDer__
        statusValue = value['status']
        instance.status = __HotUpgradeTaskStatusSerDer__().parse(statusValue)
        countValue = value['count']
        instance.count = serder.LONG.parse(countValue)
        lastUpdatedAtValue = value['lastUpdatedAt']
        instance.lastUpdatedAt = serder.DATE.parse(lastUpdatedAtValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import HotUpgradeTaskStatus
        from netbluemind.system.api.hot.upgrade.HotUpgradeTaskStatus import __HotUpgradeTaskStatusSerDer__
        statusValue = value.status
        instance["status"] = __HotUpgradeTaskStatusSerDer__().encode(statusValue)
        countValue = value.count
        instance["count"] = serder.LONG.encode(countValue)
        lastUpdatedAtValue = value.lastUpdatedAt
        instance["lastUpdatedAt"] = serder.DATE.encode(lastUpdatedAtValue)
        return instance

