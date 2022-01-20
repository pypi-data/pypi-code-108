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

class Message :
    def __init__( self):
        self.sendingAs = None
        self.to = None
        self.cc = None
        self.recipients = None
        self.subject = None
        pass

class __MessageSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Message()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.mailflow.common.api.SendingAs import SendingAs
        from netbluemind.mailflow.common.api.SendingAs import __SendingAsSerDer__
        sendingAsValue = value['sendingAs']
        instance.sendingAs = __SendingAsSerDer__().parse(sendingAsValue)
        toValue = value['to']
        instance.to = serder.ListSerDer(serder.STRING).parse(toValue)
        ccValue = value['cc']
        instance.cc = serder.ListSerDer(serder.STRING).parse(ccValue)
        recipientsValue = value['recipients']
        instance.recipients = serder.ListSerDer(serder.STRING).parse(recipientsValue)
        subjectValue = value['subject']
        instance.subject = serder.STRING.parse(subjectValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.mailflow.common.api.SendingAs import SendingAs
        from netbluemind.mailflow.common.api.SendingAs import __SendingAsSerDer__
        sendingAsValue = value.sendingAs
        instance["sendingAs"] = __SendingAsSerDer__().encode(sendingAsValue)
        toValue = value.to
        instance["to"] = serder.ListSerDer(serder.STRING).encode(toValue)
        ccValue = value.cc
        instance["cc"] = serder.ListSerDer(serder.STRING).encode(ccValue)
        recipientsValue = value.recipients
        instance["recipients"] = serder.ListSerDer(serder.STRING).encode(recipientsValue)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        return instance

