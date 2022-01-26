""" Implementation of the API """

import requests
import pandas as pd

from ._config import Config

_config = Config()
_token = None

#==============================================================================
# private implementation behind API
#==============================================================================

def data_frame_from_response( record, resp ):
    """ create dataframe from response to get or list REST API call """
    result = ''

    if isinstance( resp, list ):
        data = []
        idxs = []

        for rec in resp:
            data.append( rec[ 'values' ] )
            idxs.append( rec[ 'record' ] )

        result = pd.DataFrame( data, idxs )

    else:
        data = []
        idxs = []

        data.append( resp[ 'values' ] )
        idxs.append( record )

        result = pd.DataFrame( data, idxs )

    return result

def data_frame_from_response_history( resp ):
    """ create dataframe from response to history REST API call """
    result = ''

    if '%FIELDS' in resp[ 'values' ]:
        resp[ 'values' ].pop( '%FIELDS' )

    if '%PUBLISHER' in resp[ 'values' ]:
        resp[ 'values' ].pop( '%PUBLISHER' )

    point_time = resp[ 'values' ].pop( 'PointTime' )
    result = pd.DataFrame( resp[ 'values' ], point_time )

    return result

def check_response( response ):
    """ check if response from REST API call was error or data response"""
    if isinstance( response, dict ) and 'status' in response and response[ 'status' ].startswith( 'error_' ):
        if 'info' in response:
            return (False, response[ 'status' ] + ':' + response[ 'info' ])

        return (False, response[ 'status' ])

    return (True, '')

def history_date( dateval ):
    """ convert datetime or a string to ISO8601 format suitable for REST API call"""
    result = dateval

    if hasattr( dateval, 'isoformat' ):
        result = dateval.isoformat()

    elif isinstance( dateval, str ):
        try:
            temp = pd.to_datetime( dateval )
            result = temp.isoformat()
        except ValueError:
            pass

    return result

def rest_request( path, json, token=None, reauth=None ):
    """ issue a request to MDXT Connect REST API """
    headers = None

    error = None
    response = None

    if token:
        headers = { 'Authorization': f'Token {token}' }

    try:
        response = requests.post( _config.get_url() + path, json=json, headers=headers )

        if response.status_code == 400:
            error = 'Bad request (400). Please check parameters were correct.'

        elif response.status_code == 401:
            if reauth:
                good, msg = reauth()

                if good:
                    error, response = rest_request( path, json, _token, reauth=None )
                else:
                    error = msg

            else:
                error = 'Request unauthorized (401). Please check configured username/passkey.'

        elif response.status_code != 200:
            error = 'HTTP Error ' + str( response.status_code )

        if error:
            response = None

    except requests.exceptions.Timeout as ex:
        error = 'Request attempt timed out. Please try again or check parameters.'

    except requests.exceptions.RequestException as ex:
        error = 'HTTP Error: ' + str(ex)

    return (error, response)

def rest_authenticate():
    """ issue an auth request to REST API server and retrieve auth token  """
    global _token
    _token = None

    error, response = rest_request( '/v1/auth', json={ 'username': _config.get_username(), 'passkey': _config.get_passkey() } )

    if not error:
        _token = response.json()[ 'token' ]

    return error

def make_request( path, json ):
    """ make a request on server, authenticating first and reauthing if needed"""
    error = None
    response = None

    if not _token:
        good, msg = _config.read( )

        if not good:
            error = 'Failed to retrieve configuration. ' + msg

        else:
            error = rest_authenticate()

    if _token:
        error, response = rest_request( path, json, _token, rest_authenticate() )

    return (error, response)

#==============================================================================
# Exported API functions
#==============================================================================

def configure(*, username=None, passkey=None, url=None):
    """Set the credentials and connectivity details to be used when making requests from mdxtconnect.

    Parameters
    ----------
    username : str, optional
        username to authenticate with
    passkey : str, optional
        passkey to authenticate with
    url : str, optional
        URL to connect to.

    Returns
    -------
    str
        returns a message indicating whether configuration was successfully set and stored.

    Example
    -------
    Set username, passkey and URL

    >>> mdxtconnect.configure(username='jrandall@example.com', passkey='MIGfMA0GCSqGSIb3DQEBAQUAA4GNA', url='https://data.mdxtechnology.com')

    Switch existing configuration use different server

    >>> mdxtconnect.configure(url='https://data_test.mdxtechnology.com')

    Notes
    -----
    Calling this function writes the configuration to a file in the user's home directory. Having done this once
    the configuration is used automatically to authenticate before making any `get`, `get_list` or `history` request.

    """

    if not _config.set( username, passkey, url ):
        return 'No change.'

    good, msg = _config.write()

    if not good:
        msg = msg + ' Please check home directory is writable.'

    return msg

def get(provider, record, *, group=None, fields=None):
    """get record(s) from named provider on MDXT Connect

    Parameters
    ----------
    provider : str
        name of the provider to retrieve data from
    record : str or list
        record name or list of record names to retrieve
    group : str, optional
        name of record group record(s) will be retrieved from.
    fields : list, optional
        list of specific field names to retrieve (the default is all known fields)

    Returns
    -------
    pandas.DataFrame or str
        returns a DataFrame containing requested data if successful or an error string on failure

    Example
    -------
    Request for single record (all fields)

    >>> mdxtconnect.get('NewChangeFX', 'EUR/JPY')

    Request for multiple records (all fields)

    >>> mdxtconnect.get('NewChangeFX', ['EUR/JPY','EUR/CHF'])

    Request for multiple records and specific fields (only)

    >>> mdxtconnect.get('NewChangeFX', ['EUR/JPY','EUR/CHF'], fields=['settlementDate', 'midPrice'])

    Notes
    -----
    You need to call `mdxtconnect.configure` to set your credentials and server configuration prior to calling this.

    """

    body = { 'record': record }

    if fields:
        body[ 'fields' ] = fields

    if group:
        body[ 'group' ] = group

    error, response = make_request( '/v1/data/' + provider, json=body )

    if error:
        result = error
    else:
        good, error = check_response( response.json() )

        if good:
            result = data_frame_from_response( record, response.json() )
        else:
            result = error

    return result

def history(provider, record, *, group=None, start=None, end=None, points=None, period=None):
    """get historic data for record from named provider on MDXT Connect plaform or MDX Data Marketplace

    Parameters
    ----------
    provider : str
        name of the provider to retrieve data from
    record : str
        name of record to retrieve
    group : str, optional
        name of record group record will be retrieved from.
    start : str or datetime, optional
        start date
    end : str or datetime, optional
        end date
    points : int, optional
        number of points to retrieve
    period: {'D','W','M','Q'...}, optional
        Periodicity code for interday or intraday history. Omit for tick history. Specific periodicities depend
        on the data provider being used.

    Returns
    -------
    pandas.DataFrame or str
        returns a DataFrame containing requested data if successful or an error string on failure

    Example
    -------

    >>> mdxtconnect.history('ICE', 'BARC-LON', start='2020-01-01', end='2020-12-31', period='W')

    >>> mdxtconnect.history('ICE', 'WBS 21G-ICE', end=datetime.date(2021, 1, 1)', points=100)

    Notes
    -----
    You need to call `mdxtconnect.configure` to set your credentials and server configuration prior to calling this.

    You must specify at least two of the parameters `start`, `end` or `points`

    """

    body = { 'record': record, 'history': {} }

    if group:
        body[ 'group' ] = group

    if start:
        body[ 'history' ][ 'start' ] = history_date( start )

    if end:
        body[ 'history' ][ 'end' ] = history_date( end )

    if points:
        body[ 'history' ][ 'points' ] = points

    if period:
        body[ 'history' ][ 'period' ] = period

    error, response = make_request( '/v1/data/' + provider, json=body )

    if error:
        result = error

    else:
        good, error = check_response( response.json() )

        if good:
            result = data_frame_from_response_history( response.json() )
        else:
            result = error

    return result

def get_list(provider, listrecord, *, group=None, fields=None):
    """get records from a named list record on MDXT Connect Platform or Data Marketplace

    Parameters
    ----------
    provider : str
        name of the provider to retrieve data from
    listrecord : str
        name of list record to retrieve records from
    group : str, optional
        name of record group list will be retrieved from.
    fields : list, optional
        list of specific field names to retrieve (the default is all known fields)

    Returns
    -------
    pandas.DataFrame or str
        returns a DataFrame containing requested data if successful or an error string on failure

    Example
    -------
    Request for a list record whose name is a wildcard

    >>> mdxtconnect.get_list('NewChangeFX', 'EUR/*')

    Request for a list record whose name is predefined (for example an index)

    >>> mdxtconnect.get_list('AxessAll', 'AllBonds')

    Notes
    -----
    You need to call `mdxtconnect.configure` to set your credentials and server configuration prior to calling this.

    """

    body = { 'list': listrecord }

    if fields:
        body[ 'fields' ] = fields

    if group:
        body[ 'group' ] = group

    error, response = make_request( '/v1/data/' + provider, json=body )

    if error:
        result = error

    else:
        good, error = check_response( response.json() )

        if good:
            result = data_frame_from_response( listrecord, response.json() )
        else:
            result = error

    return result
