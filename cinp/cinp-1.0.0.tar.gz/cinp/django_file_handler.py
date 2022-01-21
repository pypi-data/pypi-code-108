import os
import tempfile
import json
import re
from datetime import datetime, timedelta

from cinp.server_common import Response, InvalidRequest
from cinp.readers import READER_REGISTRY

FILE_STORAGE = '/tmp/django_file_handler/'
FILE_TTL = timedelta( hours=2 )
CHUNK_SIZE = 4096 * 1024
INLINE_CONTENT_DISPOSITION = re.compile( r'^inline: filename="([a-zA-Z0-9_\-\. ]+)"$' )


def cleaner():  # .meta files are created at the same time, so they should clean up at the same time
  cutoff = datetime.now() - FILE_TTL
  for filename in os.listdir( FILE_STORAGE ):
    filepath = os.path.join( FILE_STORAGE, filename )
    if datetime.fromtimestamp( os.path.getctime( filepath ) ) < cutoff:
      print( 'removing "{0}"'.format( filepath ) )
      os.unlink( filepath )


def _localFileReader( refname ):
  if not re.match( '^[a-z0-9_]+$', refname ):
    raise ValueError( 'Invalid refname' )

  filepath = os.path.join( FILE_STORAGE, refname )

  try:
    meta = json.loads( open( '{0}.meta'.format( filepath ), 'r' ).read() )
  except ( json.JSONDecodeError, FileNotFoundError ):
    raise ValueError( 'Invalid refname' )

  try:
    reader = open( filepath, 'rb' )
  except FileNotFoundError:
    raise ValueError( 'Invalid refname' )

  try:
    return ( reader, meta[ 'filename' ] )
  except KeyError:
    raise ValueError( 'Invalid refname' )


def _localFileWriter( origional_filename ):
  if not os.path.exists( FILE_STORAGE ):
    os.makedirs( FILE_STORAGE )

  writer = tempfile.NamedTemporaryFile( mode='wb', prefix='', dir=FILE_STORAGE, delete=False )
  filename = writer.name

  open( '{0}.meta'.format( filename ), 'w' ).write( json.dumps( { 'filename': origional_filename } ) )

  return ( writer, os.path.basename( filename ) )


def djfh( uri ):
  reader, filename = _localFileReader( uri[ len( 'djfh://' ): ] )
  return ( reader, filename )


READER_REGISTRY[ 'djfh' ] = djfh


# for adding to django url lists
# url.append( url(), upload_view )
def upload_view( django_request ):
  pass


# for gnuicorn apps
def upload_handler( request ):  # TODO: also support multi-part
  if request.verb == 'OPTIONS':
    header_map = {}
    header_map[ 'Allow' ] = 'OPTIONS, POST'
    header_map[ 'Cache-Control' ] = 'max-age=0'
    header_map[ 'Access-Control-Allow-Methods' ] = header_map[ 'Allow' ]
    header_map[ 'Access-Control-Allow-Headers' ] = 'Accept, Content-Type, Content-Disposition'

    return Response( 200, data=None, header_map=header_map )

  if request.verb != 'POST':
    return Response( 400, data='Invalid Verb (HTTP Method)', content_type='text' )

  if request.header_map.get( 'CONTENT-TYPE', None ) != 'application/octet-stream':
    return Response( 400, data='Invalid Content-Type', content_type='text' )

  content_disposition = request.header_map.get( 'CONTENT-DISPOSITION', None )
  if content_disposition is not None:
    match = INLINE_CONTENT_DISPOSITION.match( content_disposition )
    if not match:
      return InvalidRequest( message='Invalid Content-Disposition' ).asResponse()
    filename = match.groups( 1 )[0]
  else:
    filename = None

  file_writer, refname = _localFileWriter( filename )

  buff = request.read( CHUNK_SIZE )
  while buff:
    file_writer.write( buff )
    buff = request.read( CHUNK_SIZE )

  file_writer.close()

  return Response( 202, data={ 'uri': 'djfh://{0}'.format( refname ) } )
