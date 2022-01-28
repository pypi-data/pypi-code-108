"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
import click
from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
# from flask_script import Manager
from celery import Celery

celery = Celery()


def init_api(**xargs):
    from MicroserviceApiIdentity.config import configuration
    from MicroserviceApiIdentity.db import database, redis
    from MicroserviceApiIdentity.resources import (
        TokensResource, UsersResource, UserDetailsResource, UserPasswordResetResource,
        UserPasswordUpdateResource,
        SecretResource
    )
    from MicroserviceApiIdentity.resources.service import (
        PingServiceResource
    )

    app = Flask(__name__)
    app.config['DEBUG'] = configuration.getboolean('main', 'debug')
    app.config['SECRET_KEY'] = configuration.get("main", "secret_key")
    app.config['API_PREFIX'] = configuration.get("main", "api_prefix")

    app.config['JWT_SECRET'] = configuration.get('jwt', 'secret_key')
    app.config['JWT_ALGORITHM'] = configuration.get('jwt', 'algorithm')

    app.config['REDIS_URL'] = configuration.get('redis', 'url')
    app.config['CELERY_BROKER_URL'] = configuration.get('celery', 'broker_url')

    app.config['SQLALCHEMY_DATABASE_URI'] = configuration.get('database', 'dsn')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # see also: https://docs.sentry.io/clients/python/integrations/flask/
    if configuration.getboolean('sentry', 'enabled'):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(dsn=configuration.get('sentry', 'dsn'), integrations=[FlaskIntegration()])

    database.init_app(app)
    migrate = Migrate(app, database)
    redis.init_app(app)
    celery = init_celery(app)

    # RestAPI
    api = Api(app)

    # RestAPI Identity
    api.add_resource(TokensResource, app.config['API_PREFIX'] + '/v2/tokens')
    api.add_resource(UsersResource, app.config['API_PREFIX'] + '/v2/users')
    api.add_resource(UserDetailsResource, app.config['API_PREFIX'] + '/v2/user/details')
    api.add_resource(UserPasswordUpdateResource, app.config['API_PREFIX'] + '/v2/user/password_update')
    api.add_resource(UserPasswordResetResource, app.config['API_PREFIX'] + '/v2/user/password_reset')
    api.add_resource(SecretResource, app.config['API_PREFIX'] + '/v2/user/secret')
    # RestAPI Service Endpoint
    api.add_resource(PingServiceResource, app.config['API_PREFIX'] + '/v2/_/ping')

    @app.cli.command("get-migrations-dir")
    def cli_get_migrations_dir():
        import os
        import MicroserviceApiIdentity
        print(os.path.join(MicroserviceApiIdentity.__path__[0], "migrations"))
        # pass

    return app


# def init_manage(**xargs):
#     from MicroserviceApiIdentity.config import configuration
#     from MicroserviceApiIdentity.db import database, redis
#     from .commands import GetMigrationsDirCommand
#
#     app = Flask(__name__)
#     app.config['DEBUG'] = configuration.getboolean('main', 'debug')
#     app.config['SECRET_KEY'] = configuration.get("main", "secret_key")
#
#     app.config['JWT_SECRET'] = configuration.get('jwt', 'secret_key')
#     app.config['JWT_ALGORITHM'] = configuration.get('jwt', 'algorithm')
#
#     app.config['REDIS_URL'] = configuration.get('redis', 'url')
#     app.config['CELERY_BROKER_URL'] = configuration.get('celery', 'broker_url')
#
#     app.config['SQLALCHEMY_DATABASE_URI'] = configuration.get('database', 'dsn')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
#         "pool_pre_ping": True,
#         "pool_recycle": 300
#     }
#
#     # see also: https://docs.sentry.io/clients/python/integrations/flask/
#     if configuration.getboolean('sentry', 'enabled'):
#         import sentry_sdk
#         from sentry_sdk.integrations.flask import FlaskIntegration
#         sentry_sdk.init(dsn=configuration.get('sentry', 'dsn'), integrations=[FlaskIntegration()])
#
#     database.init_app(app)
#     redis.init_app(app)
#     migrate = Migrate(app, database)
#
#     manager = Manager(app)
#
#     # manager.add_command('db', MigrateCommand)
#     manager.add_command('get-migrations-dir', GetMigrationsDirCommand)
#
#     return manager


def init_celery(app):
    """init celery app"""

    # redis.init_app(app)
    # see also: https://docs.sentry.io/clients/python/integrations/flask/
    # sentry.init_app(app, dsn=settings.get('application', 'sentry_dsn'))
    celery.conf.update(app.config.get_namespace('CELERY_'))

    # See also: https://flask.palletsprojects.com/en/1.1.x/patterns/celery/
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    # from SWSCDNAPI import tasks

    return celery


if __name__ == "__main__":
    # Для того, чтобы запускалось celery
    application = init_api()
    application.run("0.0.0.0", 5000)
    # scheduler = init_celery(application)
