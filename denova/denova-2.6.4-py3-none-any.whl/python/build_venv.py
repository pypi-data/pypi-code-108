'''
    Build virtualenv for one of our websites.

    Copyright 2013-2022 DeNova
    Last modified: 2022-01-10

    This file is open source, licensed under GPLv3 <http://www.gnu.org/licenses/>.
'''

from abc import ABCMeta, abstractmethod
import os
import sys
from subprocess import CalledProcessError
from traceback import format_exc

from denova.os.command import run
from denova.python.log import Log
from denova.python.ve import venv


class BuildVenv(metaclass=ABCMeta):
    ''' Build the virtualenv for a site.

        Each site should inherit from this abstract class with details about their environment.
    '''

    VIRTUAL_SUBDIR = 'virtualenv3'

    PROJECTS_DIR = os.path.realpath(os.path.join(os.path.abspath(os.path.dirname(__file__).replace('\\','/')), '..', '..'))

    def __init__(self):
        self.log = Log()

    def build(self):

        os.chdir(self.parent_dirname())
        self.init_virtualenv()

        if self.virtualenv_dir_exists():
            self.log(f'building virtual environment in {self.parent_dirname()}')
            os.chdir(self.virtualenv_dir())

            # activate the virtualenv
            with venv(dirname=self.virtualenv_dir()):

                # set up a link to the python lib for simplier config
                dirname = None
                entries = os.scandir(os.path.join(self.virtualenv_dir(), 'lib'))
                for entry in entries:
                    if entry.name.startswith('python3'):
                        dirname = entry.name
                        break
                if dirname is None:
                    dirname = 'python3.9'

                os.chdir('lib')
                run('ln', '-s', dirname, 'python')

                self.report('   installing requirements')
                with open(self.get_requirements()) as f:
                    for line in f.readlines():
                        if line.strip():
                            app = line.strip()
                            self.report(f'     {app}')
                            try:
                                run('pip3', 'install', app)
                            except CalledProcessError as cpe:
                                self.log(format_exc())
                                if cpe.stdout: self.log(f'stdout: {cpe.stdout}')
                                if cpe.stderr: self.log(f'stderr: {cpe.stderr}')
                                sys.exit(
                                  f'{cpe.stderr}. For more details see {self.log.pathname}')

            self.log('   linking packages')
            self.link_packages(os.path.join(self.virtualenv_dir(), 'lib', 'python', 'site-packages'))

            self.finish_build()
            self.log('   virtual environment built')
        else:
            self.log(f'!!!Error: Unable to create {self.virtualenv_dir()}')

    @abstractmethod
    def parent_dirname(self):
        ''' Directory where virtualenv will be created. '''

    @abstractmethod
    def get_requirements(self):
        ''' Return the full path to the virtualenv requirements. '''

    @abstractmethod
    def link_packages(self, site_packages_dir):
        ''' Link packages to the site-packages directory. '''

    @abstractmethod
    def virtualenv_dir(self):
        ''' Returns the full path to the virtualenv directory. '''

    def virtual_subdir(self):

        return self.VIRTUAL_SUBDIR

    def init_virtualenv(self):
        '''
            Initialize the virtualenv.

            Overwrite this function if you want
            special switches used when running virtualenv.
        '''

        if os.path.exists(self.virtual_subdir()):
            run('rm', '-fr', self.virtual_subdir())
        if os.path.exists('/usr/bin/python3.9'):
            python_pgm = 'python3.9'
        elif os.path.exists('/usr/bin/python3.5'):
            python_pgm = 'python3.5'
        else:
            entries = os.scandir('/usr/bin')
            for entry in entries:
                if entry.name.startswith('python3'):
                    python_pgm = entry.name
                    break
        run('virtualenv', '-p', f'/usr/bin/{python_pgm}', self.virtual_subdir())

    def virtualenv_dir_exists(self):
        ''' Return True if the virtualenv directory does exist. '''

        return os.path.exists(self.virtualenv_dir())

    def finish_build(self):
        ''' Overwrite if there are any final steps necessary to create the build.'''
        # do not remove the follow pass; when we strip comments, we need the pass
        pass

    def report(self, message):
        ''' Show and log the message. '''

        print(message)
        self.log(message)
