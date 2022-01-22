from DecenTT.DecenTTErrors import InvalidCallback, TopicIncompatibleType
from DecenTT.IPFS import Client as iClient  # Equipped with list of topics
from DecenTT.MQTT import Client as mClient


class Client:
    """
        Which Client ??
        0:          MQTT Client
        1:          IPFS Client

    """

    def __init__(
            self,
            host: str,
            port: int = 1883,
            username: str = None,
            password: str = None,
            on_connect=None,
            on_publish=None,
            on_message=None,
            log_path: str = ".",
            keyword: str = "secure/",
            **kwargs
    ) -> None:
        self.__keyword = keyword
        self.clients = [
            mClient(
                host=host,
                port=port,
                username=username,
                password=password,
                on_connect=on_connect,
                on_publish=on_publish,
                on_message=on_message,
                log_path=log_path,
                **kwargs
            ),

            iClient(**kwargs)
        ]

        self.iClient_subscriptions = None


    # Mock Switcher
    def __which(self, topic: str) -> object:
        if self.__keyword in topic: return self.clients[1]
        return self.clients[0]

    def __map_clients_to_topic(self, topic: list) -> tuple:
        client_0_list = list()
        client_1_list = list()
        for t_i in topic:
            if self.__keyword in str(t_i[0]):
                client_1_list.append(t_i[0])
            else:
                client_0_list.append(t_i)

        return client_0_list, client_1_list

    def subscribe(self, topic: any, callback, **kwargs):

        # check for the validity of the topic as data_structure
        if not (isinstance(topic, list) or isinstance(topic, str)):
            raise TopicIncompatibleType

        # check for valid callback
        if not ('function' in str(type(callback))):
            raise InvalidCallback(callback)

        if isinstance(topic, list):
            c0_topics, c1_topics = self.__map_clients_to_topic(topic= list(topic))
            self.clients[0].subscribe(topic=c0_topics, callback=callback)
            self.iClient_subscriptions = self.clients[1].subscribe(topic=c1_topics, callback=callback)
            return

        client = self.__which(topic=topic)
        if(isinstance(client, iClient)):
            self.iClient_subscriptions = client.subscribe(topic=topic, callback=callback, **kwargs)
        client.subscribe(topic=topic, callback=callback, **kwargs)

    def __kill_all_threads(self):
        thread_list = [sub.thread for sub in self.iClient_subscriptions]
        for thread in thread_list:
            #print(f"Closing thread: {thread}")
            thread.terminate()
            #print(f"Terminating thread: {thread}")
            thread.join()
            #print(f"Closed thread: {thread}")

    def stop(self):
        self.__kill_all_threads()

    def publish(self, topic: str, payload: str, **kwargs):
        client = self.__which(topic=topic)
        client.publish(topic=topic, payload=payload, **kwargs)

    def loop(self, **kwargs):
        self.clients[0].client.loop(**kwargs)

    def loop_start(self):
        self.clients[0].client.loop_start()

    def loop_stop(self, **kwargs):
        self.clients[0].client.loop_stop(**kwargs)
        self.__kill_all_threads()

    def loop_forever(self, **kwargs):
        self.clients[0].client.loop_forever(**kwargs)
