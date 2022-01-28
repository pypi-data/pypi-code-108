#!/usr/bin/env python
import json
import re
import subprocess
import sys
from abc import ABC

import codefast as cf

from dofast.pipe import author


class API(ABC):
    ...


class Pcloud(API):
    def __init__(self) -> None:
        self.api_url = 'https://api.pcloud.com'
        self.__token = None
        self.__vps_fileid = None

    @property
    def token(self) -> str:
        if self.__token is None:
            self.__token = author.get('PCLOUD_AUTH')
        return self.__token

    @property
    def vps_fileid(self) -> str:
        if self.__vps_fileid is None:
            self.__vps_fileid = author.get('PCLOUD_VPS_FILEID')
        return self.__vps_fileid

    def upload_to_vps(self, file_path: str):
        cmd = "curl --progress-bar --verbose -F=@'{}' '{}/uploadfile?folderid={}&filename=x.txt&auth={}' | tee /dev/null".format(
            file_path, self.api_url, self.vps_fileid, self.token)
        subprocess.call(cmd, shell=True)


def pcloud_upload_entry():
    '''upload file to pcloud'''
    Pcloud().upload_to_vps(sys.argv[1])


class FileDnContent:
    def __init__(self, file_dict, _dir) -> None:
        self._info = file_dict
        self._dir = _dir

    def __repr__(self) -> str:
        if 'size' in self._info:
            self._info['size'] = cf.fp.sizeof_fmt(self._info['size'])
        else:
            self._info['size'] = ''

        del self._info['icon']
        del self._info['urlencodedname']
        del self._info['modified']
        self._info['dir'] = self._dir
        ljustN = lambda e: e.ljust(20)
        _values = sorted(list(self._info.values()), key=len)
        return ''.join(map(ljustN, _values))


class SyncFile:
    def __init__(self) -> None:
        self.PREFIX = f'https://filedn.com/lCdtpv3siVybVynPcgXgnPm/snc'
        proxies_file = cf.io.home() + '/.config/proxies.json'
        self.proxies = None
        if cf.io.exists(proxies_file):
            self.proxies = cf.js(proxies_file)
        cf.info('proxies set to', self.proxies)

    def _get_full_url(self, filename: str) -> str:
        return f'{self.PREFIX}/{filename}'

    def sync(self) -> None:
        '''download all files from snc/'''
        for obj in self.list:
            fn = obj._info['name']
            full_url = self._get_full_url(fn)
            cf.info(f'Syncing {fn}')
            cf.net.download(full_url, name=f'/tmp/{fn}', proxies=self.proxies)

    @property
    def list(self) -> None:
        _objects = []
        bs = cf.net.get(self.PREFIX,
                        proxies=self.proxies).text.replace('\n', '')
        pat = re.compile(r'directLinkData=(.*)\;')
        links = json.loads(pat.findall(bs, re.MULTILINE)[0])
        _objects += [FileDnContent(u, 'snc') for u in links['content']]
        return _objects
