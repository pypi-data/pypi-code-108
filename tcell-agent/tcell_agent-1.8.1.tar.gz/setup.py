from setuptools import find_packages

from tcell_agent.version import VERSION

try:
    from setuptools import setup  # noqa
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tcell_agent',
    version=VERSION,
    description='tCell Python Agent',
    url='https://www.rapid7.com/products/tcell/',
    author='Rapid7',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='Free-to-use, proprietary software.',
    install_requires=["future"],
    tests_require=[
        "Django<2",
        "Flask",
        "future",
        "gunicorn",
        "mock",
        "pytest<5",
    ],
    scripts=['tcell_agent/bin/tcell_agent'],
    packages=find_packages() + ['tcell_agent/pythonpath'],
    package_data={
        'tcell_agent.rust': ['libtcellagent.so', 'libtcellagent-alpine.so', 'libtcellagent.dylib', 'libtcellagent-x64.dll']
    }
)
