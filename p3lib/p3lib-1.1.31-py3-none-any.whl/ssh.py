#!/usr/bin/env python3

import  os
import  socket
from    paramiko import SSHClient, AutoAddPolicy, RSAKey, AuthenticationException, SFTPClient
import  logging
import  threading
import  socketserver
import  select

from    getpass import getuser, getpass

class SSHError(Exception):
    pass

# -------------------------------------------------------------------------------

class ExtendedSSHClient(SSHClient):
    """@brief The ssh client class"""

    CMD_POLL_SECONDS = 0.1

    @staticmethod
    def GetLines(bytes):
        """@brief Split the text into lines.
           @param bytes The bytes containing text to be split into lines of text.
           @return A List of lines of text."""
        text = bytes.decode('utf-8')
        lines = []
        if len(text) > 0:
            elems = text.split("\n")
            lines = ExtendedSSHClient.StripEOL(elems)
        return lines

    @staticmethod
    def StripEOL(lines):
        """@brief Strip the end of line characters from the list of lines of text.
           @param lines A list of lines of text.
           @return The same list of lines of text with EOL removed."""
        noEOLLines = []
        for l in lines:
            l = l.rstrip("\n")
            l = l.rstrip("\r")
            noEOLLines.append(l)
        return noEOLLines

    def __init__(self):
        super(ExtendedSSHClient, self).__init__()
        self.set_missing_host_key_policy(AutoAddPolicy())

    def __exec_command(self, command, bufsize=-1):
        """
        Execute a command on the SSH server.  A new L{Channel} is opened and
        the requested command is executed.  The command's input and output
        streams are returned as python C{file}-like objects representing
        stdin, stdout, and stderr.

        @param command: the command to execute
        @type command: str
        @param bufsize: interpreted the same way as by the built-in C{file()} function in python
        @type bufsize: int
        @return: the stdin, stdout, and stderr of the executing command
        @rtype: tuple(L{ChannelFile}, L{ChannelFile}, L{ChannelFile})

        @raise SSHException: if the server fails to execute the command
        """
        chan = self._transport.open_session()
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        exitStatus = chan.recv_exit_status()
        return stdin, stdout, stderr, exitStatus

    def startCmd(self, command ):
        """
        Start executing a executing a command on the SSH server.  A new L{Channel} is opened and
        the requested command is executed.

        @param command: The command to execute.
        @return The SSH channel session with the command executing in it (it is up to the caller to read data from this
                channel in a timely manner).
        @raise SSHException: if the server fails to execute the command
        """
        chan = self._transport.open_session()
        chan.exec_command(command)
        return chan

    def runCmd(self, cmd, throwError=True):
        """Run a command over an ssh session and return a tuple with the following threee elements
          0 - the return code/exit status of the command
          1 - Lines of text from stdout
          2 - lines of text from stderr

          If throwError is true and the exit status of the copmmand is not 0 then an
          SSHError will be thrown
        """
        stdin, stdout, stderr, exitStatus = self.__exec_command(cmd)
        if throwError and exitStatus != 0:
            errorText = stderr.read()
            if len(errorText) > 0:
                raise SSHError(errorText)
            raise SSHError("The cmd '%s' return the error code: %d" % (cmd, exitStatus))
        return [exitStatus, ExtendedSSHClient.GetLines(stdout.read()), ExtendedSSHClient.GetLines(stderr.read())]

