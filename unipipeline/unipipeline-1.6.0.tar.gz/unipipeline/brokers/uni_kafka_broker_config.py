from typing import Tuple

from unipipeline.definitions.uni_dynamic_definition import UniDynamicDefinition


class UniKafkaBrokerConfig(UniDynamicDefinition):
    api_version: Tuple[int, ...]
    retry_max_count: int = 100
    retry_delay_s: int = 3
