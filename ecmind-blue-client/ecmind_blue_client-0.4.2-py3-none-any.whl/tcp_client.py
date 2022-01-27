import logging
import socket
from random import randint
from typing import Optional

from .client import Client
from .job import Job
from .result import Result
from .tcp_client_classes.job_caller import JobCaller

class TcpClient(Client):
    @staticmethod
    def encrypt_password(password:str) -> str:
        if password == None or password == '':
            raise(ValueError('Password must not be empty'))
        
        create_random_char = lambda: chr(ord('0') + (randint(0, 32000) % 8))

        plen = len(password)
        nmax = 4 * plen * 2
        ioff = randint(0, 32000) % max(1, nmax - plen * 3 - 3)
        cryptid = chr(ord('A') + plen) + chr(ord('A') + ioff)
        for _ in range(0, ioff):
            cryptid += create_random_char()

        replace_in_string = lambda i, c: cryptid[:i] + c + cryptid[i + 1:]

        for i in range(0, plen):
            j = 2 + ioff + i * 3
            oct_part = ioff + ord(password[i])
            oct = f'{oct_part:03o}'
            for k in range(0, 3):
                cryptid = replace_in_string(j+k, oct[k])

        for i in range(2 + ioff + 3 * plen, nmax):
            cryptid = replace_in_string(i, create_random_char())

        try:
            cryptid.encode('ascii')
            return cryptid
        except:
            return TcpClient.encrypt_password(password)

    def __attach__(self, username:str, password:str):
            session_attach_job = Job('krn.SessionAttach', Flags=0, SessionGUID='')
            session_attach_result = self.execute(session_attach_job)
            self.session_guid = session_attach_result.values['SessionGUID']

            session_properties_set_job = Job(
                'krn.SessionPropertiesSet', 
                Flags=0, 
                Properties='instname;statname;address', 
                address=f'{socket.gethostbyname(socket.gethostname())}=dummy',
                instname=self.appname,
                statname=socket.gethostname()
            )
            session_properties_set_result = self.execute(session_properties_set_job)

            session_login_job = Job(
                'krn.SessionLogin', 
                Flags=0, 
                UserName=username, 
                UserPwd=TcpClient.encrypt_password(password)
            )
            session_login_result = self.execute(session_login_job)

            if session_login_result.values['Description'] != None and session_login_result.values['Description'] != '':
                raise RuntimeError(f'Login error: {session_login_result.values["Description"]}')


    def __init__(self, 
            hostname:str, 
            port:int, 
            appname:str, 
            username:str, 
            password:str, 
            use_ssl:bool=True, 
            file_cache_byte_limit:int=33554432, 
            auto_reconnect:bool=True
        ):
        self.hostname = hostname
        self.port = port
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self.auto_reconnect = auto_reconnect
        self._connect()

    def _connect(self):
        if hasattr(self, 'job_caller') and self.job_caller != None:
            # try to close existing job_caller 
            try:
                self.job_caller.close()
            except Exception as e:
                logging.warning(e)
            # remove job_caller reference
            self.job_caller = None
        
        self.job_caller = JobCaller(self.hostname, self.port, self.use_ssl, self.file_cache_byte_limit)
        self.__attach__(self.username, self.password)
        
    def __del__(self): 
        try:
            self.job_caller.socket.close()
        except:
            pass

    def execute(self, job:Job) -> Result:
        """Send a job to the blue server (via TCP), execute it and return the response.

        Keyword arguments:
        job -- A previously created Job() object.
        """
        
        if self.auto_reconnect:
            if self.job_caller == None:
                # try to connect if current job_caller is None
                self._connect()
            
            try:
                return self.job_caller.execute(job)
            except ConnectionAbortedError as e:
                # fetch connection closed exceptions and try to reconnect and execute again
                logging.warning(e)
                self._connect()
                return self.execute(job)
        else: 
            return self.job_caller.execute(job)

class Connection():
    def __init__(self, 
        hostname:str, 
        port:int, 
        appname:str, 
        username:str, 
        password:str, 
        use_ssl:bool=True, 
        file_cache_byte_limit:int=33554432, 
        auto_reconnect:bool=True
    ):
        self.hostname = hostname
        self.port = port
        self.appname = appname
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.file_cache_byte_limit = file_cache_byte_limit
        self.auto_reconnect = auto_reconnect

    def __enter__(self):
        self.client = TcpClient(
            hostname=self.hostname,
            port=self.port,
            appname=self.appname,
            username=self.username,
            password=self.password,
            use_ssl=self.use_ssl,
            file_cache_byte_limit=self.file_cache_byte_limit,
            auto_reconnect=self.auto_reconnect
        )
        return self.client
    
    def __exit__(self, type, value, traceback):
        self.client.__del__()