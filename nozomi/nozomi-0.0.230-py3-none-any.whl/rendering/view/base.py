"""
Nozomi
Base View Module
author: hugh@blinkybeach.com
"""
from nozomi.rendering.javascript_class import JavaScriptClass
from nozomi.rendering.style import Style
from nozomi.rendering.script import Script
from nozomi.rendering.view.view import View
from nozomi.rendering.open_graph import OpenGraph
from nozomi.ancillary.configuration import Configuration
from typing import List, Dict, Optional, Any, Union
from nozomi.rendering.context import Context


class BaseView(View):
    """
    Abstract view providing low level intermediate configuration preparation
    between a concrete view and the abstract View object.
    """

    def __init__(
        self,
        configuration: Configuration,
        template: str,
        title: str,
        description: str,
        key_words: List[str],
        styles: List[Union[str, Style]],
        scripts: List[Union[str, Script]],
        classes: List[Union[str, JavaScriptClass]],
        open_graph: Optional[OpenGraph] = None,
        static_variables: Optional[Dict[str, Any]] = None,
        static_js_constants: Optional[Dict[str, Any]] = None
    ) -> None:

        all_static_js_constants = {
            'global_api_endpoint': configuration.public_api_endpoint,
            'global_debug_flag': configuration.debug
        }
        if static_js_constants is not None:
            all_static_js_constants.update(static_js_constants)

        all_variables = {
            'global_debug_flag': configuration.debug
        }
        if static_variables is not None:
            all_variables.update(static_variables)

        super().__init__(
            configuration=configuration,
            template=template,
            title=title,
            description=description,
            key_words=key_words,
            styles=styles,
            scripts=scripts,
            classes=classes,
            open_graph=open_graph,
            static_variables=all_variables,
            static_js_constants=all_static_js_constants
        )

        return
