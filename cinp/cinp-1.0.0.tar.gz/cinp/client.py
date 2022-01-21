import os
import socket
import json
import logging
import ssl
import http.client
import time
import math
import random
from datetime import datetime
from tempfile import NamedTemporaryFile
from urllib import request

from cinp.common import URI

__CLIENT_VERSION__ = '1.0.0'
__CINP_VERSION__ = '1.0'

__all__ = [ 'Timeout', 'ResponseError', 'DetailedInvalidRequest',
            'InvalidRequest', 'InvalidSession', 'NotAuthorized',
            'NotFound', 'ServerError', 'CInP' ]

DELAY_MULTIPLIER = 15
# delay of 15 results in a delay of:
# min delay = 0, 10, 16, 20, 24, 26, 29, 31, 32, 34, 35, 37, 38, 39, 40 ....
# max delay = 0, 20, 32, 40, 48, 52, 58, 62, 64, 68, 70, 74, 76, 78, 80 .....

DEFAULT_RETRY_ON = [
                     'Timeout:None',
                     'ResponseError:[Errno 101] Network is unreachable',
                     'ResponseError:[Errno 104] Connection reset by peer',
                     'ResponseError:Connection reset by peer',
                     'ResponseError:[Errno 111] Connection refused'
                  ]


class Timeout( Exception ):
  pass


class ResponseError( Exception ):
  pass


class InvalidRequest( Exception ):
  pass


class DetailedInvalidRequest( InvalidRequest ):
  def __init__( self, data ):
    for name in ( 'exception', 'error', 'message' ):
      setattr( self, name, None )  # this makes sure it is at least set
      try:
        setattr( self, name, data[ name ] )
        del data[ name ]
      except KeyError:
        pass

    self.data = data
    super().__init__( self.message )


class InvalidSession( Exception ):
  pass


class NotAuthorized( Exception ):
  pass


class NotFound( Exception ):
  pass


class ServerError( Exception ):
  pass


class RetryableException( Exception ):
  def __init__( self, exception, reason=None ):
    self.exception = exception
    self.reason = reason


def _backOffDelay( count ):
  if count < 1:  # math.log dosen't do so well below 1
    count = 1

  factor = int( DELAY_MULTIPLIER * math.log( count ) )
  return int( factor + ( random.random() * factor ) )


