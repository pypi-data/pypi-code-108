#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import zipfile
import os
import glob
import re
import requests
import time
from . import config
from .console import Console
from .check import Check
import subprocess

class Ci():
    """
    Continuous Integration helpers
    """

    EXTRACT_DIR = '/root/extract'
    CLEEP_COMMAND_URL = 'http://127.0.0.1/command'
    CLEEP_CONFIG_URL = 'http://127.0.0.1/config'

    def __init__(self):
        """
        Constructor
        """
        self.logger = logging.getLogger(self.__class__.__name__)

    def mod_install_source(self, package_path):
        """
        Install module package (zip archive) sources

        Args:
            package_path (string): package path

        Raises:
            Exception if error occured
        """
        # init
        (_, module_name, module_version) = os.path.basename(package_path).split('_')
        module_version = module_version.replace('.zip', '')[1:]
        self.logger.debug('Installing application %s[%s]' % (module_name, module_version))

        # perform some checkings
        if not module_version:
            raise Exception('Invalid package filename')
        if not re.match('\d+\.\d+\.\d+', module_version):
            raise Exception('Invalid package filename')
        console = Console()
        resp = console.command('file --keep-going --mime-type "%s"' % package_path)
        if resp['returncode'] != 0:
            raise Exception('Unable to check file validity')
        filetype = resp['stdout'][0].split(': ')[1].strip()
        self.logger.debug('Filetype=%s' % filetype)
        if filetype != 'application/zip\\012- application/octet-stream':
            raise Exception('Invalid application package file')
        
        # unzip content
        self.logger.debug('Extracting archive "%s" to "%s"' % (package_path, self.EXTRACT_DIR))
        with zipfile.ZipFile(package_path, 'r') as package:
            package.extractall(self.EXTRACT_DIR)

        # check structure
        if not os.path.exists(os.path.join(self.EXTRACT_DIR, 'backend/modules/%s' % module_name)):
            raise Exception('Invalid package structure')
        if not os.path.exists(os.path.join(self.EXTRACT_DIR, 'module.json')):
            raise Exception('Invalid package structure')

        # execute preinst script
        preinst_path = os.path.join(self.EXTRACT_DIR, 'scripts', 'preinst.sh')
        self.logger.debug('preinst.sh path "%s" exists? %s' % (preinst_path, os.path.exists(preinst_path)))
        if os.path.exists(preinst_path):
            self.logger.info('Executing "%s" preinst script' % preinst_path)
            resp = console.command('cd "%(path)s" && chmod +x "%(script)s" && "%(script)s"' % {
                'path': os.path.join(self.EXTRACT_DIR, 'scripts'),
                'script': preinst_path,
            }, 900)
            self.logger.debug('Resp: %s' % resp)
            if resp['returncode'] != 0:
                raise Exception('Preinst.sh script failed (killed=%s): %s' % (resp['killed'], resp['stderr']))

        # install sources
        self.logger.info('Installing source files')
        os.makedirs(os.path.join(config.MODULES_SRC, module_name), exist_ok=True)
        for filepath in glob.glob(self.EXTRACT_DIR + '/**/*.*', recursive=True):
            if filepath.startswith(os.path.join(self.EXTRACT_DIR, 'frontend')):
                dest = filepath.replace(os.path.join(self.EXTRACT_DIR, 'frontend/js/modules/%s' % module_name), os.path.join(config.MODULES_SRC, module_name, 'frontend'))
                self.logger.debug(' -> frontend: %s' % dest)
            elif filepath.startswith(os.path.join(self.EXTRACT_DIR, 'backend')):
                dest = filepath.replace(os.path.join(self.EXTRACT_DIR, 'backend/modules/%s' % module_name), os.path.join(config.MODULES_SRC, module_name, 'backend'))
                self.logger.debug(' -> backend: %s' % dest)
            elif filepath.startswith(os.path.join(self.EXTRACT_DIR, 'tests')):
                dest = filepath.replace(os.path.join(self.EXTRACT_DIR, 'tests'), os.path.join(config.MODULES_SRC, module_name, 'tests'))
                self.logger.debug(' -> tests: %s' % dest)
            elif filepath.startswith(os.path.join(self.EXTRACT_DIR, 'scripts')):
                dest = filepath.replace(os.path.join(self.EXTRACT_DIR, 'scripts'), os.path.join(config.MODULES_SRC, module_name, 'scripts'))
                self.logger.debug(' -> scripts: %s' % dest)
            else:
                dest = filepath.replace(self.EXTRACT_DIR, os.path.join(config.MODULES_SRC, module_name))
                self.logger.debug(' -> other: %s' % dest)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            os.rename(filepath, dest)
        os.system('cleep-cli modsync --module=%s' % module_name)

        # execute postinst script
        postinst_path = os.path.join(config.MODULES_SRC, module_name, 'scripts', 'postinst.sh')
        self.logger.debug('postinst.sh path "%s" exists? %s' % (postinst_path, os.path.exists(postinst_path)))
        if os.path.exists(postinst_path):
            self.logger.info('Executing "%s" postinst script' % postinst_path)
            resp = console.command('cd "%(path)s" && chmod +x "%(script)s" && "%(script)s"' % {
                'path': os.path.join(self.EXTRACT_DIR, 'scripts'),
                'script': postinst_path
            }, 900)
            self.logger.debug('Resp: %s' % resp)
            if resp['returncode'] != 0:
                raise Exception('Postinst.sh script failed (killed=%s): %s || %s' % (resp['killed'], resp['stdout'], resp['stderr']))

        # install tests python requirements
        tests_requirements_path = os.path.join(config.MODULES_SRC, module_name, 'tests', 'requirements.txt')
        if os.path.exists(tests_requirements_path):
            self.logger.info('Install tests python dependencies')
            resp = console.command('python3 -m pip install --trusted-host pypi.org -r "%s"' % tests_requirements_path, 900)
            self.logger.debug('Resp: %s' % resp)
            if resp['returncode'] != 0:
                raise Exception('Error installing tests python dependencies (killed=%s): %s' % (resp['killed'], resp['stderr']))

        try:
            # start cleep (non blocking)
            self.logger.info('Starting Cleep...')
            cleep_proc = subprocess.Popen(['cleep', '--noro'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(15)
            self.logger.info('Done')

            # make sure to have latest modules.json version
            self.logger.info('Updating applications list in Cleep')
            resp = requests.post(self.CLEEP_COMMAND_URL, json={
                'command': 'check_modules_updates',
                'to': 'update',
            })
            resp.raise_for_status()
            resp_json = resp.json()
            if resp_json['error']:
                raise Exception('Check_modules_updates command failed: %s' % resp_json)

            # install module in cleep (it will also install deps)
            self.logger.info('Installing "%s" application in Cleep' % module_name)
            resp = requests.post(self.CLEEP_COMMAND_URL, json={
                'command': 'install_module',
                'to': 'update',
                'params': {
                    'module_name': module_name,
                }
            })
            resp.raise_for_status()
            resp_json = resp.json()
            if resp_json['error']:
                raise Exception('Install_module command failed: %s' % resp_json)

            # wait until end of installation
            self.logger.info('Waiting end of application installation')
            while True:
                time.sleep(1.0)
                resp = requests.post(self.CLEEP_COMMAND_URL, json={
                    'command': 'get_modules_updates',
                    'to': 'update'
                })
                resp.raise_for_status()
                resp_json = resp.json()
                if resp_json['error']:
                    raise Exception('Get_modules_updates command failed')
                module_updates = resp_json['data'].get(module_name)
                self.logger.debug('Updates: %s' % module_updates)
                if not module_updates:
                    raise Exception('No "%s" application info in updates' % module_name)
                if module_updates['processing'] == False:
                    if module_updates['update']['failed']:
                        raise Exception('Application "%s" installation failed' % module_name)
                    break

            # restart cleep
            self.logger.info('Restarting cleep...')
            cleep_proc.kill()
            cleep_proc = subprocess.Popen(['cleep', '--noro'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(15)
            self.logger.info('Done')

            # check module is installed and running
            self.logger.info('Checking application is installed')
            resp = requests.post(self.CLEEP_CONFIG_URL)
            resp.raise_for_status()
            resp_json = resp.json()
            module_config = resp_json['modules'].get(module_name)
            if not module_config or not module_config.get('started'):
                self.logger.error('Found application config: %s' % module_config)
                raise Exception('Application "%s" installation failed' % module_name)
            self.logger.info('Application and its dependencies installed successfully')

        finally:
            if cleep_proc:
                cleep_proc.kill()

    def mod_check(self, module_name):
        """
        Perform some checkings (see check.py file) for continuous integration

        Args:
            module_name (string): module name

        Raises:
            Exception if error occured
        """
        check = Check()

        check.check_backend(module_name)
        check.check_frontend(module_name)
        check.check_scripts(module_name)
        check.check_tests(module_name)

