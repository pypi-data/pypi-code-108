from setuptools import setup, find_packages

setup(
    name='kaa-mess-server',
    version='0.0.2',
    description='messanger_server',
    author='KAA',
    author_email='kaa@gmail.com',
    packages=find_packages(),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
    scripts=['server/server_run']
)
