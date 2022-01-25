import io
import os

from setuptools import setup

here = os.path.dirname(__file__)

with open(os.path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='SOLIDserverRest',
    version='2.3.3',
    author='Gregory CUGAT / Alex Chauvin',
    url='https://gitlab.com/efficientip/solidserverrest',
    description='The SOLIDserverRest is a library to drive EfficientIP API',
    long_description_content_type="text/markdown",
    long_description=long_description,
    author_email='gregory.cugat@efficientip.com, ach@efficientip.com',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    install_requires=['requests~=2.27',
                      'PySocks~=1.7',
                      'urllib3~=1.26',
                      'idna~=3.3',
                      'chardet~=4.0',
                      'pyopenssl~=21.0',
                      'packaging~=21.3'],
    license='BSD 2',
    packages=['SOLIDserverRest', 'SOLIDserverRest.adv'],
    zip_safe=False,
    python_requires=">=3.6",
    py_modules=['check_python_versions'],
    entry_points={
        'console_scripts': [
            'check-python-versions = check_python_versions:main',
        ], }
)
