import sys
import os
from setuptools import setup
from setuptools.command.install import install


# confite version
VERSION = "1.0.1"


def readme():
    """print long description"""
    with open('README.md') as f:
        return f.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setup(
    name='confite',
    version='1.0.1',
    description='A simple and tiny class to easily manage configurations',
    author='HackyDojo',
    author_email='info@subvertic.com',
    packages=[
        'confite'
    ],
    classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
        ],
    cmdclass={'verify': VerifyVersionCommand}
)