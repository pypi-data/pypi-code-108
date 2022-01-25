import socket
import queue
import random
import logging
from random import randint
from threading import Lock

from .result import Result
from .job import Job
from .tcp_client_classes.job_caller import JobCaller
from .tcp_client import TcpClient


class TcpPoolClient(TcpClient):
    def __init__(self, connection_string:str, appname:str, username:str, password:str, use_ssl:bool=True, file_cache_byte_limit:int=33554432, pool_size:int=10):
        servers = []
        for serverString in connection_string.split("#"):
            serverParts = serverString.split(":")
            if len(serverParts) != 3:
                raise Exception(
                    f"Connection String invalid, server '{connection_string}' must be formatted as hostname:port:weight. For example localhost:4000:1")
            servers.append({
                "hostname": serverParts[0],
                "port": int(serverParts[1]),
                "weight": int(serverParts[2])
            })

        self.servers = servers
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self._pool_size = pool_size
        self._pool_available = queue.Queue()
        self._pool_in_use = 0
        self.lock = Lock()

    def __del__(self):
        pass

    def execute(self, job: Job) -> Result:
        job_caller = self._borrow()
        try:
            result = job_caller.execute(job)
            result.client_infos = {
                'hostname': job_caller.hostname, 'port': job_caller.port}
            self._return(job_caller)
            return result
        except ConnectionAbortedError as e:
            # fetch connection closed exceptions and try to reconnect and execute again
            logging.warning(e)
            self._invalidate(job_caller)
            return self.execute(job)

        except Exception as ex:
            self._invalidate(job_caller)
            raise ex

    def _borrow(self) -> JobCaller:
        try:
            job_caller = self._pool_available.get_nowait()
            self._pool_in_use += 1
            return job_caller
        except:
            if(self._pool_in_use >= self._pool_size):
                job_caller = self._pool_available.get()
                self._pool_in_use += 1
                return job_caller
            else:
                job_caller = self._create()
                self._pool_in_use += 1
                return job_caller

    def _invalidate(self, job_caller: JobCaller):
        self._pool_in_use -= 1
        try:
            job_caller.close()
        except:
            pass

    def _return(self, job_caller: JobCaller):
        self._pool_in_use -= 1
        self._pool_available.put(job_caller)

    def _create(self) -> JobCaller:

        self.lock.acquire()
        random.shuffle(rand_servers := [*self.servers])

        job_caller = None
        for server in rand_servers:
            try:
                job_caller = JobCaller(
                    server['hostname'], server['port'], self.use_ssl, self.file_cache_byte_limit)
            except ConnectionRefusedError as cre:
                logging.error(cre)

        if job_caller == None:
            self.lock.release()
            raise ConnectionRefusedError('No valid enaio server found')

        self.lock.release()

        session_attach_job = Job('krn.SessionAttach', Flags=0, SessionGUID='')
        session_attach_result = job_caller.execute(session_attach_job)

        session_properties_set_job = Job(
            'krn.SessionPropertiesSet',
            Flags=0,
            Properties='instname;statname;address',
            address=f'{socket.gethostbyname(socket.gethostname())}=dummy',
            instname=self.appname,
            statname=socket.gethostname()
        )
        session_properties_set_result = job_caller.execute(
            session_properties_set_job)

        session_login_job = Job(
            'krn.SessionLogin',
            Flags=0,
            UserName=self.username,
            UserPwd=TcpClient.encrypt_password(self.password)
        )
        session_login_result = job_caller.execute(session_login_job)

        if session_login_result.values['Description'] != None and session_login_result.values['Description'] != '':
            raise PermissionError(f'Login error: {session_login_result.values["Description"]}')

        return job_caller

    def __del__(self):
        try:
            for i in range(0, self._pool_available.qsize()):
                job_caller = self._pool_available.get_nowait()
                job_caller.socket.close()
        except:
            pass
