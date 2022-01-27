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
        'flask==1.1.4',
        'flask_restful==0.3.7',
        'flask_sqlalchemy==2.4.4',
        'flask_redis==0.4.0',
        'flask_migrate==2.5.3',
        'flask_script==2.0.6',
        'validators==0.14.0',
        'requests==2.22.0',
        'jsonschema==3.1.1',
        'pyjwt==1.7.1',
        'celery==4.3.0',
        'psycopg2-binary==2.9.1',
        'sentry-sdk[flask]==0.13.4',
        'crudini==0.9.3'
    ]
)
