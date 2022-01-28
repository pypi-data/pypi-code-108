import re
from setuptools import find_packages, setup


# Load the README and make modifications for unsupported sphinx commands.
with open('README.rst') as fp:
    long_description = fp.read()
long_description = long_description \
    .replace('.. doctest::', '.. code-block:: python') \
    .replace(':math:', ':code:')
long_description = re.sub(r'(\.\. automodule:: .*?$)|(\.\. toctree::)|(\.\. plot::)', r':code:`\1`',
                          long_description, flags=re.MULTILINE)


# Load the version number
try:
    with open('VERSION') as fp:
        version = fp.read().strip()
except FileNotFoundError:
    version = 'dev'


setup(
    name='pytest-bootstrap',
    packages=find_packages(),
    version=version,
    install_requires=[
        'numpy',
    ],
    extras_require={
        'tests': [
            'flake8',
            'pytest',
            'pytest-cov',
            'scipy',
            'twine',
        ],
        'docs': [
            'matplotlib',
            'sphinx',
        ]
    },
    classifiers=[
        'Framework :: Pytest',
    ],
    long_description_content_type="text/x-rst",
    long_description=long_description,
)
