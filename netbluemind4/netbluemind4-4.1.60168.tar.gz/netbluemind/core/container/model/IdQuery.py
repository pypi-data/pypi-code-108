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

class IdQuery :
    def __init__( self):
        self.filter = None
        self.limit = None
        self.offset = None
        self.knownContainerVersion = None
        pass

class __IdQuerySerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = IdQuery()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        filterValue = value['filter']
        instance.filter = __ItemFlagFilterSerDer__().parse(filterValue)
        limitValue = value['limit']
        instance.limit = serder.INT.parse(limitValue)
        offsetValue = value['offset']
        instance.offset = serder.INT.parse(offsetValue)
        knownContainerVersionValue = value['knownContainerVersion']
        instance.knownContainerVersion = serder.LONG.parse(knownContainerVersionValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        filterValue = value.filter
        instance["filter"] = __ItemFlagFilterSerDer__().encode(filterValue)
        limitValue = value.limit
        instance["limit"] = serder.INT.encode(limitValue)
        offsetValue = value.offset
        instance["offset"] = serder.INT.encode(offsetValue)
        knownContainerVersionValue = value.knownContainerVersion
        instance["knownContainerVersion"] = serder.LONG.encode(knownContainerVersionValue)
        return instance

