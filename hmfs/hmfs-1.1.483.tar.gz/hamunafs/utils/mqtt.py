import paho.mqtt.client as mqtt
import time
import os
import json
from threading import Thread
from diskcache import Deque

import uuid


class MQTTClient:
    def __init__(self, client_id, username, password, local_cache_path='../mqtt_offlines'):
        self.connected = False

        self.client = mqtt.Client(client_id=client_id + str(uuid.uuid1()), clean_session=False)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.username_pw_set(username, password)

        self.subscribes = []

        # FileIO.create_dir_if_not_exists(local_cache_path)
        os.makedirs(local_cache_path, exist_ok=True)
        self.offlines = Deque(directory=local_cache_path)

    def connect(self, host, port):
        self.thread = Thread(target=self.__mqtt_connect, args=(host, port))
        self.thread.setDaemon(True)
        self.thread.start()
        return self

    def subscribe(self, topic, qos):
        self.subscribes.append((topic, qos))

    def register_on_message_handler(self, handler):
        self.on_message_handler = handler

    def join(self):
        if self.thread:
            self.thread.join()

    def __mqtt_connect(self, host, port):
        try:
            self.client.connect(host, port=port, keepalive=60)
            self.client.loop_forever()
        except Exception as e:
            print(e)

    def _on_connect(self, client, userdata, flags, rc):
        if not self.connected:
            self.connected = True
            print("mqtt service connected")
            
            for subscribe in self.subscribes:
                print('subscribing topic: {}/qos:{}...'.format(subscribe[0], subscribe[1]))
                self.client.subscribe(subscribe[0], subscribe[1])

            while len(self.offlines) > 0:
                print('sending offlines...')
                o_data = self.offlines.pop()
                try:
                    if o_data['expires'] >= time.time() and o_data['retries'] < 5:
                        self.client.publish(o_data['topic'], o_data['message'], qos=0)
                except Exception as e:
                    o_data['retries'] += 1
                    self.offlines.append(o_data)

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        print("mqtt service disconnected")

    def _on_message(self, client, userdata, msg):
        if self.on_message_handler:
            self.on_message_handler(client, userdata, msg)

    def _on_publish(self, client, userdata, msg):
        print('published')

    def publish(self, message, topic, retain=False, qos=0, expires=7200):
        if not isinstance(message, str):
            message = json.dumps(message)

        tries = 0
        while not self.connected and tries < 5:
            time.sleep(5)
            tries += 1
        
        if tries >= 5:
            self.offlines.append({
                'topic': topic,
                'message': message,
                'expires': time.time() + expires * 1000,
                'retries': 0
            })
        else:
            try:
                self.client.publish(topic, payload=message, retain=retain, qos=qos)
                return True
            except Exception as e:
                pass
            return False
            