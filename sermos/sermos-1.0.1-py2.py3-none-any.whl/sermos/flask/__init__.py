""" Sermos' Flask Implementation and Tooling. Convenience imports here.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from rho_web.smorest import Blueprint, Api
    from rho_web.response import abort
except Exception as e:
    logger.error("Unable to import Web services (Blueprint, API, abort)"
                 f" ... {e}")

try:
    from flask_rhoauth import OpenIDConnect
except Exception as e:
    oidc = None
    OpenIDConnect = None
    logging.info("Did not initialize oidc ... {}".format(e))
else:
    if OpenIDConnect is not None:
        oidc = OpenIDConnect()

try:
    from sermos.flask.flask_sermos import FlaskSermos
except Exception as e:
    logger.exception("Unable to import Sermos services (FlaskSermos)"
                     f" ... {e}")
