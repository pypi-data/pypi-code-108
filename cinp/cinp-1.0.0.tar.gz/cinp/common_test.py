import pytest

from cinp.common import URI

# TODO: test mutli-object setting


def test_splituri_builduri():  # TODO: test invlid URIs, mabey remove some tests from client_test that are just checking the URI
  uri = URI( '/api/v1/' )

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/' )
  assert ns == []
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/'
  ns = None
  assert uri.build( ns, model, action, id_list ) == '/api/v1/'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/' )
  assert ns == [ 'ns' ]
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/'
  ns = 'ns'
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model'
  id_list = []
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/ns2/' )
  assert ns == [ 'ns', 'ns2' ]
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/ns2/'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/ns2/model' )
  assert ns == [ 'ns', 'ns2' ]
  assert model == 'model'
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/ns2/model'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model::' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list == [ '' ]
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model::'
  id_list = ''
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model::'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model:ghj:' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list == [ 'ghj' ]
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model:ghj:'
  id_list = 'ghj'
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model:ghj:'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model:ghj:dsf:sfe:' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list == [ 'ghj', 'dsf', 'sfe' ]
  assert action is None
  assert multi is True
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model:ghj:dsf:sfe:'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model(action)' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list is None
  assert action == 'action'
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model(action)'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model:sdf:(action)' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list == [ 'sdf' ]
  assert action == 'action'
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model:sdf:(action)'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/model:sdf:eed:(action)' )
  assert ns == [ 'ns' ]
  assert model == 'model'
  assert id_list == [ 'sdf', 'eed' ]
  assert action == 'action'
  assert multi is True
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/model:sdf:eed:(action)'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/', root_optional=True )
  assert ns == []
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/'
  assert uri.build( ns, model, action, id_list, in_root=False ) == '/'

  with pytest.raises( ValueError ):
    ( ns, model, action, id_list, multi ) = uri.split( '/', root_optional=False )
  ( ns, model, action, id_list, multi ) = uri.split( '/', root_optional=True )
  assert ns == []
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/'
  assert uri.build( ns, model, action, id_list, in_root=False ) == '/'

  ( ns, model, action, id_list, multi ) = uri.split( '/api/v1/ns/', root_optional=True )
  assert ns == [ 'ns' ]
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/'
  assert uri.build( ns, model, action, id_list, in_root=False ) == '/ns/'

  with pytest.raises( ValueError ):
    ( ns, model, action, id_list, multi ) = uri.split( '/ns/', root_optional=False )
  ( ns, model, action, id_list, multi ) = uri.split( '/ns/', root_optional=True )
  assert ns == [ 'ns' ]
  assert model is None
  assert id_list is None
  assert action is None
  assert multi is False
  assert uri.build( ns, model, action, id_list ) == '/api/v1/ns/'
  assert uri.build( ns, model, action, id_list, in_root=False ) == '/ns/'


def test_extract_ids():
  uri = URI( '/api/v1/' )

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model:234:', '/api/v1/ns/model:rfv:' ]
  assert uri.extractIds( id_list ) == [ 'sdf', '234', 'rfv' ]

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model:234:www:', '/api/v1/ns/model:rfv:' ]
  assert uri.extractIds( id_list ) == [ 'sdf', '234', 'www', 'rfv' ]

  id_list = [ '/api/v1/ns/model:234:www:' ]
  assert uri.extractIds( id_list ) == [ '234', 'www' ]

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model:234:www', '/api/v1/ns/model:rfv:' ]
  with pytest.raises( ValueError ):
    uri.extractIds( id_list )

  id_list = [ '/api/v1/ns/model:sdf' ]
  with pytest.raises( ValueError ):
    uri.extractIds( id_list )

  id_list = [ '/api/v1/ns/model' ]
  uri.extractIds( id_list ) == []

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model', '/api/v1/ns/model:rfv:' ]
  uri.extractIds( id_list ) == [ 'sdf', 'rfv' ]

  assert uri.extractIds( [] ) == []


def test_urilist_to_uri():
  uri = URI( '/api/v1/' )

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model:234:', '/api/v1/ns/model:rfv:' ]
  assert uri.uriListToMultiURI( id_list ) == '/api/v1/ns/model:sdf:234:rfv:'

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model:234:www:', '/api/v1/ns/model:rfv:' ]
  assert uri.uriListToMultiURI( id_list ) == '/api/v1/ns/model:sdf:234:www:rfv:'

  id_list = [ '/api/v1/ns/model:234:www:' ]
  assert uri.uriListToMultiURI( id_list ) == '/api/v1/ns/model:234:www:'

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model:234:www', '/api/v1/ns/model:rfv:' ]
  with pytest.raises( ValueError ):
    uri.uriListToMultiURI( id_list )

  id_list = [ '/api/v1/ns/model' ]
  uri.uriListToMultiURI( id_list ) == []

  id_list = [ '/api/v1/ns/model:sdf:', '/api/v1/ns/model', '/api/v1/ns/model:rfv:' ]
  uri.uriListToMultiURI( id_list ) == '/api/v1/ns/model:sdf:rfv:'

  assert uri.uriListToMultiURI( [] ) == []
