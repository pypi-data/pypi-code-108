'''
Problems are objects representing some failure that causes the processing of
the current request to be canceled. They are intended to be reported to the
user given an HTTP error code, title and description. When used with Resources,
they can be thrown as exceptions.

You can construct a Problem object for every HTTP error code defined in
`http.HTTPStatus` by calling `Problem.error_status_code_in_lowercase(...)`.

Examples:

- `HTTPStatus.BAD_REQUEST` (400):

  .. code-block:: python

    raise Problem.bad_request(detail="I don't like it.")

- `HTTPStatus.INTERNAL_SERVER_ERROR` (500):

  - **DEPRECATED**:

     .. code-block:: python

       raise Problem.internal_error(detail="Sorry, I still don't like it.")

  - recommended:

     .. code-block:: python

       raise Problem.internal_server_error(
           detail="Sorry, I still don't like it.")

- `HTTPStatus.NOT_IMPLEMENTED` (501):

  .. code-block:: python

    raise Problem.not_implemented()
'''

from http import HTTPStatus
from inspect import getmembers, isfunction
from types import new_class
from typing import Dict
from warnings import warn

from django.http import JsonResponse


def make_problem_class():
    class ProblemImpl(Exception):
        def __init__(self,
                     title: str,
                     status: HTTPStatus,
                     detail: str,
                     should_log: bool = False,
                     headers: Dict[str, str] = {}
                     ):
            self.title = title
            self.status = status
            self.detail = detail
            self.should_log = should_log
            self.headers = headers

        def to_response(self):
            resp = JsonResponse({'title': self.title,
                                 'status': self.status,
                                 'detail': self.detail})
            for key, value in self.headers.items():
                resp[key] = value
            resp.status_code = self.status
            return resp

        # -------------------------------------------------------------------
        # Methods with special features.
        # -------------------------------------------------------------------

        def method_not_allowed(allowed=None):
            headers = {}
            if allowed is not None:
                headers['Allow'] = ', '.join(allowed)
            return Problem('Method not Allowed',
                           HTTPStatus.METHOD_NOT_ALLOWED,
                           ('The requested method is not available on '
                            'this resource'),
                           should_log=False,
                           headers=headers)

        # -------------------------------------------------------------------
        # Methods which stay for backwards compatiblity.
        # -------------------------------------------------------------------

        def not_acceptable():
            return Problem(
                'Not Acceptable',
                HTTPStatus.NOT_ACCEPTABLE,
                ('The requested resource is not capable of generating '
                 'content acceptable according to the Accept headers'))

        def internal_error(detail='internal error'):
            warn('Problem.internal_error() is deprecated. '
                 'Use Problem.internal_server_error() instead.',
                 DeprecationWarning)

            return Problem('Internal Error',
                           HTTPStatus.INTERNAL_SERVER_ERROR,
                           detail,
                           should_log=True)

    overrides = map(lambda it: it[0],
                    getmembers(ProblemImpl, predicate=isfunction))
    error_statuses = dict(map(
        lambda st: (st.name.lower(), st),
        filter(lambda st: (st.value >= 400 and st.value <= 599), HTTPStatus)))

    for method_name in set(error_statuses.keys()) - set(overrides):
        status = error_statuses[method_name]

        def make_problem_function(status, method_name):
            def impl(detail=status.description):
                additionals = {}

                if status.value >= 500 and status.value <= 599:
                    additionals['should_log'] = True

                return Problem(status.phrase, status, detail, **additionals)
            return impl

        setattr(ProblemImpl,
                method_name,
                make_problem_function(status, method_name))

    return new_class('Problem', (ProblemImpl,))


Problem = make_problem_class()
