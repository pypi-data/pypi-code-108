import base64
import os
from urllib import request, parse
from io import StringIO

# reader is a function that returns a tubple that is file handle and filename, it is given the URI that is the value of the field from the client

READER_REGISTRY = {}


class InlineReader( StringIO ):
  def __init__( self, uri ):
    super().__init__( uri )
    self.seek( len( 'inline://' ) )
    self.filename = None  # should be incloded in the inline://, peek ahead and look for it

  def read( self, size ):
    return base64.b64decode( self.buffer.read( ( size * 3 ) / 2 ) )


def inline( uri ):
  reader = InlineReader( uri )

  return ( reader, reader.filename )


READER_REGISTRY[ 'inline' ] = inline


def http( uri ):
  reader = request.urlopen( uri )

  return ( reader, os.path.basename( parse.urlparse( uri ).path ) )


READER_REGISTRY[ 'http' ] = http
