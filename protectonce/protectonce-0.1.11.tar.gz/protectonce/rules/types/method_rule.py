from .base_rule import BaseRule
from ...instrument.method_interceptor import MethodInterceptor


class MethodRule(BaseRule):
    def __init__(self, rule, module=None) -> None:
        super(MethodRule, self).__init__(rule, module)

    def add_instrumentation(self) -> None:
        interceptor = MethodInterceptor(
            self.mod, self.cls, self.methods, self.handlers)
        interceptor.intercept()
