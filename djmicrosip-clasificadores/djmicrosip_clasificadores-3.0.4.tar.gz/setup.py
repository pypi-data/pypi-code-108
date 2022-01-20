import os, time, compileall, sys
from setuptools import setup, find_packages
import pathlib

if "sdist" in sys.argv:
    path = os.path.abspath(os.path.dirname(__file__))+"\\djmicrosip_clasificadores\\"
    compileall.compile_dir(path, force=True)

# README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.rst').read_text(encoding='utf-8')
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djmicrosip_clasificadores',
    version='3.0.4',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='djmicrosip_clasificadores',
    long_description='Pedidos WEB',
    url='',
    author='Servicios de Ingenieria Computacional',
    author_email='desarrollo@siccomputacion.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=REQUIREMENTS,
)
