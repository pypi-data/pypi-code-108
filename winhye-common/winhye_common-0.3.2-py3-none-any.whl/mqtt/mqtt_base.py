import base64
import hmac
import json
import time
import uuid
from hashlib import sha1

from paho.mqtt import client as mqtt

from winhye_common.utils.exception_base import WinhyeException, ExceptionCode
from winhye_common.winhye_logger import logging as logging

__all__ = ['MqttClint', 'MqttException', 'MqttSendMessageException']
logger = logging.getLogger()


class MqttException(WinhyeException):
    """mqtt exception
    """

    def __init__(self, message: str):
        super(MqttException, self).__init__(ExceptionCode.mqtt, message)


class MqttSendMessageException(WinhyeException):
    """Used only when mqtt message sending fails
    """

    def __init__(self, message: str):
        super(MqttSendMessageException, self).__init__(ExceptionCode.mqtt, message)


class MqttClint:
    def __init__(self, mqtt_config: dict):
        """
        topic 在start之前确定就可用
        :param mqtt_config: {
            "AccessKey_ID": 账号AccessKey 从阿里云账号控制台获取
            "AccessKey_Secret": 账号secretKey 从阿里云账号控制台获取
            "instance_id": 实例 ID，购买后从产品控制台获取
            "group_id": MQTT GroupID,创建实例后从 MQTT 控制台创建
            "broker": url地址
            "port": 端口
        }
        """
        access_key = mqtt_config["AccessKey_ID"]
        secret_key = mqtt_config["AccessKey_Secret"]
        instance_id = mqtt_config["instance_id"]
        group_id = mqtt_config["group_id"]
        # client_id不能重复，所以使用当前时间
        self.client_id = group_id + '@@@' + str(uuid.uuid1())
        username = 'Signature' + '|' + access_key + '|' + instance_id
        password = base64.b64encode(hmac.new(secret_key.encode(), self.client_id.encode(), sha1).digest()).decode()

        self.broker = mqtt_config["broker"]
        self.port = mqtt_config["port"]
        self.topic = mqtt_config.get("topic", "")

        self.init_config()

        self.client = mqtt.Client(self.client_id, protocol=mqtt.MQTTv311, clean_session=True)
        self.client.username_pw_set(username, password)
        self.client.connect(self.broker, self.port, 60)

    def init_config(self):
        pass

    def init_same_attr(self, *args, **kwargs):
        pass

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected with result code " + str(rc))  # 打印连接状态
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        """
        回调函数。能取到消息值的位置
        :param client:
        :param userdata:
        :param msg:
        :return:
        """
        logger.info(msg.topic + " " + ":" + str(msg.payload))  # 打印接受的消息

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logger.info("On Subscribed: qos = %d" % granted_qos)

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.info("Unexpected disconnection %s" % rc)

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_disconnect = self.on_disconnect
        self.client.loop_forever()

    def send_message(self, topic: str, data: dict):
        """
        发送消息
        :param topic:  主题
        :param data:  参数
        :return:
        """
        data = json.dumps(data)
        logger.debug(f"topic: {topic}, mqtt_data: {data}")
        rc = self.client.publish(topic, payload=data, qos=0)  # 发送消息
        logger.debug(f"clint_id: {self.client_id}, status: {rc[0]}, offset: {rc[1]}, published: {rc.is_published()}")

        # 如果发送消息失败则重连重试三次
        if rc[0] == 4:
            re_num = 0
            while re_num < 3:
                re_num += 1
                self.client.reconnect()
                time.sleep(1)
                rc = self.client.publish(topic, payload=data, qos=0)  # 发送消息
                logger.debug(
                    f"clint_id: {self.client_id}, status: {rc[0]}, offset: {rc[1]}, published: {rc.is_published()}")
                if rc[0] == 0 and rc.is_published():
                    break
            else:
                raise MqttSendMessageException("mqtt消息发送失败，请联系管理员")
