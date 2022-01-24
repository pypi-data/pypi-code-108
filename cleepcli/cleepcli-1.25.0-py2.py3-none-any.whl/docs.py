#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
from .console import EndlessConsole, Console
import logging
from . import config
import importlib
from datetime import datetime

class Docs():
    """
    Handle documentation processes
    @see https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/
    """

    GITHUB_REPO = 'git@github.com:tangb/cleep.git'
    GITHUB_DOCS_BRANCH = 'docs'
    DOCS_TEMP_PATH = '/tmp/cleep-docs'
    DOCS_ARCHIVE_NAME = 'cleep-core-docs.zip'
    DOCS_COMMIT_MESSAGE = 'API documentation update'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__endless_command_running = False
        self.__endless_command_return_code = 0
        self.__module_version = None
        self.__module_author = None

    def __console_callback(self, stdout, stderr):
        self.logger.info((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))

    def __console_end_callback(self, return_code, killed):
        self.__endless_command_running = False
        self.__endless_command_return_code = return_code

    def __get_module_data(self, module_name):
        """
        Return useful module data

        Returns:
            dict of data::

                {
                    version (string): module version
                    author (string): module author
                }

        """
        if self.__module_version:
            return {
                'version': self.__module_version,
                'author': self.__module_author
            }

        try:
            module_ = importlib.import_module('cleep.modules.%s' % (module_name))
            app_filename = getattr(module_, 'APP_FILENAME', module_name)
            del module_
            module_ = importlib.import_module('cleep.modules.%s.%s' % (module_name, app_filename))
            class_name = next((item for item in dir(module_) if item.lower() == app_filename.lower()), None)
            module_class_ = getattr(module_, class_name or '', None)
            self.__module_version = module_class_.MODULE_VERSION
            self.__module_author = module_class_.MODULE_AUTHOR

            return {
                'version': self.__module_version,
                'author': self.__module_author
            }
        except:
            self.logger.exception('Unable to get module infos. Is module valid?')
            return None

    def generate_module_docs(self, module_name, preview=False):
        """
        Generate module documentation

        Args:
            module_name (string): module name
            preview (bool): preview generated documentation as text directly on stdout
        """
        #checking module path
        path = os.path.join(config.MODULES_SRC, module_name, 'docs')
        if not os.path.exists(path):
            self.logger.error('Docs directory for module "%s" does not exist' % (module_name))
            return False

        module_data = self.__get_module_data(module_name)
        self.logger.debug('Module data: %s' % module_data)
        if module_data is None:
            return False

        today = datetime.today()

        self.logger.info('=> Generating documentation...')
        cmd = """
cd "%(DOCS_PATH)s"
/usr/bin/rm -rf "%(BUILD_DIR)s" "%(SOURCE_DIR)s"
/usr/local/bin/sphinx-apidoc -o "%(SOURCE_DIR)s/" "../backend"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "=> Building html documentation..."
/usr/local/bin/sphinx-build -M html "." "%(BUILD_DIR)s" -D project="%(MODULE_NAME_CAPITALIZED)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "=> Building singlehtml documentation..."
/usr/local/bin/sphinx-build -M singlehtml "." "%(BUILD_DIR)s" -D project="%(MODULE_NAME_CAPITALIZED)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "=> Building xml documentation..."
/usr/local/bin/sphinx-build -M xml "." "%(BUILD_DIR)s" -D project="%(MODULE_NAME_CAPITALIZED)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "=> Building text documentation..."
/usr/local/bin/sphinx-build -M text "." "%(BUILD_DIR)s" -D project="%(MODULE_NAME_CAPITALIZED)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "=> Packaging html documentation..."
/usr/bin/find "%(BUILD_DIR)s/" -type f -print0 | xargs -0 sed -i "s/backend/%(MODULE_NAME)s/g"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
/usr/bin/find "%(BUILD_DIR)s/" -type f -print0 | xargs -0 sed -i "s/Backend/%(MODULE_NAME_CAPITALIZED)s/g"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
/usr/bin/find "%(BUILD_DIR)s/" -iname \*.* | for f in $(find . -name backend*); do mv $f $(echo "$f" | sed -r 's|backend|%(MODULE_NAME)s|g'); done
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
#/bin/tar -czvf "%(MODULE_NAME)s-docs.tar.gz" "%(BUILD_DIR)s/html" --transform='s/%(BUILD_DIR)s\//\//g' && ARCHIVE=`/usr/bin/realpath "%(MODULE_NAME)s-docs.tar.gz"` && echo "ARCHIVE=$ARCHIVE"
cd "_build"; /usr/bin/zip "../%(MODULE_NAME)s-docs.zip" -r "html"; cd ..
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
/bin/cp -a "%(BUILD_DIR)s/text/source/%(MODULE_NAME)s.txt" "%(MODULE_NAME)s-docs.txt"
/bin/cp -a "%(BUILD_DIR)s/xml/source/%(MODULE_NAME)s.xml" "%(MODULE_NAME)s-docs.xml"
%(DISPLAY_TEXT)s
        """ % {
            'DOCS_PATH': path,
            'SOURCE_DIR': 'source',
            'BUILD_DIR': '_build',
            'MODULE_NAME': module_name,
            'MODULE_NAME_CAPITALIZED': module_name.capitalize(),
            'YEAR': today.year,
            'AUTHOR': module_data['author'],
            'VERSION': module_data['version'],
            'DISPLAY_TEXT': 'echo; echo; echo "========== DOC PREVIEW =========="; echo; cat "%s-docs.txt"' % module_name if preview else '',
        }

        self.logger.debug('Docs cmd: %s' % cmd)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

    def get_module_docs_archive_path(self, module_name):
        """
        Display module docs archive path if exists
        """
        #checking module path
        docs_path = os.path.join(config.MODULES_SRC, module_name, 'docs')
        if not os.path.exists(docs_path):
            self.logger.error('Docs directory for module "%s" does not exist' % (module_name))
            return False

        zip_path = os.path.join(docs_path, '%s-docs.zip' % module_name)
        if not os.path.exists(zip_path):
            self.logger.error('There is no documentation archive generated for module "%s"' % (module_name))
            return False

        self.logger.info('DOC_ARCHIVE=%s' % zip_path)
        return True

    def __get_core_data(self):
        """
        Return useful core data

        Returns:
            dict of data::

                {
                    author (string): author
                    version (string): version
                }

        """
        try:
            from cleep import __version__
            return {
                'author': 'Tanguy Bonneau',
                'version': __version__
            }
        except:
            self.logger.exception('Unable to get core infos')
            return None

    def generate_core_docs(self, publish=False):
        """
        Generate core documentation
        """
        #checking core path
        path = os.path.join(config.CORE_SRC, '../docs')
        self.logger.debug('Core docs path: %s' % path)
        if not os.path.exists(path):
            self.logger.error('Docs directory for core does not exist')
            return False

        core_data = self.__get_core_data()
        self.logger.debug('Core data: %s' % core_data)
        if core_data is None:
            return False

        today = datetime.today()

        self.logger.info('=> Generating documentation...')
        cmd = """
cd "%(DOCS_PATH)s"
# disable source generation because it is customized
# /usr/local/bin/sphinx-apidoc -o "%(SOURCE_DIR)s/" "../cleep" "../cleep/tests/**" "../cleep/modules/**"
# if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
# echo
/bin/rf -f "%(CORE)s-docs.zip"
echo "=> Building html documentation..."
/bin/rm -rf "%(BUILD_DIR)s" "%(SOURCE_DIR)s"
/usr/local/bin/sphinx-build -M html "." "%(BUILD_DIR)s" -D project="%(PROJECT)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
echo "=> Building xml documentation..."
/usr/local/bin/sphinx-build -M xml "." "%(BUILD_DIR)s" -D project="%(PROJECT)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
echo
# echo "=> Building text documentation..."
# /usr/local/bin/sphinx-build -M text "." "%(BUILD_DIR)s" -D project="%(PROJECT)s" -D copyright="%(YEAR)s %(AUTHOR)s" -D author="%(AUTHOR)s" -D version="%(VERSION)s" -D release="%(VERSION)s"
# if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
# echo
echo "=> Packaging html documentation..."
cd "_build"; /usr/bin/zip "../%(CORE)s-docs.zip" -r "html"; cd ..
if [ $? -ne 0 ]; then echo "Error occured"; exit 1; fi
# TODO /bin/cp -a "%(BUILD_DIR)s/xml/source/%(CORE)s.xml" "%(CORE)s-docs.xml"
        """ % {
            'DOCS_PATH': path,
            'SOURCE_DIR': 'source',
            'BUILD_DIR': '_build',
            'CORE': 'cleep-core',
            'PROJECT': 'Cleep core API',
            'YEAR': today.year,
            'AUTHOR': core_data['author'],
            'VERSION': core_data['version']
        }

        self.logger.debug('Docs cmd: %s' % cmd)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        # publish docs
        if publish:
            self.logger.info('=> Publishing documentation...')
            return self.publish_core_docs()

        return True

    def publish_core_docs(self):
        """
        Publish core docs to github pages
        """
        c = Console()

        # check
        docs_archive_path = os.path.join(config.REPO_DIR, 'docs/', self.DOCS_ARCHIVE_NAME)
        if not os.path.exists(docs_archive_path):
            self.logger.error('Core has no docs archive generated (%s). Please run "cleep-cli coredocs" first' % docs_archive_path)
            return False

        # clone repo
        self.logger.debug('Cloning core repository...')
        cmd = 'rm -rf "%s"; git clone -q "%s" "%s"' % (self.DOCS_TEMP_PATH, self.GITHUB_REPO, self.DOCS_TEMP_PATH)
        self.logger.debug('cmd: %s' % cmd)
        resp = c.command(cmd, 60) 
        self.logger.debug('Clone resp: %s' % resp)
        if resp['returncode'] != 0 or resp['killed']:
            self.logger.error('Error occured while cloning repository: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False
    
        # switch to branch
        self.logger.debug('Switching to %s branch' % self.GITHUB_DOCS_BRANCH)
        cmd = 'cd "%s" && git checkout "%s"' % (self.DOCS_TEMP_PATH, self.GITHUB_DOCS_BRANCH)
        self.logger.debug('cmd: %s' % cmd)
        resp = c.command(cmd, 60) 
        self.logger.debug('Switch branch resp: %s' % resp)
        if resp['returncode'] != 0 or resp['killed']:
            self.logger.error('Error occured while switching repository branch: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False

        # add docs
        self.logger.debug('Updating docs...')
        cmd = 'unzip "%s" -d "%s" && rm -rf "%s" && mv "%s" "%s"' % (
            docs_archive_path,
            self.DOCS_TEMP_PATH,
            os.path.join(self.DOCS_TEMP_PATH, 'docs'),
            os.path.join(self.DOCS_TEMP_PATH, 'html'),
            os.path.join(self.DOCS_TEMP_PATH, 'docs'),
        )
        self.logger.debug('cmd: %s' % cmd)
        resp = c.command(cmd, 60) 
        self.logger.debug('Unzip resp: %s' % resp)
        if resp['returncode'] != 0 or resp['killed']:
            self.logger.error('Error occured while unzipping core docs archive: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False

        # commit changes
        self.logger.debug('Commiting changes...')
        cmd = 'cd "%s" && git add . && git commit -m "%s" && git push' % (
            self.DOCS_TEMP_PATH,
            self.DOCS_COMMIT_MESSAGE,
        )
        self.logger.debug('cmd: %s' % cmd)
        resp = c.command(cmd, 60) 
        self.logger.debug('Commit resp: %s' % resp)
        if resp['returncode'] != 0 or resp['killed']:
            self.logger.error('Error occured while pushing changes: %s' % ('killed' if resp['killed'] else resp['stderr']))
            return False

        return True
        

