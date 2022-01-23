"""
Nozomi
ConsidersPerspective Module
author: hugh@blinkybeach.com
"""
from nozomi.security.perspective import Perspective
from nozomi.app.security.session import Session
from nozomi.http.redirect import Redirect
from typing import Set


class ConsidersPerspective:
    """Abstract class defining a protocol for views conscious of perspective"""

    allowed_perspectives: Set[Perspective] = NotImplemented

    def enforce_perspective(self, session: Session) -> None:
        """Return None if the supplied Session perspective is acceptable"""
        if not isinstance(self.allowed_perspectives, set):
            raise NotImplementedError('Implement .allowed_perspectives')
        if (
                session.perspective not in self.allowed_perspectives
        ):
            raise Redirect(destination='/signin', allow_next=False)
        return
