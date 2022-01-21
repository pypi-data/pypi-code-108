import pytest
import json

from werkzeug.datastructures import Headers

from cinp.server_common import Response, Namespace, Model, AnonymousUser
from cinp.server_werkzeug import WerkzeugServer, WerkzeugRequest, WerkzeugResponse


def getUser( auth_id, auth_token ):
  return AnonymousUser()


class FakeBody():  # set wsgi.input to  and instance of FakeBody, and set wsgi.input_terminated to true to make it work
  def __init__( self, data ):
    self.data = data.encode( 'utf-8' )

  def read( self, count ):
    return self.data

  def close( self ):
    pass


def test_werkzeug_request():
  env = {
          'SERVER_PROTOCOL': 'HTTP/1.1',
          'QUERY_STRING': '',
          'HTTP_HOST': '127.0.0.1:8888',
          'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'PATH_INFO': '/api/',
          'HTTP_USER_AGENT': 'Mozilla/5.0',
          'SERVER_PORT': '8888',
          'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
          'SCRIPT_NAME': '',
          'REMOTE_ADDR': '127.0.0.1',
          'HTTP_CONNECTION': 'keep-alive',
          'REQUEST_METHOD': 'get',
          'wsgi.url_scheme': 'http',
          'wsgi.input_terminated': True,
          'wsgi.input': FakeBody( '"test"' )
        }
  req = WerkzeugRequest( env )
  assert req.verb == 'GET'
  assert req.uri == '/api/'
  assert req.header_map == {}
  assert req.data is None  # no content type the wsgi.input should be ignored

  env = {
          'SERVER_PROTOCOL': 'HTTP/1.1',
          'QUERY_STRING': '',
          'HTTP_HOST': '127.0.0.1:8888',
          'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'PATH_INFO': '/api/ns/model:key:',
          'HTTP_USER_AGENT': 'Mozilla/5.0',
          'SERVER_PORT': '8888',
          'HTTP_ACCEPT_ENCODING': 'gzip, deflate',
          'HTTP_AUTH_ID': 'root',
          'HTTP_AUTH_TOKEN': 'kd8dkv&TTIv893ink',
          'HTTP_FILTER': 'curent',
          'SCRIPT_NAME': '',
          'REMOTE_ADDR': '127.0.0.1',
          'REQUEST_METHOD': 'DELETE',
          'CONTENT_TYPE': 'application/json;charset=utf-8',
          'HTTP_CINP_VERSION': '1.0',
          'HTTP_CONNECTION': 'keep-alive',
          'HTTP_POSITION': 50,
          'HTTP_COUNT': 34,
          'HTTP_MULTI_OBJECT': True,
          'wsgi.url_scheme': 'http',
          'wsgi.input_terminated': True,
          'wsgi.input': FakeBody( '{ "this": "works" }' )
        }
  req = WerkzeugRequest( env )
  assert req.verb == 'DELETE'
  assert req.uri == '/api/ns/model:key:'
  assert req.header_map == { 'CINP-VERSION': '1.0', 'CONTENT-TYPE': 'application/json;charset=utf-8', 'FILTER': 'curent', 'AUTH-ID': 'root', 'AUTH-TOKEN': 'kd8dkv&TTIv893ink', 'POSITION': '50', 'COUNT': '34', 'MULTI-OBJECT': 'True' }
  assert req.data == { 'this': 'works' }


def test_werkzeug_response():
  resp = Response( 201, { 'hi': 'there' }, { 'hdr': 'big' } )
  assert resp.header_map == { 'hdr': 'big' }
  wresp = WerkzeugResponse( resp ).asJSON()
  assert wresp.status_code == 201
  assert wresp.headers == Headers( [ ( 'hdr', 'big' ), ( 'Content-Type', 'application/json;charset=utf-8' ), ( 'Content-Length', '15' ) ] )
  assert wresp.data == '{"hi": "there"}'.encode( 'utf-8' )

  resp = Response( 200, 'more stuff', { 'count': 20 } )
  wresp = WerkzeugResponse( resp ).asJSON()
  assert wresp.status_code == 200
  assert wresp.headers == Headers( [ ( 'count', 20 ), ( 'Content-Type', 'application/json;charset=utf-8' ), ( 'Content-Length', '12' ) ] )
  assert wresp.data == '"more stuff"'.encode( 'utf-8' )

  resp = Response( 404, [ 'one', 2, { '3': 'three' } ] )
  wresp = WerkzeugResponse( resp ).asJSON()
  assert wresp.status_code == 404
  assert wresp.headers == Headers( [ ( 'Content-Type', 'application/json;charset=utf-8' ), ( 'Content-Length', '26' ) ] )
  assert wresp.data == '["one", 2, {"3": "three"}]'.encode( 'utf-8' )

  with pytest.raises( ValueError ):
    WerkzeugResponse( 'test' )


def test_werkzeug_server():
  server = WerkzeugServer( root_path='/api/', root_version='0.0', debug=True, get_user=getUser )
  ns = Namespace( name='ns1', version='0.1', converter=None )
  ns.addElement( Model( name='model1', field_list=[], transaction_class=None ) )
  server.registerNamespace( '/', ns )

  env = {
          'PATH_INFO': '/api/',
          'HTTP_CINP_VERSION': '1.0',
          'REQUEST_METHOD': 'DESCRIBE',
          'wsgi.url_scheme': 'http',
          'wsgi.input_terminated': True,
          'wsgi.input': FakeBody( '' )
        }
  wresp = server.handle( env )
  assert wresp.status_code == 200
  assert wresp.headers == Headers( [ ( 'Cache-Control', 'max-age=0' ), ( 'Cinp-Version', '1.0' ), ( 'Content-Type', 'application/json;charset=utf-8' ), ( 'Content-Length', '120' ), ( 'Verb', 'DESCRIBE' ), ( 'Type', 'Namespace' ) ] )
  assert json.loads( str( wresp.data, 'utf-8' ) ) == { 'multi-uri-max': 100, 'api-version': '0.0', 'path': '/api/', 'namespaces': [ '/api/ns1/' ], 'models': [], 'name': 'root' }
