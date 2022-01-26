from ... import Server


class KafkaTopic:
    def __init__(self,
                 server: Server,
                 topic_id: str
                 ):
        self.server = server
        self.topic_id = topic_id

