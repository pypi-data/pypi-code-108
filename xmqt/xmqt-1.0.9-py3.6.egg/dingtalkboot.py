import gc
import threading
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import UTC
from pytz import timezone
from dateutil.parser import parse
from dingtalkchatbot.chatbot import DingtalkChatbot
import time
import traceback
from queue import Queue
from random import randrange
from threading import Timer
from datetime import datetime
from datetime import timedelta
import json

class dingtalkboot:
    '''
        钉钉机器人
        pip install DingtalkChatbot
    '''

    def __init__(self, token, secret, client=None, usedingding=False, stocknos=[]):
        self.initxiaoding(token, secret)
        # 一分钟一次初始化小钉
        self.Time_threading_sign(60 * 30, token, secret)  # 60s*60min*24h*10day
        # 上一次消息文本
        self.lasttextmsg = ''

        self.client = client
        # 先进先出队列
        self.q = Queue(maxsize=5000)

        self.sendfinish = False

        self.usedingding = usedingding

        self.testtime = datetime.now()
        self.istest = False

        # if usedingding:
        #     print('启动线程')
        #     # 线程异步启动调度器，不堵塞主线程
        #     t1 = threading.Thread(target=self.Threading_start_sender, args=(5,))
        #     t1.start()

        self.stocknos = stocknos

    # @profile
    # 定时函数
    def Time_threading_sign(self, inc, token, secret):
        # print(datetime.now(), " 更新了access_token！")
        self.initxiaoding(token, secret)
        gc.collect()
        t = Timer(inc, self.Time_threading_sign, (inc, token, secret,))
        t.start()

    # @profile
    def initxiaoding(self, token, secret):
        if token == None or len(token) == 0:
            self.token = 'a0a98eebeb912e98d7895f44103fa367550dbf457559e5adb74e4403b675d16f'
            # https: // oapi.dingtalk.com / robot / send?access_token = 23f0d5b2eb470995ace7bbfa40b331193249ad8a2a917d2493000fd482d74184
            # https://oapi.dingtalk.com/robot/send?access_token=a0a98eebeb912e98d7895f44103fa367550dbf457559e5adb74e4403b675d16f
        import hmac
        import hashlib
        import base64
        import urllib.parse

        self.timestamp = str(round(time.time() * 1000))
        if secret == None or len(secret) == 0:
            self.secret = 'SEC451f6d91c9a029ccb93ca66d2c30f30f848d4617cdc9c33e384035088a834f06'

        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(self.timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        self.sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        # print(timestamp)
        # print(sign)

        # 初始化机器人小丁
        self.webhook = 'https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}'.format(self.token,
                                                                                                          self.timestamp,
                                                                                                          self.sign)  # 填写你自己创建的机器人
        self.headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.xiaoding = DingtalkChatbot(self.webhook)

    # @profile
    def savetxt2cache(self, message, no, buyid, level,stragename:str='empty'):
        """
            消息先缓存到服务器
        :param message:
        :return:
        """

        isoformat_time = datetime.now()
        msgbody = {
            "msg": message,
            "datetime": isoformat_time.isoformat('T') + 'Z',
            "no": no,
            "buyid": buyid,
            "level": level,
            "istest": self.istest,
            "testtime":self.testtime.isoformat('T') + 'Z',
            "stragename":stragename
        }
        influxdbpoints = [
            {
                "measurement": "signinfos_{}_{}".format(stragename,isoformat_time.strftime("%Y%m%d")),
                "time": isoformat_time.isoformat('T') + 'Z',
                "fields": msgbody
            }
        ]
        res = self.client.write_points(influxdbpoints)
        print('消息写入缓存：{}'.format(res))

    # @profile
    def shedulersend(self):
        print('启动定时器3')
        if not self.q.empty():
            print('发送消息')
            # message = str(self.q.get())
            self.xiaoding.send_text(msg=self.q.get(), is_at_all=True)

    # @profile
    def Threading_start_sender(self, interval: int = 5):
        # BlockingScheduler
        print('启动定时器0')
        scheduler = BackgroundScheduler()
        print('启动定时器')
        try:
            #timez = timezone('Asia/Shanghai')
            print('启动定时器4')
            #timezone=timez,
            scheduler.add_job(self.shedulersend, 'interval', seconds=interval, max_instances=10,
                              args=[])
            print('启动定时器2')
            scheduler.start()
        except Exception as ex:
            print(ex)


    # @profile
    def ifmsgsendfinish(self):
        while (not self.q.empty()):
            print(self.q.qsize())

    # @profile
    def sendtext(self, message, no, buyid, level: str = 'info',stragename:str='empty'):

        # data = {
        #     "msgtype": "text",
        #     "text": {
        #         "content": messgae
        #     }
        # }
        # r = requests.post(self.webhook, data=json.dumps(data), headers=self.headers)
        # print(r.text)
        # return r.text
        if self.lasttextmsg is None or len(self.lasttextmsg) == 0:
            self.lasttextmsg = message
            if self.client is not None:
                self.savetxt2cache(message, no, buyid, level,stragename)

            if self.usedingding:
                print('1')
                #print(message)
                # 增加输入股票池的过滤
                if self.stocknos.__contains__(no):
                    self.xiaoding.send_text(msg=message, is_at_all=True)
                    # print('2')
                    # print(message)
                    # self.q.put(message)

        else:
            if str(self.lasttextmsg).__eq__(str(message)):
                return
            else:
                self.lasttextmsg = message
                if self.client is not None:
                    self.savetxt2cache(message, no, buyid, level,stragename)

                if self.usedingding:
                    print('3')
                    #print(message)
                    # 增加输入股票池的过滤
                    if self.stocknos.__contains__(no):
                        self.xiaoding.send_text(msg=message, is_at_all=True)
                        # self.q.put(message)

    # @profile
    def sendimage(self, pic_url):
        self.xiaoding.send_image(pic_url=pic_url)

    # @profile
    def sendlink(self, title, text, message_url, pic_url=''):
        self.xiaoding.send_link(title=title, text=text, message_url=message_url, pic_url=pic_url)

