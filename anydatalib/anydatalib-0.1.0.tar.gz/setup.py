from setuptools import find_packages, setup
setup(
    name='anydatalib',
    packages=find_packages(),
    version='0.1.0',
    description='anydata library',
    author='anydata',
    license='anydata',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)