import asyncio
import json
import os
import sys
from typing import Type
import threading

import pika
import asyncio
import aio_pika
import simplejson as json
from aio_pika import ExchangeType
from coolname import generate_slug
import uuid
import requests
from pipedash import DrawableComponent, TDrawableComponent
from pipedash.helper import Serializable, serializeDTO, log


class PipedashWorker:
    _api_key = None
    _worker_id = None
    _secret_key = None
    _registeredComponents = {}
    _hearbeat_queue = None
    _heartbeat_channel = None


    def __init__(self, loop = None):
        self.register_unique_id()
        self._mq_channel = None
        self._rabbit_server = "pipedash.io"
        self._rabbit_port = 5672
        self._rabbit_user = os.getenv("rabbit_user")
        self._rabbit_pwd = os.getenv("rabbit_pwd")
        if os.getenv("rabbit_ip") is not None:
            self._rabbit_server = os.getenv("rabbit_ip")

        if self._rabbit_user is None:
            self._rabbit_user = self._api_key
        if self._rabbit_pwd is None:
            self._rabbit_pwd = self._secret_key


        if loop is None:
            loop = asyncio.new_event_loop()
        self.loop = loop


        return None

    def get_worker_class(self, identifier) -> DrawableComponent:
        d = self._registeredComponents[identifier]
        if d is not None:
            return d["class"]()

        return None

    def on_worker_command(self, commandMessage):
        identifier = commandMessage["component"]["component"]["identifier"]
        jobId = commandMessage["jobId"]
        instance = self.get_worker_class(identifier)
        if instance is None:
            raise Exception("Can not load your class")
        try:
            instance.run_draw_data(commandMessage)
        except Exception as e:
            print("Error in on_worker_command", e)
            self.on_worker_error(commandMessage, e)

        ## lets send data back
        plot_data = instance.get_data()
        self.send_worker_response(jobId, {
            "data": plot_data,
            "responseType": "data"
        })

    def on_worker_error(self, commandMessage, e):
        jobId = commandMessage["jobId"]
        self.send_worker_response(jobId, {
            "responseType": "error",
            "error": str(e)
        })

    def send_worker_response(self, jobId, message):

        message = {
            "worker_id": self._worker_id,
            "type": "job_response",
            "api_key": self._api_key,
            "secret_key": self._secret_key,
            "jobId": jobId,
            "message": message
        }
        message_str = json.dumps(message, default=serializeDTO)

        self._mq_channel.basic_publish("", "pipedash_command_queue", message_str)

    async def run_worker_queue(self):
        connection = await aio_pika.connect_robust(
            "amqp://thoren:thoren@78.47.96.243:5672/", loop=self.loop
        )

        async with connection:

            # Creating channel
            self.channel = await connection.channel()  # type: aio_pika.Channel
            await self.channel.set_qos(prefetch_count=1)

            # Declaring queue
            queue = await self.channel.declare_queue(
                "",
                durable=True,
                exclusive=True
            )

            src_exchange = await self.channel.declare_exchange(
                "pipedash_worker_queue", durable=True, type=ExchangeType.TOPIC
            )

            for key in self._registeredComponents.keys():
                m = self._registeredComponents[key]
                await queue.bind(src_exchange, m["identifier"])

            async with queue.iterator() as queue_iter:
                # Cancel consuming after __aexit__
                async for message in queue_iter:
                    async with message.process():
                        try:
                            message_data = json.loads(message.body)

                            self.on_worker_command(message_data)

                        except Exception as e:
                            log.error(e)
                            pass


            print("ifnished")


        return True

    def connect_to_queue(self):
        try:
            #"amqp://" + self.rabbit_info.user + ":" + self.rabbit_info.pwd + "@" + self.rabbit_info.ip + ":" + self.rabbit_info.port + "/"

            # NOTE: These parameters work with all Pika connection types
            params = pika.ConnectionParameters(
                host=self._rabbit_server,
                port=self._rabbit_port,
                credentials=pika.PlainCredentials(self._rabbit_user, self._rabbit_pwd),
                heartbeat=600,
                blocked_connection_timeout=300)

            self._connection = pika.BlockingConnection(params)

            self._mq_channel = self._connection.channel()

            self._mq_channel.exchange_declare("pipedash_heartbeat_queue", durable=True)
            self._mq_channel.queue_declare("pipedash_command_queue", durable=True)


        except Exception as e:
            print(e)
            pass



    def on_worker_job(self, channel, method_frame, header_frame, body):

        # Get ten messages and break out
        # Display the message parts
        print(body)

        channel.basic_ack(delivery_tag=method_frame.delivery_tag)



    def get_worker_id(self):
        return self.registrar.worker_id

    def register_unique_id(self):
        file_name = os.path.basename(sys.argv[0])
        fixed_worker_file = "." + file_name + ".pid"

        if os.path.exists(fixed_worker_file):
            with open(fixed_worker_file, 'r') as file:
                self._worker_id = file.read()
        else:
            self._worker_id = self.generate_worker_id()
            f = open(fixed_worker_file, "a")
            f.write(self._worker_id)
            f.close()

    def generate_worker_id(self):
        return self.get_random_string()

    def get_random_string(self, length=3):
        return generate_slug(length)+"-"+str(uuid.uuid4())

    def get_backend(self):
        if os.getenv("BACKEND") is not None:
            return os.getenv("BACKEND")
        return "https://pipedash.io"

    def check_api_key(self):
        response = requests.post(self.get_backend()+"/api/check_api_key", {"api_key": self._api_key,
                                                                           "api_secret": self._secret_key})
        if response.status_code == 200:
            return True
        raise Exception("Your api key is not okay or you are not allowed to use this api.")
        return False

    def connect_consumer(self):
        self.loop.run_until_complete(self.run_worker_queue())

    def connect(self, api_key: str, secret_key: str):
        if api_key is not None:
            self._secret_key = secret_key
            self._api_key = api_key
            # check api key
            self.check_api_key()
            self.connect_to_queue()

            # after 3 seconds all registrations need to be done.
            threading.Timer(3.0, self.connect_consumer).start()
            self.send_heartbeat_message()

        else:
            raise Exception("You need a correct api key to work")
        return True

    def check_component(self, component: Type[TDrawableComponent]):

        instance : DrawableComponent = component()
        properties = instance.get_properties()

        for p in properties:
            if not p.validate():
                raise Exception("Please check your properties again. Something is wrong.")
        return instance

    def send_heartbeat_message(self):
        threading.Timer(5.0, self.send_heartbeat_message).start()
        list_of_identifier = []
        for key in self._registeredComponents.keys():
            list_of_identifier.append(key)

        message = {
            "worker_id": self._worker_id,
            "api_key": self._api_key,
            "api_secret": self._secret_key,
            "identifiers": list_of_identifier,
            "type": "heartbeat"
        }
        message_str = json.dumps(message, default=serializeDTO)

        if self._mq_channel is not None:
            self._mq_channel.basic_publish("", "pipedash_heartbeat_queue", message_str)
        else:
            log.error("Your message channel is not connected! Can not send heartbeat!")

    def send_registration_data(self, registration_data):

        message = {
            "worker_id": self._worker_id,
            "api_secret": self._secret_key,
            "api_key": self._api_key,
            "type": "register_drawable",
            "data": registration_data
        }
        message_str = json.dumps(message, default=serializeDTO)

        if self._mq_channel is not None:
            self._mq_channel.basic_publish("", "pipedash_command_queue", message_str)
        else:
            log.error("Your message channel is not connected! Can not send any command!")

        pass

    def registerDrawable(self, component: Type[TDrawableComponent], name: str, description: str, identifier: str, imageurl: str):
        if identifier is None:
            identifier = component.__name__
        if len(identifier) < 15:
            raise("Please use a class name for your component which is very unique. Maybe add your project name to it or use the identifier option.")
        instance = self.check_component(component)


        properties = json.dumps(instance.get_properties(), default=serializeDTO)

        registration_data = {
            "identifier": identifier,
            "class": component,
            "imageUrl": imageurl,
            "icon": instance.get_icon(),
            "name": name,
            "description": description,
            "properties": properties
        }

        self.send_registration_data(registration_data)

        self._registeredComponents[identifier] = registration_data

        return True