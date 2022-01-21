import pytest

from cinp.common import URI
from cinp.server_common import __CINP_VERSION__, Converter, Paramater, Field, Namespace, Model, Action, Request, Response, Server, InvalidRequest, ServerError, ObjectNotFound, AnonymousUser

# TODO: test CORS header stuff


def sort_dsc( describe ):
  try:
    describe[ 'namespaces' ].sort()
  except KeyError:
    pass

  try:
    describe[ 'models' ].sort()
  except KeyError:
    pass

  try:
    describe[ 'fields' ].sort( key=lambda a: a[ 'name' ] )
  except KeyError:
    pass

  return describe


def fake_func():
  pass


class TestTransaction():
  def get( self, model, object_id ):
    if object_id == 'NOT FOUND':
      return None

    result = {}
    result[ '_extra_' ] = 'get "{0}"'.format( object_id )

    return result

  def create( self, element, value_map ):
    if value_map[ 'field1' ] == 'INVALID':
      raise ValueError( 'The Field is Invalid' )

    if value_map[ 'field1' ] == 'BAD':
      return 'bad bad bad'

    value_map[ '_extra_' ] = 'created'
    return ( 'new_id', value_map )

  def update( self, model, object_id, value_map ):
    if object_id == 'NOT FOUND':
      return None

    result = value_map.copy()
    result[ '_extra_' ] = 'update "{0}"'.format( object_id )

    return result

  def list( self, model, filter_name, filter_values, position, count ):
    if filter_name == 'lots':
      return ( [ 'a', 'b', 'c', 'd', filter_values[ 'more' ], 'at {0}'.format( position ), 'for {0}'.format( count ), 'combined {0}'.format( position + count ) ], 50, 100 )
    elif filter_name is None:
      return ( [ 'a', 'b' ], 0, 2 )
    elif filter_name == 'bad':
      raise ValueError( 'bad stuff' )

    return None  # just to be explicit, None is the return value if you do not return anything

  def delete( self, model, object_id ):
    if object_id == 'NOT FOUND':
      return False
    else:
      return True

  def start( self ):
    pass

  def commit( self ):
    pass

  def abort( self ):
    pass


class testUser():
  def __init__( self, mode ):
    self.mode = mode

  @property
  def is_superuser( self ):
    return self.mode == 'super'

  @property
  def is_anonymous( self ):
    return self.mode == 'anonymous'


def getUser( auth_id, auth_token ):
  if auth_id is None or auth_token is None:
    return AnonymousUser()

  if auth_id == 'super' and auth_token == 'super':
    return testUser( 'super' )

  if auth_id == 'good':
    return testUser( 'good' )

  if auth_token == 'bad':
    return testUser( 'bad' )

  if auth_id == 'me':
    return testUser( 'me' )

  return None


def checkAuth( user, verb, id_list ):
  if user.is_anonymous:
    return False

  if user.mode == 'good':
    return True

  if user.mode == 'me' and id_list[0] == 'me':
    return True

  return False


