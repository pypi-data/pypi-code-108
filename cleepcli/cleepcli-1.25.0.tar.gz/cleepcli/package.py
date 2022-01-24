#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from .console import EndlessConsole, Console
import logging
import time
from . import config
from .check import Check
from .test import Test
from github import Github
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from zipfile import ZipFile, ZIP_DEFLATED
from tempfile import NamedTemporaryFile
import json
import copy
import hashlib

class Package():
    """
    Helper for package generation. Helps to create:
     * Cleep .deb package
     * application .zip package
    """

    GITHUB_USER = 'tangb'
    GITHUB_REPO = 'cleep'

    FRONTEND_DIR = 'frontend/'
    BACKEND_DIR = 'backend/'
    SCRIPTS_DIR = 'scripts/'
    TESTS_DIR = 'tests/'

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__endless_command_running = False
        self.__endless_command_return_code = 0
        self.http = urllib3.PoolManager(num_pools=1)

    def __compute_sha256(self, fullpath):
        """
        Compute sha256 for specified file

        Args:
            fullpath (string): fullpath

        Returns:
            string: sha256 string
        """
        sha256_hash = hashlib.sha256()
        with open(fullpath,'rb') as f:
            for byte_block in iter(lambda: f.read(4096),b''):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()

    def __console_callback(self, stdout, stderr):
        self.logger.info((stdout if stdout is not None else '') + (stderr if stderr is not None else ''))

    def __console_end_callback(self, return_code, killed):
        self.__endless_command_running = False
        self.__endless_comand_return_code = return_code

    def build_cleep(self):
        """
        Build cleep debian package
        """
        self.logger.info('Building Cleep package...')
        cmd = """
SENTRY_DSN=`printenv SENTRY_DSN`

if [ -z "$SENTRY_DSN" ]; then
    echo 
    echo "ERROR: sentry DSN not defined, please set an environment variable called SENTRY_DSN with valid data"
    echo
    exit 1
fi

# Check command result
# $1: command result (usually $?)
# $2: awaited command result
# $3: error message
checkResult() {
    if [ $1 -ne $2 ]
    then
        msg=$3
        if [[ -z "$1" ]]; then
            msg="see output log"
        fi
        echo -e "${RED}Error occured: $msg.${NOCOLOR}"
        exit 1
    fi
}

# clean all files
clean() {
    echo `pwd`
    rm -rf build
    rm -rf .pybuild
    rm -rf debian/cleep
    rm -rf debian/*debhelper*
    rm -rf ../cleep_*_armhf.*
    rm -rf tmp
}

# jump in cleep root directory
cd "%s"

# clean previous build
clean

# check python version
VERSION=`head -n 1 debian/changelog | awk '{ gsub("[\(\)]","",$2); print $2 }'`
PYTHON_VERSION=`cat cleep/__init__.py | grep $VERSION | wc -l`
if [ "$PYTHON_VERSION" -ne "1" ]
then
    echo
    echo "ERROR: python version is not the same than debian version, please update cleep/__init__.py __version__ to $VERSION"
    echo
    exit 1
fi

# generate /etc/default/cleep.conf
mkdir tmp
touch tmp/cleep.conf
echo "SENTRY_DSN=$SENTRY_DSN" >> tmp/cleep.conf

# build Cleep application
debuild -us -uc
checkResult $? 0 "Failed to build deb package"

# clean python stuff
rm -rf cleep.egg-info
rm -rf pycleep.egg-info/
rm -rf tmp/

# jump in build output
cd ".."

# collect variables
DEB=`ls -A1 cleep* | grep \.deb`
# ARCHIVE=cleep_$VERSION.deb
SHA256="cleep_"$VERSION"_armhf.sha256"
# PREINST=cleep/scripts/preinst.sh
# POSTINST=cleep/scripts/postinst.sh

# build zip archive
# rm -f cleep_*.deb
# rm -f cleep_*.sha256
# cp -a $DEB cleep.deb
# cp -a $PREINST .
# cp -a $POSTINST .
# zip $ARCHIVE cleep.deb `basename $PREINST` `basename $POSTINST`
# rm -f `basename $PREINST`
# rm -f `basename $POSTINST`
# rm -f cleep.deb
sha256sum $DEB > $SHA256
        """ % (config.REPO_DIR)
        self.__endless_command_running = True
        c = EndlessConsole(cmd, self.__console_callback, self.__console_end_callback)
        c.start()

        while self.__endless_command_running:
            time.sleep(0.25)

        self.logger.debug('Return code: %s' % self.__endless_command_return_code)
        if self.__endless_command_return_code!=0:
            return False

        return True

    def __delete_github_tag(self, tag_name, token):
        """
        Delete specified tag name (this feature is not available on PyGithub API)

        Args:
            tag_name (string): tag name to delete
            token (string): github authorization token
        """
        #curl request
        #curl -X DELETE -H "Authorization: token <token>" -H "User-Agent: PyGithub/Python" https://api.github.com/repos/tangb/cleep/git/refs/tags/<tag_name>
        try:
            headers = {
                'Authorization': 'token %s' % token,
                'USer-Agent': 'PyGithub/Python',
            }
            resp = self.http.request(
                'DELETE',
                'https://api.github.com/repos/%s/%s/git/refs/tags/%s' % (self.GITHUB_USER, self.GITHUB_REPO, tag_name),
                headers=headers,
            )
            if resp.status>=200 and resp.status<300:
                return True
            else:
                self.logger.debug('Response data: %s' % resp.data.decode('utf-8'))
                self.logger.error('Unable to delete tag [status=%s]' % resp.status)
                return False
        except:
            self.logger.exception('Error deleting tag "%s"' % tag_name)
            return False

    def publish_cleep(self, version):
        """
        Publish cleep version on github
        """
        token = os.environ['GITHUB_ACCESS_TOKEN']
        github = Github(token)
        repo = github.get_repo('%s/%s' % (self.GITHUB_USER, self.GITHUB_REPO))

        #check build existence
        archive = os.path.abspath(os.path.join(config.REPO_DIR, '..', 'cleep_%s_armhf.deb' % version))
        sha256 = os.path.abspath(os.path.join(config.REPO_DIR, '..', 'cleep_%s_armhf.sha256' % version))
        changes = os.path.abspath(os.path.join(config.REPO_DIR, '..', 'cleep_%s_armhf.changes' % version))
        if not os.path.exists(archive):
            self.logger.error('Archive file "%s" does not exist' % archive)
        if not os.path.exists(sha256):
            self.logger.error('Checksum file "%s" does not exist' % sha256)
        if not os.path.exists(changes):
            self.logger.error('Changes file "%s" does not exist' % changes)

        #get changelog
        cmd = 'sed -n "/cleep (%(version)s)/,/Checksums-Sha1:/{/cleep (%(version)s)/b;/Checksums-Sha1:/b;p}" %(changes)s | tail -n +2' % {'version': version, 'changes': changes}
        self.logger.debug('Cmd = %s' % cmd)
        c = Console()
        result = c.command(cmd)
        if result['error']:
            self.logger.error('Unable to read changelog')
        changelog = '\n'.join([line.strip() for line in result['stdout']])
        self.logger.debug('Changelog:\n%s' % changelog)

        #search existing release
        release_found = None
        releases = repo.get_releases()
        for release in releases:
            self.logger.debug('Release "%s"' % release.title)
            if release.title==version:
                self.logger.debug(' -> Release found')
                release_found = release
                break

        if release_found and (release_found.prerelease or release_found.draft):
            #due to github limitation (bug or limitation?), draft assets are not downloadable
            #so we create prerelease version instead of draft and delete it before creating it
            #again when pushing version
            self.logger.info('Deleting existing release "%s"...' % release_found.tag_name)
            try:
                release_found.delete_release()
            except:
                self.logger.exception('Error deleting existing release:')
                return False

            #delete tag
            if not self.__delete_github_tag(release_found.tag_name, token):
                return False
        
        #create release
        self.logger.info('Creating new release "%s"...' % version)
        try:
            commits = repo.get_commits()
            release_found = repo.create_git_release(
                tag='v%s' % version,
                name=version,
                message=changelog,
                draft=False,
                prerelease=True,
            )
        except:
            self.logger.exception('Error occured creating new release:')
            return False

        #upload assets
        try:
            self.logger.info('Uploading asset "%s"...' % archive)
            release_found.upload_asset(archive)
            self.logger.info('Uploading asset "%s"...' % sha256)
            release_found.upload_asset(sha256)
        except:
            self.logger.exception('Error uploading assets:')
            return False

        return True

        #TODO code for draft release removed for problem downloading draft assets
        #if not release_found:
        #    #create release
        #    self.logger.info('Creating new release "%s"...' % version)
        #    try:
        #        commits = repo.get_commits()
        #        release_found = repo.create_git_release(
        #            tag='v%s' % version,
        #            name=version,
        #            message=changelog,
        #            draft=True,
        #            prerelease=False,
        #        )
        #    except:
        #        self.logger.exception('Error occured creating new release:')
        #        return False

        #else:
        #    #only update draft release !
        #    if not release_found.draft:
        #        self.logger.error('Existing release "%s" is not draft. Please create new release' % version)

        #    #update release data
        #    try:
        #        self.logger.info('Updating existing release "%s"...' % version)
        #        release_found.update_release(
        #            name=version,
        #            message=changelog,
        #            draft=True,
        #            prerelease=False,
        #        )

        #        #delete all assets
        #        self.logger.info('Deleting all existing release assets...')
        #        for asset in release_found.get_assets():
        #            asset.delete_asset()
        #    except:
        #        self.logger.exception('Error occured creating new release:')
        #        return False

    def build_module(self, module_name, ci=False):
        """
        Build module package

        Args:
            module_name (string): module name
            ci (bool): flag for CI (enable tests execution)

        Returns:
            dict: package informations::

            {
                package (string): package fullpath
                sha256 (string): package sha256
                confidence (float): code confidence indicator (based on unit test results)
                quality (float): code quality indicator (based on linter result)
            }

        """
        module_archive = None

        # collect data
        check = Check()
        data_backend = check.check_backend(module_name)
        if len(data_backend['errors']) > 0:
            raise Exception('Error in backend. Fix it before packaging application: %s' % data_backend['errors'])
        data_frontend = check.check_frontend(module_name)
        if len(data_frontend['errors']) > 0:
            raise Exception('Error in frontend. Fix it before packaging application: %s' % data_frontend['errors'])
        data_scripts = check.check_scripts(module_name)
        if len(data_scripts['errors']) > 0:
            raise Exception('Error in scripts. Fix it before packaging application: %s' % data_scripts['errors'])
        data_tests = check.check_tests(module_name)
        if len(data_tests['errors']) > 0:
            raise Exception('Error in tests. Fix it before packaging application: %s' % data_tests['errors'])
        data_changelog = check.check_changelog(module_name)
        logging.debug('Changelog: %s' % data_changelog)
        if data_changelog['version'] != data_backend['metadata']['version']:
            raise Exception('Changelog does not seems to have been updated (no version "%s" found)' % data_backend['metadata']['version'])
        if data_changelog['unreleased']:
            raise Exception('Changelog has UNRELEASED flag enabled, please remove it before publishing')
        data_code_quality = check.check_code_quality(module_name)
        if len(data_code_quality['errors']) > 0:
            raise Exception('Error in code quality. Fix it before packaging application: %s' % data_code_quality['errors'])
        if data_code_quality['score'] < 7.0:
            raise Exception('Code quality for app "%s" is too low to be packaged (%s). Please improve it to be greater than 7.0' % (module_name, data_code_quality['score']))

        data_test = {
            'score': 0.0
        }
        if ci:
            # execute tests
            test = Test()
            if not test.module_test(module_name):
                raise Exception('Test execution failed for "%s". Please fix it.' % module_name)
            data_test = test.module_test_coverage(module_name, as_json=True)

        # build module description file (module.json)
        fdesc = NamedTemporaryFile(delete=False, encoding='utf-8', mode='w')
        module_json = fdesc.name
        metadata = copy.deepcopy(data_backend['metadata'])
        metadata['icon'] = data_frontend['icon']
        metadata['quality'] = data_code_quality['score']
        metadata['confidence'] = data_test['score']
        metadata['changelog'] = data_changelog['changelog']
        fdesc.write(str(json.dumps(metadata, indent=4, ensure_ascii=False, sort_keys=True)))
        fdesc.close()

        # build zip archive
        fdesc = NamedTemporaryFile(delete=False)
        module_archive = fdesc.name
        self.logger.debug('Archive filepath: %s' % module_archive)
        archive = ZipFile(fdesc, 'w', ZIP_DEFLATED)

        # add frontend files
        for a_file in data_frontend['files']:
            archive.write(a_file['fullpath'], os.path.join(self.FRONTEND_DIR, 'js', 'modules', a_file['path']))

        # add backend files
        path_in = data_backend['files']['module']['fullpath']
        path_out = os.path.join(self.BACKEND_DIR, 'modules', data_backend['files']['module']['path'])
        archive.write(path_in, path_out)
        for a_file in data_backend['files']['events']:
            path_in = a_file['fullpath']
            path_out = os.path.join(self.BACKEND_DIR, 'modules', a_file['path'])
            archive.write(path_in, path_out)
        for a_file in data_backend['files']['formatters']:
            path_in = a_file['fullpath']
            path_out = os.path.join(self.BACKEND_DIR, 'modules', a_file['path'])
            archive.write(path_in, path_out)
        for a_file in data_backend['files']['drivers']:
            path_in = a_file['fullpath']
            path_out = os.path.join(self.BACKEND_DIR, 'modules', a_file['path'])
            archive.write(path_in, path_out)
        for a_file in data_backend['files']['misc']:
            path_in = a_file['fullpath']
            path_out = os.path.join(self.BACKEND_DIR, 'modules', a_file['path'])
            archive.write(path_in, path_out)

        # add tests
        for a_file in data_tests['files']:
            path_in = a_file['fullpath']
            path_out = a_file['path']
            archive.write(path_in, path_out)

        # add scripts
        for a_file in data_scripts['files']:
            path_in = a_file['fullpath']
            path_out = a_file['path']
            archive.write(path_in, path_out)

        # add module.json
        archive.write(module_json, 'module.json')

        # close archive
        archive.close()
        archive_path = os.path.join(os.path.dirname(module_archive), 'cleepapp_%s_v%s.zip' % (module_name, metadata['version']))
        os.rename(module_archive, archive_path)

        # clean some stuff
        if os.path.exists(module_json):
            os.remove(module_json)

        self.logger.debug('Package for app "%s" has been built into "%s"' % (module_name, archive_path))

        return {
            'package': archive_path,
            'sha256': self.__compute_sha256(archive_path),
            'quality': metadata['quality'],
            'confidence': metadata['confidence'],
        }

