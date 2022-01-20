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

class MailboxItem :
    def __init__( self):
        self.body = None
        self.imapUid = None
        self.flags = None
        pass

class __MailboxItemSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = MailboxItem()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.backend.mail.api.MessageBody import MessageBody
        from netbluemind.backend.mail.api.MessageBody import __MessageBodySerDer__
        bodyValue = value['body']
        instance.body = __MessageBodySerDer__().parse(bodyValue)
        imapUidValue = value['imapUid']
        instance.imapUid = serder.LONG.parse(imapUidValue)
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import MailboxItemFlag
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import __MailboxItemFlagSerDer__
        flagsValue = value['flags']
        instance.flags = serder.ListSerDer(__MailboxItemFlagSerDer__()).parse(flagsValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        from netbluemind.backend.mail.api.MessageBody import MessageBody
        from netbluemind.backend.mail.api.MessageBody import __MessageBodySerDer__
        bodyValue = value.body
        instance["body"] = __MessageBodySerDer__().encode(bodyValue)
        imapUidValue = value.imapUid
        instance["imapUid"] = serder.LONG.encode(imapUidValue)
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import MailboxItemFlag
        from netbluemind.backend.mail.api.flags.MailboxItemFlag import __MailboxItemFlagSerDer__
        flagsValue = value.flags
        instance["flags"] = serder.ListSerDer(__MailboxItemFlagSerDer__()).encode(flagsValue)
        return instance

