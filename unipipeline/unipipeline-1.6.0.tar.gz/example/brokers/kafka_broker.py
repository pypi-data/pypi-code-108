from typing import List, Dict, Any

from unipipeline.brokers.uni_kafka_broker import UniKafkaBroker


class KafkaBroker(UniKafkaBroker):
    def get_boostrap_servers(self) -> List[str]:
        return ['localhost:9092']

    def get_security_conf(self) -> Dict[str, Any]:
        return dict()
