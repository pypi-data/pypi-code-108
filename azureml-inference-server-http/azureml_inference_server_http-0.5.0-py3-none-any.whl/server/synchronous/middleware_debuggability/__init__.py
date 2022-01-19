import importlib
import os
import pkgutil
import sys
import traceback

def init_debuggability(logger, app):
    dbg_middlewares = {
        name: importlib.import_module('synchronous.middleware_debuggability.' + name)
        for finder, name, ispkg in pkgutil.iter_modules([os.path.dirname(os.path.realpath(__file__))])
        if name.startswith('dbg_')
    }
    try:
        for name, middleware in dbg_middlewares.items():
            if middleware.enabled():
                logger.info("Starting up middleware: %s" % name)
                app.wsgi_app = middleware.WSGIRequest(logger, app.wsgi_app)
            else:
                logger.info("Skipping middleware: %s as it's not enabled." % name)
    except:
        logger.error(
            "Encountered exception while starting up debuggability middleware: {0}".format(traceback.format_exc()))
        sys.exit(3)

