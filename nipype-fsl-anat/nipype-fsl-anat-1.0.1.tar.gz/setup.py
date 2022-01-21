# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['nipype_fsl_anat']
install_requires = \
['nibabel>=3.0.0,<4.0.0', 'nipype>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'nipype-fsl-anat',
    'version': '1.0.1',
    'description': 'Nipype interface(s) wrapping the `fsl_anat` command line tool',
    'long_description': None,
    'author': 'Andrew Ross',
    'author_email': 'andrew.ross.mail@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
