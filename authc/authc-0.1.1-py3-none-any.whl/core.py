import base64
import json
import subprocess
import sys
import threading
import time
from typing import Dict

import codefast as cf
from codefast.patterns.singleton import SingletonMeta


class Bins(object):
    LINUX: str = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tLzExN3YyL3N0dWZmL21hc3Rlci8yMDIxL2Jpbi9sYXV0aAo='
    MACOS: str = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tLzExN3YyL3N0dWZmL21hc3Rlci8yMDIxL2Jpbi9kYXV0aAo='


class Authentication(metaclass=SingletonMeta):
    """ Authentication with binary.
    """
    def __init__(self) -> None:
        self._bin_path = "/tmp/authc"
        self._info = {}

    @property
    def bin_path(self):
        if not cf.io.exists(self._bin_path):
            url = Bins.MACOS if sys.platform == 'darwin' else Bins.LINUX
            url = base64.urlsafe_b64decode(url).decode('utf-8').strip()
            cf.net.download(url, self._bin_path)
            subprocess.call(['chmod', '755', self._bin_path])
        return self._bin_path

    @property
    def info(self):
        if not self._info:
            self._info = self._query_accounts()
        return self._info

    def _query_accounts(self) -> Dict[str, str]:
        stdout: str = ''
        _accounts = {}
        try:
            cmd = self.bin_path + ' -a'
            stdout = cf.shell(cmd)
            _accounts = json.loads(stdout)
            _accounts = dict(sorted([(k, v) for k, v in _accounts.items()]))
        except json.decoder.JSONDecodeError as e:
            cf.error('failed to decode json {}, '.format(stdout, e))
        except Exception as e:
            cf.error('failed to query secrets: {}'.format(e))
        finally:
            return _accounts

    def register(self):
        cmd = self.bin_path + ' -r'
        try:
            print(cf.shell(cmd))
        except subprocess.CalledProcessError as e:
            pass

    def update(self):
        cmd = self.bin_path + ' -u'
        try:
            cf.shell(cmd)
        except subprocess.CalledProcessError as e:
            pass


def authc() -> Dict[str, str]:
    if len(sys.argv) > 1 and sys.argv[1] == '-r':
        cf.info('registering...')
        Authentication().register()
        cf.info('register complete')
    else:
        lst, thread_number = [], 7
        for _ in range(thread_number):
            threading.Thread(target=lambda d: d.append(Authentication().info),
                             args=(lst, ),
                             daemon=True).start()

        # Also add a thread to update local cache
        threading.Thread(target=lambda d: d.append(Authentication().update()),
                         args=(lst, ),
                         daemon=True).start()

        TIMEOUT, sleep_time = 10, 0.1
        while TIMEOUT >= 0:
            time.sleep(sleep_time)
            TIMEOUT -= sleep_time
            dct = next((e for e in lst if e), {})
            if dct:
                return dct
    return {}
