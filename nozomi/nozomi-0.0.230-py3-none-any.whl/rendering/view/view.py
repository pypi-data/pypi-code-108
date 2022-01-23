"""
Nozomi
View Module
author: hugh@blinkybeach.com
"""
from typing import Optional, Dict, Any, List, Union
from nozomi.rendering.view_template import ViewTemplate
from nozomi.rendering.context import Context
from nozomi.rendering.static_context import StaticContext
from nozomi.rendering.open_graph import OpenGraph
from nozomi.ancillary.configuration import Configuration
from nozomi.ancillary.immutable import Immutable
from nozomi.http.headers import Headers
from nozomi.http.query_string import QueryString
from nozomi.security.abstract_session import AbstractSession
from nozomi.security.agent import Agent
from nozomi.rendering.javascript_class import JavaScriptClass
from nozomi.rendering.style import Style
from nozomi.rendering.script import Script


class View:
    """
    An abstract class providing functionality useful for building
    views - That is, web pages that application users will view and
    interact with.

    View is an abstract class that is expected to be inherited by
    a concrete class. For example, an Splash page might be formed
    of a class Splash(View).
    """

    _transient_context = None

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

        assert isinstance(configuration, Configuration)
        self._configuration = configuration

        self._template_name = template
        assert isinstance(self._template_name, str)
        assert self._template_name[-5:] == '.html'

        assert isinstance(styles, list)
        all_styles = self._standard_css_styles + styles

        assert isinstance(classes, list)
        for jsclass in classes:
            assert jsclass not in self._standard_js_classes
        all_classes = self._standard_js_classes + classes

        assert isinstance(scripts, list)
        for script in scripts:
            assert script not in self._standard_js_scripts
        all_scripts = scripts + self._standard_js_scripts

        assert isinstance(title, str)
        if open_graph is not None:
            assert isinstance(open_graph, OpenGraph)
        assert isinstance(description, str)
        assert isinstance(key_words, list)
        assert False not in [isinstance(k, str) for k in key_words]

        static_context = StaticContext(
            all_styles,
            all_scripts,
            all_classes,
            title,
            open_graph,
            description,
            key_words,
            static_variables,
            static_js_constants
        )

        self._template = ViewTemplate(
            template_filename=self._template_name,
            static_context=static_context,
            configuration=configuration
        )

        return

    configuration = Immutable(lambda s: s._configuration)

    _standard_css_styles = Immutable(
        lambda s: s.configuration.standard_css_styles
    )
    _standard_js_classes = Immutable(
        lambda s: s.configuration.standard_js_classes
    )
    _standard_js_scripts = Immutable(
        lambda s: s.configuration.standard_js_scripts
    )

    def serve(
        self,
        headers: Headers,
        query: Optional[QueryString],
        context: Optional[Context] = None,
        session: Optional[AbstractSession] = None
    ) -> str:
        """
        Return a string response to a request
        """
        if context is None:
            context = Context()

        computed_context = self.compute_response(
            query=query,
            context=context,
            requesting_agent=session
        )
        assert isinstance(computed_context, Context)
        return self._template.render(computed_context)

    def compute_response(
        self,
        query: Optional[QueryString],
        context: Context,
        requesting_agent: Optional[Agent]
    ) -> Context:
        raise NotImplementedError

    def generate_context(self) -> Context:
        """Return a transient context for use in rendering the view"""
        self._transient_context = Context()
        return self._transient_context

    def render(self, with_context: Context) -> str:
        return self._template.render(with_context)
