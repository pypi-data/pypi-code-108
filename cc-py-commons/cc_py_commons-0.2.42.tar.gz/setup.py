from setuptools import setup, find_packages

setup(
    name='cc_py_commons',
    description='Common code for microservices',
    version='0.2.42',
    url='https://github.com/Cargo-Chief/py-commons',
    author='CargoChief',
    author_email='engineering@cargochief.com',
    packages=find_packages(),
    install_requires=['requests', 'googlemaps', 'marshmallow', 'dataclasses', 'boto3', 'inflection'],
    keywords=[]
    )
