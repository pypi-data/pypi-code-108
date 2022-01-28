from setuptools import find_packages, setup, Command
import shutil
import sys
import os

import cli

long_description = open("README.md", encoding="utf8").read()
requirements = [line.strip() for line in open("requirements.txt", encoding="utf8").readlines()]


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            here = os.path.abspath(os.path.dirname(__file__))
            shutil.rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        if os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable)) != 0:
            sys.exit(-1)

        self.status('Uploading the package to pypi via Twine…')
        if os.system('twine upload dist/*') != 0:
            sys.exit(-1)

        self.status('Pushing git tags…')
        os.system('git tag v{0}'.format(cli.__version__))
        os.system('git push --tags')

        sys.exit()


setup(
    name='argparse3',
    version=str(cli.__version__),
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords='cli',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    url='https://github.com/killf/cli',
    author='killf',
    cmdclass={
        'upload': UploadCommand,
    },
    entry_points={})
