import pytest

from cinp.client import CInP, ResponseError, InvalidRequest, DetailedInvalidRequest, InvalidSession, NotAuthorized, NotFound, ServerError

# TODO: test timeout value  passthrough
# TODO: test setting proxy, also make sure the envrionment proxy settings are handdled correctly


class MockResponse():
  def __init__( self, code, header_map, data ):
    super().__init__()
    self.code = code
    self.headers = header_map
    self.data = data.encode( 'utf-8' )

  def read( self ):
    return self.data

  def close( self ):
    pass


def test_constructor():
  CInP( 'http://localhost:8080', '/api/v1/', None )
  CInP( 'http://localhost', '/api/v1/', None )

  with pytest.raises( ValueError ):
    CInP( 'localhost', '/api/v1/', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost', '/api/v1', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost', 'api/v1', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost', 'api/v1/', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost/', '/api/v1/', None )

  with pytest.raises( ValueError ):
    CInP( 'localhost:8080', '/api/v1/', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost:8080', '/api/v1', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost:8080', 'api/v1', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost:8080', 'api/v1/', None )

  with pytest.raises( ValueError ):
    CInP( 'http://localhost:8080/', '/api/v1/', None )


def test_checkRequest():
  cinp = CInP( 'http://localhost', '/api/v1/', None )

  # describe
  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DESCRIBE', '/api/v/', None )

  cinp._checkRequest( 'DESCRIBE', '/api/v1/', None )
  cinp._checkRequest( 'DESCRIBE', '/api/v1/model', None )
  cinp._checkRequest( 'DESCRIBE', '/api/v1/ns/model', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DESCRIBE', '/api/v1/model:sadf:', None )

  cinp._checkRequest( 'DESCRIBE', '/api/v1/model(action)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DESCRIBE', '/api/v1/model:sadf:(action)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DESCRIBE', '/api/v1/model', 'sdf' )

  # get
  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/ns/', None )

  cinp._checkRequest( 'GET', '/api/v1/model:asdf:', None )
  cinp._checkRequest( 'GET', '/api/v1/model:adsf:ert:', None )
  cinp._checkRequest( 'GET', '/api/v1/ns/model:asdf:', None )
  cinp._checkRequest( 'GET', '/api/v1/ns/model:adsf:ert:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/:asdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/model:adsf', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/model:adsf:ert', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/model(sdf)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/model:ad:', {'sdf': 'sdf'} )

  # create
  cinp._checkRequest( 'CREATE', '/api/v1/model', { 'asdf': 'asdf' } )
  cinp._checkRequest( 'CREATE', '/api/v1/ns/model', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/ns/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/ns/model', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/ns/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/ns/model:sdf:234', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/model:sdf:234', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CREATE', '/api/v1/model(sdf)', None )

  # update
  cinp._checkRequest( 'UPDATE', '/api/v1/model:123:', { 'asdf': 'asdf' } )
  cinp._checkRequest( 'UPDATE', '/api/v1/ns/model:123:', { 'asdf': 'asdf' } )

  cinp._checkRequest( 'UPDATE', '/api/v1/model:asd:234:', { 'asdf': 'asdf' } )
  cinp._checkRequest( 'UPDATE', '/api/v1/ns/model:asd:123:', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/model:123:asd', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/ns/model:434:fsd', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/model:123:asd:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/ns/model:434:fsd:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/model', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/ns/model', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/ns/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/ns/model', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'UPDATE', '/api/v1/ns/model(sdf)', None )

  # delete
  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/ns/', None )

  cinp._checkRequest( 'DELETE', '/api/v1/model:asdf:', None )
  cinp._checkRequest( 'DELETE', '/api/v1/model:adsf:ert:', None )
  cinp._checkRequest( 'DELETE', '/api/v1/ns/model:asdf:', None )
  cinp._checkRequest( 'DELETE', '/api/v1/ns/model:adsf:ert:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/:asdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/model:adsf', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/model:adsf:ert', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/model(dsf)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'DELETE', '/api/v1/model:sdf:', {'sdf': 2} )

  # list
  cinp._checkRequest( 'LIST', '/api/v1/model', { 'asdf': 'asdf' } )
  cinp._checkRequest( 'LIST', '/api/v1/ns/model', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/ns/', None )

  cinp._checkRequest( 'LIST', '/api/v1/model', None )
  cinp._checkRequest( 'LIST', '/api/v1/ns/model', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/ns/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/ns/model:sdf:234', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/model:sdf:234', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'LIST', '/api/v1/model(sdf)', None )

  # call
  cinp._checkRequest( 'CALL', '/api/v1/model(act)', { 'asdf': 'asdf' } )
  cinp._checkRequest( 'CALL', '/api/v1/ns/model(act)', { 'asdf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/ns/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v/(act)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/(act)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/ns/(act)', None )

  cinp._checkRequest( 'CALL', '/api/v1/model(act)', None )
  cinp._checkRequest( 'CALL', '/api/v1/ns/model(act)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/ns/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/ns/model:sdf:234', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/model:sdf:234', None )

  cinp._checkRequest( 'CALL', '/api/v1/model:sdf:(act)', None )
  cinp._checkRequest( 'CALL', '/api/v1/ns/model:wer:(act)', None )
  cinp._checkRequest( 'CALL', '/api/v1/model:sdf:234:(act)', None )
  cinp._checkRequest( 'CALL', '/api/v1/ns/model:wer:erf:(act)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'CALL', '/api/v1/ns/model:sdf:234(act)', None )

  # bogus
  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/model', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/model', { 'adsf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/model:sdf:', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/model:sdf:asdf', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/model(sdf)', None )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'ASDF', '/api/v1/ns/model', { 'adsf': 'asdf' } )

  with pytest.raises( InvalidRequest ):
    cinp._checkRequest( 'GET', '/api/v1/ns/model:sdf:asdf', 'stuff' )


def test_request( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, {}, '' )

  with pytest.raises( InvalidRequest ):
    cinp._request( 'GET', '//api/v1/model')

  mocked_open.reset_mock()
  ( code, data, header_map ) = cinp._request( 'GET', '/api/v1/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert code == 200
  assert data is None
  assert header_map == {}

  mocked_open.reset_mock()
  ( code, data, header_map ) = cinp._request( 'UPDATE', '/api/v1/model:123:', data={ 'myval': 234 } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b'{"myval": 234}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'UPDATE'
  assert code == 200
  assert data is None
  assert header_map == {}

  mocked_open.reset_mock()
  ( code, data, header_map ) = cinp._request( 'LIST', '/api/v1/model', data={ 'myval': 'me' }, header_map={ 'Pos': 123 } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{"myval": "me"}'
  assert req.headers == { 'Pos': 123, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  assert code == 200
  assert data is None
  assert header_map == {}

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, 'not JSON' )
  with pytest.raises( ResponseError ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 400, {}, '{}' )
  with pytest.raises( InvalidRequest ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 400, {}, 'not JSON' )
  with pytest.raises( InvalidRequest ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 400, {}, '{ "message": "this is a test" }' )
  with pytest.raises( DetailedInvalidRequest ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 401, {}, '{}' )
  with pytest.raises( InvalidSession ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 403, {}, '{}' )
  with pytest.raises( NotAuthorized ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 404, {}, '{}' )
  with pytest.raises( NotFound ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 500, {}, '{}' )
  with pytest.raises( ServerError ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 500, {}, 'not JSON' )
  with pytest.raises( ServerError ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 402, {}, 'not JSON' )
  with pytest.raises( ResponseError ):
    cinp._request( 'GET', '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '{"My thing": "the value"}' )
  ( code, data, header_map ) = cinp._request( 'GET', '/api/v1/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert code == 200
  assert data == { 'My thing': 'the value' }
  assert header_map == {}

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {"Type": "model"}, '' )
  ( code, data, header_map ) = cinp._request( 'GET', '/api/v1/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert code == 200
  assert data is None
  assert header_map == { "Type": "model" }

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {"other": "model"}, '' )
  ( code, data, header_map ) = cinp._request( 'GET', '/api/v1/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert code == 200
  assert data is None
  assert header_map == {}

  cinp = CInP( 'http://bob.com:70', '/theapi/', 'http://proxy:3128/' )
  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '' )
  ( code, data, header_map ) = cinp._request( 'GET', '/theapi/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://bob.com:70/theapi/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert code == 200
  assert data is None
  assert header_map == {}

  cinp = CInP( 'http://asdf.com', '/theapi/', 'http://proxy:3128/' )
  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '' )
  ( code, data, header_map ) = cinp._request( 'GET', '/theapi/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://asdf.com/theapi/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert code == 200
  assert data is None
  assert header_map == {}


def test_get( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, {}, '{"key": "value", "thing": "stuff"}' )

  with pytest.raises( InvalidRequest ):
    cinp.get( '/api/v1/' )

  with pytest.raises( InvalidRequest ):
    cinp.get( '/api/v1/model' )

  mocked_open.reset_mock()
  rec_values = cinp.get( '/api/v1/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert rec_values == { 'key': 'value', 'thing': 'stuff' }

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, {}, '{"key": "value", "thing": "stuff"}' )
  with pytest.raises( ResponseError ):
    cinp.get( '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '"hi mom"' )
  with pytest.raises( ResponseError ):
    cinp.get( '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 404, {}, '{"key": "value", "thing": "stuff"}' )
  with pytest.raises( NotFound ):
    cinp.get( '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '{"key": "value", "thing": "stuff"}' )
  rec_values = cinp.get( '/api/v1/model:123:', force_multi_mode=True )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  assert rec_values == { 'key': 'value', 'thing': 'stuff' }


def test_list( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, { 'Position': '0', 'Count': '2', 'Total': '20' }, '["/api/v1/model:123:","/api/v1/model:124:"]' )

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/' )

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/model:asdf:' )

  mocked_open.reset_mock()
  ( items, count_map ) = cinp.list( '/api/v1/model' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{}'
  assert req.headers == { 'Position': '0', 'Count': '10', 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  assert items == [ '/api/v1/model:123:', '/api/v1/model:124:' ]
  assert count_map == { 'position': 0, 'count': 2, 'total': 20 }

  mocked_open.reset_mock()
  ( items, count_map ) = cinp.list( '/api/v1/model', count=5, position=20 )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{}'
  assert req.headers == { 'Position': '20', 'Count': '5', 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  assert items == [ '/api/v1/model:123:', '/api/v1/model:124:' ]
  assert count_map == { 'position': 0, 'count': 2, 'total': 20 }

  mocked_open.reset_mock()
  ( items, count_map ) = cinp.list( '/api/v1/model', filter_name='alpha', filter_value_map={ 'sort_by': 'age' } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{"sort_by": "age"}'
  assert req.headers == { 'Filter': 'alpha', 'Position': '0', 'Count': '10', 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  assert items == [ '/api/v1/model:123:', '/api/v1/model:124:' ]
  assert count_map == { 'position': 0, 'count': 2, 'total': 20 }

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/', filter_value_map='asdf' )

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/', position=-1 )

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/', count=-1 )

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/', position='adf' )

  with pytest.raises( InvalidRequest ):
    cinp.list( '/api/v1/', count='asdf' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, { 'Position': '0', 'Count': '2', 'Total': '20' }, '["/api/v1/model:123:","/api/v1/model:124:"]' )
  with pytest.raises( ResponseError ):
    cinp.list( '/api/v1/model' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, { 'Position': '0', 'Count': '2', 'Total': '20' }, '"adsf"' )
  with pytest.raises( ResponseError ):
    cinp.list( '/api/v1/model' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, { 'Position': '0', 'Count': '2', 'Total': '20' }, '{"adsf":"sdf"}' )
  with pytest.raises( ResponseError ):
    cinp.list( '/api/v1/model' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '["/api/v1/model:123:","/api/v1/model:124:"]' )
  ( items, count_map ) = cinp.list( '/api/v1/model' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{}'
  assert req.headers == { 'Position': '0', 'Count': '10', 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  assert items == [ '/api/v1/model:123:', '/api/v1/model:124:' ]
  assert count_map == { 'position': 0, 'count': 0, 'total': 0 }

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, { 'Position': 'a', 'Count': 'b', 'Total': 'c' }, '["/api/v1/model:123:","/api/v1/model:124:"]' )
  ( items, count_map ) = cinp.list( '/api/v1/model' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{}'
  assert req.headers == { 'Position': '0', 'Count': '10', 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  assert items == [ '/api/v1/model:123:', '/api/v1/model:124:' ]
  assert count_map == { 'position': 0, 'count': 0, 'total': 0 }


def test_create( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 201, { 'Object-Id': 'test' }, '{"asdf": "erere"}' )

  with pytest.raises( InvalidRequest ):
    cinp.create( '/api/v1/', { 'asdf': 'xcv' } )

  with pytest.raises( InvalidRequest ):
    cinp.create( '/api/v1/model:adsf:', { 'asdf': 'xcv' } )

  with pytest.raises( InvalidRequest ):
    cinp.create( '/api/v1/model', 'adsf' )

  mocked_open.reset_mock()
  rec_values = cinp.create( '/api/v1/model', {} )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CREATE'
  assert rec_values == ( 'test', { 'asdf': 'erere' } )

  mocked_open.reset_mock()
  rec_values = cinp.create( '/api/v1/model', { 'asdf': 'xcv' } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b'{"asdf": "xcv"}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CREATE'
  assert rec_values == ( 'test', { 'asdf': 'erere' } )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '"/api/v1/model:123:"' )
  with pytest.raises( ResponseError ):
    cinp.create( '/api/v1/model', { 'asdf': 'xcv' } )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, {}, '["/api/v1/model:123:"]' )
  with pytest.raises( ResponseError ):
    cinp.create( '/api/v1/model', { 'asdf': 'xcv' } )

  mocked_open.return_value = MockResponse( 200, {}, '{ "hi": "there"}' )
  with pytest.raises( ResponseError ):
    cinp.create( '/api/v1/model', { 'asdf': 'xcv' } )


def test_update( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, {}, '{"hi": "there"}' )

  with pytest.raises( InvalidRequest ):
    cinp.update( '/api/v1/', { 'asdf': 'xcv' } )

  with pytest.raises( InvalidRequest ):
    cinp.update( '/api/v1/model', 'adsf' )

  with pytest.raises( InvalidRequest ):
    cinp.update( '/api/v1/model', { 'asdf': 'xcv' } )

  mocked_open.reset_mock()
  rec_values = cinp.update( '/api/v1/model:asdf:', { 'asdf': 'xcv' } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:asdf:'
  assert req.data == b'{"asdf": "xcv"}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'UPDATE'
  assert rec_values == { 'hi': 'there' }

  mocked_open.reset_mock()
  rec_values = cinp.update( '/api/v1/model:asdf:123:', { 'asdf': 'xcv' } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:asdf:123:'
  assert req.data == b'{"asdf": "xcv"}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'UPDATE'
  assert rec_values == { 'hi': 'there' }

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '"/api/v1/model:123:"' )
  with pytest.raises( ResponseError ):
    cinp.update( '/api/v1/model:123:', { 'asdf': 'xcv' } )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '["/api/v1/model:123:"]' )
  with pytest.raises( ResponseError ):
    cinp.update( '/api/v1/model:123:', { 'asdf': 'xcv' } )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, {}, '{ "hi": "there"}' )
  with pytest.raises( ResponseError ):
    cinp.update( '/api/v1/model:123:', { 'asdf': 'xcv' } )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 404, {}, '{"hi": "there"}' )
  with pytest.raises( NotFound ):
    cinp.update( '/api/v1/model:123:', { 'asdf': 'xcv' } )


def test_delete( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, {}, '{}' )

  with pytest.raises( InvalidRequest ):
    cinp.delete( '/api/v1/' )

  with pytest.raises( InvalidRequest ):
    cinp.delete( '/api/v1/model' )

  mocked_open.reset_mock()
  result = cinp.delete( '/api/v1/model:123:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'DELETE'
  assert result is True

  mocked_open.reset_mock()
  result = cinp.delete( '/api/v1/model:123:asdf:' )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:123:asdf:'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'DELETE'
  assert result is True

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, {}, '{}' )
  with pytest.raises( ResponseError ):
    cinp.delete( '/api/v1/model:123:' )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 404, {}, '{}' )
  with pytest.raises( NotFound ):
    cinp.delete( '/api/v1/model:123:' )


def test_call( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, {}, '{}' )

  with pytest.raises( InvalidRequest ):
    cinp.call( '/api/v1/', {} )

  with pytest.raises( InvalidRequest ):
    cinp.call( '/api/v1/model', {} )

  with pytest.raises( InvalidRequest ):
    cinp.call( '/api/v1/model:dfs:', {} )

  with pytest.raises( InvalidRequest ):
    cinp.call( '/api/v1/model(adsf)', 'sdf' )

  mocked_open.reset_mock()
  return_value = cinp.call( '/api/v1/model(myfunc)', {} )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model(myfunc)'
  assert req.data == b'{}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CALL'
  assert return_value == {}

  mocked_open.reset_mock()
  return_value = cinp.call( '/api/v1/model:234:(myfunc)', {} )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:234:(myfunc)'
  assert req.data == b'{}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CALL'
  assert return_value == {}

  mocked_open.reset_mock()
  return_value = cinp.call( '/api/v1/model:234:sdf:(myfunc)', {} )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model:234:sdf:(myfunc)'
  assert req.data == b'{}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CALL'
  assert return_value == {}

  mocked_open.reset_mock()
  return_value = cinp.call( '/api/v1/model(myfunc)', { 'arg1': 12 } )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model(myfunc)'
  assert req.data == b'{"arg1": 12}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CALL'
  assert return_value == {}

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '"The Value"' )
  return_value = cinp.call( '/api/v1/model(myfunc)', {} )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model(myfunc)'
  assert req.data == b'{}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CALL'
  assert return_value == 'The Value'

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 200, {}, '{ "stuff": "nice"}' )
  return_value = cinp.call( '/api/v1/model(myfunc)', {} )
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model(myfunc)'
  assert req.data == b'{}'
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'CALL'
  assert return_value == { 'stuff': 'nice' }

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 404, {}, '' )
  with pytest.raises( NotFound ):
    cinp.call( '/api/v1/model:123:(myfunc)', {} )

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, {}, '' )
  with pytest.raises( ResponseError ):
    cinp.call( '/api/v1/model(myfunc)', {} )


def test_describe( mocker ):
  header_map = {}
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, header_map, '' )

  with pytest.raises( InvalidRequest ):
    cinp.describe( '/api/v1/model:sdf:' )

  header_map[ 'Type' ] = 'Namespace'
  mocked_open.reset_mock()
  data, type = cinp.describe( '/api/v1/' )
  assert type == 'Namespace'
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'DESCRIBE'
  assert data is None

  header_map[ 'Type' ] = 'Model'
  mocked_open.reset_mock()
  data, type = cinp.describe( '/api/v1/model' )
  assert type == 'Model'
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'DESCRIBE'
  assert data is None

  header_map[ 'Type' ] = 'Action'
  mocked_open.reset_mock()
  data, type = cinp.describe( '/api/v1/model(sdf)' )
  assert type == 'Action'
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/model(sdf)'
  assert req.data == b''
  assert req.headers == { 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'DESCRIBE'
  assert data is None

  mocked_open.reset_mock()
  mocked_open.return_value = MockResponse( 201, {}, '' )
  with pytest.raises( ResponseError ):
    cinp.describe( '/api/v1/model' )


def test_setauth():
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  cinp.setAuth( 'user', 'token' )
  cinp.setAuth()


def test_get_multi( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, {}, '{"/api/v1/ns/model:asd:":{"key1":"value1"},"/api/v1/ns/model:efe:":{"key2":"value2"}}' )

  mocked_open.reset_mock()
  gen = cinp.getMulti( '/api/v1/ns/model:asd:efe:' )
  assert mocked_open.call_args is None
  assert sorted( list( gen ) ) == sorted( [ ( '/api/v1/ns/model:asd:', { 'key1': 'value1' } ), ( '/api/v1/ns/model:efe:', { 'key2': 'value2' } ) ] )
  assert mocked_open.call_count == 1
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model:asd:efe:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'

  mocked_open.reset_mock()
  gen = cinp.getMulti( '/api/v1/ns/model', [ 'asd', 'efe' ] )
  assert mocked_open.call_args is None
  assert sorted( list( gen ) ) == sorted( [ ( '/api/v1/ns/model:asd:', { 'key1': 'value1' } ), ( '/api/v1/ns/model:efe:', { 'key2': 'value2' } ) ] )
  assert mocked_open.call_count == 1
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model:asd:efe:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'

  mocked_open.reset_mock()
  gen = cinp.getMulti( '/api/v1/ns/model:123:', [ 'asd', 'efe' ] )
  assert mocked_open.call_args is None
  assert sorted( list( gen ) ) == sorted( [ ( '/api/v1/ns/model:asd:', { 'key1': 'value1' } ), ( '/api/v1/ns/model:efe:', { 'key2': 'value2' } ) ] )
  assert mocked_open.call_count == 1
  req = mocked_open.call_args[0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model:asd:efe:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'

  mocked_open.reset_mock()
  gen = cinp.getMulti( '/api/v1/ns/model', [ 'asd', 'efe', 'qwe', '123' ], chunk_size=2 )
  assert mocked_open.call_args is None
  assert sorted( list( gen ) ) == sorted( [ ( '/api/v1/ns/model:asd:', { 'key1': 'value1' } ), ( '/api/v1/ns/model:efe:', { 'key2': 'value2' } ), ( '/api/v1/ns/model:asd:', { 'key1': 'value1' } ), ( '/api/v1/ns/model:efe:', { 'key2': 'value2' } ) ] )
  assert mocked_open.call_count == 2
  req = mocked_open.call_args_list[0][0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model:asd:efe:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'
  req = mocked_open.call_args_list[1][0][0]
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model:qwe:123:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'


def test_get_filtered_objects( mocker ):
  cinp = CInP( 'http://localhost:8080', '/api/v1/', None )
  mocked_open = mocker.patch( 'urllib.request.OpenerDirector.open' )
  mocked_open.return_value = MockResponse( 200, { 'Position': 0, 'Count': 2, 'Total': 2 }, '["/api/v1/ns/model:asd:","/api/v1/ns/model:efe:"]' )

  gen = cinp.getFilteredObjects( '/api/v1/ns/model' )
  req = mocked_open.call_args[0][0]
  assert mocked_open.call_count == 1
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model'
  assert req.data == b'{}'
  assert req.headers == { 'Count': '100', 'Position': '0', 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'LIST'
  mocked_open.return_value = MockResponse( 200, {}, '{"/api/v1/ns/model:asd:":{"key1":"value1"},"/api/v1/ns/model:efe:":{"key2":"value2"}}' )
  assert sorted( list( gen ) ) == sorted( [ ( '/api/v1/ns/model:asd:', { 'key1': 'value1' } ), ( '/api/v1/ns/model:efe:', { 'key2': 'value2' } ) ] )
  req = mocked_open.call_args[0][0]
  assert mocked_open.call_count == 2
  assert req.full_url == 'http://localhost:8080/api/v1/ns/model:asd:efe:'
  assert req.data == b''
  assert req.headers == { 'Multi-object': True, 'Content-type': 'application/json;charset=utf-8' }
  assert req.get_method() == 'GET'


# TODO: figure how to test and then test having multiple LIST calls, will probably take a smarter MockResponse class
