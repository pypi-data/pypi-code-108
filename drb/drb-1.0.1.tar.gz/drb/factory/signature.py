import ast
import abc
import copy
import re
import logging
from typing import List

from ..node import DrbNode
from ..predicat import Predicate
from ..exceptions import DrbException


class Signature(abc.ABC):
    """
    A signature describes a recognition mechanism for a specific type of DRB
    Item (ItemClass). This recognition mechanism is applied on a DRB Node.
    """
    @abc.abstractmethod
    def matches(self, node: DrbNode) -> bool:
        """
        Allowing to check if the given node match the signature.
        Parameters:
            node (DrbNode): item to check
        Returns:
            bool - ``True`` if the given node match, otherwise ``False``
        """
        raise NotImplementedError


class SignatureAggregator(Signature):
    """
    Allowing to check if a DRB Node match a signature set.
    Parameters:
        signatures List[Signature]: signature list to match
    """
    def __init__(self, signatures: List[Signature]):
        self.__signatures = signatures

    def matches(self, node: DrbNode) -> bool:
        if len(self.__signatures) == 0:
            return False
        return all(map(lambda s: s.matches(node), self.__signatures))


class NameSignature(Signature):
    """
    Allowing to check if a DRB Node name match a specific regex.
    Parameters:
        regex (str): regex pattern to match
    """
    def __init__(self, regex: str):
        self.__regex = regex

    def matches(self, node: DrbNode) -> bool:
        return re.match(self.__regex, node.name) is not None


class NamespaceSignature(Signature):
    """
    Allowing to check if a DRB Node namespace_uri match a specific regex.
    Parameters:
        regex (str): regex pattern to match
    """
    def __init__(self, regex: str):
        self.__regex = regex

    def matches(self, node: DrbNode) -> bool:
        return re.match(self.__regex, node.namespace_uri) is not None


class PathSignature(Signature):
    """
    Allowing to check if a DRB Node path match a specific regex.
    Parameters:
        regex (str): regex pattern to match
    """
    def __init__(self, regex: str):
        self.__regex = regex

    def matches(self, node: DrbNode) -> bool:
        return re.match(self.__regex, node.path.name) is not None


class AttributeSignature(Signature):
    """
    Allowing to check if a DRB Node having a specific attribute and also to
    check its value.
    Parameters:
        name (str): attribute name
    Keyword Arguments:
        namespace (str): attribute namespace
        value (Any): attribute value
    """
    def __init__(self, name: str, **kwargs):
        self.__name = name
        self.__namespace = kwargs.get('namespace', None)
        self.__check_value = 'value' in kwargs.keys()
        self.__value = kwargs.get('value', None)

    def matches(self, node: DrbNode) -> bool:
        try:
            value = node.get_attribute(self.__name, self.__namespace)
            if self.__check_value:
                return self.__value == value
            return True
        except DrbException:
            return False


class AttributesSignature(SignatureAggregator):
    """
    Allowing to check one or several attribute of a node.
    """
    def __init__(self, attributes: list):
        signatures = []
        for data in attributes:
            signatures.append(AttributeSignature(**data))
        super().__init__(signatures)


class ChildSignature(Signature):
    """
    Allowing to check if a DRB Node having a child matching specific criteria.

    Parameters:
        name (str): child name pattern

    Keyword Arguments:
        namespace (str): child node namespace (default: None)
        namespaceAware (bool): namespace_aware node flag (default: ``False``)
    """
    class _ChildPredicate(Predicate):
        def __init__(self, name: str, ns: str = None, aware: bool = False):
            self.__name = name
            self.__ns = ns
            self.__ns_aware = aware

        def matches(self, node) -> bool:
            match = re.match(self.__name, node.name)
            if match is None:
                return False
            if self.__ns is not None:
                return True if node.namespace_uri == self.__ns else False
            if self.__ns_aware:
                return self.__ns == node.namespace_uri
            return True

    def __init__(self, name: str, **kwargs):
        name = name
        ns = kwargs.get('namespace', None)
        aware = kwargs.get('namespaceAware', False)
        self.__predicate = ChildSignature._ChildPredicate(name, ns, aware)

    def matches(self, node: DrbNode) -> bool:
        n = node / self.__predicate
        return len(n) > 0


class ChildrenSignature(SignatureAggregator):
    """
    Allowing to check if specific children of a DRB Node match their associated
    criteria.

    Parameters:
        children (list): data list, each data must allow generation of a
                         ChildSignature
    """
    def __init__(self, children: list):
        signatures = []
        for data in children:
            signatures.append(ChildSignature(**data))
        super().__init__(signatures)


class ParentSignature(Signature):
    """
    Allowing to check if the parent node match a signature.
    """
    def __init__(self, data: dict):
        raise NotImplementedError

    def matches(self, node: DrbNode) -> bool:
        # TODO
        return False


class XquerySignature(Signature):
    """
    Allowing to check if a DRB Node match a specific XQuery.
    """
    def __init__(self, query: str):
        raise NotImplementedError

    def matches(self, node: DrbNode) -> bool:
        # TODO XQuery engine
        return False


class PythonSignature(Signature):
    """
    Allowing to check if a DRB Node match a custom signature.

    Parameters:
        script (str): custom Python (3.8+) script signature, this script must
                    return a boolean, otherwise ``False`` will be always
                    returned
    """

    _logger = logging.getLogger('PythonSignature')
    _ident = '  '

    def __init__(self, script: str):
        code = self._ident + script.replace('\n',  f'\n{self._ident}')
        self._script = f'def match():\n{code}\nmatch()'

    # code from https://stackoverflow.com/questions/33409207
    @staticmethod
    def _convert_expr2expression(expr) -> ast.Expression:
        expr.lineno = 0
        expr.col_offset = 0
        result = ast.Expression(expr.value, lineno=0, col_offset=0)
        return result

    # code from https://stackoverflow.com/questions/33409207
    # updated to include the current node in the execution context
    @staticmethod
    def _exec_with_return(code: str, node: DrbNode):
        code_ast = ast.parse(code)

        init_ast = copy.deepcopy(code_ast)
        init_ast.body = code_ast.body[:-1]

        last_ast = copy.deepcopy(code_ast)
        last_ast.body = code_ast.body[-1:]

        my_globals = globals()
        my_globals['node'] = node

        exec(compile(init_ast, "<ast>", "exec"), my_globals)
        if type(last_ast.body[0]) == ast.Expr:
            return eval(compile(
                PythonSignature._convert_expr2expression(last_ast.body[0]),
                "<ast>", "eval"), my_globals)
        else:
            exec(compile(last_ast, "<ast>", "exec"), my_globals)

    def matches(self, node: DrbNode) -> bool:
        try:
            result = PythonSignature._exec_with_return(self._script, node)
            if isinstance(result, bool):
                return result
            return False
        except Exception as ex:
            self._logger.debug('An error occurred during a Python signature'
                               f' check: {ex}')
            return False


SIGNATURES = {
    'name': NameSignature,
    'namespace': NamespaceSignature,
    'path': PathSignature,
    'attributes': AttributesSignature,
    'children': ChildrenSignature,
    'parent': ParentSignature,
    'xquery': XquerySignature,
    'python': PythonSignature,
}


def parse_signature(data: dict) -> Signature:
    signatures = []
    for key in data.keys():
        signatures.append(SIGNATURES[key](data[key]))
    return SignatureAggregator(signatures)
