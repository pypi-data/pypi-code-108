# Copyright 2016 Cisco Systems, Inc
import json
from django.http import JsonResponse
from ..nconf import SessionKey, NetconfSession, NetconfNotSupported


def json_request(decoratee):
    """Decorator for views that expect a request in JSON format."""
    def decorated(request, *args, **kwargs):
        jsondata = {}
        if request.body:
            try:
                jsondata = json.loads(request.body.decode('utf-8'))
            except json.decoder.JSONDecodeError:
                return JsonResponse({}, status=400,
                                    reason="Malformed JSON request")
        return decoratee(request, *args, jsondata=jsondata, **kwargs)
    decorated.__doc__ = decoratee.__doc__
    return decorated


def netconf_session_request(decoratee):
    """Decorator for GET or json_request views that use NetconfSessions.

    Handles the cases where:
    - no device is specified
    - the specified device doesn't exist
    - the specified device doesn't support NETCONF
    """
    def decorated(request, jsondata=None, *args, **kwargs):
        if not jsondata:
            jsondata = {}
        device = jsondata.get('device') or request.GET.get('device')
        if not device:
            return JsonResponse({'reply': "No device profile"},
                                status=400, reason="No device profile")
        user = request.user.username
        key = SessionKey(user, device)
        try:
            NetconfSession.get(key)
        except OSError:
            return JsonResponse({'reply': "No such device"}, status=404,
                                reason="No such device")
        except NetconfNotSupported as exc:
            return JsonResponse({'reply': str(exc)},
                                status=400, reason=str(exc))
        try:
            return decoratee(request, *args,
                             jsondata=jsondata, key=key, **kwargs)
        except Exception as exc:
            return JsonResponse({'reply': str(exc)},
                                status=500, reason=str(exc))

    decorated.__doc__ = decoratee.__doc__
    return decorated
