
from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python :: 3'
]

setup(
    name='kinimlearn',
    version='0.0.6',
    description='Custom Decision Tree',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='http://pypi.python.org/pypi/PackageName/',
    author='Mithun Kini',
    author_email='kinimithun@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='decision tree',
    packages=find_packages(),
    install_requires=['numpy','pandas']
)