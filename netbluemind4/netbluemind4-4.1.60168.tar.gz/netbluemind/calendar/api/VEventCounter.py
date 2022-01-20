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

class VEventCounter :
    def __init__( self):
        self.originator = None
        self.counter = None
        pass

class __VEventCounterSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = VEventCounter()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.calendar.api.VEventCounterCounterOriginator import VEventCounterCounterOriginator
        from netbluemind.calendar.api.VEventCounterCounterOriginator import __VEventCounterCounterOriginatorSerDer__
        originatorValue = value['originator']
        instance.originator = __VEventCounterCounterOriginatorSerDer__().parse(originatorValue)
        from netbluemind.calendar.api.VEventOccurrence import VEventOccurrence
        from netbluemind.calendar.api.VEventOccurrence import __VEventOccurrenceSerDer__
        counterValue = value['counter']
        instance.counter = __VEventOccurrenceSerDer__().parse(counterValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.calendar.api.VEventCounterCounterOriginator import VEventCounterCounterOriginator
        from netbluemind.calendar.api.VEventCounterCounterOriginator import __VEventCounterCounterOriginatorSerDer__
        originatorValue = value.originator
        instance["originator"] = __VEventCounterCounterOriginatorSerDer__().encode(originatorValue)
        from netbluemind.calendar.api.VEventOccurrence import VEventOccurrence
        from netbluemind.calendar.api.VEventOccurrence import __VEventOccurrenceSerDer__
        counterValue = value.counter
        instance["counter"] = __VEventOccurrenceSerDer__().encode(counterValue)
        return instance

