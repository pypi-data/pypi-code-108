from setuptools import setup
from setuptools import find_packages

REQUIRED_PACKAGES = [
    'pandas-gbq>=0.13.2',
    'pathlib',
    'google-cloud-datastore','google-cloud-bigquery','google-cloud-storage','tqdm','google-cloud-bigquery-storage',
    'pyarrow',
    'pandas==0.25.3'
]

setup(
    name='humailib',
    version='1.0.17',
    description='HUMAI framework package',
    url='',
    author='HUMAI',
    author_email='research@humai.nl',
    license='',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    zip_safe=False
)