def test_namespace():
  ns = Namespace( name=None, version='0.0', root_path='/api/', converter=None )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }

  with pytest.raises( ValueError ):
    Namespace( name='root', version='0.0', converter=None )

  with pytest.raises( ValueError ):
    Namespace( name=None, version='0.0', converter=None )

  with pytest.raises( ValueError ):
    Namespace( name=None, version='0.0', root_path='/asd', converter=None )

  ns2 = Namespace( name='ns2', version='2.0', converter=None )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2.describe( ns2.converter ).data ) == { 'name': 'ns2', 'path': None, 'api-version': '2.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  ns.addElement( ns2 )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [ '/api/ns2/' ], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2.describe( ns2.converter ).data ) == { 'name': 'ns2', 'path': '/api/ns2/', 'api-version': '2.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }

  ns3 = Namespace( name='ns3', version='3.0', converter=None )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [ '/api/ns2/' ], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2.describe( ns2.converter ).data ) == { 'name': 'ns2', 'path': '/api/ns2/', 'api-version': '2.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns3.describe( ns3.converter ).data ) == { 'name': 'ns3', 'path': None, 'api-version': '3.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  ns.addElement( ns3 )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [ '/api/ns2/', '/api/ns3/' ], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2.describe( ns2.converter ).data ) == { 'name': 'ns2', 'path': '/api/ns2/', 'api-version': '2.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns3.describe( ns3.converter ).data ) == { 'name': 'ns3', 'path': '/api/ns3/', 'api-version': '3.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }

  ns2_1 = Namespace( name='ns2_1', version='2.1', converter=None, doc='stuff' )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [ '/api/ns2/', '/api/ns3/' ], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2.describe( ns2.converter ).data ) == { 'name': 'ns2', 'path': '/api/ns2/', 'api-version': '2.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns3.describe( ns3.converter ).data ) == { 'name': 'ns3', 'path': '/api/ns3/', 'api-version': '3.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2_1.describe( ns2_1.converter ).data ) == { 'name': 'ns2_1', 'path': None, 'api-version': '2.1', 'namespaces': [], 'models': [], 'multi-uri-max': 100, 'doc': 'stuff' }
  ns2.addElement( ns2_1 )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [ '/api/ns2/', '/api/ns3/' ], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2.describe( ns2.converter ).data ) == { 'name': 'ns2', 'path': '/api/ns2/', 'api-version': '2.0', 'namespaces': [ '/api/ns2/ns2_1/' ], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns3.describe( ns3.converter ).data ) == { 'name': 'ns3', 'path': '/api/ns3/', 'api-version': '3.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( ns2_1.describe( ns2_1.converter ).data ) == { 'name': 'ns2_1', 'path': '/api/ns2/ns2_1/', 'api-version': '2.1', 'namespaces': [], 'models': [], 'multi-uri-max': 100, 'doc': 'stuff' }

  assert ns.describe( ns.converter ).header_map == { 'Cache-Control': 'max-age=0', 'Verb': 'DESCRIBE', 'Type': 'Namespace' }

  assert ns.options().header_map == { 'Allow': 'OPTIONS, DESCRIBE', 'Cache-Control': 'max-age=0' }
  assert ns.options().data is None


def test_field():
  converter = Converter( None )

  with pytest.raises( ValueError ):
    Field( name='test1', type='Unknown' )

  with pytest.raises( ValueError ):
    Field( name='test1', type='Integer', mode='R' )

  field = Field( name='test1', type='String', length=10 )
  assert converter.toPython( field, 'asdf', None ) == 'asdf'
  assert converter.toPython( field, 123, None ) == '123'
  assert converter.toPython( field, 3.21, None ) == '3.21'
  assert converter.toPython( field, None, None ) is None
  assert converter.fromPython( field, 333 ) == '333'
  assert converter.fromPython( field, 23.32 ) == '23.32'
  assert converter.fromPython( field, 'efe' ) == 'efe'
  assert converter.fromPython( field, None ) is None

  with pytest.raises( ValueError ):
    converter.toPython( field, 'Much Much longer than 10 chars', None )

  field = Field( name='test1', type='String' )
  assert converter.toPython( field, 'Much Much longer than 10 chars', None ) == 'Much Much longer than 10 chars'

  field = Field( name='test2', type='Integer' )
  assert converter.toPython( field, 1, None ) == 1
  assert converter.toPython( field, '23', None ) == 23
  with pytest.raises( ValueError ):
    converter.toPython( field, '23.4', None )
  with pytest.raises( ValueError ):
    converter.toPython( field, 'a', None )
  assert converter.toPython( field, None, None ) is None
  assert converter.toPython( field, 12, None ) == 12
  assert converter.toPython( field, '32', None ) == 32
  with pytest.raises( ValueError ):
    converter.fromPython( field, '3.4' )
  with pytest.raises( ValueError ):
    converter.fromPython( field, 'wer' )
  converter.fromPython( field, None ) is None

  field = Field( name='test3', type='Float' )
  assert converter.toPython( field, 12.5, None ) == 12.5
  assert converter.toPython( field, '3.4', None ) == 3.4
  assert converter.toPython( field, '65', None ) == 65.0
  assert converter.toPython( field, None, None ) is None
  with pytest.raises( ValueError ):
    converter.toPython( field, 'ewq', None )
  assert converter.fromPython( field, 5.2 ) == 5.2
  assert converter.fromPython( field, 87 ) == 87.0
  assert converter.fromPython( field, '4.5' ) == 4.5
  with pytest.raises( ValueError ):
    converter.fromPython( field, 'yhn' )
  converter.fromPython( field, None ) is None

  field = Field( name='test4', type='Boolean' )
  # TODO: test boolean, datatime, map, model(includeing model_resolve er) and file


def test_model():
  ns = Namespace( name=None, version='0.0', root_path='/api/', converter=None )

  model1 = Model( name='model1', transaction_class=TestTransaction, field_list=[] )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [], 'models': [], 'multi-uri-max': 100 }
  assert sort_dsc( model1.describe( ns.converter ).data ) == { 'name': 'model1', 'path': None, 'fields': [], 'actions': [], 'constants': {}, 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] }
  ns.addElement( model1 )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [], 'models': [ '/api/model1' ], 'multi-uri-max': 100 }
  assert sort_dsc( model1.describe( model1.parent.converter ).data ) == { 'name': 'model1', 'path': '/api/model1', 'fields': [], 'actions': [], 'constants': {}, 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] }

  field_list = []
  field_list.append( Field( name='field1', type='String', length=50 ) )
  field_list.append( Field( name='field2', type='Integer', mode='RO' ) )

  model2 = Model( name='model2', transaction_class=TestTransaction, field_list=field_list, id_field_name='field2' )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [], 'models': [ '/api/model1' ], 'multi-uri-max': 100 }
  assert sort_dsc( model1.describe( model1.parent.converter ).data ) == { 'name': 'model1', 'path': '/api/model1', 'fields': [], 'actions': [], 'constants': {}, 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] }
  assert sort_dsc( model2.describe( ns.converter ).data ) == { 'name': 'model2', 'path': None, 'fields': [ { 'type': 'String', 'length': 50, 'name': 'field1', 'mode': 'RW', 'required': True, }, { 'type': 'Integer', 'name': 'field2', 'mode': 'RO', 'required': True } ], 'actions': [], 'constants': {}, 'id-field-name': 'field2', 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] }
  ns.addElement( model2 )
  assert sort_dsc( ns.describe( ns.converter ).data ) == { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [], 'models': [ '/api/model1', '/api/model2' ], 'multi-uri-max': 100 }
  assert sort_dsc( model1.describe( model1.parent.converter ).data ) == { 'name': 'model1', 'path': '/api/model1', 'fields': [], 'actions': [], 'constants': {}, 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] }
  assert sort_dsc( model2.describe( model2.parent.converter ).data ) == { 'name': 'model2', 'path': '/api/model2', 'fields': [ { 'type': 'String', 'length': 50, 'name': 'field1', 'mode': 'RW', 'required': True }, { 'type': 'Integer', 'name': 'field2', 'mode': 'RO', 'required': True } ], 'actions': [], 'constants': {}, 'id-field-name': 'field2', 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] }

  assert model2.describe( model2.parent.converter ).header_map == { 'Cache-Control': 'max-age=0', 'Verb': 'DESCRIBE', 'Type': 'Model' }

  assert model2.options().header_map == { 'Allow': 'OPTIONS, DESCRIBE, GET, LIST, CREATE, UPDATE, DELETE' }
  assert model2.options().data is None


