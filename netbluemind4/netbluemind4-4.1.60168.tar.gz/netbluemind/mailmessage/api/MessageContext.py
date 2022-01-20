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

class MessageContext :
    def __init__( self):
        self.fromIdentity = None
        self.recipients = None
        self.messageClass = None
        self.subject = None
        pass

class __MessageContextSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MessageContext()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.mailflow.common.api.SendingAs import SendingAs
        from netbluemind.mailflow.common.api.SendingAs import __SendingAsSerDer__
        fromIdentityValue = value['fromIdentity']
        instance.fromIdentity = __SendingAsSerDer__().parse(fromIdentityValue)
        from netbluemind.mailflow.common.api.Recipient import Recipient
        from netbluemind.mailflow.common.api.Recipient import __RecipientSerDer__
        recipientsValue = value['recipients']
        instance.recipients = serder.ListSerDer(__RecipientSerDer__()).parse(recipientsValue)
        messageClassValue = value['messageClass']
        instance.messageClass = serder.STRING.parse(messageClassValue)
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
        fromIdentityValue = value.fromIdentity
        instance["fromIdentity"] = __SendingAsSerDer__().encode(fromIdentityValue)
        from netbluemind.mailflow.common.api.Recipient import Recipient
        from netbluemind.mailflow.common.api.Recipient import __RecipientSerDer__
        recipientsValue = value.recipients
        instance["recipients"] = serder.ListSerDer(__RecipientSerDer__()).encode(recipientsValue)
        messageClassValue = value.messageClass
        instance["messageClass"] = serder.STRING.encode(messageClassValue)
        subjectValue = value.subject
        instance["subject"] = serder.STRING.encode(subjectValue)
        return instance