class SSH(object):
    """@brief responsible for connecting an ssh connection, excuting commands."""

    PRIVATE_KEY_FILE_LIST               = ["id_rsa", "id_dsa", 'id_ecdsa']
    PUBLIC_KEY_FILE_LIST                = ["id_rsa.pub", "id_dsa.pub", 'id_ecdsa.pub']
    LOCAL_SSH_CONFIG_PATH               = os.path.join(os.path.expanduser("~"), ".ssh")
    DEFAULT_REMOTE_SSH_AUTH_KEYS_FILE   = "~/.ssh/authorized_keys"
    DROPBEAR_DIR                        = "/etc/dropbear"
    DROPBEAR_AUTH_KEYS_FILE             = "%s/authorized_keys" % (DROPBEAR_DIR)
    SSH_COPY_PROG                       = "/usr/bin/ssh-copy-id"
    SERVER_AUTHORISED_KEYS_FILE         = "~/.ssh/authorized_keys"
    DEFAULT_SSH_CONNECTION_TIMEOUT      = 20

    @staticmethod
    def GetPublicKeyFile():
        """@brief Get the public key file from the <HOME>/.ssh"""
        homeFolder = SSH.LOCAL_SSH_CONFIG_PATH
        if not os.path.isdir(homeFolder):
            username = getuser()
            if username == 'root':
                homeFolder = '/root/.ssh'
            else:
                homeFolder = '/home/%s/.ssh' % (username)

        for key in SSH.PUBLIC_KEY_FILE_LIST:
            keyFile = os.path.join(homeFolder, key)
            if os.path.isfile(keyFile):
                return keyFile

        raise SSHError("Unable to find a public key file. Please use the 'ssh-keygen -t rsa' command to generate a key pair.")

    @staticmethod
    def GetPrivateKeyFile():
        """@brief Get the private key file from the <HOME>/.ssh"""
        homeFolder = SSH.LOCAL_SSH_CONFIG_PATH
        if not os.path.isdir(homeFolder):
            username = getuser()
            if username == 'root':
                homeFolder = '/root/.ssh'
            else:
                homeFolder = '/home/%s/.ssh' % (username)

        for key in SSH.PRIVATE_KEY_FILE_LIST:
            keyFile = os.path.join(homeFolder, key)
            if os.path.isfile(keyFile):
                return keyFile

        raise SSHError("Unable to find a public key file. Please use the 'ssh-keygen -t rsa' command to generate a key pair.")

    @staticmethod
    def GetPublicKey():
        """@brief Get the public ssh key from the local machine
           @return The public key."""
        pubKeyFile = SSH.GetPublicKeyFile()

        fd = open(pubKeyFile, 'r')
        lines = fd.readlines()
        fd.close()

        if len(lines) < 1:
            raise SSHError("No public key text found in the %s file on the local computer." % (pubKeyFile))

        publicKey = lines[0]
        publicKey = publicKey.strip('\n')
        publicKey = publicKey.strip('\r')
        publicKey = publicKey.strip()
        return publicKey

    @staticmethod
    def GetSSHKeyAttributes(authKey):
        """@brief Extract the following from an ssh key and return them in a tuple.
           @return a tuple containing

           hostname
           username
           keytype
           key

           If unable to extract the above attributes then None is returned.
        """
        hostname = None

        elems = authKey.split()
        if len(elems) > 2:
            keytype = elems[0]
            key = elems[1]
            tmpElems = elems[2].split("@")
            if len(tmpElems) > 1:
                username = tmpElems[0]
                hostname = tmpElems[1]
            else:
                username = elems[2]
                hostname = "?"

        if hostname != None:
            return (hostname, username, keytype, key)
        return (None, None, None, None)

    def __init__(self, host, username, password=None, useCompression=True, port=22, uio=None, privateKeyFile = None):
        """@brief Constructor
           @param host The SSH hostname
           @param username The ssh username
           @param password The ssh password (default=None)
           @param useCompression If True then use compression on the ssh session (default=True)
           @param port The ssh port number (default = 22)
           @param uio A UIO instance (default=None)
           @param privateKeyFile The private ssh keyfile (default=None=Use default private keyfile)
           """
        self._host              = host
        self._port              = port
        self._username          = username
        self._localAddress      = None
        self.useCompression     = useCompression
        self._password          = password
        self._uio               = uio
        if privateKeyFile:
            self._privateKeyFile    = privateKeyFile
        else:
            self._privateKeyFile = SSH.GetPrivateKeyFile()

        self._sshPrivateKey = RSAKey.from_private_key_file(self._privateKeyFile)

        self._ssh = ExtendedSSHClient()
        logging.getLogger("paramiko").setLevel(logging.WARNING)
        self._ssh.set_missing_host_key_policy(AutoAddPolicy())
        self._sftp = None

    def _info(self, text):
        """@brief Present an info level message to the user.
           @param text The text to be presented to the user."""
        if self._uio:
            self._uio.info(text)

    def _warn(self, text):
        """@brief Present an warning level message to the user.
           @param text The text to be presented to the user."""
        if self._uio:
            self._uio.warn(text)

    def _connect(self, connectSFTPSession=False, timeout=DEFAULT_SSH_CONNECTION_TIMEOUT):
        """@brief Connect the ssh connection
           @param connectSFTPSession If True then just after the ssh connection
                  is built an SFT session will be built ready for file transfer.
           @param timeout The connection timeout in seconds.
           @return a ref to the SSHClient object"""
        if not self._ssh:
            self._ssh = ExtendedSSHClient()

        self._ssh.connect(self._host, username=self._username, password=self._password, port=self._port,
                          pkey=self._sshPrivateKey, timeout=timeout)
        # It can be usefull to know what local IP address was used to reach the ssh server
        self._localAddress = self._ssh.get_transport().sock.getsockname()[0]
        self._ssh.get_transport().use_compression(self.useCompression)
        if connectSFTPSession:
            self._sftp = SFTPClient.from_transport( self._ssh.get_transport() )
        return self._ssh

    def getLocalAddress(self):
        """@brief Get the local IP address of the network interface used to connect to the ssh server"""
        return self._localAddress

    def getSSHClient(self):
        """@brief return a ref to the SSHClient object"""
        return self._ssh

    def close(self):
        """@brief Close an open ssh connection."""
        if self._ssh:
            self._ssh.close()
            self._ssh = None

        if self._sftp:
            self._sftp = None

    def getTransport(self):
        """@brief Get the ssh transport object. Should only be
                  called when the ssh session is connected.
           @return The ssh transport object."""
        return self._ssh.get_transport()

    def runCmd(self, cmd, throwError = True):
        """@brief Run a command over an ssh session.
           @return A tuple with the following three elements when the command is complete.
          0 - the return code/exit status of the command
          1 - Lines of text from stdout
          2 - lines of text from stderr

          If throwError is true and the exit status of the copmmand is not 0 then an
          SSHError will be thrown
        """
        return self._ssh.runCmd(cmd, throwError=throwError)

    def startCmd(self, cmd):
        """@brief Start executing a command. This will return after starting the command and before the command has completed.
                    The following methods maybe called to interrogate the command executions
                        channel.exit_status_ready()
                        channel.recv_ready()
                            channel.channel.recv(len(channel.in_buffer))
                        channel.recv_stderr_ready()
                            channel.recv_stderr(len(channel.in_stderr_buffer))

                        When the command is complete the caller should call channel.close()
           @return A channel instance in which the command is executing.
           """
        return self._ssh.startCmd(cmd)

    def connect(self, enableAutoLoginSetup=False, connectSFTPSession=False, timeout=DEFAULT_SSH_CONNECTION_TIMEOUT):
        """@brief Connect the ssh connection
           @param enableAutoLoginSetup If True and auto login is not setup the
                  user is prompted for the password and the local ssh public key
                  is copied to the server.
           @param connectSFTPSession If True then just after the ssh connection
                  is built an SFT session will be built ready for file transfer.
           @param timeout The connection timeout in seconds.
           @return True if connected without setting up auto login. False if auto
                   login was setup for connection to succeed."""
        setupAutoLogin = False
        try:
            self._connect(connectSFTPSession=connectSFTPSession, timeout=timeout)

        except AuthenticationException:
            self._setupAutologin(timeout)
            self._connect(connectSFTPSession=connectSFTPSession, timeout=timeout)
            setupAutoLogin = True
        return setupAutoLogin

    def _setupAutologin(self, timeout=DEFAULT_SSH_CONNECTION_TIMEOUT):
        """@brief Setup autologin on the ssh server.
           @param timeout The connection timeout in seconds."""

        publicKeyFilename = "{}.pub".format(self._privateKeyFile)
        publicKeyFile = os.path.join(SSH.LOCAL_SSH_CONFIG_PATH, publicKeyFilename)
        if not os.path.isfile(publicKeyFile):
            raise SSHError(
                "{} public key file not found. Please create a public/private key pair and try again.".format(
                    publicKeyFile))

        self._warn("Auto login to the ssh server failed authentication.")
        self._info("Copying the local public ssh key to the ssh server for automatic login.")
        self._info("Please enter the ssh server ({}) password for the user: {}".format(self._host, self._username))

        self._password = self._uio.getPassword("SSH password: ")

        self._connect()

        self._ensureAutoLogin()

        self.close()

        self._info("Local public ssh key copied to the ssh server.")

    def _ensureAutoLogin(self):
        """@brief Ensure that ssh auto login is enabled."""

        localPublicKey = SSH.GetPublicKey()
        _hostname, _username, _keytype, _ = SSH.GetSSHKeyAttributes(localPublicKey)
        if _hostname == None:
            _hostname = socket.gethostname()
        if _username == None:
            _username = getpass.getuser()

        self._info("Using key: %s@%s" % (_username, _hostname))
        remoteAuthorisedKeys = self.getRemoteAuthorisedKeys()
        # Check to see if the remote authorised keys contains the local public key
        updateAuthKeys = True
        for remoteAuthorisedKeys in remoteAuthorisedKeys:
            if remoteAuthorisedKeys.find(localPublicKey) == 0:
                updateAuthKeys = False
                break

        if updateAuthKeys:
            remoteAuthKeysFile = self.updateAuthorisedKeys(localPublicKey)
            self._info("Updated the remote %s file from the local %s file." % (remoteAuthKeysFile, SSH.GetPublicKeyFile()))
        else:
            self._info("The server already has the local ssh key (%s) in its authorized_key file." % (SSH.GetPublicKeyFile()))

    def updateAuthorisedKeys(self, publicKey):
        """Update the authorised keys file on the remote ssh server with the
           public ssh key"""
        authKeysFile = self.getRemoteAuthorisedKeyFile()
        cmd = "test -d %s" % (authKeysFile)
        rc, stdoutlines, stderrlines = self.runCmd(cmd, throwError=False)
        if rc == 0:
            # If this is a dir with nothing in it, delete it and create an empty
            # authorized_keys file.
            self.runCmd("rmdir %s" % (authKeysFile))
            self.runCmd("touch %s" % (authKeysFile))

        self.runCmd("echo \"%s\" >> %s" % (publicKey, authKeysFile))
        self.runCmd("chmod 600 %s" % (authKeysFile))
        return authKeysFile

    def getRemoteAuthorisedKeys(self):
        """Get the remote authorised keys file over the ssh connection."""
        authKeysFile = self.getRemoteAuthorisedKeyFile()
        cmd = "test -f %s" % (authKeysFile)
        rc, stdoutLines, stderrLines = self.runCmd(cmd, throwError=False)
        if rc != 0:
            # Auth keys file not found, attempt to create an empty one.
            cmd = "touch %s" % (authKeysFile)
            rc, stdoutLines, stderrLines = self.runCmd(cmd, throwError=False)
            cmd = "test -f %s" % (authKeysFile)
            rc, stdoutLines, stderrLines = self.runCmd(cmd, throwError=False)
            if rc != 0:
                raise SSHError("!!! Server auth keys file not found (%s). Failed to create it." % (authKeysFile))

        rc, stdoutLines, stderrLines = self.runCmd("cat %s" % (authKeysFile), throwError=False)

        # Ensure we only return non empty lines
        authKeyLines = []
        for l in stdoutLines:
            if len(l.strip()) > 0:
                authKeyLines.append(l)
        return authKeyLines

    def getRemoteAuthorisedKeyFile(self):
        """@brief Return the remote authorised key file for the current ssh connection."""

        authKeysFile = SSH.DEFAULT_REMOTE_SSH_AUTH_KEYS_FILE

        cmd = "test -d %s" % (SSH.DROPBEAR_DIR)
        rc, stdoutLines, stderrLines = self.runCmd(cmd, throwError=False)
        if rc == 0:
            authKeysFile = SSH.DROPBEAR_AUTH_KEYS_FILE

        return authKeysFile

    def getFile(self, remoteFilePath, localFilePath ):
        """@brief Get a file from the sftp server
           @param remoteFilePath The remote file on the ssh server.
           @param localFilePath The path of the file after it's been received"""
        if self._sftp:
            self._sftp.get(remoteFilePath,localFilePath)
        else:
            raise SSHError("SFTP not connected.")

    def putFile(self, localFilePath, remoteFilePath ):
        """@brief Get a file from the sftp server
           @param localFilePath The path of the file after it's been received
           @param remoteFilePath The remote file on the ssh server."""
        if self._sftp:
            self._sftp.put(localFilePath, remoteFilePath)
        else:
            raise SSHError("SFTP not connected.")

    def getAuthKeyBackupFile(self, maxBackupFileCount=10):
        """@brief Get the name of the backup name for the authorised keys file.
           @param maxBackupFileCount The maximum number of backup files to keep.
           @return None
           - We create up to maxBackupFileCount backup files.
           - Once all the backup files have been created we always replace the oldest
             backup file.
           - The backup files have the suffix .backup1, .backup2 etc.
        """
        authKeysFile = self.getRemoteAuthorisedKeyFile()
        authKeyBackupFilePart = "%s.backup" % (authKeysFile)
        suffixNum = 1
        while True:
            authKeyBackupFileName = "%s%d" % (authKeyBackupFilePart, suffixNum)
            rc, stdoutLines, stderrLines = self.runCmd("test -f %s" % (authKeyBackupFileName), throwError=False)
            if rc != 0:
                return authKeyBackupFileName
            # If all the backup files have been created
            if suffixNum >= maxBackupFileCount:
                # List the files in creation order (oldest first)
                rc, stdoutLines, stderrLines = self.runCmd("ls -ltr %s*" % (authKeyBackupFilePart), throwError=False)
                if rc == 0:
                    if len(stdoutLines) > 0:
                        elems = stdoutLines[0].split()
                        if len(elems) > 0:
                            # Return the oldest file as the next backup filename so that we roll
                            # around the always replacing the oldest backup file.
                            backupfile = elems[len(elems) - 1]
                            return backupfile

                raise SSHError("Unable to %s to %s. Please manually remove the backup files on the ssh server." % (
                authKeysFile, authKeyBackupFilePart))

            suffixNum = suffixNum + 1

    def _getPublicKeyID(self, publicKey):
        """@brief Get the public key ID string.
           @param publicKey The ssh public key string"""
        elems = publicKey.split()
        if len(elems) == 3:
            return elems[2]
        raise SSHError("{} is an invalid public key.".format(publicKey) )

    def removeAuthKey(self, publicKey):
        """@brief Remove authorised keys from the server authorised keys file.
           @param publicKeysForRemoval A list of public keys for removal."""
        remove = False
        previousAuthKeysFile = self.getAuthKeyBackupFile()
        publicKeyID = self._getPublicKeyID(publicKey)
        self._info("Public ssh key ID: {}".format(publicKeyID))
        authKeysFile = self.getRemoteAuthorisedKeyFile()
        tmpAuthKeysFile = "%s.tmp" % (authKeysFile)
        retCode, publicKeyList, _ = self.runCmd("cat {}".format(authKeysFile), throwError=False)
        if retCode == 0:
            newAuthKeysList = []
            for publicKey in publicKeyList:
                if publicKey.find(publicKeyID) >= 0:
                    self._info("Found {} public key on ssh server.".format(publicKeyID))
                    remove = True
                else:
                    newAuthKeysList.append(publicKey)

        if remove:
            # Remove any pre existing tmp auth keys file
            self.runCmd("rm -f %s" % (tmpAuthKeysFile), throwError=False)

            # Create empty tmp auth keys file
            self.runCmd("touch %s" % (tmpAuthKeysFile))

            for newAuthKey in newAuthKeysList:
                self.runCmd("echo \"%s\" >> %s" % (newAuthKey, tmpAuthKeysFile), throwError=False)

            # Remove any pre existing previous auth keys file
            self.runCmd("rm -f %s" % (previousAuthKeysFile), throwError=False)

            # Move the current auth keys file to the old one and the tmp to the current one
            self.runCmd("mv %s %s" % (authKeysFile, previousAuthKeysFile))
            self.runCmd("mv %s %s" % (tmpAuthKeysFile, authKeysFile))
            self._info("Removed {} public key from the ssh server.".format(publicKeyID))
        else:
            self._info("{} public key not found in ssh server authorised keys file.".format(publicKeyID))

        return remove

