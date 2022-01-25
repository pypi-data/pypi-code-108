from setuptools import find_packages, setup

dependencies = ['matplotlib','numpy','pandas','seaborn','sklearn','scipy','sklearn']

setup(
    name='psmpy',
    packages=find_packages(include=['matplotlib','seaborn','sklearn']),
    version='0.1.3',
    description='Propensity score matching for python and graphical plots',
    author='Adrienne Kline',
    author_email='askline1@gmail.com',
    license='MIT',
    install_requires = dependencies,
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)