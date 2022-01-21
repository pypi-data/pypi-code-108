# coding: utf-8
import os
import setuptools
import nofus

with open(os.path.join(os.path.dirname(__file__), 'README.md'), "r") as fh:
    readme = fh.read()

setuptools.setup(
    name='nofus',
    packages=['nofus'],
    version=nofus.__version__,
    license='BSD 2-clause',
    description='NOFUS - Nate\'s One-File Utilities Stash',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Nate Collins',
    author_email='npcollins@gmail.com',
    url='https://github.com/natecollins/nofus-python/',
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
