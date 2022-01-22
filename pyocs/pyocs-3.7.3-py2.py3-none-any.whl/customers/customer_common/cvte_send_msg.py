#!/usr/bin/python2
#coding:utf-8
import sys 
import json
import requests
import urllib
import logging
import time

class Messager(object):
    def get_authorization_str(self,key):
        params = urllib.urlencode({
            'appid':'ea19828c-5514-48b2-b510-2f8ed36ed12b', 
            'secret':'474b95da-9ebe-463c-8f16-'+key
            })
        f = urllib.urlopen(
            "https://itapis.cvte.com/iac/app/access_token?%s" %params)
        content=json.loads(f.read().decode("utf-8"))
        return content["data"]["accessToken"]

    def __init__(self,msgType):
        self.url = ('http://api.backend.cvteapi.com/wopush-platform'
        '/push/internal')
        self._message_body = {
            'canReply':'false',
            'notifyWay':msgType,
            'content':'122',
            'title':'信息中心系统服务部',
            'config':'{\"sms\":{\"type\":\"1\"}}',
            'toUser':'[{\"username\":\"shenyingfeng\"}]'
        }

    def finish_sending(self,resp):
        print("{response}".format(**self.gather_info(resp)))
        print("{url}\n{body}\n{response}".format(**self.gather_info(resp)))

    def change_field(self, field, value):
        self._message_body[field] = value

    def _change_content(self, title, content):
        self.change_field('title', title)
        self.change_field('content', content)

    def add_targets(self, targets):
        self._message_body['toUser']  = '[{\"username\":\"'+targets+'\"}]'

    def gather_info(self, response_object):
        summary = {'url': response_object.request.url,
                   'body': response_object.request.body,
                   'response': response_object.text}
        return summary

    def send(self, content, title='message for cvte it'):
        self._change_content(title, content)
        return self

    def to(self, user, key):
        self.add_targets(user)
        auth = self.get_authorization_str(key)
        resp = requests.post(self.url+'?',
                             json=self._message_body,
                             headers={'access-token': auth})
        self.finish_sending(resp)


def get_msg_type(msgType):
    intType=0
    strType=""
    for one in dictMsgType:
        if(one in msgType):
            intType =intType + dictMsgType[one]

    if(intType == 0):
        print ("msgType ERROR")
        sys.exit(1)
    else:
        return str( '%04d' % intType)

if __name__ == '__main__':
    dictMsgType = {'SMS': 1, 'MAIL': 10, 'IM': 100, 'WX': 1000}
    #  参数判断
    if len(sys.argv) == 5 :
        subject = "Notify MSG"
    elif len(sys.argv) == 6 :
        subject = sys.argv[5]
    else:
        print ("Parameter error,use as:python cvte_send_msg.py $key "
            "$msgType $toSomeone $content $subject(Optional for mail)")
        sys.exit(1)

    key = sys.argv[1]
    msgType = sys.argv[2]
    to_user = sys.argv[3]
    content = sys.argv[4]
    strType = get_msg_type(msgType)

    logging.basicConfig(filename='./message_cvte_send_msg.log', filemode='a+',
        format=(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + ',' +
        key + ',' + msgType + ',' + to_user + ',' + content + ',' + subject))
    try:
        messager = Messager(strType)
        messager.send(content.strip(),subject).to(to_user,key)
        sys.exit(0)
    except Exception as e:
        logging.exception(e)
        sys.exit(1)    
