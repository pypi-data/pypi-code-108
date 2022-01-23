"""
Nozomi
Secure View Module
author: hugh@blinkybeach.com
"""
from nozomi.rendering.view.open import OpenView
from nozomi.http.headers import Headers
from nozomi.http.query_string import QueryString
from nozomi.app.security.session import Session
from nozomi.security.perspective import Perspective
from nozomi.rendering.context import Context
from nozomi.security.considers_perspective import ConsidersPerspective
from typing import Optional, Set
from nozomi.security.request_credentials import RequestCredentials
from nozomi.http.redirect import Redirect
from nozomi.errors.not_authenticated import NotAuthenticated
from nozomi.security.abstract_session import AbstractSession
from nozomi.http.character import Character


class SecureView(OpenView, ConsidersPerspective):
    """A view that requires authentication"""

    allowed_perspectives: Set[Perspective] = NotImplemented
    login_redirect_path: Optional[str] = None

    def login_redirect(
        self,
        query: Optional[QueryString]
    ) -> Optional[Redirect]:
        return None

    def compute_response(
        self,
        query: Optional[QueryString],
        context: Context,
        requesting_agent: AbstractSession,
        character: Character
    ) -> Context:
        raise NotImplementedError

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

        if session is None:
            redirect = self.login_redirect(query)
            if redirect is not None:
                raise redirect
            if self.login_redirect_path is not None:
                raise Redirect(
                    destination=self.login_redirect_path,
                    allow_next=True,
                    preserve_arguments=True,
                )
            raise NotAuthenticated

        if context is None:
            context = Context()

        assert isinstance(session, Session)
        self.enforce_perspective(session)

        return super().serve(
            headers=headers,
            query=query,
            context=context,
            session=session
        )