def test_action():
  ns = Namespace( name=None, version='0.0', root_path='/api/', converter=None )
  model = Model( name='model1', transaction_class=TestTransaction, field_list=[] )
  ns.addElement( model )

  action1 = Action( name='act1', return_paramater=Paramater( type='String' ), func=fake_func )
  assert sort_dsc( action1.describe( ns.converter ).data ) == { 'name': 'act1', 'return-type': { 'type': 'String' }, 'paramaters': [], 'static': True, 'path': None }
  model.addAction( action1 )
  assert sort_dsc( action1.describe( action1.parent.parent.converter ).data ) == { 'name': 'act1', 'return-type': { 'type': 'String' }, 'paramaters': [], 'static': True, 'path': '/api/model1(act1)' }

  action2 = Action( name='act2', return_paramater=Paramater( type='Integer' ), static=False, func=fake_func )
  assert sort_dsc( action2.describe( ns.converter ).data ) == { 'name': 'act2', 'return-type': { 'type': 'Integer' }, 'paramaters': [], 'static': False, 'path': None }

  action3 = Action( name='act3', return_paramater=Paramater( type='Boolean' ), paramater_list=[ Paramater( name='bob', type='Float' ) ], static=False, func=fake_func )
  model.addAction( action3 )
  assert sort_dsc( action3.describe( action3.parent.parent.converter ).data ) == { 'name': 'act3', 'return-type': { 'type': 'Boolean' }, 'paramaters': [ { 'name': 'bob', 'type': 'Float' } ], 'static': False, 'path': '/api/model1(act3)' }

  assert action3.describe( action3.parent.parent.converter ).header_map == { 'Cache-Control': 'max-age=0', 'Verb': 'DESCRIBE', 'Type': 'Action' }

  assert action3.options().header_map == { 'Allow': 'OPTIONS, DESCRIBE, CALL' }
  assert action3.options().data is None


