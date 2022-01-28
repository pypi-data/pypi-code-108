from .base_rule import BaseRule
from ..handlers.virtual_module import VirtualModule


class VirtualModuleRule(BaseRule):
    def __init__(self, rule) -> None:
        super(VirtualModuleRule, self).__init__(rule, None)
        VirtualModule.register(rule)

    @staticmethod
    def is_virtual_module(module):
        return module.startswith('<') and module.endswith('>')

    def add_instrumentation(self) -> None:
        # This should only create a virtual module. instrumentation will be added later
        pass
