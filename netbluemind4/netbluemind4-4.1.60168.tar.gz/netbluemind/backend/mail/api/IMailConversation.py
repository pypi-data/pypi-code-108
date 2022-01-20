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

IMailConversation_VERSION = "4.1.60168"

class IMailConversation(BaseEndpoint):
    def __init__(self, apiKey, url ,conversationContainer ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mail_conversation/{conversationContainer}'
        self.conversationContainer_ = conversationContainer
        self.base = self.base.replace('{conversationContainer}',conversationContainer)

    def getComplete (self, uid ):
        postUri = "/{uid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailConversation_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.Conversation import Conversation
        from netbluemind.backend.mail.api.Conversation import __ConversationSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__ConversationSerDer__()), response)
    def byFolder (self, folder , filter ):
        postUri = "";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(filter)
        __encoded__ = json.dumps(__data__)
        queryParams = {  'folder': folder    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailConversation_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.Conversation import Conversation
        from netbluemind.backend.mail.api.Conversation import __ConversationSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__ConversationSerDer__())), response)
    def removeMessage (self, containerUid , itemId ):
        postUri = "/{containerUid}/{itemId}/_message";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{containerUid}",containerUid);
        postUri = postUri.replace("{itemId}",itemId);
        queryParams = {    };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailConversation_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
