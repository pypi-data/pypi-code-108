#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WSGI middleware to record requests and responses.
"""

from __future__ import print_function, unicode_literals

import logging
import time
import os
import ast

# Required to be loaded early to avoid hitting deadlock situation when processing requests
# See http://code.google.com/p/modwsgi/wiki/ApplicationIssues (at the bottom, under Non Blocking Module Imports)
import _strptime

import itertools
from kafka import KafkaProducer
import json

try:
    from StringIO import StringIO  ## for Python 2
except ImportError:
    from io import StringIO  ## for Python 3
    from io import BytesIO

print("CDC config CDC_KAFKA=", os.getenv('CDC_KAFKA'))
print("CDC config CDC_TOPIC=", os.getenv('CDC_TOPIC'))
print("CDC config CDC_DEBUG=", os.getenv('CDC_DEBUG'))
print("CDC config CDC_DISABLED=", os.getenv('CDC_DISABLED'))

# Set kafka producer if CDC_KAFKA is defined
if os.getenv('CDC_KAFKA') is not None:
    if os.getenv('CDC_DISABLED') is True:
        print("CDC_DISABLED is set to true. Ignore producer")
    else:
        producer = KafkaProducer(bootstrap_servers=os.getenv('CDC_KAFKA'),
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))


class RequestResponseState(object):
    """Capture the data for a request-response."""

    def __init__(self, id, method, url, request_headers, content_length, request_body):
        self.request_id = id
        self.method = method
        self.url = url
        self.request_headers = request_headers
        self.content_length = content_length
        self.request_body = request_body
        self.status = -1
        self.response_headers = None
        self.response_chunks = None
        self.duration_msecs = 0
        self.started_at = time.time()

    def start_response(self, status, response_headers):
        self.status = status
        self.response_headers = response_headers

    def finish_response(self, response_chunks):
        self.duration_msecs = 1000.0 * (time.time() - self.started_at)
        self.response_chunks = response_chunks
        return response_chunks


class SessionRecorderMiddleware(object):
    """WSGI Middleware for recording of request-response"""

    def __init__(self, app, recorder):
        self.app = app
        self.recorder = recorder
        self.request_counter = itertools.count().__next__  # Threadsafe counter

    def __call__(self, environ, start_response):
        state = RequestResponseState(
            self.request_counter(),
            environ['REQUEST_METHOD'],
            self.request_url(environ),
            [(k, v) for k, v in self.parse_request_headers(environ)],
            *self.request_body(environ)
        )

        def _start_response(status, response_headers, *args):
            # Capture status and response_headers for later processing
            state.start_response(status, response_headers)
            return start_response(status, response_headers, *args)

        response_chunks = state.finish_response(self.app(environ, _start_response))
        self.recorder(state)

        # return data to WSGI server
        return response_chunks

    def request_url(self, environ):
        return '{0}{1}{2}'.format(
            environ.get('SCRIPT_NAME', ''),
            environ.get('PATH_INFO', ''),
            '?' + environ['QUERY_STRING'] if environ.get('QUERY_STRING') else '',
        )

    _parse_headers_special = {
        'HTTP_CGI_AUTHORIZATION': 'Authorization',
        'CONTENT_LENGTH': 'Content-Length',
        'CONTENT_TYPE': 'Content-Type',
    }

    def parse_request_headers(self, environ):
        try:
            for cgi_var, value in environ.iteritems():
                if cgi_var in self._parse_headers_special:
                    yield self._parse_headers_special[cgi_var], value
                elif cgi_var.startswith('HTTP_'):
                    yield cgi_var[5:].title().replace('_', '-'), value
        except Exception as e:
            pass

    def request_body(self, environ):
        content_length = environ.get('CONTENT_LENGTH')
        body = ''
        if content_length:
            if content_length == '-1':
                # This is a special case, where the content length is basically undetermined
                body = environ['wsgi.input'].read(-1)
                content_length = len(body)
            else:
                content_length = int(content_length)
                body = environ['wsgi.input'].read(content_length)
            try:
                environ['wsgi.input'] = StringIO(body)  # reset request body for the nested app
            except:
                environ['wsgi.input'] = BytesIO(body)  # reset request body for the nested app
        else:
            content_length = 0
        return content_length, body


def is_binary_content_type(content_type):
    type_subtype = content_type.split(';')
    _type, subtype = type_subtype.split('/')
    if _type == 'text':
        return False
    elif _type == 'application':
        return subtype not in (
            'atom+xml', 'ecmascript', 'json', 'javascript', 'rss+xml', 'soap+xml', 'xhtml+xml')
    else:
        return True


def publish_result_to_kafka(state):
    if os.getenv('CDC_DISABLED') is True:
        print("ignore CDC event, CDC_DISABLED is disabled")
        return

    if os.getenv('CDC_KAFKA') is None or os.getenv('CDC_TOPIC') is None:
        print("ignore CDC event, CDC_KAFKA or CDC_TOPIC is not define")
    else:
        # Dump logs if debug is on
        if os.getenv('CDC_DEBUG') is not None:
            print("(CDC) Request/Response:", state.request_body, '{0} {1}'.format(state.method, state.url),
                  state.status)

        # Convert to string if required
        req_body = state.request_body
        if isinstance(req_body, (bytes, bytearray)):
            req_body = json.loads(req_body.decode('utf-8'))

        # Send it over kafka
        try:
            f = producer.send(os.getenv('CDC_TOPIC'), {
                "request": {
                    "body": req_body,
                    "method": state.method,
                    "url": state.url
                },
                "response": {
                    "status": state.status
                }
            })
            f.get(timeout=60)
        except Exception as e:
            print("Error in sending CDC event", err)
            pass


def log_results(state):
    print("(v1) Request Body", state.request_body, '{0} {1}'.format(state.method, state.url))
    print("(v1) Response Statue", state.status)


def log_results_1(state):
    # TODO: create an HttpArchive
    data = [
               'SR: {0}'.format(state.request_id),
               '{0} {1}'.format(state.method, state.url),
               str(state.request_headers),
               # TODO: sanitize binary request body => look at request Content-Type
               '{0} bytes: {1}'.format(state.content_length, state.request_body or '<EMPTY>'),
               '=> {0} :: {1:.3f} ms :: {2}'.format(
                   state.status, state.duration_msecs, str(state.response_headers)),
           ] + (
               # TODO: sanitize binary response body => look at response Content-Type
               state.response_chunks
           ) + ['========']
    logging.info('\n'.join(data))

# TODO: unit tests
# def recorder(state):
#    log_results(state)
#
# app.wsgi_app = SessionRecorderMiddleware(app.wsgi_app, recorder)
