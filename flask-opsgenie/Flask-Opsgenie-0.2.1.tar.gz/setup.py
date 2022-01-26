"""
Flask-Opsgenie
---------------

An easy to use Opsgenie extension for flask. Allows user
to raise an opsgenie alert on unwanted response status code,
increased response latency and on unhandled exception thrown
by routes.
With flask-opsgenie, you will no more have to add alerting
logic to your code manually, rather all you need to do is configure
this extension with different alert conditions and attributes.
"""

from setuptools import find_packages, setup

setup(
    name="Flask-Opsgenie",
    url="https://github.com/djmgit/flask-opsgenie",
    license="",
    author="Deepjyoti Mondal",
    description="Opsgenie extension for Flask",
    download_url="https://github.com/djmgit/flask-opsgenie/archive/refs/tags/v0.2.1.tar.gz",
    long_description=__doc__,
    zip_safe=False,
    keywords = ['Alerting', 'flask', 'web', 'Reliability', 'DevOps'],
    platforms="any",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "Flask>=1.1.2"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
    ],
    version='0.2.1'
)
