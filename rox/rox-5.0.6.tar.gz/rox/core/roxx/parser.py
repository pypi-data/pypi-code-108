from rox.core.logging.logging import Logging
from rox.core.roxx import basic_operators
from rox.core.roxx.core_stack import CoreStack
from rox.core.error_handling.userspace_handler_exception import UserspaceHandlerException
from rox.core.roxx.evaluation_result import EvaluationResult
from rox.core.roxx.node import NodeTypes
from rox.core.roxx.regular_expression_extensions import RegularExpressionExtensions
from rox.core.roxx.token_type import TokenTypes
from rox.core.roxx.tokenized_expression import TokenizedExpression
from rox.core.roxx.value_compare_extensions import ValueCompareExtensions


class Parser:
    def __init__(self, user_unhandled_error_invoker):
        self.operatorsMap = {}
        self.global_context = None
        self.set_basic_operators()
        self.user_unhandled_error_invoker = user_unhandled_error_invoker
        ValueCompareExtensions(self).extend()
        RegularExpressionExtensions(self).extend()

    def set_basic_operators(self):
        self.add_operator('isUndefined', basic_operators.is_undefined)
        self.add_operator('now', basic_operators.now)
        self.add_operator('and', basic_operators.and_)
        self.add_operator('or', basic_operators.or_)
        self.add_operator('ne', basic_operators.ne)
        self.add_operator('eq', basic_operators.eq)
        self.add_operator('not', basic_operators.not_)
        self.add_operator('ifThen', basic_operators.if_then)
        self.add_operator('inArray', basic_operators.in_array)
        self.add_operator('md5', basic_operators.md5)
        self.add_operator('concat', basic_operators.concat)
        self.add_operator('b64d', basic_operators.b64d)

    def add_operator(self, oper, operation):
        self.operatorsMap[oper] = operation

    def set_global_context(self, global_context):
        self.global_context = global_context

    def evaluate_expression(self, expression, context=None):
        stack = CoreStack()
        tokens = TokenizedExpression(expression, self.operatorsMap.keys()).get_tokens()
        reverse_tokens = reversed(tokens)
        try:
            for token in reverse_tokens:
                node = token
                if node.type == NodeTypes.RAND:
                    stack.push(node.value)
                elif node.type == NodeTypes.RATOR:
                    handler = self.operatorsMap.get(node.value, None)
                    if handler is not None:
                        handler(self, stack, context)
                else:
                    return EvaluationResult(None)

            result = stack.pop()
            if result == TokenTypes.UNDEFINED:
                result = None
            return EvaluationResult(result)
        except UserspaceHandlerException as ex:
            self.user_unhandled_error_invoker.invoke(ex.exception_source, ex.exception_trigger, ex.exception)
            Logging.get_logger().warn('Roxx Exception: Failed evaluate expression, user unhandled expression: {}'.format(ex))
            return EvaluationResult(None)
        except Exception as ex:
            Logging.get_logger().warn('Roxx Exception: Failed evaluate expression: %s' % ex)
            return EvaluationResult(None)
