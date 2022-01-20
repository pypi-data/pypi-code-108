# Copyright 2016 Cisco Systems, Inc
import json
from django.http import JsonResponse


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
