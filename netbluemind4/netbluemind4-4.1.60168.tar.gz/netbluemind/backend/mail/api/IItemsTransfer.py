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
import json
from netbluemind.python import serder
from netbluemind.python.client import BaseEndpoint

IItemsTransfer_VERSION = "4.1.60168"

class IItemsTransfer(BaseEndpoint):
    def __init__(self, apiKey, url ,fromMailboxUid ,toMailboxUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mail_items_transfer/{fromMailboxUid}/{toMailboxUid}'
        self.fromMailboxUid_ = fromMailboxUid
        self.base = self.base.replace('{fromMailboxUid}',fromMailboxUid)
        self.toMailboxUid_ = toMailboxUid
        self.base = self.base.replace('{toMailboxUid}',toMailboxUid)

    def move (self, itemIds ):
        postUri = "/move";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(itemIds)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IItemsTransfer_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemIdentifierSerDer__()), response)
    def copy (self, itemIds ):
        postUri = "/copy";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(itemIds)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IItemsTransfer_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemIdentifierSerDer__()), response)
