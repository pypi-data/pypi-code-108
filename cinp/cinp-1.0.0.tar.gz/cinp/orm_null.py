import re
from cinp.server_common import Converter, Namespace, Model, Action, Paramater, checkAuth_true, checkAuth_false


def paramater_type_to_kwargs( paramater_type ):
  result = {}

  if isinstance( paramater_type, dict ):
    result[ 'type' ] = paramater_type[ 'type' ]

    try:
      result[ 'doc' ] = paramater_type[ 'doc' ]
    except KeyError:
      pass

    try:
      result[ 'length' ] = paramater_type[ 'length' ]
    except KeyError:
      pass

    try:
      result[ 'is_array' ] = paramater_type[ 'is_array' ]
    except KeyError:
      pass

    try:
      result[ 'allowed_scheme_list' ] = paramater_type[ 'allowed_scheme_list' ]
    except KeyError:
      pass

  else:
    result[ 'type' ] = paramater_type

  return result


class NullConverter( Converter ):
  pass


# decorator for the models
class NullCInP():
  def __init__( self, name, version='0.0', doc='' ):
    super().__init__()
    if not re.match( '^[0-9a-zA-Z]*$', name ):
      raise ValueError( 'name "{0}" is invalid'.format( name ) )

    self.name = name
    self.version = version
    self.doc = doc
    self.model_list = []
    self.action_map = {}
    self.check_auth_map = {}

  # this is called to get the namespace to attach to the server
  def getNamespace( self, uri ):
    namespace = Namespace( name=self.name, version=self.version, doc=self.doc, converter=NullConverter( uri ) )
    namespace.checkAuth = checkAuth_true
    for model in self.model_list:
      check_auth = self.check_auth_map.get( model.name, None )
      if check_auth is None:
        check_auth = checkAuth_false

      namespace.addElement( model )
      model.checkAuth = check_auth
      for action in self.action_map.get( model.name, [] ):
        action.checkAuth = eval( 'lambda user, verb, id_list: check_auth( user, verb, id_list, "{0}" )'.format( action.name ), { 'check_auth': check_auth } )  # TODO: eval ew, find a better way
        model.addAction( action )

    return namespace

  def model( self, cache_length=3600 ):
    def decorator( cls ):

      name = cls.__qualname__

      model = Model( name=name, transaction_class=NullTransaction, field_list=[], list_filter_map={}, constant_set_map={}, not_allowed_verb_list=[ 'LIST', 'GET', 'CREATE', 'UPDATE', 'DELETE' ] )
      self.model_list.append( model )
      return cls

    return decorator

  def action( self, return_type=None, paramater_type_list=None ):  # must decorate the @staticmethod decorator to detect if it is static or not
    def decorator( func ):
      if type( func ).__name__ == 'staticmethod':
        static = True
        func = func.__func__
      else:
        raise ValueError( 'action must be a staticmethod' )

      paramater_type_list_ = paramater_type_list or []
      ( model_name, name ) = func.__qualname__.split( '.' )
      if model_name not in self.action_map:
        self.action_map[ model_name ] = []

      if static:
        paramater_name_list = func.__code__.co_varnames[ 0:func.__code__.co_argcount ]
      else:
        paramater_name_list = func.__code__.co_varnames[ 1:func.__code__.co_argcount ]  # skip 'self'

      default_list = func.__defaults__
      default_offset = len( paramater_name_list ) - len( default_list or [] )

      if len( paramater_name_list ) != len( paramater_type_list_ ):
        raise ValueError( 'paramater_name_list({0}) is not the same length as paramater_type_list({1}) for "{2}" of "{3}"'.format( len( paramater_name_list ), len( paramater_type_list_ ), name, model_name ) )

      paramater_list = []
      for index in range( 0, len( paramater_type_list_ ) ):
        kwargs = paramater_type_to_kwargs( paramater_type_list_[ index ] )
        kwargs[ 'name' ] = paramater_name_list[ index ]
        if index >= default_offset:
          kwargs[ 'default' ] = default_list[ index - default_offset ]

        paramater_list.append( Paramater( **kwargs ) )

      return_paramater = Paramater( **paramater_type_to_kwargs( return_type ) )

      try:
        doc = func.__doc__.strip()
      except AttributeError:
        doc = ''

      self.action_map[ model_name ].append( Action( name=name, doc=doc, func=func, return_paramater=return_paramater, paramater_list=paramater_list, static=static ) )
      return func

    return decorator

  def check_auth( self ):
    def decorator( func ):
      if type( func ).__name__ != 'staticmethod':
        raise ValueError( 'check_auth func must be a staticmethod' )

      ( model_name, _ ) = func.__func__.__qualname__.split( '.' )
      self.check_auth_map[ model_name ] = func.__func__

      return func

    return decorator


class NullTransaction():
  def __init__( self ):
    super().__init__()

  def get( self, model, object_id ):
    return None

  def create( self, model, value_map ):
    pass

  def update( self, model, object_id, value_map ):
    return None

  def list( self, model, filter_name, filter_values, position, count ):
    return []

  def delete( self, model, object_id ):
    return False

  def start( self ):
    pass

  def commit( self ):
    pass

  def abort( self ):
    pass