def test_call():
  converter = Converter( None )
  field_list = []
  field_list.append( Field( name='field1', type='String', length=50 ) )
  field_list.append( Field( name='field2', type='Integer' ) )
  model = Model( name='model1', transaction_class=TestTransaction, field_list=field_list )
  transaction = model.transaction_class()

  action1 = Action( name='act1', return_paramater=Paramater( type='String' ), func=lambda: 'hello' )
  resp = action1.call( converter, transaction, None, {}, None, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CALL', 'Multi-Object': 'False' }
  assert resp.data == 'hello'

  action2 = Action( name='act2', return_paramater=Paramater( type='String' ), paramater_list=[ Paramater( name='p1', type='String', default='alice' ) ], func=lambda p1: 'hello "{0}"'.format( p1 ) )
  # with pytest.raises( InvalidRequest ):  # should we be ignorning data?
  #  resp = action2.call( converter, transaction, None, { 'p1': 'bob', 'nope': 'sue' }, None, False )

  resp = action2.call( converter, transaction, None, {}, None, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CALL', 'Multi-Object': 'False' }
  assert resp.data == 'hello "alice"'

  resp = action2.call( converter, transaction, None, { 'p1': 'bob' }, None, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CALL', 'Multi-Object': 'False' }
  assert resp.data == 'hello "bob"'

  action3 = Action( name='act3', return_paramater=Paramater( type='String' ), func=lambda a: 'hello "{0}"'.format( a ), static=False )
  model.addAction( action3 )
  with pytest.raises( InvalidRequest ):
    action3.call( converter, transaction, None, { 'a': 'bob' }, None, False )

  resp = action3.call( converter, transaction, [ 'sue' ], {}, None, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CALL', 'Multi-Object': 'False' }
  assert resp.data == 'hello "{\'_extra_\': \'get "sue"\'}"'

  with pytest.raises( ObjectNotFound ):
    action3.call( converter, transaction, [ 'NOT FOUND' ], {}, None, False )

  action4 = Action( name='act4', func=lambda: 'hello' )
  resp = action4.call( converter, transaction, [], {}, None, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CALL', 'Multi-Object': 'False' }
  assert resp.data is None

  action9 = Action( name='act9', return_paramater=Paramater( type='String' ), paramater_list=[ Paramater( name='p1', type='String' ), Paramater( name='p2', type='_USER_' ) ], func=lambda p1, p2: '{0}: {1}'.format( p1, p2 ) )
  resp = action9.call( converter, transaction, None, { 'p1': 'stuff' }, 'Me The User', False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CALL', 'Multi-Object': 'False' }
  assert resp.data == 'stuff: Me The User'


def test_create():
  converter = Converter( None )
  field_list = []
  field_list.append( Field( name='field1', mode='RW', type='String', length=50 ) )
  field_list.append( Field( name='field2', mode='RW', type='Integer' ) )
  field_list.append( Field( name='field3', mode='RW', type='String', length=20, required=False, default='Hello World' ) )
  field_list.append( Field( name='field4', mode='RO', type='String', length=20, required=False, default='Not Me' ) )
  model = Model( name='model1', field_list=field_list, transaction_class=TestTransaction )
  transaction = model.transaction_class()

  resp = model.create( converter, transaction, { 'field1': 'hello', 'field2': 5 } )
  assert resp.http_code == 201
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CREATE', 'Object-Id': 'None:new_id:' }
  assert resp.data == { '_extra_': 'created', 'field1': 'hello', 'field2': 5, 'field3': 'Hello World' }

  resp = model.create( converter, transaction, { 'field1': 'by', 'field2': 30, 'field3': 'good by' } )
  assert resp.http_code == 201
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'CREATE', 'Object-Id': 'None:new_id:' }
  assert resp.data == { '_extra_': 'created', 'field1': 'by', 'field2': 30, 'field3': 'good by' }

  with pytest.raises( InvalidRequest ):
    model.create( converter, transaction, { 'field1': 'hello', 'field2': 'sdf' } )

  with pytest.raises( InvalidRequest ):
    model.create( converter, transaction, { 'field1': 'hello' } )

  with pytest.raises( InvalidRequest ):
    model.create( converter, transaction, {} )

  with pytest.raises( InvalidRequest ):
    model.create( converter, transaction, { 'field1': 'hello', 'field2': 'sdf', 'fieldX': 'bad' } )

  with pytest.raises( InvalidRequest ):
    model.create( converter, transaction, { 'field1': 'INVALID', 'field2': 5 } )

  with pytest.raises( ServerError ):
    model.create( converter, transaction, { 'field1': 'BAD', 'field2': 5 } )


def test_list():
  converter = Converter( None )
  field_list = []
  list_filter_map = {}
  list_filter_map[ 'lots' ] = { 'more': Paramater( name='more', type='String', length=10 ) }
  list_filter_map[ 'bad' ] = {}
  model = Model( name='model1', field_list=field_list, list_filter_map=list_filter_map, transaction_class=TestTransaction )
  transaction = model.transaction_class()

  resp = model.list( converter, transaction, {}, {} )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'LIST', 'Position': '0', 'Count': '2', 'Total': '2', 'Id-Only': 'False' }
  assert resp.data == [ 'None:a:', 'None:b:' ]

  resp = model.list( converter, transaction, { 'more': 'bob' }, { 'FILTER': 'lots', 'POSITION': '23', 'COUNT': '45' } )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'LIST', 'Position': '50', 'Count': '8', 'Total': '100', 'Id-Only': 'False' }
  assert resp.data == [ 'None:a:', 'None:b:', 'None:c:', 'None:d:', 'None:bob:', 'None:at 23:', 'None:for 45:', 'None:combined 68:' ]

  with pytest.raises( InvalidRequest ):
    model.list( converter, transaction, { 'more': 'bob' }, { 'FILTER': 'lots', 'POSITION': 'sdf', 'COUNT': '45' } )

  with pytest.raises( InvalidRequest ):
    model.list( converter, transaction, { 'more': 'bob' }, { 'FILTER': 'lots', 'POSITION': '23', 'COUNT': 'rf' } )

  with pytest.raises( InvalidRequest ):
    model.list( converter, transaction, {}, { 'FILTER': 'not exist' } )

  with pytest.raises( InvalidRequest ):
    model.list( converter, transaction, {}, { 'FILTER': 'bad' } )


def test_get():
  converter = Converter( None )
  field_list = []
  field_list.append( Field( name='field1', mode='RW', type='String', length=50 ) )
  field_list.append( Field( name='field2', mode='RW', type='Integer' ) )
  model = Model( name='model1', field_list=field_list, transaction_class=TestTransaction )
  transaction = model.transaction_class()

  resp = model.get( converter, transaction, [ 'bob' ], False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'GET', 'Multi-Object': 'False' }
  assert resp.data == { '_extra_': 'get "bob"' }

  resp = model.get( converter, transaction, [ 'bob' ], True )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'GET', 'Multi-Object': 'True' }
  assert resp.data == { 'None:bob:': { '_extra_': 'get "bob"' } }

  resp = model.get( converter, transaction, [ 'bob', 'martha', 'sue' ], True )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'GET', 'Multi-Object': 'True' }
  assert resp.data == { 'None:bob:': { '_extra_': 'get "bob"' }, 'None:martha:': { '_extra_': 'get "martha"' }, 'None:sue:': { '_extra_': 'get "sue"' } }

  resp = model.get( converter, transaction, [ 'bob', 'martha', 'sue' ], False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'GET', 'Multi-Object': 'False' }
  assert resp.data == { '_extra_': 'get "bob"' }  # this is right, if multi is false, we ignore the rest of the ids, upstream takes care of making sure that dosen't happen

  with pytest.raises( ObjectNotFound ):
    model.get( converter, transaction, [ 'bob', 'NOT FOUND', 'sue' ], True )

  model.get( converter, transaction, [ 'bob', 'NOT FOUND', 'sue' ], False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'GET', 'Multi-Object': 'False' }
  assert resp.data == { '_extra_': 'get "bob"' }  # see above

  with pytest.raises( ObjectNotFound ):
    model.get( converter, transaction, [ 'NOT FOUND' ], False )

  with pytest.raises( ObjectNotFound ):
    model.get( converter, transaction, [ 'NOT FOUND' ], True )


def test_update():
  converter = Converter( None )
  field_list = []
  field_list.append( Field( name='field1', mode='RW', type='String', length=50 ) )
  field_list.append( Field( name='field2', mode='RO', type='Integer' ) )
  model = Model( name='model1', field_list=field_list, transaction_class=TestTransaction )
  transaction = model.transaction_class()

  resp = model.update( converter, transaction, [ 'bob' ], {}, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'UPDATE', 'Multi-Object': 'False' }
  assert resp.data == { '_extra_': 'update "bob"' }

  resp = model.update( converter, transaction, [ 'bob' ], { 'field1': 'goodies' }, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'UPDATE', 'Multi-Object': 'False' }
  assert resp.data == { '_extra_': 'update "bob"', 'field1': 'goodies' }

  with pytest.raises( InvalidRequest ):
    resp = model.update( converter, transaction, [ 'bob' ], { 'field2': 42 }, False )

  with pytest.raises( InvalidRequest ):
    resp = model.update( converter, transaction, [ 'NOT FOUND' ], { 'field2': 42 }, False )

  with pytest.raises( ObjectNotFound ):
    resp = model.update( converter, transaction, [ 'NOT FOUND' ], { 'field1': 'goodies' }, False )

  resp = model.update( converter, transaction, [ 'bob', 'martha', 'sue' ], { 'field1': 'goodies' }, False )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'UPDATE', 'Multi-Object': 'False' }
  assert resp.data == { '_extra_': 'update "bob"', 'field1': 'goodies' }  # this is right, if multi is false, we ignore the rest of the ids, upstream takes care of making sure that dosen't happen

  resp = model.update( converter, transaction, [ 'bob' ], { 'field1': 'goodies' }, True )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'UPDATE', 'Multi-Object': 'True' }
  assert resp.data == { 'None:bob:': { '_extra_': 'update "bob"', 'field1': 'goodies' } }

  resp = model.update( converter, transaction, [ 'bob', 'martha', 'sue' ], { 'field1': 'goodies' }, True )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'UPDATE', 'Multi-Object': 'True' }
  assert resp.data == { 'None:bob:': { '_extra_': 'update "bob"', 'field1': 'goodies' }, 'None:martha:': { '_extra_': 'update "martha"', 'field1': 'goodies' }, 'None:sue:': { '_extra_': 'update "sue"', 'field1': 'goodies' } }


