from importlib import import_module

from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin


class SessionWithThirdPartyMiddleware(MiddlewareMixin):

    def __init__(self, get_response=None):
        self.get_response = get_response
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore

    def process_response(self, request, response):
        session_id = request.GET.get('session_id', None)
        if session_id:
            request.session = self.SessionStore(session_id)
            # Should be set before the response is returned, because of the modified session.
            request.session['THIRD_PARTY_LOGIN'] = True
            return redirect(request.path)
        return response
