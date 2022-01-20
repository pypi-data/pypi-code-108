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

class VEventSeries :
    def __init__( self):
        self.main = None
        self.occurrences = None
        self.counters = None
        self.properties = None
        self.icsUid = None
        self.acceptCounters = None
        pass

class __VEventSeriesSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VEventSeries()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.calendar.api.VEvent import VEvent
        from netbluemind.calendar.api.VEvent import __VEventSerDer__
        mainValue = value['main']
        instance.main = __VEventSerDer__().parse(mainValue)
        from netbluemind.calendar.api.VEventOccurrence import VEventOccurrence
        from netbluemind.calendar.api.VEventOccurrence import __VEventOccurrenceSerDer__
        occurrencesValue = value['occurrences']
        instance.occurrences = serder.ListSerDer(__VEventOccurrenceSerDer__()).parse(occurrencesValue)
        from netbluemind.calendar.api.VEventCounter import VEventCounter
        from netbluemind.calendar.api.VEventCounter import __VEventCounterSerDer__
        countersValue = value['counters']
        instance.counters = serder.ListSerDer(__VEventCounterSerDer__()).parse(countersValue)
        propertiesValue = value['properties']
        instance.properties = serder.MapSerDer(serder.STRING).parse(propertiesValue)
        icsUidValue = value['icsUid']
        instance.icsUid = serder.STRING.parse(icsUidValue)
        acceptCountersValue = value['acceptCounters']
        instance.acceptCounters = serder.BOOLEAN.parse(acceptCountersValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.calendar.api.VEvent import VEvent
        from netbluemind.calendar.api.VEvent import __VEventSerDer__
        mainValue = value.main
        instance["main"] = __VEventSerDer__().encode(mainValue)
        from netbluemind.calendar.api.VEventOccurrence import VEventOccurrence
        from netbluemind.calendar.api.VEventOccurrence import __VEventOccurrenceSerDer__
        occurrencesValue = value.occurrences
        instance["occurrences"] = serder.ListSerDer(__VEventOccurrenceSerDer__()).encode(occurrencesValue)
        from netbluemind.calendar.api.VEventCounter import VEventCounter
        from netbluemind.calendar.api.VEventCounter import __VEventCounterSerDer__
        countersValue = value.counters
        instance["counters"] = serder.ListSerDer(__VEventCounterSerDer__()).encode(countersValue)
        propertiesValue = value.properties
        instance["properties"] = serder.MapSerDer(serder.STRING).encode(propertiesValue)
        icsUidValue = value.icsUid
        instance["icsUid"] = serder.STRING.encode(icsUidValue)
        acceptCountersValue = value.acceptCounters
        instance["acceptCounters"] = serder.BOOLEAN.encode(acceptCountersValue)
        return instance

