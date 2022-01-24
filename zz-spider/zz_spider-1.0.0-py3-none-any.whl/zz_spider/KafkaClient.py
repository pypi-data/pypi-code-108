from zz_spider import KkProducer, KafkaReceive, KkOffset


class KafkaClient(object):
    _INSTANCE = None

    def __new__(cls, *args, **kwargs):
        if not cls._INSTANCE:
            cls._INSTANCE = super().__new__(cls)
        return cls._INSTANCE

    _shortcut = {
        "product": KkProducer,
        "KafkaReceive": KafkaReceive,
        "KkOffset": KkOffset
    }

    def __init__(self,
                 bootstrap_servers: str,
                 options_name: str,
                 task_info: dict,
                 try_max_times: int = 3,
                 type: int=0
                 ):
        self.bootstrap_servers = bootstrap_servers
        self.options_name = options_name
        self.task_info = task_info
        self.type = type
        self.try_max_times = try_max_times
        self.session = self._session

    @property
    def _session(self):
        return self._shortcut[list(self._shortcut.keys())[self.type]]