def test_delete():
  field_list = []
  model = Model( name='model1', field_list=field_list, transaction_class=TestTransaction )
  transaction = model.transaction_class()

  resp = model.delete( transaction, [ 'bob' ] )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'DELETE' }
  assert resp.data is None

  resp = model.delete( transaction, [ 'bob', 'sue', 'martha' ] )
  assert resp.http_code == 200
  assert resp.header_map == { 'Cache-Control': 'no-cache', 'Verb': 'DELETE' }
  assert resp.data is None

  with pytest.raises( ObjectNotFound ):
    model.delete( transaction, [ 'bob', 'NOT FOUND', 'martha' ] )

  with pytest.raises( ObjectNotFound ):
    model.delete( transaction, [ 'NOT FOUND' ] )


def test_getElement():
  uri = URI( root_path='/api/' )
  root_ns = Namespace( name=None, version='0.0', root_path='/api/', converter=None )
  ns2 = Namespace( name='ns2', version='0.1', converter=None )
  ns3 = Namespace( name='ns3', version='0.2', converter=None )
  ns2_2 = Namespace( name='ns2_2', version='0.1', converter=None )
  root_ns.addElement( ns2 )
  root_ns.addElement( ns3 )
  ns2.addElement( ns2_2 )
  mdl1 = Model( name='mdl1', field_list={}, transaction_class=TestTransaction )
  mdl2 = Model( name='mdl2', field_list={}, transaction_class=TestTransaction )
  root_ns.addElement( mdl1 )
  ns2_2.addElement( mdl2 )
  act1 = Action( name='act1', return_paramater=Paramater( type='String' ), paramater_list=[ Paramater( name='bob', type='Float' ) ], static=False, func=fake_func )
  act2 = Action( name='act2', return_paramater=Paramater( type='String' ), paramater_list=[ Paramater( name='stuff', type='Boolean' ) ], func=fake_func )
  mdl1.addAction( act1 )
  mdl2.addAction( act2 )

  assert root_ns.getElement( uri.split( '/api/', root_optional=True ) ) == root_ns
  assert root_ns.getElement( uri.split( '/api/ns2/', root_optional=True ) ) == ns2
  assert root_ns.getElement( uri.split( '/api/ns3/', root_optional=True ) ) == ns3
  assert root_ns.getElement( uri.split( '/api/ns2/ns2_2/', root_optional=True ) ) == ns2_2
  assert root_ns.getElement( uri.split( '/', root_optional=True ) ) == root_ns
  assert root_ns.getElement( uri.split( '/ns2/', root_optional=True ) ) == ns2
  assert root_ns.getElement( uri.split( '/ns3/', root_optional=True ) ) == ns3
  assert root_ns.getElement( uri.split( '/ns2/ns2_2/', root_optional=True ) ) == ns2_2
  assert root_ns.getElement( uri.split( '/api/mdl1', root_optional=True ) ) == mdl1
  assert root_ns.getElement( uri.split( '/api/ns2/ns2_2/mdl2', root_optional=True ) ) == mdl2
  assert root_ns.getElement( uri.split( '/mdl1', root_optional=True ) ) == mdl1
  assert root_ns.getElement( uri.split( '/ns2/ns2_2/mdl2', root_optional=True ) ) == mdl2
  assert root_ns.getElement( uri.split( '/api/mdl1(act1)', root_optional=True ) ) == act1
  assert root_ns.getElement( uri.split( '/api/ns2/ns2_2/mdl2(act2)', root_optional=True ) ) == act2
  assert root_ns.getElement( uri.split( '/mdl1(act1)', root_optional=True ) ) == act1
  assert root_ns.getElement( uri.split( '/ns2/ns2_2/mdl2(act2)', root_optional=True ) ) == act2

  with pytest.raises( ValueError ):
    root_ns.getElement( '/api/' )

  assert root_ns.getElement( uri.split( '/api/nsX/' ) ) is None
  assert root_ns.getElement( uri.split( '/api/ns2/mdlX' ) ) is None
  assert root_ns.getElement( uri.split( '/api/mdl1(actX)' ) ) is None


