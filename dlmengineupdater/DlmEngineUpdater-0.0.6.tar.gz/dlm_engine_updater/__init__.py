import argparse
import configparser
import subprocess
import logging
import os
import random
import socket
import stat
import sys
import time
from logging.handlers import TimedRotatingFileHandler

from pep3143daemon import PidFile
import requests


def main():
    parser = argparse.ArgumentParser(description="DLM Updater Updater")

    parser.add_argument("--cfg", dest="cfg", action="store",
                        default="/etc/dlm_engine_updater/config.ini",
                        help="Full path to configuration")

    parser.add_argument("--after_reboot", dest="rbt", action="store_true",
                        default=False,
                        help="has to be used from init systems, to indicated that the script was called while booting.")

    parsed_args = parser.parse_args()

    instance = DlmEngineUpdater(
        cfg=parsed_args.cfg,
        rbt=parsed_args.rbt,
    )
    instance.work()


class DlmEngineLock(object):
    def __init__(self, log, lock_name, ca, secret, secret_id, endpoint, wait, wait_max):
        self._ca = ca
        self._secret = secret
        self._secret_id = secret_id
        self._endpoint = endpoint
        self._lock_name = lock_name
        self._wait = wait
        self._wait_max = wait_max
        self.log = log

    @property
    def ca(self):
        return self._ca

    @property
    def secret(self):
        return self._secret

    @property
    def secret_id(self):
        return self._secret_id

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def lock_name(self):
        return self._lock_name

    @property
    def wait(self):
        return self._wait

    @property
    def wait_max(self):
        return self._wait_max

    @property
    def lock_url(self):
        return "{0}locks/{1}".format(self._endpoint, self.lock_name)

    def acquire(self):
        self.log.debug("waiting is set to {0}".format(self.wait))
        self.log.debug("max wait time is set to {0}".format(self.wait_max))
        if self.wait:
            _waited = 0
            while True:
                if self._acquire():
                    self.log.error("blarg")
                    return
                else:
                    if _waited > self.wait_max:
                        self.log.error("exceeded max wait time, quiting")
                        sys.exit(1)
                    _sleep = random.randint(10, 60)
                    _waited += _sleep + 2
                    self.log.error("sleeping {0} seconds".format(_sleep))
                    time.sleep(_sleep)
        else:
            if not self._acquire():
                self.log.error("quiting")
                sys.exit(1)

    def _acquire(self):
        self.log.info("trying to acquire: {0}".format(self.lock_url))
        resp = requests.post(
            json={
                "data": {
                    "acquired_by": socket.getfqdn()
                }
            },
            headers={
                'x-id': self.secret_id,
                'x-secret': self.secret
            },
            timeout=2.0,
            url=self.lock_url,
            verify=self.ca
        )
        self.log.debug("http status_code is: {0}".format(resp.status_code))
        self.log.debug("http_response is {0}".format(resp.json()))
        if resp.status_code == 201:
            self.log.info("success acquiring lock")
            return True
        else:
            self.log.error("could not acquire lock: {0}".format(resp.json()))
            return False

    def release(self):
        self.log.info("trying to release: {0}".format(self.lock_url))
        retries = 10
        while retries > 0:
            try:
                resp = requests.delete(
                    json={
                        "data": {
                            "acquired_by": socket.getfqdn()
                        }
                    },
                    headers={
                        'x-id': self.secret_id,
                        'x-secret': self.secret
                    },
                    timeout=2.0,
                    url=self.lock_url,
                    verify=self.ca
                )
                self.log.debug("http status_code is: {0}".format(resp.status_code))
                self.log.debug("http_response is {0}".format(resp.json()))
                if resp.status_code == 200:
                    self.log.info("success releasing lock")
                    return
                else:
                    self.log.error("could not release lock: {0}".format(resp.json()))
                    sys.exit(1)
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout
            ) as err:
                self.log.error("connection error, retrying: {0}".format(err))
                retries -= 1
                time.sleep(5)
        self.log.fatal("could not release lock")
        sys.exit(1)


