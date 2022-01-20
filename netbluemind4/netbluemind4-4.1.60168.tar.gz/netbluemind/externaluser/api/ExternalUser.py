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

from netbluemind.directory.api.DirBaseValue import DirBaseValue
from netbluemind.directory.api.DirBaseValue import __DirBaseValueSerDer__
class ExternalUser (DirBaseValue):
    def __init__( self):
        DirBaseValue.__init__(self)
        self.contactInfos = None
        pass

class __ExternalUserSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = ExternalUser()
        __DirBaseValueSerDer__().parseInternal(value,instance)

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        contactInfosValue = value['contactInfos']
        instance.contactInfos = __VCardSerDer__().parse(contactInfosValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):
        __DirBaseValueSerDer__().encodeInternal(value,instance)

        from netbluemind.addressbook.api.VCard import VCard
        from netbluemind.addressbook.api.VCard import __VCardSerDer__
        contactInfosValue = value.contactInfos
        instance["contactInfos"] = __VCardSerDer__().encode(contactInfosValue)
        return instance

