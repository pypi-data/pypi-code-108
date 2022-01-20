# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

readme = ''

setup(
    description='蓝鲸API网关',
    long_description=readme,
    name='bkapi-bk-apigateway',
    version='1.0.5',
    python_requires='!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*,<4.0,>=2.7',
    author='blueking',
    license='Apach License 2.0',
    packages=find_packages(),
    namespace_packages=find_packages(exclude=["*.*"]),
    package_dir={"": "."},
    package_data={"bkapi.bk_apigateway": ["py.typed", "*.pyi"]},
    install_requires=[
        'bkapi-client-core>=1.0.2,<2.0.0',
    ],
    extras_require={
        'django': ['bkapi-client-core[django]>=1.0.2,<2.0.0'],
    },
)
