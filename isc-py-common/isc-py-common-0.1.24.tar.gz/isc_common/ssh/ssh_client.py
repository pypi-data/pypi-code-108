import logging

from isc_common import Stack

logger = logging.getLogger(__name__)


class SSH_Client:
    def __init__(self, hostname, username, password, port=22):
        import paramiko
        import os
        import socket
        import traceback

        hostkey = None
        clients = None
        busy = False

        try:
            host_keys = paramiko.util.load_host_keys(
                os.path.expanduser("~/.ssh/known_hosts")
            )
        except IOError:
            try:
                # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
                host_keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/ssh/known_hosts")
                )
            except IOError:
                logger.debug("*** Unable to open host keys file")
                host_keys = {}

        if hostname in host_keys:
            hostkeytype = host_keys[hostname].keys()[0]
            hostkey = host_keys[hostname][hostkeytype]
            # logger.debug("Using host key of type %s" % hostkeytype)
            # logger.debug("Using host key %s" % str(hostkey))

        try:
            t = paramiko.Transport((hostname, port))
            t.connect(
                # hostkey=hostkey,
                username=username,
                password=password,
                gss_host=socket.getfqdn(hostname),
                gss_auth=False,
                gss_kex=False,
            )
            self.sftp = paramiko.SFTPClient.from_transport(t)
            self.hostname = hostname
            self.username = username
            self.password = password
            self.port = port
            self.busy = False
        except Exception as e:
            logger.error("*** Caught exception: %s: %s" % (e.__class__, e))
            traceback.print_exc()
            raise e

    def __str__(self):
        return f'-p {self.port} {self.username}@{self.hostname}'

    def reconnect(self):
        import paramiko
        import socket

        t = paramiko.Transport((self.hostname, self.port))
        t.connect(
            # hostkey=hostkey,
            username=self.username,
            password=self.password,
            gss_host=socket.getfqdn(self.hostname),
            gss_auth=False,
            gss_kex=False,
        )
        self.sftp = paramiko.SFTPClient.from_transport(t)
        self.clients.push(self)
        logger.debug(f'\nReconnect: {str(self)}')

    def get(self, remotepath, localpath, callback=None):
        try:
            self.busy = True
            self.sftp.get(remotepath=remotepath, localpath=localpath, callback=callback)
        except IOError as ex:
            logger.error(f'{remotepath} {str(ex)}')

    def put(self, localpath, remotepath, callback=None, confirm=True):
        try:
            self.sftp.put(localpath=localpath, remotepath=remotepath, callback=callback, confirm=confirm)
            return None
        except Exception as ex:
            logger.error(ex)
            return ex

    def getcwd(self):
        try:
            res = self.sftp.getcwd()
            return res, True
        except Exception as ex:
            logger.error(ex)
            return None, None

    def exists(self, path):
        try:
            self.sftp.stat(path)
            return True
        except FileNotFoundError:
            return False
        except IOError:
            return False
        except OSError:
            self.reconnect()
            self.sftp.stat(path)
            return True

    def listdir(self, path):
        return self.sftp.listdir(path)

    def getsize(self, path):
        if self.exists(path=path):
            return self.sftp.stat(path).st_size
        else:
            None

    def stat(self, path):
        if self.exists(path=path):
            return self.sftp.stat(path)
        else:
            None

    def open(self, filename, mode="r", bufsize=-1):
        if self.exists(path=filename):
            self.busy = True
            return self.sftp.open(filename=filename, mode=mode, bufsize=bufsize)
        else:
            None

    def remove(self, path):
        if self.exists(path=path):
            self.sftp.remove(path=path)
        else:
            None

    def rename(self, oldpath, newpath):
        self.sftp.rename(oldpath=oldpath, newpath=newpath)

    def chmod(self, path, mode):
        if self.exists(path=path):
            self.sftp.chmod(path=path, mode=mode)
        else:
            None

    def close(self):
        self.sftp.close()


class SSH_Clients:
    max_connect = 10;

    clients = Stack()

    def client(self, client_connect):
        # logger.debug(f'request connetc: {client_connect}')
        logger.debug(f'lenght stack: {self.clients.size()}')

        if self.clients.size() > self.max_connect:
            for connect in self.clients.stack[: - self.max_connect // 2]:
                connect.close()

            self.clients.stack = self.clients.stack[: -self.max_connect // 2]
            logger.debug(f'lenght stack: {self.clients.size()}')

        # clients = list(filter(lambda x: x.busy is False, self.clients.find(lambda client: client.hostname == client_connect.get('SSH_HOST') and
        #                                                                                   client.port == client_connect.get('SSH_PORT') and
        #                                                                                   client.username == client_connect.get('SSH_USER') and
        #                                                                                   client.password == client_connect.get('SSH_PASSWORD')
        #                                                                    )))
        # if len(clients) > 0:
        #     return clients[0]
        # else:
        res = SSH_Client(
            hostname=client_connect.get('SSH_HOST'),
            username=client_connect.get('SSH_USER'),
            password=client_connect.get('SSH_PASSWORD'),
            port=client_connect.get('SSH_PORT')
        )
        res.clients = self.clients
        self.clients.push(res)
        return res

    def close(self):
        for client in self.clients:
            client.close()
