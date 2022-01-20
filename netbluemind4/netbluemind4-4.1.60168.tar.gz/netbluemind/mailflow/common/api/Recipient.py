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

class Recipient :
    def __init__( self):
        self.email = None
        self.name = None
        self.addressType = None
        self.recipientType = None
        pass

class __RecipientSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = Recipient()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        emailValue = value['email']
        instance.email = serder.STRING.parse(emailValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        from netbluemind.mailflow.common.api.RecipientAddressType import RecipientAddressType
        from netbluemind.mailflow.common.api.RecipientAddressType import __RecipientAddressTypeSerDer__
        addressTypeValue = value['addressType']
        instance.addressType = __RecipientAddressTypeSerDer__().parse(addressTypeValue)
        from netbluemind.mailflow.common.api.RecipientRecipientType import RecipientRecipientType
        from netbluemind.mailflow.common.api.RecipientRecipientType import __RecipientRecipientTypeSerDer__
        recipientTypeValue = value['recipientType']
        instance.recipientType = __RecipientRecipientTypeSerDer__().parse(recipientTypeValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        emailValue = value.email
        instance["email"] = serder.STRING.encode(emailValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        from netbluemind.mailflow.common.api.RecipientAddressType import RecipientAddressType
        from netbluemind.mailflow.common.api.RecipientAddressType import __RecipientAddressTypeSerDer__
        addressTypeValue = value.addressType
        instance["addressType"] = __RecipientAddressTypeSerDer__().encode(addressTypeValue)
        from netbluemind.mailflow.common.api.RecipientRecipientType import RecipientRecipientType
        from netbluemind.mailflow.common.api.RecipientRecipientType import __RecipientRecipientTypeSerDer__
        recipientTypeValue = value.recipientType
        instance["recipientType"] = __RecipientRecipientTypeSerDer__().encode(recipientTypeValue)
        return instance