class DlmEngineUpdater(object):
    def __init__(self, cfg, rbt):
        self._config_file = cfg
        self._config = configparser.ConfigParser()
        self._config_dict = None
        self._rbt = rbt
        self.log = logging.getLogger('application')
        self.config.read_file(open(self._config_file))
        self._logging()
        self._lock = PidFile(self.config.get('main', 'lock'))
        self._dlm_lock = DlmEngineLock(
            log=self.log,
            ca=self.config.get('main', 'ca', fallback=None),
            endpoint=self.config.get('main', 'endpoint'),
            secret=self.config.get('main', 'secret'),
            secret_id=self.config.get('main', 'secret_id'),
            lock_name=self.config.get('main', 'lock_name'),
            wait=self.config.getboolean('main', 'wait', fallback=False),
            wait_max=self.config.getint('main', 'wait_max', fallback=3600),
        )
        self._dlm_lock_aquired = False

    @property
    def config(self):
        return self._config

    @property
    def dlm_lock(self):
        return self._dlm_lock

    @property
    def dlm_lock_acquired(self):
        return self._dlm_lock_aquired

    @dlm_lock_acquired.setter
    def dlm_lock_acquired(self, value):
        self._dlm_lock_aquired = value

    @property
    def lock(self):
        return self._lock

    @property
    def rbt(self):
        return self._rbt

    def _logging(self):
        logfmt = logging.Formatter('%(asctime)sUTC - %(levelname)s - %(threadName)s - %(message)s')
        logfmt.converter = time.gmtime
        handlers = []
        aap_level = self.config.get('main', 'log_level')
        log = self.config.get('main', 'log')
        retention = self.config.getint('main', 'log_retention')
        handlers.append(TimedRotatingFileHandler(log, 'd', 1, retention))

        for handler in handlers:
            handler.setFormatter(logfmt)
            self.log.addHandler(handler)
        self.log.setLevel(aap_level)
        self.log.debug("logger is up")

    def execute_shell(self, args):
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in p.stdout:
            self.log.info(line.rstrip())
        p.stdout.close()
        return p.wait()

    @property
    def task(self):
        try:
            with open(self.config.get('main', 'state'), 'r') as state:
                return state.readline().rstrip("\n")
        except FileNotFoundError:
            return 'needs_update'

    @task.deleter
    def task(self):
        try:
            os.remove(self.config.get('main', 'state'))
        except OSError as err:
            self.log.error("could not remove state file: {0}".format(err))

    @task.setter
    def task(self, task):
        self.log.info("setting task to {0}".format(task))
        try:
            with open(self.config.get('main', 'state'), 'w') as state:
                state.write("{0}\n".format(task))
        except OSError as err:
            self.log.fatal("could not set state: {0}".format(err))
            sys.exit(1)

    def check_rbt(self):
        if self.rbt:
            if self.task != 'post_update':
                self.log.info("reboot was not triggered by dlm_engine_updater, exiting")
                sys.exit(0)
            else:
                self.log.info("reboot was triggered by dlm_engine_updater, picking up remaining tasks")

    def dlm_lock_get(self):
        self.dlm_lock.acquire()
        self.dlm_lock_acquired = True
        self.do_ext_notify(
            phase='main',
            script='none',
            return_code=0
        )
        self.task = "pre_update"

    def dlm_lock_release(self):
        self.log.info("releasing lock")
        self.dlm_lock.release()
        self.dlm_lock_acquired = False
        self.do_ext_notify(
            phase='main',
            script='none',
            return_code=0,
            updater_running=False
        )
        del self.task
        sys.exit(0)

    def do_ext_notify(self, phase, script, return_code, updater_running=True):
        files = self.get_scripts('ext_notify.d')
        for _file in files:
            self.log.info("running ext notify script: {0}".format(_file))
            self.execute_shell([
                _file,
                self.dlm_lock.lock_name,
                str(self._dlm_lock_aquired),
                str(updater_running),
                phase,
                script,
                str(return_code)
            ])

    def get_scripts(self, path):
        _path = self.config.get('main', path)
        files = list()
        candidates = os.listdir(_path)
        candidates.sort()
        for _file in candidates:
            _file = os.path.join(_path, _file)
            self.log.debug("found the file: {0}".format(_file))
            if not os.path.isfile(_file):
                continue
            if not os.stat(_file).st_uid == 0:
                self.log.warning("file not owned by root")
                continue
            if os.stat(_file).st_mode & stat.S_IXUSR != 64:
                self.log.warning("file not executable by root")
                continue
            if os.stat(_file).st_mode & stat.S_IWOTH == 2:
                self.log.warning("file group writeable")
                continue
            if os.stat(_file).st_mode & stat.S_IWGRP == 16:
                self.log.warning("file world writeable")
                continue
            files.append(_file)
        return files

    def needs_update(self):
        update = False
        self.log.info("checking if updates are available")
        files = self.get_scripts('needs_update.d')
        for _file in files:
            self.log.info("running: {0}".format(_file))
            return_code = self.execute_shell([_file])
            if return_code != 0:
                self.log.info("updates are available")
                update = True
            self.do_ext_notify(
                phase='needs_update',
                script=_file,
                return_code=return_code
            )
            self.log.info("running: {0} done".format(_file))
        if update:
            self.task = "lock_get"
        else:
            self.log.info("no updates available")
            self.do_ext_notify(
                phase='main',
                script='none',
                return_code=0,
                updater_running=False
            )
            sys.exit(0)

    def update(self):
        self.log.info("running_update scripts")
        files = self.get_scripts('update.d')
        for _file in files:
            self.log.info("running: {0}".format(_file))
            return_code = self.execute_shell([_file])
            if return_code != 0:
                self.log.info("script failed, stopping, keeping lock")
                sys.exit(1)
            self.do_ext_notify(
                phase='update',
                script=_file,
                return_code=return_code
            )
            self.log.info("running: {0} done".format(_file))
        self.task = "needs_reboot"

    def post_update(self):
        self.log.info("running post_update scripts")
        self.dlm_lock_acquired = True
        files = self.get_scripts('post_update.d')
        for _file in files:
            self.log.info("running: {0}".format(_file))
            return_code = self.execute_shell([_file])
            if return_code != 0:
                self.log.info("script failed, stopping, keeping lock")
                sys.exit(1)
            self.do_ext_notify(
                phase='post_update',
                script=_file,
                return_code=return_code
            )
            self.log.info("running: {0} done".format(_file))
        self.task = "lock_release"

    def pre_update(self):
        self.log.info("running pre_update scripts")
        files = self.get_scripts('pre_update.d')
        for _file in files:
            self.log.info("running: {0}".format(_file))
            return_code = self.execute_shell([_file])
            if return_code != 0:
                self.log.info("script failed, stopping, keeping lock")
                sys.exit(1)
            self.do_ext_notify(
                phase='pre_update',
                script=_file,
                return_code=return_code
            )
            self.log.info("running: {0} done".format(_file))
        self.task = "update"

    def reboot(self):
        self.log.info("rebooting")
        self.task = "post_update"
        sys.exit(self.execute_shell([self.config.get('main', 'reboot_cmd')]))

    def needs_reboot(self):
        self.log.info("running needs reboot scripts")
        reboot = True
        files = self.get_scripts('needs_reboot.d')
        for _file in files:
            self.log.info("running: {0}".format(_file))
            return_code = self.execute_shell([_file])
            if return_code != 0:
                self.log.info("running: {0} done".format(_file))
                self.do_ext_notify(
                    phase='needs_reboot',
                    script=_file,
                    return_code=return_code
                )
                reboot = True
                break
            else:
                reboot = False
            self.log.info("running: {0} done".format(_file))
        if reboot:
            self.task = "reboot"
        else:
            self.task = "post_update"

    def work(self):
        self.lock.acquire()
        self.check_rbt()
        while True:
            task = self.task
            if task == "needs_update":
                self.needs_update()
            elif task == "lock_get":
                self.dlm_lock_get()
            elif task == "lock_release":
                self.dlm_lock_release()
            elif task == "pre_update":
                self.pre_update()
            elif task == "update":
                self.update()
            elif task == "needs_reboot":
                self.needs_reboot()
            elif task == "reboot":
                self.reboot()
            elif task == "post_update":
                self.post_update()
            else:
                self.log.fatal("found garbage in status file: {0}".format(self.task))
                del self.task
                sys.exit(1)
