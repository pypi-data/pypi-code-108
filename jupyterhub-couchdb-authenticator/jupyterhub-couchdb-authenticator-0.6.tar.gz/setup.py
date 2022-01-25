import os
from setuptools import setup

this_directory = os.path.abspath(os.path.dirname(__file__))

metadata = {}
with open(os.path.join(this_directory, "couchdbauthenticator", "metadata.py"), encoding="utf-8") as fp:
    exec(fp.read(), metadata)

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='jupyterhub-couchdb-authenticator',
    version=metadata["__version__"],
    description='Couchdb Authenticator for JupyterHub',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/1kastner/CouchDBAuthenticator',
    author=metadata["__author__"],
    author_email=metadata["__email__"],
    license='MIT',
    packages=['couchdbauthenticator'],
    install_requires=[
        # Used to communicate with CouchDB REST API
        'requests',

        # Boilerplate of JupyterHub authenticator
        'jupyterhub',
        'tornado',
        'traitlets'
    ],
    extras_require={
        'example': [
            # Only needed to run the example JupyterHub
            'python-dotenv'
        ],
        'dev': [
            # Only needed for development
            'flake8',
            'pylint',
            'twine'
        ]
    }
)