class SSHTunnelManager(object):
    """@brief Responsible for setting up, tearing down and maintaining lists of
              SSH port forwarding and ssh reverse port forwarding connections."""

    RX_BUFFER_SIZE = 4096

    def __init__(self, uio, ssh, useCompression):
        """@brief Constructor
           @param uio  UIO instance
           @param ssh An instance of SSHClient that has previously been
                      connected to an ssh server"""
        self._uio = uio
        self._ssh = ssh
        self._useCompression = useCompression
        if not self._ssh.getTransport().is_active():
            raise SSHError("!!! The ssh connection is not connected !!!")

        self._forwardingServerList = []
        self._reverseSShDict = {}

    def startFwdSSHTunnel(self, serverPort, destHost, destPort):
        """@brief Start an ssh port forwarding tunnel. This is a non blocking method.
                  A separate thread will be started to handle data transfer over the
                  ssh forwarding connection.
           @param serverPort The TCP server port. On a port forwarding connection
                             the TCP server runs on the src end of the ssh connection.
                             This is the machine that this python code is executing on.
           @param destHost   The host address of the tunnel destination at the remote
                             end of the ssh connection.
           @param destPort   The host TCP port of the tunnel destination at the remote
                             end of the ssh connection."""
        self._uio.info("Forwarding local TCP server port (%d) to %s:%d on the remote end of the ssh connection." % (
        serverPort, destHost, destPort))
        transport = self._ssh.getTransport()

        class SubHander(ForwardingHandler):
            chain_host = destHost
            chain_port = destPort
            ssh_transport = transport
            ssh_transport.use_compression(self._useCompression)
            uo = self._uio

        forwardingServer = ForwardingServer(('', serverPort), SubHander)
        self._forwardingServerList.append(forwardingServer)
        newThread = threading.Thread(target=forwardingServer.serve_forever)
        newThread.setDaemon(True)
        newThread.start()

    def stopFwdSSHTunnel(self, serverPort):
        """@brief stop a previously started ssh port forwarding server
           @param serverPort The TCP server port which is currently accepting
                             port forwarding connections on."""
        for forwardingServer in self._forwardingServerList:
            forwardingServerPort = forwardingServer.server_address[1]
            if forwardingServerPort == serverPort:
                forwardingServer.shutdown()
                forwardingServer.server_close()
                self._uio.info("Shutdown ssh port forwarding connection using local server port %d." % (serverPort))

    def stopAllFwdSSHTunnels(self):
        """@brief Stop all previously started ssh port forwarding servers.."""
        for forwardingServer in self._forwardingServerList:
            forwardingServer.shutdown()
            forwardingServer.server_close()
            self._uio.info("Shutdown ssh port forwarding on %s." % (str(forwardingServer.server_address)))

    def startRevSSHTunnel(self, serverPort, destHost, destPort):
        """@brief Start an ssh reverse port forwarding tunnel
           @param serverPort The TCP server port. On a reverse port forwarding connection
                             the TCP server runs on the dest end of the ssh connection.
                             This is the machine at the remote end of the ssh connection.
           @param destHost   The host address of the tunnel destination at the local
                             end of the ssh connection.
           @param destPort   The host TCP port of the tunnel destination at the local
                             end of the ssh connection."""
        self._uio.info("Forwarding (reverse) Remote TCP server port (%d) to %s:%d on this end of the ssh connection." % (
        serverPort, destHost, destPort))
        # We add the None refs as the placeholders will be used later
        chan = None
        sock = None
        self._reverseSShDict[serverPort] = (destHost, destPort, chan, sock)

        self._ssh.getTransport().use_compression(self._useCompression)
        self._ssh.getTransport().request_port_forward('', serverPort, handler=self._startReverseForwardingHandler)

    def stopRevSSHTunnel(self, serverPort):
        """@brief stop a previously started reverse ssh port forwarding server
           @param serverPort The TCP server port which is currently accepting
                             port forwarding connections on."""
        if serverPort in self._reverseSShDict:
            revSSHParams = self._reverseSShDict[serverPort]
            chan = revSSHParams[2]
            sock = revSSHParams[3]

            if chan:
                chan.close()

            if sock:
                sock.close()

            self._uio.info("Shutdown reverse ssh port forwarding connection using remote server port %d." % (serverPort))

    def stopAllRevSSHTunnels(self):
        """@brief Stop all previously started reverse ssh port forwarding servers."""
        for key in list(self._reverseSShDict.keys()):
            revSSHParams = self._reverseSShDict[key]
            chan = revSSHParams[2]
            sock = revSSHParams[3]

            if chan:
                chan.close()

            if sock:
                sock.close()

            self._uio.info("Shutdown reverse ssh port forwarding connection using remote server port %d." % (key))

    def stopAllSSHTunnels(self):
        """@brief Stop all ssh tunnels."""
        self.stopAllFwdSSHTunnels()
        self.stopAllRevSSHTunnels()

    # !!! The following methods are internal and should noit be called externally.
    def _getDestination(self, serverPort):
        """@brief Get destination (address and port) for the given server port.
           @param serverPort The TCP server port on the ssh server."""
        if serverPort in self._reverseSShDict:
            revSSHParams = self._reverseSShDict[serverPort]
            return (revSSHParams[0], revSSHParams[1])

        return None

    def _startReverseForwardingHandler(self, chan, xxx_todo_changeme, xxx_todo_changeme1):
        """@brief Called when a channel is connected in order to start a handler thread fot it."""
        (origin_addr, origin_port) = xxx_todo_changeme
        (server_addr, serverPort) = xxx_todo_changeme1
        destHost, destPort = self._getDestination(serverPort)

        hThread = threading.Thread(target=self._reverseForwardingHandler, args=(chan, serverPort, destHost, destPort))
        hThread.setDaemon(True)
        hThread.start()

    def _reverseForwardingHandler(self, chan, serverPort, destHost, destPort):
        """@brief Handle a reverse ssh forwarding connection.
           @param chan A connected channel over an ssh connection.
           @param serverPort The server port (on remote ssh server) from where the reverse ssh connection originated.
           @param destHost The destination host address.
           @param destPort The destination port address."""

        sock = socket.socket()
        # Add references to the chnl and sock so that they can be closed if required
        self._reverseSShDict[serverPort] = (destHost, destPort, chan, sock)
        try:
            sock.connect((destHost, destPort))
        except Exception as e:
            self._uio.error('Forwarding (reverse) request to %s:%d failed: %r' % (destHost, destPort, e))
            return

        self._uio.info('Connected!  Reverse tunnel open %r -> %r -> %r' % (chan.origin_addr,
                                                                          chan.getpeername(), (destHost, destPort)))
        while True:
            r, w, x = select.select([sock, chan], [], [])
            if sock in r:
                data = sock.recv(SSHTunnelManager.RX_BUFFER_SIZE)
                if len(data) == 0:
                    break
                try:
                    chan.send(data)
                except:
                    break
            if chan in r:
                data = chan.recv(SSHTunnelManager.RX_BUFFER_SIZE)
                if len(data) == 0:
                    break
                try:
                    sock.send(data)
                except:
                    break
        chan.close()
        sock.close()
        self._uio.info('Tunnel closed from server port %d' % (serverPort))


class ForwardingServer(socketserver.ThreadingTCPServer):
    """@brief Server responsible for ssh port forwarding"""
    daemon_threads = True
    allow_reuse_address = True


class ForwardingHandler(socketserver.BaseRequestHandler):
    """@brief handler for ssh port forwarding connections."""

    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            self.uo.error('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                                    self.chain_port,
                                                                    repr(e)))
            return
        if chan is None:
            self.uo.error('Incoming request to %s:%d was rejected by the SSH server.' %
                          (self.chain_host, self.chain_port))
            return

        self.uo.info('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                                 chan.getpeername(),
                                                                 (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(SSHTunnelManager.RX_BUFFER_SIZE)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(SSHTunnelManager.RX_BUFFER_SIZE)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        self.uo.info('Tunnel closed from %r' % (peername,))