def test_request():
  req = Request( 'DESCRIBE', '/api/v1/ns/model', { 'CINP-VERSION': '1.0', 'AUTH-ID': 'root', 'AUTH-TOKEN': 'stuff', 'CONTENT-TYPE': 'text/plain', 'FILTER': 'stuff', 'POSITION': 0, 'COUNT': 50, 'Multi-Object': 'True' } )
  assert req.verb == 'DESCRIBE'
  assert req.uri == '/api/v1/ns/model'
  assert req.header_map == { 'CINP-VERSION': '1.0', 'AUTH-ID': 'root', 'AUTH-TOKEN': 'stuff', 'CONTENT-TYPE': 'text/plain', 'FILTER': 'stuff', 'POSITION': 0, 'COUNT': 50 }

  req = Request( 'GET', '/api/v2/model:key:', { 'CINP-VERSION': '1.0', 'USER-AGENT': 'mybrowser' } )
  assert req.verb == 'GET'
  assert req.uri == '/api/v2/model:key:'
  assert req.header_map == { 'CINP-VERSION': '1.0' }

  req.fromJSON( '"My Text"' )
  assert req.data == 'My Text'

  req.fromJSON( '{ "key": "value" }' )
  assert req.data == { 'key': 'value' }

  req.fromJSON( '' )
  assert req.data is None

  req.fromJSON( '[ 1 ,2 ,3 ]' )
  assert req.data == [ 1, 2, 3 ]


def test_response():
  resp = Response( 200 )
  assert resp.http_code == 200
  assert resp.data is None
  assert resp.header_map == {}
  assert resp.asJSON() is None

  resp = Response( 201, { 'hi': 'there' } )
  assert resp.http_code == 201
  assert resp.data == { 'hi': 'there' }
  assert resp.header_map == {}
  assert resp.asJSON() is None  # yea, still none, base Responose dosen't asXXXX anything

  resp = Response( 201, 'more stuff', { 'hdr': 'big' } )
  assert resp.http_code == 201
  assert resp.data == 'more stuff'
  assert resp.header_map == { 'hdr': 'big' }
  assert resp.asJSON() is None  # yea, still none, base Responose dosen't asXXXX anything


