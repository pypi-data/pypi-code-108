from threading import Thread, Lock
import types
from .message import Message
from .connection import Connection
from .util import check_type
import re
from json_cpp import JsonList, JsonObject


class Router:
    def __init__(self):
        self.routes = {}
        self.failed_message = None
        self.failed_route = None
        self.unrouted_message = None
        self.routing_count = 0

    def add_route(self, pattern: str, handler, body_type=None):
        check_type(handler, (types.FunctionType, types.MethodType), "incorrect type for handler")
        self.routes[pattern] = (handler, body_type)

    def get_manifest(self):
        manifest = JsonList()
        for pattern in self.routes.keys():
            (handler, body_type) = self.routes[pattern]
            if body_type:
                body_type_str = body_type.__name__
            else:
                body_type_str = ""
            manifest.append(JsonObject(route=pattern, input_type=body_type_str))
        return manifest

    def route(self, message: Message):
        responses = []
        check_type(message, Message, "incorrect type for message")
        if message.header == "!manifest":
            responses.append(self.get_manifest())
        for pattern in self.routes.keys():
            if re.search(pattern, message.header):
                (handler, body_type) = self.routes[pattern]
                try:
                    if body_type:
                        responses.append(handler(message.get_body(body_type)))
                    else:
                        responses.append(handler(message))
                except:
                    if self.failed_route:
                        self.failed_route(message)
        if not responses:
            if self.unrouted_message:
                self.unrouted_message(message)
        self.routing_count += 1
        return responses

    def attend(self, connection: Connection):
        RouterProcess.attend(connection, self)


class RouterProcess:
    __handler = None
    __mutex = Lock()

    @staticmethod
    def attend(connection: Connection, router: Router):
        RouterProcess.__mutex.acquire()
        if RouterProcess.__handler is None:
            RouterProcess.__handler = RouterProcess()
        RouterProcess.__handler.connections.append((connection, router))
        RouterProcess.__mutex.release()

    def __init__(self):
        if RouterProcess.__handler:
            raise Exception("ConnectionHandler is a singleton, use ConnectionHandler.handle")
        self.connections = list()
        self.incoming_messages_threads = []
        self.running = False
        self.thread = Thread(target=self.__process__)
        self.thread.daemon = True
        self.thread.start()
        while not self.running:
            pass
        RouterProcess.__handler = self

    @staticmethod
    def __incoming_message__(connection: Connection, router: Router, message: Message):
        message._source = connection
        responses = router.route(message)
        if responses:
            for response in responses:
                if isinstance(response, Message):
                    response.id = message.id
                    connection.send(response)
                elif isinstance(response, bool):
                    response_message = Message(message.header + "_response", "success" if response else "fail")
                    response_message.id = message.id
                    connection.send(response_message)
                else:
                    if response:
                        response_message = Message(message.header + "_response", str(response))
                        response_message.id = message.id
                        connection.send(response_message)

    def __process__(self):
        self.running = True
        while self.running:
            clean_up_required = []
            for index, (connection, router) in enumerate(self.connections):
                try:
                    if connection.state == Connection.State.Open:
                        message = connection.receive()
                        if message:
                            #RouterProcess.__incoming_message(connection, router, message)
                            Thread(target=RouterProcess.__incoming_message__, args=(connection, router, message)).start()
                    else:
                        clean_up_required.append(index)
                except:
                   clean_up_required.append(index)

            if clean_up_required:
                RouterProcess.__mutex.acquire()
                for failed_connection in clean_up_required:
                    try:
                        del self.connections[failed_connection]
                    except:
                        pass
                if len(self.connections) == 0:
                    RouterProcess.__handler = None
                    self.running = False
                RouterProcess.__mutex.release()

            to_remove = []
            while len(self.incoming_messages_threads) >= 10:
                for t in self.incoming_messages_threads:
                    if not t.is_alive():
                        to_remove.append(t)
                for t in to_remove:
                    self.incoming_messages_threads.remove(t)


