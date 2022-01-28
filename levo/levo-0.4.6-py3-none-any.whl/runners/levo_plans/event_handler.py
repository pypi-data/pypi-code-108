from typing import Any, Dict, List

import attr
from levo_commons import events
from levo_commons.models import Module
from levo_commons.providers import Provider

from ...config import TestPlanCommandConfig
from ...handlers import EventHandler
from ...logger import get_logger
from .context import ExecutionContext
from .modules import get_provider_for_module

log = get_logger(__name__)


@attr.s()
class LevoPlansEventHandler(EventHandler):
    config: TestPlanCommandConfig = attr.ib()
    modules: Dict[Module, Provider] = attr.ib(factory=dict)
    reporters: List[EventHandler] = attr.ib(factory=list)

    def delegate_to_reporters(self, context, event):
        for reporter in self.reporters:
            reporter.handle_event(context, event)

    def setup_modules(self, module_names: list[str]) -> dict[Module, Provider]:
        for module_name in module_names:
            module = Module[module_name]
            if module not in self.modules or not self.modules[module].is_running():
                provider = get_provider_for_module(module_name)
                provider.start()
                self.modules[module] = provider
        return self.modules

    def handle_event(self, context: ExecutionContext, event: events.Event) -> None:
        if isinstance(event, events.BeforeTestSuiteExecution):
            if event.payload.modules:
                self.setup_modules(event.payload.modules)
        elif isinstance(event, events.BeforeTestCaseExecution):
            if event.payload.module:
                self.setup_modules([event.payload.module])

        # Delegate all the events to the reporters too.
        self.delegate_to_reporters(context, event)

        if (
            isinstance(event, events.Finished)
            or isinstance(event, events.InternalError)
            or isinstance(event, events.Interrupted)
        ):
            # Stop all the modules
            for provider in self.modules.values():
                provider.stop()
