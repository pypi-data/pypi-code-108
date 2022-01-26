try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
    from pkgutil import walk_packages

    def find_packages(path='.', prefix=""):
        """Quick & dirty replacement if setuptools is not available."""
        yield prefix
        prefix = prefix + "."
        for _, name, ispkg in walk_packages(path, prefix):
            if ispkg:
                yield name

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = "Python dbt executor with custom logging and alerting that fits into your stack"

INSTALL_REQUIRES = [
    'dbt-core==1.0.*', 'datadog==0.40.1', 'python-dotenv==0.17.0',
    'pygments>=2.4.0', 'sentry-sdk==1.4.*', "prometheus-client==0.11.0"
]

TEST_REQUIRES = [
    'flake8~=3.9.2',
    'pytest~=6.2.4',
    'pytest-cov~=2.12.1',
    'yapf~=0.21.0',
    'mock~=2.0.0',
]

setup(
    name='pydbt',
    version="0.7.0",
    url='https://github.com/henriblancke/dbt-py',
    license='MIT',
    author="Henri Blancke",
    author_email="blanckehenri@gmail.com",
    description='Python dbt executor with customizable logging and alerting',
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=INSTALL_REQUIRES,
    test_requires=TEST_REQUIRES,
    extras_require={'dev': TEST_REQUIRES},
    scripts=[
        'scripts/pydbt',
    ],
)
