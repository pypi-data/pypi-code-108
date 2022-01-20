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

class AttachedFile :
    def __init__( self):
        self.publicUrl = None
        self.expirationDate = None
        self.name = None
        pass

class __AttachedFileSerDer__:
    def __init__( self ):
        pass

    def parse(self, value):
        if(value == None):
            return None
        instance = AttachedFile()

        self.parseInternal(value, instance)
        return instance

    def parseInternal(self, value, instance):
        publicUrlValue = value['publicUrl']
        instance.publicUrl = serder.STRING.parse(publicUrlValue)
        expirationDateValue = value['expirationDate']
        instance.expirationDate = serder.LONG.parse(expirationDateValue)
        nameValue = value['name']
        instance.name = serder.STRING.parse(nameValue)
        return instance

    def encode(self, value):
        if(value == None):
            return None
        instance = dict()
        self.encodeInternal(value,instance)
        return instance

    def encodeInternal(self, value, instance):

        publicUrlValue = value.publicUrl
        instance["publicUrl"] = serder.STRING.encode(publicUrlValue)
        expirationDateValue = value.expirationDate
        instance["expirationDate"] = serder.LONG.encode(expirationDateValue)
        nameValue = value.name
        instance["name"] = serder.STRING.encode(nameValue)
        return instance

