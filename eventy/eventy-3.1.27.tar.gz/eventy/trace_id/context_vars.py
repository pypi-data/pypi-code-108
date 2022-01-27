# Copyright (c) Qotto, 2021

"""
Trace IDs context variables
"""

from contextvars import ContextVar

correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
"""
correlation_id context variable

>>> from eventy.trace_id import correlation_id_var
>>> correlation_id_var.set('my_operation_using_many_services')
>>> print(correlation_id_var.get())
'my_operation_using_many_services'
"""

request_id_var: ContextVar[str] = ContextVar('request_id', default='')
"""
request_id trace context variable

>>> from eventy.trace_id import request_id_var
>>> request_id_var.set('my_service_request')
>>> print(request_id_var.get())
'my_service_request'
"""
