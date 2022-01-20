from __future__ import print_function
import clarus
import clarus.api
from clarus.models import ApiResponse, ApiError
from clarus.multipart import PartWrapper
from requests_toolbelt import MultipartDecoder


def api_request(serviceCategory, service, output=None, responses=None, stream=False, onClose=None, onError=None, onMessage=None, **params):
    if stream:
        clarus.api.streamingRequest(serviceCategory, service, onClose=onClose, onError=onError, onMessage=onMessage, **params)
    else:
        httpresp = clarus.api.request(serviceCategory, service, output, **params);
        if (httpresp.status_code != 200):
            raise ApiError(httpresp)
        else:
            content_type = httpresp.headers.get('content-type', None)

            if (content_type is not None and content_type.startswith('multipart/')):
                decoder = MultipartDecoder.from_response(httpresp)

                rs=[ApiResponse(PartWrapper(part, httpresp)) for part in decoder.parts]

                if (responses is not None):
                    contexts = extract_contexts(params)
                    idx = 0
                    for r in rs: 
                        if contexts is not None and len(rs) == len(contexts):
                            r.set_context(contexts[idx])
                            idx += 1
                        responses.append(r)

                return rs[0]
            else:
                return ApiResponse(httpresp);


def extract_contexts(params):
    params_lower = {k.lower():v for k,v in params.items()}
    contextString = params_lower.get('context')
    if contextString is not None:
        contexts = contextString.split(',')
        return contexts
    return None
