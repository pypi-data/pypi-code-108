"""
Just a way to have clean import sequences at app module inits
"""
import os

from gevent import monkey

if not os.environ.get('gevent_no_patch'):
    monkey.patch_all()

fn_backd = lambda: os.environ['var_dir'] + '/proc_enter.sock'


def start_pywsgi_server(application, bind=None, with_backdoor=None):
    """Normal way to start a gevent wsgi server """
    import gevent
    from devapp.app import FLG, app
    from devapp.tools import host_port
    from structlogging import adapters

    # (would be far simpler in threaded bottle, but its a good blueprint
    # for some async http)
    host, port = host_port(bind or FLG.bind)
    s = gevent.pywsgi.WSGIServer
    # devapp adapter to get structlogging from pywsgi plain logging
    server = adapters.adapt_gevent_pywsgi(s((host, port)), logger=app.log)
    server.application = application
    # default logging is structlog, i.e. **kw style:
    fnb = fn_backd()
    if os.path.exists(fnb):
        os.remove(fnb)

    if with_backdoor:
        from gevent.backdoor import BackdoorServer
        from gevent import socket

        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(fn_backd())
        listener.listen(1)
        # has a ref to the app module if its a devapp:

        bdserver = BackdoorServer(
            listener,
            banner='You are connected into %s' % app.name,
            locals={'app': app.mod},
        )
        gevent.spawn(bdserver.serve_forever)

    app.log.info('Start serving', host=host, port=port)
    server.serve_forever()
