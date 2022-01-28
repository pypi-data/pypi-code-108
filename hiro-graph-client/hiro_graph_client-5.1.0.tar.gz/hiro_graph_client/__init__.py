"""
Package which contains the classes to communicate with HIRO Graph.
"""
import site
from os import path

from hiro_graph_client.appclient import HiroApp
from hiro_graph_client.authclient import HiroAuth
from hiro_graph_client.authzclient import HiroAuthz
from hiro_graph_client.client import HiroGraph
from hiro_graph_client.clientlib import AbstractTokenApiHandler, AuthenticationTokenError, FixedTokenError, \
    TokenUnauthorizedError, PasswordAuthTokenApiHandler, FixedTokenApiHandler, EnvironmentTokenApiHandler, \
    SSLConfig
from hiro_graph_client.iamclient import HiroIam
from hiro_graph_client.kiclient import HiroKi
from hiro_graph_client.variablesclient import HiroVariables
from hiro_graph_client.version import __version__

this_directory = path.abspath(path.dirname(__file__))

__all__ = [
    'HiroGraph', 'HiroAuth', 'HiroApp', 'HiroIam', 'HiroKi', 'HiroAuthz', 'HiroVariables',
    'AbstractTokenApiHandler', 'PasswordAuthTokenApiHandler', 'FixedTokenApiHandler', 'EnvironmentTokenApiHandler',
    'AuthenticationTokenError', 'FixedTokenError', 'TokenUnauthorizedError', '__version__',
    'SSLConfig'
]

site.addsitedir(this_directory)
