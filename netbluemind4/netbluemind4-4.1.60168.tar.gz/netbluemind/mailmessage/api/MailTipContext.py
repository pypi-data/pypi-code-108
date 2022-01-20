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

class MailTipContext :
    def __init__( self):
        self.messageContext = None
        self.filter = None
        pass

class __MailTipContextSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailTipContext()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.mailmessage.api.MessageContext import MessageContext
        from netbluemind.mailmessage.api.MessageContext import __MessageContextSerDer__
        messageContextValue = value['messageContext']
        instance.messageContext = __MessageContextSerDer__().parse(messageContextValue)
        from netbluemind.mailmessage.api.MailTipFilter import MailTipFilter
        from netbluemind.mailmessage.api.MailTipFilter import __MailTipFilterSerDer__
        filterValue = value['filter']
        instance.filter = __MailTipFilterSerDer__().parse(filterValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.mailmessage.api.MessageContext import MessageContext
        from netbluemind.mailmessage.api.MessageContext import __MessageContextSerDer__
        messageContextValue = value.messageContext
        instance["messageContext"] = __MessageContextSerDer__().encode(messageContextValue)
        from netbluemind.mailmessage.api.MailTipFilter import MailTipFilter
        from netbluemind.mailmessage.api.MailTipFilter import __MailTipFilterSerDer__
        filterValue = value.filter
        instance["filter"] = __MailTipFilterSerDer__().encode(filterValue)
        return instance

