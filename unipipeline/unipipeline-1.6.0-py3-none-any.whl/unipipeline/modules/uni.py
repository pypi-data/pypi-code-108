from typing import Dict, Any, Union, Optional

from unipipeline.errors.uni_payload_error import UniPayloadSerializationError
from unipipeline.brokers.uni_broker import UniBroker
from unipipeline.config.uni_config import UniConfig, UniConfigError
from unipipeline.utils.uni_echo import UniEcho
from unipipeline.modules.uni_mediator import UniMediator
from unipipeline.message.uni_message import UniMessage
from unipipeline.utils.uni_util import UniUtil
from unipipeline.waiting.uni_wating import UniWaiting
from unipipeline.worker.uni_worker import UniWorker


def camel_case(snake_cased: str) -> str:
    return ''.join(word.title() for word in snake_cased.split('_'))


class Uni:
    def __init__(self, config: Union[UniConfig, str], echo_level: Optional[Union[str, int]] = None) -> None:
        self._util = UniUtil()
        self._util.template.set_filter('camel', camel_case)

        self._echo = UniEcho('UNI', level=echo_level, colors=self._util.color)

        if isinstance(config, str):
            config = UniConfig(self._util, self._echo, config)
        if not isinstance(config, UniConfig):
            raise ValueError(f'invalid config type. {type(config).__name__} was given')
        self._mediator = UniMediator(self._util, self._echo, config)

    @property
    def echo(self) -> UniEcho:
        return self._mediator.echo

    @property
    def util(self) -> UniUtil:
        return self._util

    @property
    def config(self) -> UniConfig:
        return self._mediator.config

    def set_echo_level(self, level: int) -> None:
        self._mediator.set_echo_level(level)

    def scaffold(self) -> None:
        try:
            for waiting_def in self._mediator.config.waitings.values():
                waiting_def.type.import_class(UniWaiting, self.echo, auto_create=True, create_template_params=waiting_def, util=self._util)

            for broker_def in self._mediator.config.brokers.values():
                broker_def.type.import_class(UniBroker, self.echo, auto_create=True, create_template_params=broker_def, util=self._util)

            for message_def in self._mediator.config.messages.values():
                message_def.type.import_class(UniMessage, self.echo, auto_create=True, create_template_params=message_def, util=self._util)

            for worker_def in self._mediator.config.workers.values():
                if worker_def.marked_as_external:
                    continue
                assert worker_def.type is not None
                worker_def.type.import_class(UniWorker, self.echo, auto_create=True, create_template_params=worker_def, util=self._util)

        except UniConfigError as e:
            self.echo.exit_with_error(str(e))

    def check(self) -> None:
        try:
            for waiting_def in self._mediator.config.waitings.values():
                waiting_def.type.import_class(UniWaiting, self.echo, util=self._util)

            for broker_def in self._mediator.config.brokers.values():
                broker_def.type.import_class(UniBroker, self.echo, util=self._util)

            for message_def in self._mediator.config.messages.values():
                message_def.type.import_class(UniMessage, self.echo, util=self._util)

            for worker_def in self._mediator.config.workers.values():
                if worker_def.marked_as_external:
                    continue
                assert worker_def.type is not None
                worker_def.type.import_class(UniWorker, self.echo, util=self._util)

        except UniConfigError as e:
            self.echo.exit_with_error(str(e))

    def start_cron(self) -> None:
        try:
            self._mediator.start_cron()
        except KeyboardInterrupt:
            self.echo.log_warning('interrupted')
            exit(0)

    def initialize_cron_producer_workers(self) -> None:
        for t in self._mediator.config.cron_tasks.values():
            self.init_producer_worker(t.worker.name)

    def initialize(self, everything: bool = False) -> None:
        if everything:
            for wn in self._mediator.config.workers.keys():
                self._mediator.add_worker_to_init_list(wn, no_related=True)
        self._mediator.initialize(create=True)

    def init_cron(self) -> None:
        for task in self._mediator.config.cron_tasks.values():
            self._mediator.add_worker_to_init_list(task.worker.name, no_related=True)

    def init_producer_worker(self, name: str) -> None:
        self._mediator.add_worker_to_init_list(name, no_related=True)

    def init_consumer_worker(self, name: str) -> None:
        self._mediator.add_worker_to_init_list(name, no_related=False)
        self._mediator.add_worker_to_consume_list(name)

    def send_to(self, name: str, data: Union[Dict[str, Any], UniMessage], alone: bool = False) -> None:
        try:
            self._mediator.send_to(name, data, alone=alone)
        except UniPayloadSerializationError as e:
            self.echo.exit_with_error(f'invalid props in message: {e}')

    def exit(self) -> None:
        self.echo.log_info('exit!')
        self._mediator.exit()

    def start_consuming(self) -> None:
        try:
            self._mediator.start_consuming()
        except KeyboardInterrupt:
            self.echo.log_warning('interrupted')
            exit(0)
