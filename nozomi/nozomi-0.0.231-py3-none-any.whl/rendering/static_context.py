"""
Nozomi
Static Context Module
Copyright Amatino Pty Ltd
"""

from typing import List, Optional, Dict, Any, Union
from nozomi.rendering.open_graph import OpenGraph
from nozomi.rendering.script import Script
from nozomi.rendering.javascript_class import JavaScriptClass
from nozomi.rendering.style import Style
from nozomi.rendering.context import Context


class StaticContext(Context):
    """
    Storage, validation, and output of variables used in first pass rendering
    of HTML pages.
    """
    def __init__(
        self,
        styles: List[Union[str, Style]],
        scripts: List[Union[str, Style]],
        classes: List[Union[str, Style]],
        title: str,
        open_graph: Optional[OpenGraph],
        description: str,
        key_words: List[str],
        other_variables: Optional[Dict[str, Any]] = None,
        js_constants: Optional[Dict[str, Any]] = None
    ) -> None:

        super().__init__()

        if title == '':
            raise NotImplementedError('Missing page title')

        assert isinstance(title, str)
        assert isinstance(description, str)

        JSC = JavaScriptClass

        assert False not in [
            (isinstance(s, str) or isinstance(s, Style)) for s in styles
        ]
        assert False not in [
            (isinstance(s, str) or isinstance(s, Script)) for s in scripts
        ]
        assert False not in [
            (isinstance(c, str) or isinstance(c, JSC)) for c in classes
        ]
        assert False not in [isinstance(k, str) for k in key_words]

        self._open_graph = None
        if open_graph is not None:
            assert isinstance(open_graph, OpenGraph)
            self._open_graph = open_graph.as_dict()

        static_context = {
            'styles': [
                (Style(s) if isinstance(s, str) else s) for s in styles
            ],
            'scripts': [
                (Script(s) if isinstance(s, str) else s) for s in scripts
            ],
            'classes': [
                (JSC(c) if isinstance(c, str) else c) for c in classes
            ],
            'title': title,
            'open_graph': self._open_graph,
            'description': description,
            'key_words': ','.join(key_words)
        }

        for key in static_context:
            self.add(key, static_context[key])

        if other_variables:
            for key in other_variables:
                self.add(key, other_variables[key])

        if js_constants:
            for key in js_constants:
                self.add_javascript_constant(key, js_constants[key])

        return
