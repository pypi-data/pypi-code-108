import socket
import tempfile
from typing import Optional, List

from divinegift import logger

try:
    from smb.SMBConnection import SMBConnection
    from smb.base import SharedFile
except ImportError:
    raise ImportError("pysmb isn't installed. Run: pip install -U pysmb")


class SmbClient:
    def __init__(self,
                 path: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 domain: Optional[str] = 'group.s7'):
        self.path: Optional[str] = path
        self.username: Optional[str] = username
        self.password: Optional[str] = password
        self.domain: Optional[str] = domain

        self.remote_name: Optional[str] = None
        self.service_name: Optional[str] = None
        self.share_path: Optional[str] = None

        self.conn: Optional[SMBConnection] = None

    def prepare_connection(self):
        '''
        Fill internal variables
        :return: None
        '''
        if self.path:
            path_arr = self.path.replace('\\', '/').split('/')[2:]
            self.remote_name = path_arr[0]
            self.service_name = path_arr[1]
            self.share_path = '/'.join(path_arr[2:])

    def set_path(self, path: str):
        self.path = path

    def set_credentials(self, username: str, password: str, domain='group.s7'):
        assert username, "Empty username isn't allowed"
        assert password, "Empty password isn't allowed"
        self.username = username
        self.password = password
        self.domain = domain

    def connect(self) -> SMBConnection:
        '''
        Connect to SMB
        :return: SMBConnection instance
        '''
        assert self.username, 'No username provided'
        assert self.password, 'No password provided'

        conn = SMBConnection(username=self.username,
                             password=self.password,
                             my_name=socket.gethostname(),
                             remote_name=self.remote_name,
                             domain=self.domain,
                             use_ntlm_v2=True,
                             is_direct_tcp=True)

        assert conn.connect(socket.gethostbyname(self.remote_name), 445)

        self.conn = conn
        return self.conn

    def download(self, filename, path_to='.') -> bool:
        '''
        Download file from SMB
        :param filename: filename
        :param path_to: path to store file in local system
        :return: True if file downloaded else False
        '''
        tmp_file, got_file = self.download_as_tmp(filename)
        if got_file:
            try:
                name = f'{path_to}/{filename}'
                with open(name, 'wb') as f:
                    f.write(tmp_file.read())
            except Exception as ex:
                got_file = False
            finally:
                if tmp_file is not None:
                    tmp_file.close()
        return got_file
    
    def download_as_tmp(self, filename) -> tuple[tempfile.TemporaryFile, bool]:
        '''
        Download file from SMB to temporary file
        :param filename: filename
        :return: tupe[temporary file from SMB, download success status]
        '''
        try:
            tmp_file = tempfile.TemporaryFile()
            self.conn.retrieveFile(self.service_name, f'{self.share_path}/{filename}', tmp_file)
            tmp_file.seek(0)
            return tmp_file, True
        except Exception as ex: 
            logger.log_err(f"Couldn't download file from {self.share_path}/{filename}")
            return None, False
    
    def upload(self, filename, path_from):
        '''
        Upload file to SMB
        :param filename: File name
        :param path_from: where file stored in local storage
        :return:
        '''
        try:
            name = f'{path_from}/{filename}'
            with open(name, 'rb') as f:
                b = self.conn.storeFile(self.service_name, f'{self.share_path}/{filename}', f)
        except Exception as ex:
            logger.log_err(f"Couldn't store file {self.share_path}/{filename}")
    
    def upload_tmp_file(self, filename, tmp_file):
        '''
        Upload tmp file to SMB
        :param filename: File name to save in remote storage
        :param tmp_file: temporary file to upload to SMB
        :return:
        '''
        try:
            _ = self.conn.storeFile(self.service_name, f'{self.share_path}/{filename}', tmp_file)
        except Exception as ex:
            logger.log_err(f"Couldn't store tmp file {self.share_path}/{filename}")
        
    def delete(self, filename):
        '''
        Delete file from SMB
        :param filename: File name
        :return:
        '''
        try:
            self.conn.deleteFiles(self.service_name, f'{self.share_path}/{filename}')
        except Exception as ex:
            logger.log_err(f"Couldn't delete file {self.share_path}/{filename}")

    def ls(self, subfolder=''):
        '''
        Print list of files to STDOUT
        :param subfolder: Subfolder where to look for files
        :return:
        '''
        file_list = self.get_list_files(subfolder)
        for file in file_list:
            print(file.filename)

    def get_list_files(self, additional_directory='') -> List[SharedFile]:
        '''
        Get list of files from SMB
        :param additional_directory: Subfolder where to look for files
        :return:
        '''
        try:
            file_list = self.conn.listPath(self.service_name, f'{self.share_path}/{additional_directory}')
            return [x for x in file_list if x.filename not in ('.', '..')]
        except Exception as ex:
            logger.log_err(f"Couldn't get list of files {self.share_path}/{additional_directory}")
