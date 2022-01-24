"""
    Set up the sdc_helpers package
"""
from distutils.command.sdist import sdist as _sdist

from setuptools import setup


class sdistzip(_sdist):
    """Override sdist to always produce .zip archive"""

    def initialize_options(self):
        _sdist.initialize_options(self)
        self.formats = 'zip'


setup(
    name='sdc_dp_helpers',
    packages=
    [
        'sdc_dp_helpers',
        'sdc_dp_helpers.google_analytics',
        'sdc_dp_helpers.google_search_console',
        'sdc_dp_helpers.sailthru',
        'sdc_dp_helpers.azure',
        'sdc_dp_helpers.api_utilities',
        'sdc_dp_helpers.falcon',
        'sdc_dp_helpers.pyspark',
        'sdc_dp_helpers.onesignal',
        'sdc_dp_helpers.zoho',
        'sdc_dp_helpers.google_ads',
        'sdc_dp_helpers.facebook'
    ],
    install_requires=[
        'boto3',
        'google-api-python-client',
        'httplib2',
        'oauth2client',
        'numpy',
        'pandas',
        'pyOpenSSL',
        'python-interface',
        'sailthru-client',
        'azure-storage-blob',
        'sdc-helpers==1.6.2',
        'requests',
        'zcrmsdk==2.0.10',
        'mysql',
        'mysql-connector',
        'httplib2',
        'googleads==28.0.0',
        'google-ads==13.0.0',
        'protobuf==3.17.3'
    ],
    extras_require={'pyspark': ['pyspark']},
    cmdclass={'sdist_zip': sdistzip},
    description="A module for developing data pipelines from external api\'s and on ETL like services",
    version='1.2.20',
    url='http://github.com/RingierIMU/sdc-dataPipeline-helpers',
    author='Ringier South Africa',
    author_email='tools@ringier.co.za',
    keywords=[
        'pip',
        'datapipeline',
        'helpers',
    ],
    download_url='https://github.com/RingierIMU/sdc-global-dataPipeline-helpers/archive/v0.9.0.zip'
)
