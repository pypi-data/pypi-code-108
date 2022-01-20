import setuptools
from setuptools import setup

setup(
    name='easyDataverse',
    version='0.2.8',
    author='Jan Range',
    author_email='jan.range@simtech.uni-stuttgart.de',
    license='MIT License',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['api-generator=easyDataverse.api_generator:main']
    },
    install_requires=[
        'pydantic',
        'jinja2',
        'pydataverse',
        'pandas',
        'datamodel_code_generator',
        'pyaml',
        'coloredlogs',
        'xmltodict'
    ]
)
