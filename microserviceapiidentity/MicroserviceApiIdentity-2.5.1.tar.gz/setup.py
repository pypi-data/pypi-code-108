from setuptools import setup
import MicroserviceApiIdentity

setup(
    name="MicroserviceApiIdentity",
    version=MicroserviceApiIdentity.__version__,
    author='Vyacheslav Anzhiganov',
    author_email='hello@anzhiganov.com',
    url="https://stackwebservices.com",
    packages=[
        'MicroserviceApiIdentity',
        'MicroserviceApiIdentity.controllers',
        'MicroserviceApiIdentity.models',
        'MicroserviceApiIdentity.resources',
        'MicroserviceApiIdentity.resources.service',
    ],
    package_data={
        'MicroserviceApiIdentity': [
            'migrations/*.ini',
            'migrations/*.py',
            'migrations/versions/*.py',
        ]
    },
    scripts=[
        'ms-identity-manage',
        'ms-identity-db-upgrade',
        'ms-identity-db-revision',
        'ms-identity-runserver',
    ],
    install_requires=[
        'flask==2.0.2',
        'flask_restful==0.3.9',
        'flask_sqlalchemy==2.5.1',
        'flask_redis==0.4.0',
        'flask_migrate==3.1.0',
        'validators==0.18.2',
        'requests==2.27.1',
        'jsonschema==4.4.0',
        'pyjwt==2.3.0',
        'celery==5.2.3',
        'psycopg2-binary==2.9.3',
        'sentry-sdk[flask]==0.13.4',
        'crudini==0.9.3',
        'MicroserviceLibSender==0.2.1'
    ]
)
