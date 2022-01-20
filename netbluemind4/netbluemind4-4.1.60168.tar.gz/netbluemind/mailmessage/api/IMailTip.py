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

IMailTip_VERSION = "4.1.60168"

class IMailTip(BaseEndpoint):
    def __init__(self, apiKey, url ,domainUid ):
        self.url = url
        self.apiKey = apiKey
        self.base = url +'/mailtip/{domainUid}'
        self.domainUid_ = domainUid
        self.base = self.base.replace('{domainUid}',domainUid)

    def getMailTips (self, mailtipContext ):
        postUri = "";
        __data__ = None
        __encoded__ = None
        from netbluemind.mailmessage.api.MailTipContext import MailTipContext
        from netbluemind.mailmessage.api.MailTipContext import __MailTipContextSerDer__
        __data__ = __MailTipContextSerDer__().encode(mailtipContext)
        __encoded__ = json.dumps(__data__)
        queryParams = {   };

        response = requests.post( self.base + postUri, params = queryParams, verify=False, headers = {'X-BM-ApiKey' : self.apiKey, 'Accept' : 'application/json', 'X-BM-ClientVersion' : IMailTip_VERSION}, data = __encoded__);
        from netbluemind.mailmessage.api.MailTips import MailTips
        from netbluemind.mailmessage.api.MailTips import __MailTipsSerDer__
        return self.handleResult__(serder.ListSerDer(__MailTipsSerDer__()), response)
