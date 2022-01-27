"""Just the setup file"""
from setuptools import setup

setup(
    name='naapi',
    version='0.1.7',
    packages=['naapi'],
    url='https://github.com/netactuate/naapi/',
    license='MIT',
    description='NetActuate API SDK, With both normal and asyncio packages',
    keywords='api sdk cloud python netactuate',
    author='NetActuate',
    author_email='support@netactuate.com',
    long_description='Provides a basic interface to execute public api endpoints',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['requests>=2.21.0',],
)
