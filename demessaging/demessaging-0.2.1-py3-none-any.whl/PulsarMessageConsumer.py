import asyncio
import base64
import concurrent.futures
import json
import sys
import textwrap
import threading
from datetime import datetime
from sys import stderr
from time import sleep
from typing import Dict, List, Optional

import websocket

from demessaging.PulsarConnection import PulsarConnection
from demessaging.PulsarMessageConstants import (
    MessageType,
    PropertyKeys,
    PulsarConfigKeys,
)

# patch the asyncio loop if we are on windows
# see https://github.com/tornadoweb/tornado/issues/2751
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class PulsarMessageConsumer(PulsarConnection):
    INITIAL_TIMEOUT_SLEEP = 10  # seconds
    MAX_CONNECTION_ATTEMPTS = 20
    MAX_PAYLOAD_SIZE = 4 * 1024 * 1024
    PULSAR_PING_INTERVAL = 60  # 1min

    def __init__(
        self,
        pulsar_config: dict,
        handle_request,
        handle_response=None,
        module_info: dict = None,
    ):
        super().__init__(pulsar_config)
        self.pulsarConfig = pulsar_config
        self.handle_request = handle_request
        self.handle_response = handle_response
        self.module_info = module_info

        self.check_config()

        # init event loop
        self.loop = asyncio.get_event_loop()
        self.request_semaphore: Optional[threading.BoundedSemaphore] = None
        if pulsar_config.get(PulsarConfigKeys.QUEUE_SIZE) is not None:
            self.request_semaphore = threading.BoundedSemaphore(
                value=pulsar_config.get(PulsarConfigKeys.QUEUE_SIZE, 1)
            )
        self.pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=pulsar_config.get(PulsarConfigKeys.MAX_WORKERS)
        )
        self.send_lock = threading.Lock()

        self.connectionAttempts = 0
        self.reconnectTimeout = PulsarMessageConsumer.INITIAL_TIMEOUT_SLEEP
        self.subscription = None
        self.producers: Dict[str, websocket.WebSocket] = {}

    def check_config(self):
        for key in PulsarConfigKeys:
            # check for config key in config
            if (
                key == PulsarConfigKeys.QUEUE_SIZE
                or key == PulsarConfigKeys.MAX_WORKERS
            ):
                # skip optinal keys
                continue

            if key not in self.pulsarConfig:
                raise AttributeError("Missing pulsar config property: " + key)

        if (
            self.pulsarConfig.get(PulsarConfigKeys.QUEUE_SIZE) is not None
            and self.pulsarConfig.get(PulsarConfigKeys.MAX_WORKERS) is not None
            and self.pulsarConfig.get(PulsarConfigKeys.QUEUE_SIZE)
            < self.pulsarConfig.get(PulsarConfigKeys.MAX_WORKERS)
        ):
            raise AttributeError(
                f"{PulsarConfigKeys.QUEUE_SIZE}({self.pulsarConfig[PulsarConfigKeys.QUEUE_SIZE]}) needs to be at least "
                f"{PulsarConfigKeys.MAX_WORKERS}({self.pulsarConfig[PulsarConfigKeys.MAX_WORKERS]})"
            )

    def connect(self):
        # disconnect if already connected
        if self.subscription:
            self.disconnect()

        # prepare timestamp string as part of subscription name
        timestr = datetime.now().isoformat()[:19]
        subscription_name = "backend-module-" + timestr

        # create consumer socket subscription
        while (
            not self.connectionAttempts
            > PulsarMessageConsumer.MAX_CONNECTION_ATTEMPTS
        ):
            try:
                self.connectionAttempts += 1
                print("connection attempt {}".format(self.connectionAttempts))
                self.subscription = self.open_socket(
                    subscription=subscription_name
                )

                if self.subscription:
                    # successful connection - reset timeout and attempt count
                    self.connectionAttempts = 0
                    self.reconnectTimeout = (
                        PulsarMessageConsumer.INITIAL_TIMEOUT_SLEEP
                    )
                    self.start_ping_loop()
                    return
            except Exception as e:
                print(
                    f"unable to establish connection (reason: {e}), next attempt in {self.reconnectTimeout} sec."
                )
                # unable to connect - wait and try again
                sleep(self.reconnectTimeout)
                # increase the timeout for the next attempt
                self.reconnectTimeout *= 2

    def disconnect(self):
        # close consumer
        if self.subscription:
            try:
                self.subscription.close()
            except Exception as e:
                print(
                    "warn: error while closing subscription socket: {0}".format(
                        e
                    )
                )
            finally:
                self.subscription = None

        # close producers
        for producer in self.producers.values():
            try:
                producer.close()
            except Exception as e:
                print(
                    "warn: error while closing producer socket: {0}".format(e)
                )

        self.producers.clear()

    def _pulsar_ping(self, timeout, event: threading.Event):
        while not event.wait(timeout):
            if self.subscription and self.subscription.connected:
                try:
                    # print('ping {}'.format(datetime.now()))
                    self.subscription.ping()
                except Exception as e:
                    print("error in pulsar ping routine: {}".format(e))
                    break
            else:
                print(
                    "quitting pulsar ping loop due to unconnected or missing subscription"
                )
                break

    def start_ping_loop(self):
        event = threading.Event()
        thread = threading.Thread(
            target=self._pulsar_ping,
            args=(PulsarMessageConsumer.PULSAR_PING_INTERVAL, event),
        )
        thread.setDaemon(True)
        thread.start()

    def wait_for_request(self):
        # register request event handler
        print("waiting for incoming request")
        self.loop.add_reader(self.subscription, self.receive_request)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("keyboard interrupt received")
        finally:
            print("shutting down event loop and disconnecting sockets")
            if self.loop.is_running():
                self.loop.stop()
            # self.loop.close()
            self.disconnect()

    def reconnect(self):
        print("reconnect, attempt {0}".format(self.connectionAttempts))

        # do we exceed the maximum number of connection attempts
        if self.connectionAttempts > self.MAX_CONNECTION_ATTEMPTS:
            print(
                "exceeding maximum connection attempts: {0}".format(
                    self.connectionAttempts
                )
            )
            self.loop.stop()
            self.disconnect()
        elif self.subscription:
            # there already is a subscription - remove it from the loop
            # in case the subscription is not connected anymore the reader has been already removed
            if self.subscription.connected:
                # only try to remove the subscription reader if still connected
                try:
                    self.loop.remove_reader(self.subscription)
                except ValueError:
                    print(
                        "ignoring exception in remove reader during reconnect"
                    )

            # disconnect and (re-)connect
            self.connect()

            # add the subscription to the running loop
            self.loop.add_reader(self.subscription, self.receive_request)

    def receive_request(self):
        if not self.subscription or not self.subscription.connected:
            print("subscription connection lost")
            # the socket is not connected anymore
            self.reconnect()
            return

        try:
            # receive json message
            msg = self.subscription.recv()

            # handle empty message
            if msg is None:
                print("empty message received")
                return

            # parse json message
            msg = json.loads(msg)

            # validate message
            # verify that we got a response_topic
            if PulsarMessageConsumer.is_valid_request(msg):
                # acknowledge request
                # FIXME: when do we actually acknowledge a message? right after receiving it or after processing it?
                self.acknowledge(msg)

                # handle according to message type
                msg_type = PulsarMessageConsumer.extract_message_type(msg)
                if msg_type == MessageType.PING:
                    # simply reply with pong
                    self.send_pong(msg)
                elif msg_type == MessageType.PONG:
                    # handle pong message
                    self.handle_pong(msg)
                elif msg_type == MessageType.INFO:
                    # handle info message
                    self.handle_info(msg)
                elif msg_type == MessageType.REQUEST:
                    # handle request message later via event loop
                    # self.loop.call_soon(self.handle_request, msg)
                    if self.request_semaphore is None:
                        # no bounded queue - directly pass the request to the executor
                        self.loop.run_in_executor(
                            self.pool, self.handle_request, msg
                        )
                    else:
                        # bounded queue size - check available space
                        if self.request_semaphore.acquire(blocking=False):
                            # there is still space in the queue - pass to executor queue
                            self.loop.run_in_executor(
                                self.pool, self.handle_request_via_queue, msg
                            )
                        else:
                            # queue is full - reject request
                            self.send_error(
                                request=msg,
                                error_message="request rejected due to queue overflow, try again later",
                            )

                    # todo: do we need to address any exceptions here?? e.g. via future.add_done_callback()
                    # Process(target=self.handle_request, args=(msg,)).start()
                elif msg_type == MessageType.RESPONSE:
                    if self.handle_response:
                        # handle response message later via event loop
                        self.loop.call_soon(self.handle_response, msg)
                        # Process(target=self.handle_response, args=(msg,)).start()
                    else:
                        print(
                            "ignoring response message due to missing handle_response function"
                        )
                else:
                    print("received unsupported message type: " + msg_type)
            else:
                print(
                    "message with unsupported structure received - ignoring it"
                )
        except SystemError:
            print("receive interrupted")
            self.loop.stop()
            return
        except Exception as e:
            print(
                "error in receive message loop {0} - trying to reconnect".format(
                    e
                )
            )
            # reconnect
            self.reconnect()

    def handle_request_via_queue(self, msg):
        # here the semaphore has already been acquired
        try:
            self.handle_request(msg)
        finally:
            # no matter what - release the semaphore
            self.request_semaphore.release()

    def acknowledge(self, msg):
        self.subscription.send(json.dumps({"messageId": msg["messageId"]}))

    def send_error(self, request, error_message):
        self.send_response(
            request=request,
            response_payload=error_message,
            response_properties={"status": "error"},
        )

    def send_response(
        self,
        request,
        response_payload=None,
        msg_type=MessageType.RESPONSE,
        response_properties=None,
    ):
        with self.send_lock:
            # validate original request
            if PulsarMessageConsumer.is_valid_request(request):
                # the request is valid - create a producer for the given response topic
                response_topic = PulsarMessageConsumer.extract_response_topic(
                    request
                )

                if response_properties is None:
                    response_properties = {}

                # prepare response
                response_properties[
                    PropertyKeys.REQUEST_CONTEXT
                ] = PulsarMessageConsumer.extract_context(request)
                response_properties[PropertyKeys.MESSAGE_TYPE] = msg_type

                if response_topic in self.producers:
                    # we already have a producer for this
                    producer = self.producers[response_topic]
                else:
                    # no producer yet, create one
                    producer = self.open_socket(topic=response_topic)
                    self.producers[response_topic] = producer

                # send the response
                msg = {"properties": response_properties, "payload": ""}
                if response_payload:
                    if isinstance(response_payload, str):
                        response_payload = response_payload.encode("utf-8")
                    elif isinstance(response_payload, dict):
                        response_payload = json.dumps(response_payload).encode(
                            "utf-8"
                        )

                    if len(response_payload) > self.MAX_PAYLOAD_SIZE:
                        print("sending fragmented message")
                        # the payload exceeds the maximum size - send fragmented message
                        payload_fragments: List[str] = textwrap.wrap(
                            text=base64.b64encode(response_payload).decode(
                                "utf-8"
                            ),
                            width=self.MAX_PAYLOAD_SIZE,
                        )

                        num_fragments = len(payload_fragments)
                        for i in range(num_fragments):
                            fragment_props = response_properties.copy()
                            fragment_props[PropertyKeys.FRAGMENT] = i
                            fragment_props[
                                PropertyKeys.NUM_FRAGMENTS
                            ] = num_fragments

                            fragmented_msg = {
                                "properties": fragment_props,
                                "payload": payload_fragments[i],
                            }
                            producer.send(json.dumps(fragmented_msg))

                            # receive acknowledgment
                            ack = json.loads(producer.recv())
                            if ack["result"] != "ok":
                                print(
                                    "Failed to send message: {}".format(ack),
                                    file=stderr,
                                )

                            # sleep 100ms
                            sleep(0.05)

                        print("sent {} fragments".format(num_fragments))
                        return

                    # send unfragmented message
                    msg["payload"] = base64.b64encode(response_payload).decode(
                        "utf-8"
                    )

                producer.send(json.dumps(msg))

                # receive acknowledgment
                # fixme: is this thread proof???
                #  what happens if the same producer send multiple messages at the same time?
                #  how can we assign the acknowledgment to the sent message?
                ack = json.loads(producer.recv())
                if ack["result"] != "ok":
                    print(
                        "Failed to send message: {}".format(ack), file=stderr
                    )

    def send_pong(self, request):
        self.send_response(request=request, msg_type=MessageType.PONG)

    def handle_pong(self, request):
        print("pong received {0}", request)

    def handle_info(self, info_request):
        # check for available module info
        if self.module_info is None:
            # no module info provided
            print("missing info")
            self.send_response(
                info_request,
                response_properties={
                    "info": "This module does not provide capability information."
                },
            )
            return

        print("sending info response...")
        self.send_response(
            request=info_request,
            response_properties={"info": json.dumps(self.module_info)},
        )

    @staticmethod
    def extract_response_topic(msg):
        if PropertyKeys.RESPONSE_TOPIC in msg["properties"]:
            return msg["properties"][PropertyKeys.RESPONSE_TOPIC]
        else:
            return None

    @staticmethod
    def extract_context(msg):
        if PropertyKeys.REQUEST_CONTEXT in msg["properties"]:
            return msg["properties"][PropertyKeys.REQUEST_CONTEXT]
        else:
            return None

    @staticmethod
    def extract_message_type(msg):
        if PropertyKeys.MESSAGE_TYPE in msg["properties"]:
            return msg["properties"][PropertyKeys.MESSAGE_TYPE]
        else:
            return None

    @staticmethod
    def is_valid_value(value):
        return value is not None and isinstance(value, str) and len(value) > 0

    @staticmethod
    def is_valid_request(request_message):
        # for now the request is valid if we find a valid response topic, context and message type
        return (
            PulsarMessageConsumer.is_valid_value(
                PulsarMessageConsumer.extract_response_topic(request_message)
            )
            and PulsarMessageConsumer.is_valid_value(
                PulsarMessageConsumer.extract_context(request_message)
            )
            and PulsarMessageConsumer.is_valid_value(
                PulsarMessageConsumer.extract_message_type(request_message)
            )
        )
