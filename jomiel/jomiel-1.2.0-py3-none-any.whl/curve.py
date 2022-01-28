#
# jomiel
#
# Copyright
#  2019-2020 Toni Gündoğdu
#
#
# SPDX-License-Identifier: Apache-2.0
#
"""TODO."""


def setup(socket):
    """Load the CURVE certificates required for a secure server
    connection.

    Args:
        socket (obj): The zmq socket to use

    Returns:
        Nothing

    """
    from jomiel.cache import opts
    from zmq import Context

    ctx = Context.instance()

    def auth_init():
        """Start an authenticator for this context."""
        from zmq.auth.thread import ThreadAuthenticator
        from jomiel.log import lg

        auth = ThreadAuthenticator(ctx, log=lg())
        auth.start()
        auth.allow(opts.curve_allow)

        # Tell the authenticator to use the client certificates in the
        # specified directory.
        #
        from os.path import abspath

        pubdir = abspath(opts.curve_public_key_dir)
        auth.configure_curve(domain=opts.curve_domain, location=pubdir)

        return auth

    auth = auth_init()

    from jomiel_comm.auth.curve import load_cert_file

    (pubkey, seckey) = load_cert_file(opts.curve_server_key_file)

    socket.curve_secretkey = seckey
    socket.curve_publickey = pubkey

    # Must come before bind.
    socket.curve_server = True

    return auth


# vim: set ts=4 sw=4 tw=72 expandtab:
