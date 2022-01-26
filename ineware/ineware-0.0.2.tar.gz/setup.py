from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='ineware',
    version='0.0.2',
    description='A light weight Python library for INE API json-stat',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Roberto Gamero",
    author_email="rgameroe@alumnos.unex.es",
    url='https://bitbucket.org/rgameroe/ineware/src/master/',
    install_requires=[
        'requests>=2.25.1'
    ],
    license='MIT',
    packages=['ineware'],
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.9'
    ],
)
