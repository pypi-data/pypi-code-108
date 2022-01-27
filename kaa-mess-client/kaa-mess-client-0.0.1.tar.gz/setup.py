from setuptools import setup, find_packages

setup(
    name='kaa-mess-client',
    version='0.0.1',
    description='messanger_client',
    author='KAA',
    author_email='kaa@gmail.com',
    packages=find_packages(),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
)
