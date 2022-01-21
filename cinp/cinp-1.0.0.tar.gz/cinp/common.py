import re
import sys


class URI():
  def __init__( self, root_path ):
    super().__init__()
    if root_path[-1] != '/' or root_path[0] != '/':
      raise ValueError( 'root_path must start and end with "/"' )

    self.root_path = root_path
    self.uri_regex = re.compile( r'^({0}|/)(([a-zA-Z0-9\-_.!~*<>]+/)*)([a-zA-Z0-9\-_.!~*<>]+)?(:([a-zA-Z0-9\-_.!~*\'<>]*:)*)?(\([a-zA-Z0-9\-_.!~*<>]+\))?$'.format( self.root_path ) )

  def split( self, uri, root_optional=False ):
    uri_match = self.uri_regex.match( uri )
    if not uri_match:
      raise ValueError( 'Unable to parse URI "{0}"'.format( uri ) )

    ( root, namespace, _, model, rec_id, _, action ) = uri_match.groups()
    if root != self.root_path and not root_optional:
      raise ValueError( 'URI does not start in the root_path' )

    if namespace != '':
      namespace_list = namespace.rstrip( '/' ).split( '/' )
    else:
      namespace_list = []

    if rec_id is not None:
      id_list = rec_id.strip( ':' ).split( ':' )
      multi = len( id_list ) > 1
    else:
      id_list = None  # id_list = [] is an empty list of ids, where None means the list is not even present
      multi = False

    if action is not None:
      action = action[ 1:-1 ]

    return ( namespace_list, model, action, id_list, multi )

  def build( self, namespace=None, model=None, action=None, id_list=None, in_root=True ):
    """
    build a uri, NOTE: if model is None, id_list and action are skiped
    """
    if in_root:
      result = self.root_path
    else:
      result = '/'

    if namespace is not None:
      if not isinstance( namespace, list ):
        namespace = [ namespace ]

      if len( namespace ) > 0:
        result = '{0}{1}/'.format( result, '/'.join( namespace ) )

    if model is None:
      return result

    result = '{0}{1}'.format( result, model )

    if id_list is not None and id_list != []:
      if not isinstance( id_list, list ):
        id_list = [ id_list ]

      result = '{0}:{1}:'.format( result, ':'.join( id_list ) )

    if action is not None:
      result = '{0}({1})'.format( result, action )

    return result

  def extractIds( self, uri_list ):  # TODO: should we make sure the namespace/model do not change in the list?
    """
    extract the record IDs from the URI's in uri_list, can handle some/all/none
    of the URIs having multiple IDs in them allready, does not force uniqunes
    order should remain intact
    """
    if isinstance( uri_list, str ):
      uri_list = [ uri_list ]

    if not isinstance( uri_list, list ):
      raise ValueError( 'uri_list must be string or list of strings' )

    result = []
    for uri in uri_list:
      uri_match = self.uri_regex.match( uri )
      if not uri_match:
        raise ValueError( 'Unable to parse URI "{0}"'.format( uri ) )

      ( _, _, _, _, rec_id, _, _ ) = uri_match.groups()
      if rec_id is None:
        continue

      result += rec_id.strip( ':' ).split( ':' )

    return result

  def uriListToMultiURI( self, uri_list ):
    """
    runs extract Ids on the list, then takes the first uri and applies all
    the ids to it
    """
    if not uri_list:
      return []

    id_list = self.extractIds( uri_list )
    if not id_list:
      return []

    ( namespace_list, model, action, _, _ ) = self.split( uri_list[0] )
    return self.build( namespace_list, model, action, id_list, True )


# barrowed from https://www.python.org/dev/peps/pep-0257/
def doccstring_prep( docstring ):
  if not docstring:
    return ''

  # Convert tabs to spaces (following the normal Python rules)
  # and split into a list of lines:
  lines = docstring.expandtabs().splitlines()

  # Determine minimum indentation (first line doesn't count):
  indent = sys.maxsize
  for line in lines[ 1: ]:
    stripped = line.lstrip()
    if stripped:
      indent = min( indent, len( line ) - len( stripped ) )

  # Remove indentation (first line is special):
  trimmed = [ lines[0].strip() ]
  if indent < sys.maxsize:
    for line in lines[1:]:
      trimmed.append( line[ indent: ].rstrip() )
  # Strip off trailing and leading blank lines:
  while trimmed and not trimmed[-1]:
    trimmed.pop()
  while trimmed and not trimmed[0]:
    trimmed.pop( 0 )

  # Return a single string:
  return '\n'.join( trimmed )
