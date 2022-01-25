
import traceback
from gnsq import Producer, Consumer, Message, NsqdHTTPClient
from ansq import open_connection
import asyncio
import orjson
import time

from hamunafs.utils.singleton_wrapper import Singleton


class MQManager(Singleton):
    def __init__(self, host, port, async_mq=False, init=True):
        if not self.need_init():
            return
        self.host = host
        self.port = port
        self.async_mq = async_mq
        self.inited = False
        if init:
            self._init()
        self._inited = True

    def _init(self):
        if self.async_mq:
            self.mq = asyncio.get_event_loop().run_until_complete(open_connection(self.host, self.port))
        else:
            self.addr = '{}:{}'.format(self.host, self.port)
            self.producer = Producer(nsqd_tcp_addresses=[self.addr])
            self.producer.start()
        self.inited = True

    async def get_mq_conn(self):
        return await open_connection(self.host, self.port)
            
    def _encode_message(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        else:
            message = orjson.dumps(message)
        return message
            
    def publish(self, topic, message, multi=False):
        try:
            if multi and isinstance(message, list):
                message = list(map(self._encode_message, message))
            else:
                message = self._encode_message(message)
            
            if multi:
                pub_func = self.producer.multipublish
            else:
                pub_func = self.producer.publish
            
            ret = pub_func(topic, message).decode()
        except Exception as e:
            traceback.print_exc()
            ret = False
        max_t = 5
        t = 0
        while ret != 'OK' and t < max_t: 
            try:
                ret = pub_func(topic, message).decode()
            except:
                ret = 'ERR'
            if ret == 'ERR':
                time.sleep(1)
            t += 1
        ret = ret == 'OK'
        if ret:
            print('nsq publish success!')
        return ret

    async def async_publish(self, topic, message, mq=None):
        try:
            if isinstance(message, str):
                message = message.encode('utf-8')
            elif isinstance(message, bytes):
                pass
            else:
                message = orjson.dumps(message)
            print('publishing')

            if mq is None:
                if self.inited:
                    mq = self.mq
                else:
                    self._init()
                    mq = self.mq

            ret = await mq.pub(topic, message)
            max_t = 5
            t = 0
            while not ret and t < max_t: 
                try:
                    ret = await mq.pub(topic, message)
                except:
                    ret = False
                t += 1
            return ret
        except Exception as e:
            print(traceback.print_exc())
            ret = False

if __name__ == "__main__":
    manager = MQManager('kafka.ai.hamuna.club', 34150, async_mq=True)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(manager._init_async())
    
    for i in range(100):
        ret = loop.run_until_complete(manager.async_publish('test', 'test'))
        # ret = manager.publish('test', 'test'.encode('utf-8'))
        print(ret)