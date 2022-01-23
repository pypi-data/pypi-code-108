"""
Nozomi
Open View Module
author: hugh@blinkybeach.com
"""
from nozomi.rendering.javascript_class import JavaScriptClass
from nozomi.rendering.style import Style
from nozomi.rendering.script import Script
from nozomi.rendering.view.base import BaseView
from nozomi.http.headers import Headers
from nozomi.rendering.context import Context
from nozomi.rendering.open_graph import OpenGraph
from nozomi.ancillary.configuration import Configuration
from nozomi.security.abstract_session import AbstractSession
from typing import List, Dict, Optional, Any, Type, Union
from nozomi.http.query_string import QueryString
from nozomi.security.request_credentials import RequestCredentials


class OpenView(BaseView):
    """A view that supports optional authentication"""

    session_implementation: Type[AbstractSession] = NotImplemented
    requests_may_change_state: bool = NotImplemented

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

        assert isinstance(self.session_implementation, type)
        assert isinstance(self.requests_may_change_state, bool)

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
            static_variables=static_variables,
            static_js_constants=static_js_constants
        )

        return

    def serve(
        self,
        headers: Headers,
        query: Optional[QueryString],
        context: Optional[Context] = None,
        session: Optional[AbstractSession] = None
    ) -> str:

        if session is None:
            session = self.session_implementation.from_headers(
                headers=headers,
                configuration=self.configuration,
                credentials=RequestCredentials.on_behalf_of_agent(
                    agent=self.configuration.api_agent,
                    configuration=self.configuration
                ),
                request_may_change_state=self.requests_may_change_state
            )

        if context is None:
            context = Context()

        if session is not None:
            context.add('agent', session.agent)
            context.add_javascript_constant('global_api_key', session.api_key)
            context.add_javascript_constant(
                'global_session_id',
                session.session_id
            )
            context.add_javascript_constant(
                'requesting_agent_id',
                session.agent_id
            )

        return super().serve(
            headers=headers,
            query=query,
            context=context,
            session=session
        )
