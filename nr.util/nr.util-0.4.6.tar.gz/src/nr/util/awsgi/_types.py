
import typing as t


class ASGIApp(t.Protocol):

  def __call__(self, scope, receive, send):
    raise NotImplementedError


class WSGIApp(t.Protocol):

  def __call__(self, environ, start_response):
    raise NotImplementedError
