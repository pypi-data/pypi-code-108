from .base_rule import BaseRule

from ...instrument.class_interceptor import ClassInterceptor


class ClassRule(BaseRule):
    def __init__(self, rule, module=None) -> None:
        super(ClassRule, self).__init__(rule, module)

    def add_instrumentation(self) -> None:
        interceptor = ClassInterceptor(
            self.mod, self.cls, self.methods, self.handlers)
        interceptor.intercept()
