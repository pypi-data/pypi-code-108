from setuptools import setup
import os

_here = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(_here, 'pyrasgo', 'version.py')) as f:
    exec(f.read(), version)

with open(os.path.join(_here, 'DESCRIPTION.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyrasgo',
    version=version['__version__'],
    description=('Alpha version of the Rasgo Python interface.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Patrick Dougherty',
    author_email='patrick@rasgoml.com',
    url='https://www.rasgoml.com/',
    license='GNU Affero General Public License v3 or later (AGPLv3+)',
    packages=['pyrasgo',
              'pyrasgo.api',
              'pyrasgo.primitives',
              'pyrasgo.schemas',
              'pyrasgo.storage',
              'pyrasgo.storage.dataframe',
              'pyrasgo.storage.datawarehouse',
              'pyrasgo.utils'],
    install_requires=[
        # Note these are duplicated in requirements.txt
        "more-itertools",
        "pandas",
        "pydantic",
        "pyyaml",
        "requests",
        "tqdm",
        "snowflake-connector-python>=2.7.1",
        "snowflake-connector-python[pandas]",
        "idna>=3.3",
        "pyarrow>=5.0.0"
    ],
    extras_require={
        "df":  [
            "shap",
            "catboost"
        ],
        "snowflake":  [
            "snowflake-connector-python>=2.7.1",
            "snowflake-connector-python[pandas]",
            "idna>=3.3",
            "pyarrow>=5.0.0"
        ],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.7'],
)
