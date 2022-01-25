""" Sermos implementation as a Flask extension
"""
import os
if os.getenv('USE_GEVENT', 'false').lower() == 'true':
    import gevent.monkey
    gevent.monkey.patch_all()

import logging
from functools import partial
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from rho_web.smorest import Api, Blueprint
from sermos_tools import SermosTools
from sermos.utils.task_utils import TaskRunner, PipelineResult
from sermos.logging_config import setup_logging
from sermos.extensions import sermos_config
from sermos.flask import oidc
from sermos.constants import DEFAULT_OPENAPI_CONFIG, DEFAULT_RHOAUTH_CONFIG
from sermos import __version__

logger = logging.getLogger(__name__)


class FlaskSermos:
    """ Sermos Flask extension.
    """
    def __init__(self, app: Flask = None):
        """ Class init
        """
        self.app = app
        self.sermos_config = sermos_config if sermos_config is not None else {}

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask, init_api: bool = False):
        """ Sermos bootstrapping process.

        Application config variables to set include:

            SERMOS_CLIENT_VERSION (default: v?.?.?)
            RHOAUTH_ENABLED (default: True)
            SERMOS_HIJACK_ROOT_LOGGER (default: False)

        Optional, if `init_api` is True:

            API_DOCUMENTATION_TITLE
            API_DOCUMENTATION_DESCRIPTION
            OPENAPI_VERSION
            OPENAPI_URL_PREFIX
            OPENAPI_SWAGGER_APP_NAME
            OPENAPI_SWAGGER_UI_PATH
            OPENAPI_SWAGGER_BASE_TEMPLATE
            OPENAPI_SWAGGER_URL
            OPENAPI_SWAGGER_UI_URL
            SWAGGER_UI_DOC_EXPANSION
            EXPLAIN_TEMPLATE_LOADING

        Args:
            app (Flask): Flask Application to initialize.
            init_api (bool): If `True`, Sermos will initialize its
                core APIs (including Pipelines, Scheduled Tasks, etc.) and
                provide a pre-configured OpenAPI Spec/Swagger UI interface
                available at the route defined in your application's config
                under `OPENAPI_URL_PREFIX` (default `/api`). Refer to
                [flask-smorest](https://flask-smorest.readthedocs.io/en/latest/openapi.html)
                documentation for additional configuration options.
        """
        # Ensure there's a SERMOS_CLIENT_VERSION on app config
        app.config.setdefault(
            'SERMOS_CLIENT_VERSION',
            app.config.get("SERMOS_CLIENT_VERSION", "v?.?.?"))

        # Bootstrap logging if app requests
        self._bootstrap_logging(app)

        # Register Sermos Tools in app extensions
        app.extensions = getattr(app, 'extensions', {})
        app.extensions.setdefault('sermos_tools', SermosTools())

        # Add Sermos tooling to instantiated SermosTools
        app.extensions['sermos_tools'].set_tool(TaskRunner)
        app.extensions['sermos_tools'].set_tool(PipelineResult)

        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.url_map.strict_slashes = False

        # Create and register the sermos blueprint
        bp = Blueprint('sermos',
                       __name__,
                       template_folder='../templates',
                       static_folder='../static',
                       url_prefix='/sermos')
        app.register_blueprint(bp)

        # Bootstrap RhoAuth if app requests
        self._bootstrap_rhoauth(app)

        # Bootstrap api if app requests
        if init_api is True:
            self._bootstrap_api(app)

    def _bootstrap_rhoauth(self, app: Flask):
        """ If RHOAUTH_ENABLED is True, bootstrap the application with default
            configuration, precedent given to the provide app.
        """
        # TODO Remove rhoauth by default and/or entirely in future release.
        rhoauth_enabled = str(app.config.get('RHOAUTH_ENABLED',
                                             True)).lower() == 'true'
        app.config.setdefault('RHOAUTH_ENABLED', rhoauth_enabled)
        if rhoauth_enabled is True:
            # Set useful defaults so users don't need to request.
            for rhoauth_config in DEFAULT_RHOAUTH_CONFIG:
                app.config.setdefault(
                    rhoauth_config[0],
                    app.config.get(rhoauth_config[0], rhoauth_config[1]))

        # Initialize open id connect for authentication
        if rhoauth_enabled is True:
            logger.info("Initializing using RhoAuth ...")
            self.oidc = oidc
            self.oidc.init_app(app)

            @app.route('/logout')
            def logout():
                return self.oidc.logout("/")

    @staticmethod
    def _bootstrap_logging(app: Flask):
        """ If application requests Sermos logging, enable here

            Main reason to do this is to have clear versioning in each log
            and to supress the elasticsearch log level by default, which is
            extremely verbose if using elasticsearch-py. There is no dependency
            on elasticsearch - we simply create the logger and upgrade level
            because it's extremely annoying if you do need to use ES.
        """
        if app.config.get('SERMOS_HIJACK_ROOT_LOGGER', False):
            overload_es = app.config.get('OVERLOAD_ES_LOGGING', True)
            logger.info("Initializing using Sermos logging ...")
            setup_logging(app_version=__version__,
                          client_version=app.config['SERMOS_CLIENT_VERSION'],
                          default_level=app.config.get("LOG_LEVEL", "INFO"),
                          overload_elasticsearch=overload_es,
                          establish_logging_config=True)

    def _bootstrap_api(self, app: Flask):
        """ If initializing the API, we will create the core Sermos API paths
            and initialize the default Swagger documentation.
        """
        # Set sensible defaults for Swagger docs. Provided `app` will
        # take precedent.
        for swagger_config in DEFAULT_OPENAPI_CONFIG:
            app.config.setdefault(
                swagger_config[0],
                app.config.get(swagger_config[0], swagger_config[1]))

        # Attempt to override with values from client's sermos.yaml if
        # they are available. This will add new tags and new docs if
        # defined and add to the core Sermos API docs.
        api_config = self.sermos_config.get('apiConfig', {})
        api_docs = api_config.get('apiDocumentation', {})

        custom_tags = api_config.get('prefixDescriptions', [])

        app.config['SERMOS_CLIENT_VERSION'] = \
            api_docs.get('version', None) \
            if api_docs.get('version', None) is not None \
            else app.config['SERMOS_CLIENT_VERSION']

        app.config['API_DOCUMENTATION_TITLE'] = \
            api_docs.get('title', None) \
            if api_docs.get('title', None) is not None \
            else app.config['API_DOCUMENTATION_TITLE']

        app.config['API_DOCUMENTATION_DESCRIPTION'] = \
            api_docs.get('description', None) \
            if api_docs.get('description', None) is not None \
            else app.config['API_DOCUMENTATION_DESCRIPTION']

        # Set default Sermos Tags along with custom tags from sermos.yaml
        tags = [{
            'name': 'Pipelines',
            'description': 'Operations related to Pipelines'
        }, {
            'name': 'Schedules',
            'description': 'Operations related to Schedules'
        }] + custom_tags

        # Set up  the initializing spec kwargs for API
        spec_kwargs = {
            'title': app.config['API_DOCUMENTATION_TITLE'],
            'version': f"Sermos: {__version__} - "
            f"Client: {app.config['SERMOS_CLIENT_VERSION']}",
            'description': app.config['API_DOCUMENTATION_DESCRIPTION'],
            'tags': tags
        }
        try:
            # Initialize the API documentation and ensure RhoAuth validates
            # correct `role`
            if str(app.config['RHOAUTH_ENABLED']).lower() == 'true':
                decorator = partial(self.oidc.require_login,
                                    roles=['sermos-client-api-docs'])
                api = Api(auth_decorator=decorator)
            else:
                api = Api()

            api.init_app(app, spec_kwargs=spec_kwargs)

            # Register available Sermos API Namespaces
            self._register_api_namespaces(api)

        except Exception as e:
            api = None
            logging.exception(f"Unable to initialize API ... {e}")

        # Register the Sermos Core API as an extension for use in Client App
        app.extensions.setdefault('sermos_core_api', api)

    @staticmethod
    def _register_api_namespaces(api: Api):
        """ Register Default API namespaces
            TODO add metrics APIs
        """
        from sermos.flask.api.pipelines import bp as pipelinesbp
        api.register_blueprint(pipelinesbp)
        from sermos.flask.api.schedules import bp as schedulesbp
        api.register_blueprint(schedulesbp)
