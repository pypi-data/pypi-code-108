# encoding=utf-8

from logbook import Logger

from hansken.auth import resolve
from hansken.remote import Connection, ProjectContext


log = Logger(__name__)


def connect(endpoint,
            idp=None,
            username=None,
            password=None,
            auth=None,
            keystore=None,
            preference=None,
            verify=True,
            interactive=False,
            connection_pool_size=None,
            **kwargs):
    """
    Connect to the Hansken REST API at *endpoint*.

    .. note::
        Only *endpoint* is a required argument here, but note that most Hansken
        environments will require some way of authentication. For environments
        configured with a single authentication option, ``hansken.py`` will
        automatically use the only option. When a choice is required, calls to
        `.connect` will raise an error listing the options for the *idp*
        argument.

        Likewise, authentication methods requiring a *username* and *password*
        will produce an error when these are omitted and *interactive* is left
        ``False`` (setting this to ``True`` will make ``hansken.py`` prompt for
        required values that are missing).

        Manually passing a `HanskenAuthBase` object is supported through the
        *auth* argument, but not recommended.

    :param endpoint: the URL of the Hansken REST API to connect to
    :param idp: an identity provider id to authenticate to
    :param username: a username to authenticate as
    :param password: the password for *username* at *idp*
    :param auth: a preconfigured authentication object (other authentication
        related arguments will be ignored)
    :param keystore: the URL of the Hansken Keystore REST API
    :param preference: the URL of the Hansken Preference REST API
    :param verify: whether to check validity of SSL/TLS certificates
    :param interactive: whether to allow interactivity (like prompting for a
        password)
    :param connection_pool_size: maximum size of HTTP(S) connection pool
    :param kwargs: (ignored)
    :return: a `.Connection` object connected to the Hansken REST API at
        *endpoint*
    """
    if kwargs:
        # kwargs are ignored, warn the user in case some of these were meant to be something else
        log.warn('ignoring {} keyword arguments to {}.connect: {}',
                 len(kwargs), __name__, ', '.join(sorted(kwargs.keys())))

    # take either a preconfigured HanskenAuthBase or resolve one against the remote
    auth = auth or resolve(base_url=endpoint, idp_id=idp,
                           username=username, password=password,
                           interactive=interactive,
                           verify=verify)
    return Connection(base_url=endpoint, keystore_url=keystore, preference_url=preference,
                      auth=auth,
                      connection_pool_size=connection_pool_size,
                      verify=verify)


def connect_project(endpoint,
                    project,
                    idp=None,
                    username=None,
                    password=None,
                    auth=None,
                    keystore=None,
                    preference=None,
                    verify=True,
                    interactive=False,
                    connection_pool_size=None,
                    **kwargs):
    """
    Connect to the Hansken REST API at *endpoint*, using *project* as the
    project to attach to.

    .. note::
        Only *endpoint* and *project are required arguments here, but note that
        most Hansken environments will require some way of authentication. For
        environments configured with a single authentication option,
        ``hansken.py`` will automatically use the only option. When a choice is
        required, calls to `.connect_project` will raise an error listing the
        options for the *idp* argument.

        Likewise, authentication methods requiring a *username* and *password*
        will produce an error when these are omitted and *interactive* is left
        ``False`` (setting this to ``True`` will make ``hansken.py`` prompt for
        required values that are missing).

        Manually passing a `HanskenAuthBase` object is supported through the
        *auth* argument, but not recommended.

    :param endpoint: the URL of the Hansken REST API to connect to
    :param project: the project id to attach to
    :param idp: an identity provider id to authenticate to
    :param username: a username to authenticate as
    :param password: the password for *username* at *idp*
    :param auth: a preconfigured authentication object (other authentication
        related arguments will be ignored)
    :param keystore: the URL of the Hansken Keystore REST API
    :param preference: the URL of the Hansken Preference REST API
    :param verify: whether to check validity of SSL/TLS certificates
    :param interactive: whether to allow interactivity (like prompting for a
        password)
    :param connection_pool_size: maximum size of HTTP(S) connection pool
    :param kwargs: (ignored)
    :return: a `.ProjectContext` object connected to the Hansken REST API at
        *endpoint*, attached to project *project*
    """
    # reuse connect to create a Connection (not using project)
    connection = connect(endpoint,
                         idp=idp,
                         username=username,
                         password=password,
                         auth=auth,
                         keystore=keystore,
                         preference=preference,
                         verify=verify,
                         interactive=interactive,
                         connection_pool_size=connection_pool_size,
                         **kwargs)
    # attach connection to project
    return ProjectContext(connection, project)
