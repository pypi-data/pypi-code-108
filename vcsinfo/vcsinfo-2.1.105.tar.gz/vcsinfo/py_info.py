"""
Copyright 2021 Adobe
All Rights Reserved.

NOTICE: Adobe permits you to use, modify, and distribute this file in accordance
with the terms of the Adobe license agreement accompanying it.
"""

import email.parser
import io
import logging
import os
import re

import vcsinfo


LOGGER = logging.getLogger(__name__)


class VCSPyInfo(vcsinfo.VCS):
    """Minimal class for querying Python info files"""

    VERSION_RE = re.compile(r'(?P<coarse>[.\d]*\d)\.(?P<number>\d+)(.dev(?P<modified>\d+))?')

    def __init__(self, dirname):
        vcsinfo.VCS.__init__(self)

        # Look for a specific .egg-info subdirectory which will contain more information
        # than just a PKG-INFO in dirname.
        files = os.listdir(dirname)
        contents = [ent for ent in files if ent.endswith('.egg-info')]
        if contents:
            LOGGER.debug(f'Found {contents}')
            _dirname = os.path.join(dirname, contents[0])
            LOGGER.debug(f'Picking {_dirname}')
        else:
            # Didn't find a .egg-info - stick with dirname
            _dirname = dirname
        self.detect_source_root(_dirname)
        LOGGER.debug(f'Matched {self.vcs}: {dirname}')


    def detect_source_root(self, dirname):
        '''Identify if a directory might be an .info-info directory.'''

        dirname = os.path.realpath(dirname)
        try:
            pi_path = os.path.join(dirname, 'PKG-INFO')
            LOGGER.debug(f'Reading {pi_path}')
            with io.open(pi_path, encoding='utf-8', errors='replace') as piobj:
                raw_pi = piobj.read()
            self.pkg_info = email.parser.Parser().parsestr(raw_pi)
        except (ValueError, IOError) as err:
            raise TypeError(f'Directory "{dirname}" is not an pkg_info directory: {err}') from err
        self.source_root = dirname
        sources_txt = os.path.join(dirname, 'SOURCES.txt')
        try:
            with io.open(sources_txt, encoding='utf-8', errors='replace') as st_obj:
                self.files = [line.rstrip(os.linesep) for line in st_obj.readlines()]
        except IOError as err:
            raise TypeError(f'Failed reading {sources_txt}: {err}') from err


    def _get_version(self):
        return self.pkg_info.get('Version')


    def _match_version(self):
        try:
            mobj = self._ver_mobj
        except AttributeError:
            # pylint: disable=attribute-defined-outside-init
            mobj = self._ver_mobj = re.match(self.VERSION_RE, self._get_version())
        return mobj


    @property
    def name(self):
        return self.pkg_info.get('Name')


    @property
    def branch(self):
        mobj = self._match_version()
        if mobj:
            branch = mobj.groupdict().get('coarse', '0') or '0'
        else:
            branch = '0'
        return branch


    @property
    def user(self):
        return None


    @property
    def id(self):
        mobj = self._match_version()
        if mobj:
            ids = '.'.join((
                mobj.groupdict().get('coarse', '0') or '0',
                mobj.groupdict().get('number', '0') or '0',
            ))
        else:
            ids = '0'
        return ids


    @property
    def id_short(self):
        return self.id


    @property
    def number(self):
        mobj = self._match_version()
        if mobj:
            number = mobj.groupdict().get('number', '0') or '0'
        else:
            number = '0'
        return int(number)


    def list_files(self):
        return self.files


    @property
    def modified(self):
        mobj = re.match(self.VERSION_RE, self.id)
        if mobj:
            mod = mobj.groupdict().get('modified', '0') or '0'
        else:
            mod = '0'
        return int(mod)


VCS = VCSPyInfo


# Local Variables:
# fill-column: 100
# End:
