"""
Nozomi
Context Module
Copyright Amatino Pty Ltd
"""
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from decimal import Decimal
from nozomi.data.encodable import Encodable

RESERVED_WORDS = ['year', 'javascript_constants']


class Context:
    """
    Abstract class defining interfaces and default methods for the storage,
    validation, and output of variables used in rendering HTML pages
    """

    def __init__(self) -> None:
        self._js_constants: List[Dict] = list()
        self._context: Dict[str, Any] = dict()
        self._has_rendered = False
        self._context['year'] = str(datetime.now().year)
        return

    def add(self, key: str, value: Any) -> None:
        """
        Add a value to the render context, under the given key. E.g. to make a
        value '"hello world"' available under the name 'world', supply
        add('world', 'hello world').
        """
        assert isinstance(key, str)
        if key in RESERVED_WORDS:
            raise RuntimeError(key + ' is a reserved word')
        if key in self._context:
            raise RuntimeError('Duplicate render context key: ' + key)
        self._context[key] = value
        return

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a key stored in this context"""
        if key in self._context:
            return self._context[key]
        return None

    context = property(lambda s: s._compute_context())

    def _compute_context(self) -> dict:
        """
        Return a dictionary of static context variables suitable for stage 1
        rendering
        """
        if self._has_rendered is not False:
            raise RuntimeError('Duplicate context render - not allowed')
        context = dict(self._context)
        context['javascript_constants'] = list(self._js_constants)
        self._context = dict()  # Ensure the context can only be rendered once
        self._js_constants = list()
        self._has_rendered = True
        return context

    def add_javascript_constant(self, name: str, value: Any) -> None:
        """
        Add a javascript constant to the render context, under a given constant
        name. Constants will be made available before the execution of scripts.
        """
        if name == 'javascript_constants':
            raise RuntimeError('"javascript_constants" is a reserved word')
        if name.upper() in [v['name'] for v in self._js_constants]:
            raise RuntimeError('Duplicate constant name: ' + name)
        value = self._adapt_js_constant(value)
        self._js_constants.append({
            'name': name.upper(),
            'value': value
        })
        return

    def _adapt_js_constant(
        self,
        value: Any,
        recursing_serialisation=False
    ) -> Union[int, str]:
        if isinstance(value, int) and value > 2**32:
            return "'" + str(value) + "'"
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.replace("'", "\\'")
            return "'" + value + "'"
        if isinstance(value, bool):
            if value is True:
                return 'true'
            else:
                return 'false'
        if isinstance(value, Decimal):
            return "'" + str(value) + "'"
        if isinstance(value, list):
            return "'" + json.dumps(
                [self._adapt_js_constant(v, True) for v in value]
            ) + "'"
        if value is None:
            return 'null'
        if isinstance(value, Encodable):
            if recursing_serialisation:
                return value.encode()
            return value.serialise()
        if isinstance(value, float):
            return "'" + str(value) + "'"
        if isinstance(value, dict):
            return "'" + json.dumps(value) + "'"
        raise RuntimeError(
            'Cannot adapt: ' + str(type(value)) + ', ' + str(value)
        )
