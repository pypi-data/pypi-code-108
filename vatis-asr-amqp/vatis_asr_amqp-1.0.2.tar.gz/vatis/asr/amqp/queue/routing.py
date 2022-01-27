from typing import Dict, Union
from typing import Optional, List, Any
import json
import jsonpickle

from jsonpath_ng import parse, JSONPath, DatumInContext
from pika.exchange_type import ExchangeType
from vatis.asr_commons.static.request import TranscriptionRequest

from . import environment
from vatis.asr_commons.config.logging import get_logger
from .model import Queue, Exchange, DEFAULT_EXCHANGE

logger = get_logger(__name__)


class Route:
    def __init__(self, queue: Optional[Union[Queue, dict]] = None,
                 exchange: Union[Exchange, dict] = DEFAULT_EXCHANGE):
        self.queue: Optional[Queue] = None
        if queue is not None:
            self.queue = queue if isinstance(queue, Queue) else Queue(**queue)

        self.exchange: Exchange = exchange if isinstance(exchange, Exchange) else Exchange(**exchange)

        if self.queue is None and self.exchange.type != ExchangeType.fanout.value:
            raise ValueError('Empty queue only allowed when specifying a fanout exchange')


class RoutingRule:
    def __init__(self, json_path: JSONPath, value: str, route: Union[Route, dict]):
        assert json_path is not None
        assert value is not None
        assert route is not None

        self.json_path: JSONPath = json_path
        self.value: str = value
        self.route: Route = route if isinstance(route, Route) else Route(**route)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


_routing_rules: Optional[List[RoutingRule]] = None


def __init__():
    global _routing_rules

    if _routing_rules is None:
        _routing_rules = []
    else:
        raise

    rule_dicts: List[dict] = json.loads(environment.RABBITMQ_ROUTING_RULES_JSON)

    if not len(rule_dicts):
        logger.warn('Empty routing rules')

    for rule_dict in rule_dicts:
        rule_dict['json_path'] = parse(rule_dict['json_path'])
        rule: RoutingRule = RoutingRule(**rule_dict)

        _routing_rules.append(rule)

    logger.info('Initialized routing rules:\n%s', str(_routing_rules))


def get_routes(request: TranscriptionRequest) -> List[Route]:
    json_request: str = jsonpickle.encode(request, unpicklable=False)
    dict_request: Dict[str, Any] = json.loads(json_request)

    rules: List[Route] = []

    for rule in _routing_rules:
        results: List[DatumInContext] = rule.json_path.find(dict_request)

        if len(results) > 1:
            raise ValueError(f'Invalid number of results: {str(results)}')
        elif len(results) == 1:
            result: DatumInContext = results[0]

            if result.value == rule.value:
                rules.append(rule.route)

    return rules