def test_saninity_checks():
  server = Server( root_path='/api/', root_version='0.0' )
  ns = Namespace( name='ns', version='0.1', converter=None )
  model = Model( name='model', field_list=[], transaction_class=TestTransaction )
  ns.addElement( model )
  action = Action( name='action', return_paramater=Paramater( type='String' ), func=fake_func )
  model.addAction( action )
  server.registerNamespace( '/', ns )

  res = server.dispatch( Request( 'BOB', '/api/', { 'CINP-VERSION': '1.0' } ) )
  assert res.http_code == 400
  assert res.data == { 'message': 'Invalid Verb (HTTP Method) "BOB"' }

  res = server.dispatch( Request( 'DESCRIBE', 'invalid', { 'CINP-VERSION': '1.0' } ) )
  assert res.http_code == 400
  assert res.data == { 'message': 'Unable to Parse "invalid"' }

  res = server.dispatch( Request( 'DESCRIBE', '/api/ns/model:' + ':'.join( 'id' * 101 ) + ':', { 'CINP-VERSION': '1.0' } ) )
  assert res.http_code == 400
  assert res.data == { 'message': 'id_list longer than supported length of "100"' }

  res = server.dispatch( Request( 'DESCRIBE', '/api/nope', { 'CINP-VERSION': '1.0' } ) )
  assert res.http_code == 404
  assert res.data == { 'message': 'path not found "/api/nope"' }

  res = server.handle( Request( 'DESCRIBE', '/api/', {} ) )
  assert res.http_code == 400
  assert res.data == { 'message': 'Invalid CInP Protocol Version' }

  res = server.handle( Request( 'DESCRIBE', '/api/', { 'Cinp-Version': '0' } ) )
  assert res.http_code == 400
  assert res.data == { 'message': 'Invalid CInP Protocol Version' }

  with pytest.raises( ValueError ):  # checkAuth not implemented, for this round of tests we call good
    server.dispatch( Request( 'DESCRIBE', '/api/ns/model(action)', { 'CINP-VERSION': '1.0' } ) )

  for verb in ( 'GET', 'LIST', 'CREATE', 'UPDATE', 'DELETE' ):
    res = server.dispatch( Request( verb, '/api/ns/model(action)', { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Invalid verb "{0}" for request with action'.format( verb ) }

  for verb in ( 'GET', 'LIST', 'CREATE', 'UPDATE', 'DELETE' ):
    res = server.dispatch( Request( verb, '/api/ns/model:id:(action)', { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Invalid verb "{0}" for request with action'.format( verb ) }

  for uri in ( '/api/', '/api/ns/', '/api/ns/model', '/api/ns/model:id:' ):
    res = server.dispatch( Request( 'CALL', uri, { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Verb "CALL" requires action' }

  for verb in ( 'LIST', 'CREATE', 'DESCRIBE' ):
    res = server.dispatch( Request( verb, '/api/ns/model:id:', { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Invalid Verb "{0}" for request with id'.format( verb ) }

  for verb in ( 'GET', 'UPDATE', 'DELETE' ):
    res = server.dispatch( Request( verb, '/api/ns/model', { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Verb "{0}" requires id'.format( verb ) }

  for verb in ( 'GET', 'DELETE' ):
    req = Request( verb, '/api/ns/model:d:', { 'CINP-VERSION': '1.0' } )
    req.data = { 'some': 'data' }
    res = server.dispatch( req )
    assert res.http_code == 400
    assert res.data == { 'message': 'Invalid verb "{0}" for request with data'.format( verb ) }

  for verb in ( 'DESCRIBE', ):
    req = Request( verb, '/api/ns/model', { 'CINP-VERSION': '1.0' } )
    req.data = { 'some': 'data' }
    res = server.dispatch( req )
    assert res.http_code == 400
    assert res.data == { 'message': 'Invalid verb "{0}" for request with data'.format( verb ) }

  for verb in ( 'UPDATE', ):
    res = server.dispatch( Request( verb, '/api/ns/model:id:', { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Verb "{0}" requires data'.format( verb ) }

  for verb in ( 'CREATE', ):
    res = server.dispatch( Request( verb, '/api/ns/model', { 'CINP-VERSION': '1.0' } ) )
    assert res.http_code == 400
    assert res.data == { 'message': 'Verb "{0}" requires data'.format( verb ) }

  for verb in ( 'LIST', 'CREATE' ):  # also 'GET', 'UPDATE', 'DELETE' which also requires an Id which requires a model so already covered
    req = Request( verb, '/api/ns/', { 'CINP-VERSION': '1.0' } )
    req.data = { 'some': 'data' }
    res = server.dispatch( req )
    assert res.http_code == 400
    assert res.data == { 'message': 'Verb "{0}" requires model'.format( verb ) }


def test_server():
  server = Server( root_path='/api/', root_version='0.0', debug=True )
  ns1 = Namespace( name='ns1', version='0.1', converter=None )
  ns1.checkAuth = lambda user, verb, id_list: True
  model1 = Model( name='model1', field_list=[], transaction_class=TestTransaction )
  model1.checkAuth = lambda user, verb, id_list: True
  ns1.addElement( model1 )
  model2 = Model( name='model2', field_list=[], transaction_class=TestTransaction )
  model2.checkAuth = lambda user, verb, id_list: True
  ns1.addElement( model2 )
  server.registerNamespace( '/', ns1 )

  ns2 = Namespace( name='ns2', version='0.2', converter=None )
  server.registerNamespace( '/api/', ns2 )

  req = Request( 'OPTIONS', '/api/', {} )
  res = server.handle( req )
  assert res.http_code == 200
  assert res.header_map == { 'Allow': 'OPTIONS, DESCRIBE', 'Cache-Control': 'max-age=0', 'Cinp-Version': '1.0' }

  path = '/api/'
  desc_ref = sort_dsc( { 'name': 'root', 'path': '/api/', 'api-version': '0.0', 'namespaces': [ '/api/ns1/', '/api/ns2/' ], 'models': [], 'multi-uri-max': 100 } )
  assert sort_dsc( server.root_namespace.getElement( server.uri.split( path ) ).describe( ns1.converter ).data ) == desc_ref
  req = Request( 'DESCRIBE', path, { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200
  assert sort_dsc( res.data ) == desc_ref
  assert res.header_map == { 'Type': 'Namespace', 'Verb': 'DESCRIBE', 'Cache-Control': 'max-age=0', 'Cinp-Version': '1.0' }

  path = '/api/ns1/'
  desc_ref = sort_dsc( { 'name': 'ns1', 'path': '/api/ns1/', 'api-version': '0.1', 'namespaces': [], 'models': [ '/api/ns1/model1', '/api/ns1/model2' ], 'multi-uri-max': 100 } )
  assert sort_dsc( server.root_namespace.getElement( server.uri.split( path ) ).describe( ns1.converter ).data ) == desc_ref
  req = Request( 'DESCRIBE', path, { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200
  assert sort_dsc( res.data ) == desc_ref
  assert res.header_map == { 'Type': 'Namespace', 'Verb': 'DESCRIBE', 'Cache-Control': 'max-age=0', 'Cinp-Version': '1.0' }

  path = '/api/ns1/model1'
  desc_ref = sort_dsc( { 'name': 'model1', 'path': '/api/ns1/model1', 'fields': [], 'actions': [], 'constants': {}, 'list-filters': {}, 'not-allowed-verbs': [], 'query-filter-fields': [], 'query-sort-fields': [] } )
  assert sort_dsc( server.root_namespace.getElement( server.uri.split( path ) ).describe( ns1.converter ).data ) == desc_ref
  req = Request( 'DESCRIBE', path, { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200
  assert sort_dsc( res.data ) == desc_ref
  assert res.header_map == { 'Type': 'Model', 'Verb': 'DESCRIBE', 'Cache-Control': 'max-age=0', 'Cinp-Version': '1.0' }

  # TODO: more more more


def test_multi():
  server = Server( root_path='/api/', root_version='0.0', debug=True )
  ns1 = Namespace( name='ns1', version='0.1', converter=None )
  ns1.checkAuth = lambda user, verb, id_list: True
  model1 = Model( name='model1', field_list=[], transaction_class=TestTransaction )
  model1.checkAuth = lambda user, verb, id_list: True
  ns1.addElement( model1 )
  server.registerNamespace( '/', ns1 )

  req = Request( 'GET', '/api/ns1/model1:abc:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200
  assert res.header_map == { 'Cache-Control': 'no-cache', 'Cinp-Version': '1.0', 'Verb': 'GET', 'Multi-Object': 'False' }
  assert res.data == { '_extra_': 'get "abc"' }

  req = Request( 'GET', '/api/ns1/model1:abc:def:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200
  assert res.header_map == { 'Cache-Control': 'no-cache', 'Cinp-Version': '1.0', 'Verb': 'GET', 'Multi-Object': 'True' }
  assert res.data == { '/api/ns1/model1:abc:': { '_extra_': 'get "abc"' }, '/api/ns1/model1:def:': { '_extra_': 'get "def"' } }

  req = Request( 'GET', '/api/ns1/model1:abc:', { 'CINP-VERSION': __CINP_VERSION__, 'MULTI-OBJECT': 'true' } )
  res = server.handle( req )
  assert res.http_code == 200
  assert res.header_map == { 'Cache-Control': 'no-cache', 'Cinp-Version': '1.0', 'Verb': 'GET', 'Multi-Object': 'True' }
  assert res.data == { '/api/ns1/model1:abc:': { '_extra_': 'get "abc"' } }

  req = Request( 'GET', '/api/ns1/model1:abc:def:', { 'CINP-VERSION': __CINP_VERSION__, 'MULTI-OBJECT': 'true' } )
  res = server.handle( req )
  assert res.http_code == 200
  assert res.header_map == { 'Cache-Control': 'no-cache', 'Cinp-Version': '1.0', 'Verb': 'GET', 'Multi-Object': 'True' }
  assert res.data == { '/api/ns1/model1:abc:': { '_extra_': 'get "abc"' }, '/api/ns1/model1:def:': { '_extra_': 'get "def"' } }

  req = Request( 'GET', '/api/ns1/model1:abc:def:', { 'CINP-VERSION': __CINP_VERSION__, 'MULTI-OBJECT': 'false' } )
  res = server.handle( req )
  assert res.http_code == 400
  assert res.header_map == { 'Cinp-Version': '1.0' }
  assert res.data == { 'message': 'requested non multi-object, however multiple ids where sent' }


def test_not_allowed_verbs():
  server = Server( root_path='/api/', root_version='0.0', debug=True )
  ns1 = Namespace( name='ns1', version='0.1', converter=Converter( URI( '/api/' ) ) )
  ns1.checkAuth = lambda user, verb, id_list: True
  field_list = []
  field_list.append( Field( name='field1', type='String', length=50 ) )
  model1 = Model( name='model1', field_list=field_list, not_allowed_verb_list=[], transaction_class=TestTransaction )
  model2 = Model( name='model2', field_list=field_list, not_allowed_verb_list=[ 'GET', 'LIST', 'CALL', 'CREATE', 'UPDATE', 'DELETE', 'DESCRIBE' ], transaction_class=TestTransaction )
  model1.checkAuth = lambda user, verb, id_list: True
  model2.checkAuth = lambda user, verb, id_list: True
  action1 = Action( name='act', return_paramater=Paramater( type='String' ), func=fake_func )
  action2 = Action( name='act', return_paramater=Paramater( type='String' ), func=fake_func )
  action1.checkAuth = lambda user, verb, id_list: True
  action2.checkAuth = lambda user, verb, id_list: True
  model1.addAction( action1 )
  model2.addAction( action2 )
  ns1.addElement( model1 )
  ns1.addElement( model2 )
  server.registerNamespace( '/', ns1 )

  with pytest.raises( ValueError ):
    Model( name='modelX', field_list=[], not_allowed_verb_list=[ 'OPTIONS' ], transaction_class=TestTransaction )

  with pytest.raises( ValueError ):
    Model( name='modelX', field_list=[], not_allowed_verb_list=[ 'ASDF' ], transaction_class=TestTransaction )

  req = Request( 'OPTIONS', '/api/ns1/model1', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'OPTIONS', '/api/ns1/model2', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'DESCRIBE', '/api/ns1/model1', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'DESCRIBE', '/api/ns1/model2', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'GET', '/api/ns1/model1:asd:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'GET', '/api/ns1/model2:asd:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'LIST', '/api/ns1/model1', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'LIST', '/api/ns1/model2', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'CREATE', '/api/ns1/model1', { 'CINP-VERSION': __CINP_VERSION__ } )
  req.data = { 'field1': 'stuff' }
  res = server.handle( req )
  assert res.http_code == 201

  req = Request( 'CREATE', '/api/ns1/model2', { 'CINP-VERSION': __CINP_VERSION__ } )
  req.data = { 'field1': 'stuff' }
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'UPDATE', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__ } )
  req.data = { 'field1': 'stuff' }
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'UPDATE', '/api/ns1/model2:sdf:', { 'CINP-VERSION': __CINP_VERSION__ } )
  req.data = { 'field1': 'stuff' }
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'DELETE', '/api/ns1/model1:asd:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'DELETE', '/api/ns1/model2:asd:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'CALL', '/api/ns1/model1(act)', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'CALL', '/api/ns1/model2(act)', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 403


def test_user():
  server = Server( root_path='/api/', root_version='0.0', debug=True )
  server.getUser = getUser
  ns1 = Namespace( name='ns1', version='0.1', converter=None )
  ns1.checkAuth = checkAuth
  field_list = []
  model1 = Model( name='model1', field_list=field_list, transaction_class=TestTransaction )
  model1.checkAuth = checkAuth
  action1 = Action( name='act', return_paramater=Paramater( type='String' ), func=fake_func )
  action1.checkAuth = checkAuth
  model1.addAction( action1 )
  ns1.addElement( model1 )
  server.registerNamespace( '/', ns1 )

  req = Request( 'GET', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__ } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'GET', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__, 'AUTH-ID': 'nope', 'AUTH-TOKEN': 'nope' } )
  res = server.handle( req )
  assert res.http_code == 401

  req = Request( 'GET', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__, 'AUTH-ID': 'good', 'AUTH-TOKEN': 'nope' } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'GET', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__, 'AUTH-ID': 'nope', 'AUTH-TOKEN': 'bad' } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'GET', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__, 'AUTH-ID': 'super', 'AUTH-TOKEN': 'super' } )
  res = server.handle( req )
  assert res.http_code == 200

  req = Request( 'GET', '/api/ns1/model1:sdf:', { 'CINP-VERSION': __CINP_VERSION__, 'AUTH-ID': 'me', 'AUTH-TOKEN': 'me' } )
  res = server.handle( req )
  assert res.http_code == 403

  req = Request( 'GET', '/api/ns1/model1:me:', { 'CINP-VERSION': __CINP_VERSION__, 'AUTH-ID': 'me', 'AUTH-TOKEN': 'me' } )
  res = server.handle( req )
  assert res.http_code == 200
