from base64 import b64decode

class IPFSResponse:
    """
        Sample JSON Response from IPFS HTTP API:
            {
                "from":"ACQIARIgvsDLWj3HNX2jJQGZ5H1Ij1RJfOXDj/tshfztcgwO57M=",
                "data":"aGVsbG8gd29ybGRz",
                "seqno":"Frs0H9ZNr5Y=",
                "topicIDs":["abc"]
            }
    """
    class UserData:
        def __init__(self, from_user:str, seq_no:str)-> None:
            self.from_user = from_user
            self.seq_no=seq_no

    class Message:
        class Payload:
            def __init__(self, data:str):
                self.__data = data

            def decode(self)->str:
                return b64decode(self.__data).decode("utf-8")

            def __str__(self):
                return self.__data


        def __init__(self, topic:str, data:str)->None:
            self.topic = topic
            self.payload = self.Payload(data=data)
            self.qos = None
            self.retain = None

    def __init__(self, in_dict:dict) -> None:
        self.raw_dict = in_dict
        self.userdata = self.UserData(from_user=self.raw_dict["from"], seq_no=self.raw_dict["seqno"])
        self.msg = self.Message(topic=self.raw_dict["topicIDs"][0], data=self.raw_dict["data"])

