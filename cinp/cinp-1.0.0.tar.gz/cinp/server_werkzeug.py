import werkzeug
import json
import logging
from importlib import import_module

from cinp.server_common import Server, Request, Response, Namespace, Converter, InvalidRequest


class NoCINP( Exception ):
  pass


class WerkzeugServer( Server ):
  def __init__( self, get_user, *args, **kwargs ):
    super().__init__( *args, **kwargs )
    self.getUser = get_user

  def handle( self, envrionment ):
    try:
      response = super().handle( WerkzeugRequest( envrionment ) )

      if not isinstance( response, Response ):
        if self.debug:
          message = 'Invalid Response from handle, got "{0}" expected WerkzeugResponse'.format( type( response ).__name__ )
        else:
          message = 'Invalid Response from handle'

        return werkzeug.wrappers.BaseResponse( response=message, status=500, content_type='text/plain' )

      return WerkzeugResponse( response ).buildNativeResponse()

    except InvalidRequest as e:
      return WerkzeugResponse( e.asResponse() ).buildNativeResponse()

    except Exception as e:
      logging.exception( 'Top level Exception, "{0}"({1})'.format( e, type( e ).__name__ ) )
      return werkzeug.wrappers.BaseResponse( response='Error getting WerkzeugResponse, "{0}"({1})'.format( e, type( e ).__name__ ), status=500, content_type='text/plain' )

  def __call__( self, envrionment, start_response ):
    """
    called by werkzeug for every request
    """
    return self.handle( envrionment )( envrionment, start_response )

  # add a namespace to the path, either from included module, or an empty namespace with name and version
  def registerNamespace( self, path, module=None, name=None, version=None ):
    if module is None:
      if name is None or version is None:
        raise ValueError( 'name and version must be specified if no module is specified' )

      namespace = Namespace( name=name, version=version, converter=Converter( self.uri ) )

    else:
      if isinstance( module, Namespace ):
        namespace = module

      else:
        module = import_module( '{0}.models'.format( module ) )
        if not hasattr( module, 'cinp' ):
          raise NoCINP( 'module "{0}" missing cinp'.format( module ) )

        namespace = module.cinp.getNamespace( self.uri )

    super().registerNamespace( path, namespace )


class WerkzeugRequest( Request ):
  def __init__( self, envrionment, *args, **kwargs ):
    werkzeug_request = werkzeug.wrappers.BaseRequest( envrionment )
    header_map = {}
    for ( key, value ) in werkzeug_request.headers:
      header_map[ key.upper().replace( '_', '-' ) ] = value

    # script_root should be what ever path was consumed by the script handler configuration
    # ie: the  "/api" of: WSGIScriptAlias /api <path to wsgi script>
    uri = werkzeug_request.script_root + werkzeug_request.path

    super().__init__( verb=werkzeug_request.method.upper(), uri=uri, header_map=header_map, *args, **kwargs )

    content_type = self.header_map.get( 'CONTENT-TYPE', None )
    if content_type is not None:  # if it is none, there isn't (or shoudn't) be anthing to bring in anyway
      if content_type.startswith( 'application/json' ):
        self.fromJSON( str( werkzeug_request.stream.read( 164160 ), 'utf-8' ) )  # hopfully the request isn't larger than 160k, if so, we may need to rethink things

      elif content_type.startswith( 'text/plain' ):
        self.fromText( str( werkzeug_request.stream.read( 164160 ), 'utf-8' ) )

      elif content_type.startswith( 'application/xml' ):
        self.fromXML( str( werkzeug_request.stream.read( 164160 ), 'utf-8' ) )

      elif content_type.startswith( 'application/octet-stream' ):
        self.stream = werkzeug_request.stream
        if 'CONTENT-DISPOSITION' in header_map:  # cheet a little, Content-Disposition isn't pure CInP, but this is a bolt on file uploader
          self.header_map[ 'CONTENT-DISPOSITION' ] = header_map[ 'CONTENT-DISPOSITION' ]
        pass  # do nothing, down stream is going to have to read from the stream

      else:
        raise InvalidRequest( message='Unknown Content-Type "{0}"'.format( content_type ) )

    if 'X-FORWARDED-FOR' in header_map:  # hm... should we really be doing this here?
      self.remote_addr = header_map[ 'X-FORWARDED-FOR' ]
    else:
      self.remote_addr = werkzeug_request.remote_addr
    self.is_secure = werkzeug_request.is_secure
    werkzeug_request.close()

  def read( self, size ):
    return self.stream.read( size )


class WerkzeugResponse():  # TODO: this should be a subclass of the server_common Response, to much redundant stuff
  def __init__( self, response ):
    if not isinstance( response, Response ):
      raise ValueError( 'response must be of type Response' )

    super().__init__()
    self.content_type = response.content_type
    self.data = response.data
    self.status = response.http_code
    self.header_list = []
    for name in response.header_map:
      self.header_list.append( ( name, response.header_map[ name ] ) )

  def buildNativeResponse( self ):
    if self.content_type == 'json':
      return self.asJSON()
    elif self.content_type == 'xml':
      return self.asXML()
    elif self.content_type == 'bytes':
      return self.asBytes()

    return self.asText()

  def asText( self ):
    return werkzeug.wrappers.BaseResponse( response=self.data.encode( 'utf-8' ), status=self.status, headers=self.header_list, content_type='text/plain;charset=utf-8' )

  def asJSON( self ):
    if self.data is None:
      response = ''.encode( 'utf-8' )
    else:
      response = json.dumps( self.data ).encode( 'utf-8' )

    return werkzeug.wrappers.BaseResponse( response=response, status=self.status, headers=self.header_list, content_type='application/json;charset=utf-8'  )

  def asXML( self ):
    return werkzeug.wrappers.BaseResponse( response='<xml>Not Implemented</xml>', status=self.response.http_code, headers=self.header_list, content_type='application/xml;charset=utf-8' )

  def asBytes( self ):
    return werkzeug.wrappers.BaseResponse( response=self.data, status=self.status, headers=self.header_list, content_type='application/octet-stream'  )
