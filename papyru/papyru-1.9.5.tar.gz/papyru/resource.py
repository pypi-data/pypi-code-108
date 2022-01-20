'''
A base class for RESTful resource implementations to be used as Django views.
Dispatching is handled based on the HTTP method of the request. When handling
a request, the instance-method named exactly like the lowercase version of
the HTTP method is called. The response depends on the control flow of the
specific handler.
If it returns normally, whatever value is returned from the handler is the
response. Otherwise the `Resource` tries to emit a meaningful error message.

- If a `Problem` was raised, it is returned as a response.
- If an ObjectDoesNotExist exception was raised, a `Problem.not_found` instance
  is returned.
- Otherwise the exception is wrapped in a `Problem.internal_error`.

All Problems belonging to the 5XX-class of HTTP errors are logged to stdout.
'''

from django.core.exceptions import ObjectDoesNotExist

from papyru.logger import LogSequence, log_root
from papyru.problem import Problem

# defined in RFC 7231
HTTP_METHODS = set(['get', 'head', 'post', 'put', 'delete', 'connect',
                    'options', 'trace'])


class Resource:
    @log_root()
    def __call__(self, request, *args):
        try:
            with LogSequence('%s %s' % (
                    request.method, request.get_full_path())) as log:

                request_id = request.headers.get('pap-request-id', None)

                if request_id is not None:
                    log.info('Request-ID: %s' % request_id)

                try:
                    method = getattr(self.__class__, request.method.lower())
                except AttributeError:
                    if (request.method.lower() == 'head' and
                            getattr(self.__class__, 'get', False)):
                        return self._simple_head(request, *args)

                    allowed = set(dir(self.__class__)) & HTTP_METHODS
                    raise Problem.method_not_allowed(allowed)

                return method(self, request, *args)

        except Problem as problem:
            return problem.to_response()

        except ObjectDoesNotExist:
            return Problem.not_found().to_response()

        except NotImplementedError:
            return Problem.not_implemented().to_response()

        except Exception as exc:
            return Problem.internal_error(
                'unexpected error: %s' % exc).to_response()

    def _simple_head(self, request, *args):
        method = getattr(self.__class__, 'get')
        resp = method(self, request, *args)
        resp.content = ''
        return resp
