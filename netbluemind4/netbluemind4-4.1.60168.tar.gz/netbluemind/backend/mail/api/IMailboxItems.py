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

IMailboxItems_VERSION = "4.1.60168"

class IMailboxItems(BaseEndpoint):
    def __init__(self, apiKey, url ,replicatedMailboxUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mail_items/{replicatedMailboxUid}'
        self.replicatedMailboxUid_ = replicatedMailboxUid
        self.base = self.base.replace('{replicatedMailboxUid}',replicatedMailboxUid)

    def filteredChangesetById (self, since , arg1 ):
        postUri = "/_filteredChangesetById";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {  'since': since    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemVersion import ItemVersion
        from netbluemind.core.container.model.ItemVersion import __ItemVersionSerDer__
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(__ItemVersionSerDer__()), response)
    def getForUpdate (self, id ):
        postUri = "/{id}/getForUpdate";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxItem import MailboxItem
        from netbluemind.backend.mail.api.MailboxItem import __MailboxItemSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxItemSerDer__()), response)
    def changeset (self, since ):
        postUri = "/_changeset";
        __data__ = None
        __encoded__ = None
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.STRING), response)
    def deleteFlag (self, flagUpdate ):
        postUri = "/_deleteFlag";
        __data__ = None
        __encoded__ = None
        from netbluemind.backend.mail.api.flags.FlagUpdate import FlagUpdate
        from netbluemind.backend.mail.api.flags.FlagUpdate import __FlagUpdateSerDer__
        __data__ = __FlagUpdateSerDer__().encode(flagUpdate)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
    def changesetById (self, since ):
        postUri = "/_changesetById";
        __data__ = None
        __encoded__ = None
        queryParams = {  'since': since   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangeset import ContainerChangeset
        from netbluemind.core.container.model.ContainerChangeset import __ContainerChangesetSerDer__
        return self.handleResult__(__ContainerChangesetSerDer__(serder.LONG), response)
    def unreadItems (self):
        postUri = "/_unread";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.LONG), response)
    def uploadPart (self, part ):
        postUri = "/_part";
        __data__ = None
        __encoded__ = None
        __data__ = serder.STREAM.encode(part)
        __encoded__ = __data__
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(serder.STRING, response)
    def create (self, value ):
        postUri = "";
        __data__ = None
        __encoded__ = None
        from netbluemind.backend.mail.api.MailboxItem import MailboxItem
        from netbluemind.backend.mail.api.MailboxItem import __MailboxItemSerDer__
        __data__ = __MailboxItemSerDer__().encode(value)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.ImapItemIdentifier import ImapItemIdentifier
        from netbluemind.backend.mail.api.ImapItemIdentifier import __ImapItemIdentifierSerDer__
        return self.handleResult__(__ImapItemIdentifierSerDer__(), response)
    def getCompleteById (self, id ):
        postUri = "/{id}/completeById";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxItem import MailboxItem
        from netbluemind.backend.mail.api.MailboxItem import __MailboxItemSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(__ItemValueSerDer__(__MailboxItemSerDer__()), response)
    def recentItems (self, deliveredOrUpdatedAfter ):
        postUri = "/_recent";
        __data__ = None
        __encoded__ = None
        __data__ = serder.DATE.encode(deliveredOrUpdatedAfter)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.LONG), response)
    def unexpunge (self, itemId ):
        postUri = "/_unexpunge/{itemId}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{itemId}",itemId);
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemIdentifier import ItemIdentifier
        from netbluemind.core.container.model.ItemIdentifier import __ItemIdentifierSerDer__
        return self.handleResult__(__ItemIdentifierSerDer__(), response)
    def getVersion (self):
        postUri = "/_version";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(serder.LONG, response)
    def expunge (self):
        postUri = "/_expunge";
        __data__ = None
        __encoded__ = None
        queryParams = {  };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def count (self, arg0 ):
        postUri = "/_count";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.ItemFlagFilter import ItemFlagFilter
        from netbluemind.core.container.model.ItemFlagFilter import __ItemFlagFilterSerDer__
        __data__ = __ItemFlagFilterSerDer__().encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Count import Count
        from netbluemind.core.container.api.Count import __CountSerDer__
        return self.handleResult__(__CountSerDer__(), response)
    def fetchComplete (self, imapUid ):
        postUri = "/eml/{imapUid}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{imapUid}",imapUid);
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return response.content
    def sortedIds (self, sorted ):
        postUri = "/_sorted";
        __data__ = None
        __encoded__ = None
        from netbluemind.core.container.model.SortDescriptor import SortDescriptor
        from netbluemind.core.container.model.SortDescriptor import __SortDescriptorSerDer__
        __data__ = __SortDescriptorSerDer__().encode(sorted)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(serder.ListSerDer(serder.LONG), response)
    def itemChangelog (self, uid , arg1 ):
        postUri = "/{uid}/_itemchangelog";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{uid}",uid);
        __data__ = serder.LONG.encode(arg1)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ItemChangelog import ItemChangelog
        from netbluemind.core.container.model.ItemChangelog import __ItemChangelogSerDer__
        return self.handleResult__(__ItemChangelogSerDer__(), response)
    def addFlag (self, flagUpdate ):
        postUri = "/_addFlag";
        __data__ = None
        __encoded__ = None
        from netbluemind.backend.mail.api.flags.FlagUpdate import FlagUpdate
        from netbluemind.backend.mail.api.flags.FlagUpdate import __FlagUpdateSerDer__
        __data__ = __FlagUpdateSerDer__().encode(flagUpdate)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.api.Ack import Ack
        from netbluemind.core.container.api.Ack import __AckSerDer__
        return self.handleResult__(__AckSerDer__(), response)
    def multipleDeleteById (self, arg0 ):
        postUri = "/_multipleDelete";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def removePart (self, partId ):
        postUri = "/{partId}/_part";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{partId}",partId);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def updateById (self, id , value ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.backend.mail.api.MailboxItem import MailboxItem
        from netbluemind.backend.mail.api.MailboxItem import __MailboxItemSerDer__
        __data__ = __MailboxItemSerDer__().encode(value)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.ImapAck import ImapAck
        from netbluemind.backend.mail.api.ImapAck import __ImapAckSerDer__
        return self.handleResult__(__ImapAckSerDer__(), response)
    def multipleById (self, ids ):
        postUri = "/_multipleById";
        __data__ = None
        __encoded__ = None
        __data__ = serder.ListSerDer(serder.LONG).encode(ids)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.MailboxItem import MailboxItem
        from netbluemind.backend.mail.api.MailboxItem import __MailboxItemSerDer__
        from netbluemind.core.container.model.ItemValue import ItemValue
        from netbluemind.core.container.model.ItemValue import __ItemValueSerDer__
        return self.handleResult__(serder.ListSerDer(__ItemValueSerDer__(__MailboxItemSerDer__())), response)
    def containerChangelog (self, arg0 ):
        postUri = "/_changelog";
        __data__ = None
        __encoded__ = None
        __data__ = serder.LONG.encode(arg0)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.container.model.ContainerChangelog import ContainerChangelog
        from netbluemind.core.container.model.ContainerChangelog import __ContainerChangelogSerDer__
        return self.handleResult__(__ContainerChangelogSerDer__(), response)
    def fetch (self, imapUid , address , encoding , mime , charset , filename ):
        postUri = "/part/{imapUid}/{address}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{imapUid}",imapUid);
        postUri = postUri.replace("{address}",address);
        queryParams = {    'encoding': encoding  , 'mime': mime  , 'charset': charset  , 'filename': filename   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return response.content
    def deleteById (self, id ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        queryParams = {   };

        response = requests.delete( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        return self.handleResult__(None, response)
    def createById (self, id , value ):
        postUri = "/id/{id}";
        __data__ = None
        __encoded__ = None
        postUri = postUri.replace("{id}",id);
        from netbluemind.backend.mail.api.MailboxItem import MailboxItem
        from netbluemind.backend.mail.api.MailboxItem import __MailboxItemSerDer__
        __data__ = __MailboxItemSerDer__().encode(value)
        __encoded__ = json.dumps(__data__)
        queryParams = {    };

        response = requests.put( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.backend.mail.api.ImapAck import ImapAck
        from netbluemind.backend.mail.api.ImapAck import __ImapAckSerDer__
        return self.handleResult__(__ImapAckSerDer__(), response)
    def allIds (self, filter , knownContainerVersion , limit , offset ):
        postUri = "/_itemIds";
        __data__ = None
        __encoded__ = None
        queryParams = {  'filter': filter  , 'knownContainerVersion': knownContainerVersion  , 'limit': limit  , 'offset': offset   };

        response = requests.get( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailboxItems_VERSION}, data = __encoded__);
        from netbluemind.core.api.ListResult import ListResult
        from netbluemind.core.api.ListResult import __ListResultSerDer__
        return self.handleResult__(__ListResultSerDer__(serder.LONG), response)
