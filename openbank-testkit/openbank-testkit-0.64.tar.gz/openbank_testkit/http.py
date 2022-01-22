#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ssl
import urllib.request
import urllib.response
import socket
import time
import http
import io


class RealResponse(object):

  def __init__(self, response):
    self.__underlying = response

  def read(self, *args, **kwargs):
    return self.__underlying.read(*args, **kwargs)

  def getheader(self, key):
    return self.__underlying.getheader(key)

  @property
  def content_type(self):
    return self.__underlying.info().get_content_type()

  @property
  def status(self):
    return self.__underlying.status

  def __del__(self):
    self.__underlying.read()
    del self.__underlying


class StubResponse(object):

  def __init__(self, status, body):
    self.status = status
    self.__body = body

  def read(self, *args, **kwargs):
    return self.__body.read(*args, **kwargs)

  def getheader(self, key):
    return None

  @property
  def content_type(self):
    return 'text-plain'


class Request(object):

  def __init__(self, **kwargs):
    self.__underlying = urllib.request.Request(**kwargs)

  def add_header(self, key, value):
    self.__underlying.add_unredirected_header(key, value)

  @property
  def data(self):
    return self.__underlying.data

  @data.setter
  def data(self, value):
    self.__underlying.data = value.encode('utf-8')

  def __str__(self):
    return str(self.__underlying)

  def do(self):
    timeout = 30
    last_exception = None
    
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.options |= (
      ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    )
    ctx.set_ciphers("ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20")
    ctx.verify_mode = ssl.CERT_NONE

    deadline = time.monotonic() + (2 * timeout)
    while deadline > time.monotonic():
      try:
        return RealResponse(urllib.request.urlopen(self.__underlying, timeout=timeout, context=ctx))
      except (http.client.RemoteDisconnected, socket.timeout, ssl.SSLError) as err:
        return StubResponse(504, io.BytesIO(str(err).encode('utf-8')))
      except urllib.error.HTTPError as err:
        return StubResponse(err.code, err)
      except urllib.error.URLError as err:
        last_exception = err
        time.sleep(0.5)

    if last_exception:
      raise last_exception
    else:
      raise AssertionError('timeout after {} seconds'.format(timeout))
