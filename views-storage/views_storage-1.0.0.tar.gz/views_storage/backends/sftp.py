from typing import Optional
from stat import S_ISDIR, S_ISREG
import os
from tempfile import NamedTemporaryFile
from cryptography import x509
import paramiko
import psycopg2
import sqlalchemy as sa
from .. import models
from . import storage_backend


class Sftp(storage_backend.StorageBackend[str, bytes]):
    """
    Sftp
    ====

    parameters:
        host (str)
        port (int)
        user (Optional[str])
        key_db_host (str)
        key_db_dbname (str)
        key_db_user (Optional[str]): Inferred if not provided = None
        key_db_sslmode (str) = "require"
        key_db_password (Optional[str]): Cert auth. if not provided
        key_db_port (int) = 5432
        folder (str):  Root folder on sftp server = "."

    Backend that stores and retrieves files via SFTP. Authentication is done
    via a database, which requires you to have a valid client certificate
    installed at ~/.postgresql.

    If key database username is not provided, the username is attempted
    inferred from the database certificate at ~/.postgresql/postgresql.crt
    """

    def __init__(self,
            host: str,
            port: int,
            user: str,
            key_db_host: str,
            key_db_dbname: str,
            key_db_user: Optional[str] = None,
            key_db_sslmode: str = "require",
            key_db_password: Optional[str] = None,
            key_db_port: int = 5432,
            folder: str = "."):

        self._keystore_connection_string = (
            f"host={key_db_host} "
            f"port={key_db_port} "
            f"dbname={key_db_dbname} "
            f"user={key_db_user if key_db_user else self.get_cert_username()} "
            f"sslmode={key_db_sslmode}"
        )

        if key_db_password:
            self._keystore_connection_string += f" password={key_db_password}"


        self._sftp_host = host
        self._sftp_port = port
        self._sftp_user = user

        self.key        = self._fetch_paramiko_key()
        self.connection = self._connect()
        self._folder    = os.path.join("",folder)

        self.setup_dir(self._folder)

    def store(self, key: str, value: bytes) -> None:
        """
        store
        =====

        parameters:
            key (str)
            value (bytes)

        Store file in remote folder, at path specified by "key".
        """
        path = self._path(key)
        with self.connection.open(path, "wb") as f:
            f.write(value)

    def retrieve(self, key: str) -> bytes:
        """
        retrieve
        ========

        paramters:
            key (str)

        returns:
            bytes

        Retrieve contents of file at path specified by "key".
        """
        path = self._path(key)
        with self.connection.open(path, "rb") as f:
            return f.read()

    def exists(self, key: str) -> bool:
        """
        exists
        ======

        parameters:
            key (str)

        Check for existence of file at "key".
        """
        key = self._path(key)
        try:
            _ = self.connection.stat(key)
            return True
        except IOError:
            return False

    def list(self, key: str = ".") -> models.Listing:
        """
        list
        ====

        parameters:
            path (str)

        returns:
            views_storage.models.Listing

        List contents of folder at "key"
        """
        folders = []
        files = []

        for entry in self.connection.listdir_attr(self._path(key)):
            mode = entry.st_mode
            if S_ISDIR(mode):
                folders.append(entry.filename)
            elif S_ISREG(mode):
                files.append(entry.filename)

        return models.Listing(folders=folders, files=files)

    def keys(self):
        """
        keys
        ====

        Show available keys (at ".")
        """
        return self.list()

    def _db_connect(self):
        return psycopg2.connect(self._keystore_connection_string)

    def _fetch_paramiko_key(self) -> paramiko.Ed25519Key:
        """
        _fetch_paramiko_key
        ===================

        returns:
            paramiko.Ed25519Key

        Connects to a certificate store on "key" server to the writing server using SSL.
        This is currently Janus, but can be migrated to any safe store solution like a vault.
        Getting a private key in this way SHOULD be safe, since we do it based on already critical SSL certs.
        If these are compromised the whole chain is compromised. If you have a better idea, however, do say.
        The user key will be rotated frequently, so is not cached.
        This key points to a very low privileged user that can only write or read from a dedicated store.
        The dedicated store is chrooted to and from the server.
        """
        cert_table = sa.Table(
            "sftp_cert",
            sa.MetaData(),
            sa.Column("sftp_cert", sa.String),
            schema="public")

        query = sa.select([cert_table.c["sftp_cert"]])

        with self._db_connect() as con:
            c = con.cursor()
            c.execute(str(query))
            cert,*_ = c.fetchone()

        with NamedTemporaryFile(dir=".", mode="w") as x:
            x.write(cert)
            x.seek(0)
            key = paramiko.Ed25519Key.from_private_key_file(x.name, password=None)
            return key

    def _connect(self) -> paramiko.SFTPClient:
        """
        _connect
        ========

        returns:
            paramiko.SFTPClient

        Initialize a connection and connect to the sftp store.
        The user and key are the dedicated user and key generated above.
        DO NOT use your views user share!
        """
        t = paramiko.Transport((self._sftp_host, self._sftp_port))
        t.connect(hostkey=None, pkey=self.key, username=self._sftp_user)
        return paramiko.SFTPClient.from_transport(t)

    @staticmethod
    def _file_name_fixer(file_name, extension):
        extension = extension.strip(" .").lower()
        file_name = file_name.strip().lower()
        ext_len = -(len(extension) + 1)
        file_name = (
            file_name
            if file_name[ext_len:] == f".{extension}"
            else file_name + "." + extension
        )
        return file_name

    def _path(self, key):
        return os.path.join(self._folder, key)

    def __del__(self):
        """
        Destruct the key and close the connection if it exists.
        :return: Nothing, it's a destructor.
        """
        self.key = None
        try:
            self.connection.close()
        except TypeError:
            pass

    @staticmethod
    def get_cert_username():
        cert_file_path = os.path.expanduser("~/.postgresql/postgresql.crt")
        try:
            assert os.path.exists(cert_file_path)
        except AssertionError:
            return None

        with open(cert_file_path) as f:
            cert = x509.load_pem_x509_certificate(f.read().encode())

        common_name = cert.subject.rfc4514_string().split(",")
        try:
            # Extract the content of the CN field from the x509 formatted string.
            views_user_name = [
                i.split("=")[1] for i in common_name if i.split("=")[0] == "CN"
            ][0]
        except IndexError:
            raise ConnectionError(
                "Something is wrong with the ViEWS Certificate. Contact ViEWS to obtain authentication!"
            )
        return views_user_name

    def _folder_exists(self, path):
        """
        exists
        ======
       
        parameters:
            path(str)

        Checks if a folder exists on the server.
        """

        try:
            prev = self.connection.getcwd()
            self.connection.chdir(path)
            self.connection.chdir(prev)
            return True
        except IOError:
            return False

    def setup_dir(self, dir: str) -> None:
        """
        _mkdir
        ======

        parameters:
            path (str)

        Used to initialize the target folder on the remote host.
        """
        existing = ""
        for path_element in dir.split("/"):
            to_make = os.path.join(existing, path_element)

            if not self._folder_exists(to_make):
                self.connection.mkdir(to_make)

            existing = to_make
