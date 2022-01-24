# -*- coding: utf-8 -*-
# @Time    : 10/14/21 5:21 PM
# @Author  : ZZK
# @File : RabbitMq.py
# @describe ：处理rabbitmq内容
import pika
import requests
import json
from retrying import retry
from pika.exceptions import AMQPError

def retry_if_rabbit_error(exception):
    return isinstance(exception, AMQPError)

class DealRabbitMQ(object):
    def __init__(self,host,user, passwd,port,url_port):
        """

        :param host:
        :param user:
        :param passwd:
        :param port:
        :param url_port:
        :param spider_main:
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.url_port = url_port

        credentials = pika.PlainCredentials(user, passwd)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials,
                                                                       heartbeat=0))  # heartbeat 表示7200时间没反应后就报错
        self.channel = connection.channel()
        self.channel.basic_qos(prefetch_size=0, prefetch_count=1)

    @retry(retry_on_exception=retry_if_rabbit_error)
    def get_count_by_url(self,queue_name):
        """
        :return: ready,unack,total
        """
        try:
            url = 'http://{0}:{1}/api/queues/%2f/{2}'.format(self.host,self.url_port,queue_name)
            r = requests.get(url, auth=(self.user, self.passwd))
            if r.status_code != 200:
                return -1
            res = r.json()
            # ready,unack,total
            true_count = self.channel.queue_declare(queue=queue_name, durable=True).method.message_count
            lax_count = max(true_count,res['messages'])
            return res['messages_ready'], res['messages_unacknowledged'], lax_count
            # return dic['messages']
        except Exception as e:
            print("rabbitmq connect url error:",e)
            raise ConnectionError("rabbitmq connect url error:{0}".format(e))

    def callback(self,ch, method, properties, body):
        """
        :param ch:
        :param method:
        :param properties:
        :param body:
        :return:
        """
        res = json.loads(body)
        self.spider_main(res)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    @retry(retry_on_exception=retry_if_rabbit_error)
    def consumer_mq(self,spider_main,queue_name):
        self.spider_main = spider_main
        self.channel.basic_consume(queue_name, self.callback, False)
        while self.channel._consumer_infos:
            ready_count, unack_count, total_count = self.get_count_by_url(queue_name)
            print("ready中的消息量：{0}",total_count)
            if total_count == 0:   #当真实消息量以及ready中全为0才代表消耗完
                self.channel.stop_consuming()  # 退出监听
            self.channel.connection.process_data_events(time_limit=1)
        try:
            self.channel.queue_delete(queue_name)
            print("消费完成：成功清除队列")
        except TypeError:
            print("消费完成：成功清除队列")

    @retry(retry_on_exception=retry_if_rabbit_error)
    def send_mq(self,queue_name,msg):
        """
        往错误队列中写入数据
        :return:
        """
        if not queue_name or not msg:
            raise ValueError("queue_name or msg is None")
        if 'error' not in queue_name:
            raise ValueError("queue_name is not error queue")
        self.channel.queue_declare(queue=queue_name, durable=True)

        self.channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=str(msg),
                              properties=pika.BasicProperties(delivery_mode=2)
                              )
        print('成功写入消息')