class CInP():
  def __init__( self, host, root_path, proxy=None, verify_ssl=True, retry_event=None ):  # retry_event should be an Event Object, use to cancel retry loops, if the event get's set the retry loop will throw the most recent Exception it ignored
    super().__init__()
    self.retry_event = retry_event

    if not host.startswith( ( 'http:', 'https:' ) ):
      raise ValueError( 'hostname must start with http(s):' )

    if host[-1] == '/':
      raise ValueError( 'hostname must not end with "/"' )

    self.proxy = proxy
    self.host = host
    logging.debug( 'cinp: new client host: "{0}", root_path: "{1}", via: "{2}"'.format( self.host, root_path, self.proxy ) )

    self.uri = URI( root_path )

    self.opener = request.OpenerDirector()

    if self.proxy:  # not doing 'is not None', so empty strings don't try and proxy   # have a proxy option to take it from the envrionment vars
      self.opener.add_handler( request.ProxyHandler( { 'http': self.proxy, 'https': self.proxy } ) )
    else:
      self.opener.add_handler( request.ProxyHandler( {} ) )

    self.opener.add_handler( request.HTTPHandler() )
    if hasattr( http.client, 'HTTPSConnection' ):
      if not verify_ssl:
        self.opener.add_handler( request.HTTPSHandler( context=ssl._create_unverified_context() ) )
      else:
        self.opener.add_handler( request.HTTPSHandler() )

    self.opener.add_handler( request.UnknownHandler() )

    self.opener.addheaders = [
                                ( 'User-Agent', 'python CInP client {0}'.format( __CLIENT_VERSION__ ) ),
                                ( 'Accepts', 'application/json' ),
                                ( 'Accept-Charset', 'utf-8' ),
                                ( 'CInP-Version', __CINP_VERSION__ )
                              ]

  def _checkRequest( self, verb, uri, data ):  # TODO: also check if verb is allowed to have headers ( other than thoes provided by the opener ), also check to make sure they are valid heaaders
    logging.debug( 'cinp: check "{0}" to "{1}"'.format( verb, uri ) )

    if verb not in ( 'GET', 'LIST', 'UPDATE', 'CREATE', 'DELETE', 'CALL', 'DESCRIBE' ):
      raise InvalidRequest( 'Invalid Verb (HTTP Method) "{0}"'.format( verb ) )

    if data is not None and not isinstance( data, dict ):
      raise InvalidRequest( 'Data must be a dict' )

    try:
      ( _, model, action, id_list, _ ) = self.uri.split( uri )
    except ValueError as e:
      raise InvalidRequest( str( e ) )

    if id_list == []:
      id_list = None

    if action is not None and verb not in ( 'CALL', 'DESCRIBE' ):
      raise InvalidRequest( 'Invalid verb "{0}" for request with action'.format( verb ) )

    if verb in ( 'CALL', ) and action is None:
      raise InvalidRequest( 'Verb "{0}" requires action'.format( verb ) )

    if id_list is not None and verb not in ( 'GET', 'UPDATE', 'DELETE', 'CALL' ):
      raise InvalidRequest( 'Invalid verb "{0}" for request with id'.format( verb ) )

    if verb in ( 'GET', 'UPDATE', 'DELETE' ) and id_list is None:
      raise InvalidRequest( 'verb "{0}" requires id'.format( verb ) )

    if data is not None and verb not in ( 'LIST', 'UPDATE', 'CREATE', 'CALL' ):
      raise InvalidRequest( 'Invalid verb "{0}" for request with data'.format( verb ) )

    if verb in ( 'UPDATE', 'CREATE' ) and data is None:
      raise InvalidRequest( 'Verb "{0}" requires data'.format( verb ) )

    if verb in ( 'GET', 'LIST', 'UPDATE', 'CREATE', 'DELETE', 'CALL' ) and not model:
      raise InvalidRequest( 'Verb "{0}" requires model'.format( verb ) )

  def _request( self, verb, uri, data=None, header_map=None, timeout=30, retry_count=0, retry_on=None ):
    _retry_on = retry_on or DEFAULT_RETRY_ON

    last_exception = None
    for retry in range( 0, retry_count + 1 ):
      if retry > 0:
        logging.debug( 'cinp: retry "{0}" of "{1}" for request to "{2}"'.format( retry, retry_count, uri ) )
        if self.retry_event is not None:
          if self.retry_event.is_set():
            raise last_exception

          self.retry_event.wait( _backOffDelay( retry ) )

        else:
          time.sleep( _backOffDelay( retry ) )

      try:
        return self.__request( verb, uri, data, header_map, timeout )
      except RetryableException as e:
        signature = '{0}:{1}'.format( e.exception.__class__.__name__, e.reason )
        if signature not in _retry_on:
          logging.debug( 'cinp: exception signature "{0}" not in the retry_on list'.format( signature ) )
          raise e.exception

        logging.debug( 'cinp: got exception "{0}", ignoring...'.format( e ) )
        last_exception = e.exception

    raise last_exception

  def __request( self, verb, uri, data=None, header_map=None, timeout=30 ):
    logging.debug( 'cinp: making "{0}" request to "{1}"'.format( verb, uri ) )
    if header_map is None:
      header_map = {}

    if verb == 'UPLOAD':  # not a CINP verb, just using it to bypass some checking here in __request
      header_map[ 'Content-Type' ] = 'application/octet-stream'
      if not hasattr( data, 'read' ):
        raise InvalidRequest( 'data must be an readable stream' )
      verb = 'POST'  # not to be handled by CInP on the other end, but by a file upload handler

    elif verb == 'RAWGET':  # not a CINP verb, just using it to bypass some checking here in __request
      verb = 'GET'

    else:
      header_map[ 'Content-Type' ] = 'application/json;charset=utf-8'
      self._checkRequest( verb, uri, data )
      if data is None:
        data = ''.encode( 'utf-8' )
      else:
        data = json.dumps( data, default=JSONDefault ).encode( 'utf-8' )

    url = '{0}{1}'.format( self.host, uri )
    req = request.Request( url, data=data, headers=header_map, method=verb )
    try:
      resp = self.opener.open( req, timeout=timeout )

    except request.HTTPError as e:
      raise RetryableException( ResponseError( 'HTTPError "{0}"'.format( e ) ), reason=e.reason )

    except request.URLError as e:
      if isinstance( e.reason, socket.timeout ):
        raise RetryableException( Timeout( 'Request Timeout after {0} seconds'.format( timeout ) ) )

      raise RetryableException( ResponseError( 'URLError "{0}" for "{1}" via "{2}"'.format( e, url, self.proxy ) ), reason=e.reason )

    except socket.timeout:
      raise RetryableException( Timeout( 'Request Timeout after {0} seconds'.format( timeout ) ) )

    except OSError as e:
      raise RetryableException( ResponseError( 'Socket Error "{0}"'.format( e ) ), reason=e.strerror )

    http_code = resp.code
    if http_code not in ( 200, 201, 202, 400, 401, 403, 404, 500 ):
      raise ResponseError( 'HTTP code "{0}" unhandled'.format( resp.code ) )

    logging.debug( 'cinp: got HTTP code "{0}"'.format( http_code ) )

    if http_code == 401:
      resp.close()
      logging.warning( 'cinp: Invalid Session' )
      raise InvalidSession()

    if http_code == 403:
      resp.close()
      logging.warning( 'cinp: Not Authorized' )
      raise NotAuthorized()

    if http_code == 404:
      resp.close()
      logging.warning( 'cinp: Not Found' )
      raise NotFound()

    buff = str( resp.read(), 'utf-8' ).strip()
    if not buff:
      data = None
    else:
      try:
        data = json.loads( buff )
      except ValueError:
        data = None
        if http_code not in ( 400, 500 ):  # these two codes can deal with non dict data
          logging.warning( 'cinp: Unable to parse response "{0}"'.format( buff[ 0:200 ] ) )
          raise ResponseError( 'Unable to parse response "{0}"'.format( buff[ 0:200 ] ) )

    header_map = {}
    for item in ( 'Position', 'Count', 'Total', 'Type', 'Multi-Object', 'Object-Id', 'verb' ):
      try:
        header_map[ item ] = resp.headers[ item ]
      except KeyError:
        pass

    resp.close()

    if http_code == 400:
      try:
        data[ 'message' ]
        e = DetailedInvalidRequest( data )
      except ( KeyError, ValueError, TypeError ):
        e = InvalidRequest( buff[ 0:200 ] )

      logging.warning( 'cinp: Invalid Request "{0}"'.format( e.args[0] ) )
      raise e

    if http_code == 500:
      if isinstance( data, dict ):
        try:
          message = 'Server Error "{0}"\n{1}'.format( data[ 'message' ], data[ 'trace' ] )
        except KeyError:
          try:
            message = 'Server Error "{0}"'.format( data[ 'message' ] )
          except KeyError:
            message = data

      else:
        message = 'Server Error: "{0}"'.format( buff[ 0:200 ] )

      logging.error( 'cinp: {0}'.format( message ) )
      raise ServerError( message )

    return ( http_code, data, header_map )

  def setAuth( self, auth_id=None, auth_token=None ):
    """
    Sets the Authencation id and token headers, call with out paramaters to remove the headers.
    """
    if not auth_id:
      logging.debug( 'cinp: removing auth info' )
      for index in range( len( self.opener.addheaders ) - 1, -1, -1 ):
        if self.opener.addheaders[ index ][0] in ( 'Auth-Id', 'Auth-Token' ):
          del self.opener.addheaders[ index ]

    else:
      logging.debug( 'cinp: setting auth info, id "{0}"'.format( auth_id ) )
      self.opener.addheaders += [ ( 'Auth-Id', auth_id ), ( 'Auth-Token', auth_token ) ]

  def describe( self, uri, timeout=30, retry_count=0, retry_on=None ):
    """
    DESCRIE
    """
    logging.debug( 'cinp: DESCRIBE "{0}"'.format( uri ) )
    ( http_code, data, header_map ) = self._request( 'DESCRIBE', uri, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for DESCRIBE'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for DESCRIBE'.format( http_code ) )

    return data, header_map[ 'Type' ]

  def list( self, uri, filter_name=None, filter_value_map=None, position=0, count=10, timeout=30, retry_count=0, retry_on=None ):
    """
    LIST
    """
    if filter_value_map is None:
      filter_value_map = {}

    if not isinstance( filter_value_map, dict ):
      raise InvalidRequest( 'list filter_value_map must be a dict' )

    if not isinstance( position, int ) or not isinstance( count, int ) or position < 0 or count < 0:
      raise InvalidRequest( 'position and count must bot be int and greater than 0' )

    header_map = { 'Position': str( position ), 'Count': str( count ) }  # TODO set position and coint to default to None, and don't send them if npt specified, rely on the server's defaults
    if filter_name is not None:
      header_map[ 'Filter' ] = filter_name

    logging.debug( 'cinp: LIST "{0}" with filter "{1}"'.format( uri, filter_name ) )
    ( http_code, id_list, header_map ) = self._request( 'LIST', uri, data=filter_value_map, header_map=header_map, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for LIST'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for LIST'.format( http_code ) )

    if not isinstance( id_list, list ):
      logging.warning( 'cinp: Response id_list must be a list for LIST' )
      raise ResponseError( 'Response id_list must be a list for LIST' )

    count_map = { 'position': 0, 'count': 0, 'total': 0 }
    for item in ( 'Position', 'Count', 'Total' ):  # NOTE HTTP Headers typicaly are CamelCase, but we want lower case for our count dictomary
      try:
        count_map[ item.lower() ] = int( header_map[ item ] )
      except ( KeyError, ValueError ):
        pass

    return ( id_list, count_map )

  def get( self, uri, force_multi_mode=False, timeout=30, retry_count=0, retry_on=None ):
    """
    GET
    """
    header_map = {}
    if force_multi_mode:
      header_map[ 'Multi-Object' ] = True

    logging.debug( 'cinp: GET "{0}"'.format( uri ) )
    ( http_code, rec_values, header_map ) = self._request( 'GET', uri, header_map=header_map, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for GET'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for GET'.format( http_code ) )

    if not isinstance( rec_values, dict ):
      logging.warning( 'cinp: Response rec_values must be a dict for GET' )
      raise ResponseError( 'Response rec_values must be a dict for GET' )

    return rec_values

  def create( self, uri, values, timeout=30, retry_count=0, retry_on=None ):
    """
    CREATE
    """
    if not isinstance( values, dict ):
      raise InvalidRequest( 'values must be a dict' )

    logging.debug( 'cinp: CREATE "{0}"'.format( uri ) )
    ( http_code, rec_values, header_map ) = self._request( 'CREATE', uri, data=values, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 201:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for CREATE'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for CREATE'.format( http_code ) )

    if not isinstance( rec_values, dict ):
      logging.warning( 'cinp: Response rec_values must be a dict for CREATE' )
      raise ResponseError( 'Response rec_values must be a dict for CREATE' )

    try:
      object_id = header_map[ 'Object-Id' ]
    except KeyError:
      raise ResponseError( 'Object-Id header missing' )

    return ( object_id, rec_values )

  def update( self, uri, values, force_multi_mode=False, timeout=30, retry_count=0, retry_on=None ):
    """
    UPDATE
    """
    if not isinstance( values, dict ):
      raise InvalidRequest( 'values must be a dict' )

    header_map = {}
    if force_multi_mode:
      header_map[ 'Multi-Object' ] = True

    logging.debug( 'cinp: UPDATE "{0}"'.format( uri ) )
    ( http_code, rec_values, _ ) = self._request( 'UPDATE', uri, data=values, header_map=header_map, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for UPDATE'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for UPDATE'.format( http_code ) )

    if not isinstance( rec_values, dict ):
      logging.warning( 'cinp: Response rec_values must be a dict for UPDATE' )
      raise ResponseError( 'Response rec_values must be a str for UPDATE' )

    return rec_values

  def delete( self, uri, timeout=30, retry_count=0, retry_on=None ):
    """
    DELETE
    """
    logging.debug( 'cinp: DELETE "{0}"'.format( uri ) )
    ( http_code, _, _ ) = self._request( 'DELETE', uri, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for DELETE'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for DELETE'.format( http_code ) )

    return True

  def call( self, uri, args, force_multi_mode=False, timeout=30, retry_count=0, retry_on=None ):
    """
    CALL
    """
    if not isinstance( args, dict ):
      raise InvalidRequest( 'args must be a dict' )

    header_map = {}
    if force_multi_mode:
      header_map[ 'Multi-Object' ] = True

    logging.debug( 'cinp: CALL "{0}"'.format( uri ) )
    ( http_code, return_value, _ ) = self._request( 'CALL', uri, data=args, header_map=header_map, timeout=timeout, retry_count=retry_count, retry_on=retry_on )

    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for CALL'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for CALL'.format( http_code ) )

    return return_value

  def getMulti( self, uri, id_list=None, chunk_size=10, retry_count=0, retry_on=None ):
    """
    returns a generator that will iterate over the uri/id_list, reterieving from the server in chunk_size blocks
    each item is ( rec_id, rec_values )
    if uri is a list, id_list is ignored
    """
    if isinstance( uri, list ):
      id_list = []
      for item in uri:
        ( _, _, _, tmp_id_list, _ ) = self.uri.split( item )
        id_list += tmp_id_list

      ( namespace, model, _, tmp_id_list, _ ) = self.uri.split( uri[0] )

    else:
      ( namespace, model, _, tmp_id_list, _ ) = self.uri.split( uri )
      if id_list is None:
        id_list = tmp_id_list

    result_list = []
    pos = 0

    while pos < len( id_list ):
      tmp_data = self.get( self.uri.build( namespace, model, None, id_list[ pos: pos + chunk_size ] ), force_multi_mode=True, retry_count=retry_count, retry_on=retry_on )
      pos += chunk_size
      for key in tmp_data:
        result_list.append( ( key, tmp_data[ key ] ) )

      while len( result_list ) > 0:
        yield result_list.pop( 0 )

  def getFilteredObjects( self, uri, filter_name=None, filter_value_map=None, list_chunk_size=100, get_chunk_size=10, timeout=30, retry_count=0, retry_on=None ):
    pos = 0
    total = 1
    while pos < total:
      ( tmp_id_list, count_map ) = self.list( uri, filter_name=filter_name, filter_value_map=filter_value_map, position=pos, count=list_chunk_size, retry_count=retry_count, retry_on=retry_on )
      id_list = self.uri.extractIds( tmp_id_list )
      pos = count_map[ 'position' ] + count_map[ 'count' ]
      total = count_map[ 'total' ]
      return self.getMulti( uri, id_list, get_chunk_size, retry_count=retry_count, retry_on=retry_on )  # TODO: need to found out how to get the next chunk, return/yeild something

  def getFilteredURIs( self, uri, filter_name=None, filter_value_map=None, list_chunk_size=100, get_chunk_size=10, timeout=30, retry_count=0, retry_on=None ):
    pos = 0
    total = 1
    while pos < total:
      ( tmp_id_list, count_map ) = self.list( uri, filter_name=filter_name, filter_value_map=filter_value_map, position=pos, count=list_chunk_size, retry_count=retry_count, retry_on=retry_on )
      id_list = self.uri.extractIds( tmp_id_list )
      pos = count_map[ 'position' ] + count_map[ 'count' ]
      total = count_map[ 'total' ]

      while len( id_list ) > 0:
        yield id_list.pop( 0 )

  def getFile( self, uri, target_dir='/tmp', file_object=None, cb=None, timeout=30, chunk_size=( 4096 * 1024 ) ):
    """
    if file_object is defined:
       The file contense are written to it and the filename as specified by the
       server is returned, None is returned if not filename is detected.  The
       file_object is not closed. file_object must be opened with the 'b' attribute.

    Otherwise a file is created in target_dir, and the full path is returned.  If the
      filename is not specified by the server, and a random filename is chosen.
      WARNING: there isn't checking done to make sure the target file does not allready
      exist, there is a possibility it could clober something that allready exists.
      we do make sure the filename fits a regex pattern that prevents it from escaping
      the target_dir.  The "filename" as sent by the server is the "model" of the uri.
      make sure target_dir exists before calling getFile
    """

    uri_parser = URI( '/' )
    try:  # TODO: There has to be a better way to validate this uri
      ( _, filename, _, _, _ ) = uri_parser.split( uri )
    except ValueError as e:
      raise InvalidRequest( str( e ) )

    # Due to the return value we have to do our own request, this is pretty much a stright GET
    url = '{0}{1}'.format( self.host, uri )
    req = request.Request( url )
    req.get_method = lambda: 'GET'
    try:
      resp = self.opener.open( req, timeout=timeout )

    except request.HTTPError as e:
      raise ResponseError( 'HTTPError "{0}"'.format( e ) )

    except request.URLError as e:
      if isinstance( e.reason, socket.timeout ):
        raise Timeout( 'Request Timeout after {0} seconds'.format( timeout ) )

      raise ResponseError( 'URLError "{0}" for "{1}" via "{2}"'.format( e, url, self.proxy ) )

    http_code = resp.code
    if http_code != 200:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for File Get'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for File Get'.format( http_code ) )

    try:
      size = resp.headers[ 'Content-Length' ]
    except KeyError:
      size = 0

    if file_object is not None:
      file_writer = file_object

    else:
      if filename is None:
        file_writer = NamedTemporaryFile( dir=target_dir, mode='wb' )
        filename = file_writer.name

      else:
        filename = os.path.join( target_dir, filename )
        file_writer = open( filename, 'wb' )

    buff = resp.read( chunk_size )
    while buff:
      file_writer.write( buff )
      if cb:
        cb( file_writer.tell(), size )
      buff = resp.read( chunk_size )

    resp.close()

    if file_object is not None:
      return filename

    else:
      file_writer.close()
      return filename

  def uploadFile( self, uri, filepath, filename=None, cb=None, timeout=30 ):
    """
    filepath can be a string of the path name or a file object.  If a file object
    either specify the filename or make sure your file object exposes the attribute
    'name'.  Also if file object, must be opened in binary mode, ie: 'rb'

    NOTE: this is not a CInP function, but a conviance function for uploading large files.
    """
    uri_parser = URI( '/' )
    try:  # TODO: There has to be a better way to validate this uri
      ( namespace, model, action, id_list, _ ) = uri_parser.split( uri )
    except ValueError as e:
      raise InvalidRequest( str( e ) )

    if action is not None or id_list is not None:
      raise InvalidRequest( 'file upload target can\'t be an action nor have ids' )

    if isinstance( filepath, str ):
      if filename is None:
        filename = os.path.basename( filepath )

      file_reader = _readerWrapper( open( filepath, 'rb' ), cb )

    else:
      if filename is None:
        filename = os.path.basename( filepath.name )

      file_reader = _readerWrapper( filepath, cb )

    header_map = {
                   'Content-Disposition': 'inline: filename="{0}"'.format( filename ),
                   'Content-Length': len( file_reader )
                 }

    ( http_code, data, _ ) = self._request( 'UPLOAD', uri_parser.build( namespace, model ), data=file_reader, header_map=header_map, timeout=timeout )

    if http_code != 202:
      logging.warning( 'cinp: Unexpected HTTP Code "{0}" for File Upload'.format( http_code ) )
      raise ResponseError( 'Unexpected HTTP Code "{0}" for File Upload'.format( http_code ) )

    return data[ 'uri' ]


class _readerWrapper():
  def __init__( self, reader, cb ):
    self._cb = cb
    self._size = os.fstat( reader.fileno() ).st_size
    self._reader = reader

  def __len__( self ):
    return self._size

  def read( self, size ):
    if self._cb:
      self._cb( self._reader.tell(), self._size )
    buff = self._reader.read( size )
    return buff


def JSONDefault( obj ):
   if isinstance( obj, datetime ):
     return obj.isoformat()

   return json.JSONEncoder.default( obj )
