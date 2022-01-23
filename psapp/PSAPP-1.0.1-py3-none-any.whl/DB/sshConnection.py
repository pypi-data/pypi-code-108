import os
from posixpath import dirname
import time
from paramiko import SSHClient, AutoAddPolicy, SFTPClient, Transport, RSAKey
from paramiko.py3compat import decodebytes
from stat import S_ISDIR, S_ISREG
# import asyncio, asyncssh

class SSHConnection:

    # clientConnection: SSHClient = None
    # ftpConnection: SFTPClient = None
    # transport: Transport = None

    def __init__(self, host: str, username: str, password: str, win: bool = False, port: int = 22) -> None:
        # know_host_key = "<KEY>"
        # keyObj = RSAKey(data=decodebytes(know_host_key.encode()))
        self.__clientConnection: SSHClient = SSHClient()
        self.__clientConnection.set_missing_host_key_policy(AutoAddPolicy())
        # self.__clientConnection.get_host_keys().add(hostname=host, keytype="ssh-rsa", key=keyObj)
        self.__clientConnection.connect(hostname=host, username=str(username), password=str(password), port=port, look_for_keys=False)
        # self.__transport: Transport = None
        self.__host: str = host
        self.__username: str = username
        self.__password: str = password
        self.__win: bool = win
        self.__port: int = port
        self.__transport: Transport = Transport((host, port))
        self.__transport.connect(username=str(username), password=str(password))
        self.__ftpConnection: SFTPClient = SFTPClient.from_transport(self.__transport)

    # # @staticmethod
    # def createSSHConnection(self, host, username, password, port: int = 22) -> SSHClient:
    #     self.__clientConnection = SSHClient()
    #     # SSHConnection.clientConnection.load_host_keys(f"{environ['HOME']}/.ssh/known_hosts")
    #     # SSHConnection.clientConnection.load_system_host_keys()
    #     # SSHConnection.clientConnection.set_missing_host_key_policy(AutoAddPolicy())
    #     # SSHConnection.clientConnection.connect(hostname=host, username=str(username), password=str(password), port=port)
    #     self.__clientConnection.connect(hostname=host, username=str(username), password=str(password), port=port)
    #     return self.__clientConnection

    # @staticmethod
    def createDirectory(self, destPath: str, dirName: str):
        print(self.__ftpConnection.getcwd())
        print(destPath)
        print(dirName)
        # exit()
        self.__ftpConnection.chdir(destPath)
        self.__ftpConnection.mkdir(dirName)

    # @staticmethod
    def transferFile(self, sourcePath: str, destPath: str, win: bool):
        if (win):
            path = destPath.split('\\')
            self.__ftpConnection.chdir("\\".join(path[:-1]))
            # if ("TOOL_DUMPS" in self.__ftpConnection.listdir()):
            #     self.__ftpConnection.chdir("TOOL_DUMPS")
            # else:
            #     self.__ftpConnection.mkdir("TOOL_DUMPS")
            #     self.__ftpConnection.chdir("TOOL_DUMPS")
            if (path[-1] in self.__ftpConnection.listdir()):
                self.__ftpConnection.chdir(path[-1])
            else:
                self.__ftpConnection.mkdir(path[-1])
                self.__ftpConnection.chdir(path[-1])
            if (os.path.basename(sourcePath) in self.__ftpConnection.listdir()):
                if (self.__ftpConnection.stat(os.path.join(self.__ftpConnection.getcwd(), os.path.basename(sourcePath))).st_size != os.stat(sourcePath).st_size):
                    self.__ftpConnection.put(sourcePath, os.path.join(self.__ftpConnection.getcwd(), os.path.basename(sourcePath)))
            else:
                self.__ftpConnection.put(sourcePath, os.path.join(self.__ftpConnection.getcwd(), os.path.basename(sourcePath)))
        else:
            path = destPath.split('/')
            self.__ftpConnection.chdir("/".join(path[:-1]))
            if (path[-1] in self.__ftpConnection.listdir()):
                self.__ftpConnection.chdir(path[-1])
            else:
                self.__ftpConnection.mkdir(path[-1])
                self.__ftpConnection.chdir(path[-1])
            if (os.path.basename(sourcePath) in self.__ftpConnection.listdir()):
                if (self.__ftpConnection.stat(os.path.join(self.__ftpConnection.getcwd(), os.path.basename(sourcePath))).st_size != os.stat(sourcePath).st_size):
                    self.__ftpConnection.put(sourcePath, os.path.join(self.__ftpConnection.getcwd(), os.path.basename(sourcePath)))
            else:
                self.__ftpConnection.put(sourcePath, os.path.join(self.__ftpConnection.getcwd(), os.path.basename(sourcePath)))
    
    def transferDirectory(self, sourcePath: str, destPath: str, win: bool = None):
        if (win):
            print(sourcePath)
            print(destPath)
            pathSplit = destPath.split("\\")
            print(self.__ftpConnection.getcwd())
            print("\\".join(pathSplit[:-1]))
            self.__ftpConnection.chdir(None)
            self.__ftpConnection.chdir("\\".join(pathSplit[:-1]))
            print(self.__ftpConnection.getcwd())
            if (pathSplit[-1] not in self.__ftpConnection.listdir()):
                self.__ftpConnection.mkdir(pathSplit[-1])
        else:
            pathSplit = destPath.split("/")
            self.__ftpConnection.chdir(None)
            self.__ftpConnection.chdir("/".join(pathSplit[:-1]))
            if (pathSplit[-1] not in self.__ftpConnection.listdir()):
                self.__ftpConnection.mkdir(pathSplit[-1])
        
        for item in os.listdir(sourcePath):
            if (os.path.isfile(os.path.join(sourcePath, item))):
                print(sourcePath)
                print(destPath)
                print(item)
                print("test1")
                self.__ftpConnection.chdir(None)
                self.__ftpConnection.chdir(destPath)
                print("test2")
                self.__ftpConnection.put(os.path.join(sourcePath, item), os.path.join(self.__ftpConnection.getcwd(), item))
                print("test3")
            else:
                print("test4")
                print(destPath)
                print(item)
                self.__ftpConnection.chdir(None)
                self.createDirectory(destPath=destPath, dirName=item)
                # if (win):
                #     self.createDirectory(destPath=destPath.split("\\")[-1], dirName=item)
                # else:
                #     self.createDirectory(destPath=destPath, dirName=item)
                print(destPath)
                print(item)
                # exit()
                # self.createDirectory(destPath=destPath, dirName=item)
                print("test5")
                # if (win):
                #     self.__ftpConnection.chdir(destPath.split("\\")[-1])
                # else:
                #     self.__ftpConnection.chdir(destPath)
                # self.__ftpConnection.chdir(destPath)
                print("test6")
                self.transferDirectory(os.path.join(sourcePath, item), os.path.join(self.__ftpConnection.getcwd(), item))
                print("test7")
        
    def changeDirectoryMode(self, directoryPath: str):
        win = self.checkIfWindows()
        tempPath = directoryPath
        for item in self.__ftpConnection.listdir_attr(directoryPath):
            if (win):
                remotePath = directoryPath + "\\" + item.filename
            else:
                remotePath = directoryPath + "/" + item.filename
            mode = item.st_mode
            if (S_ISDIR(mode)):
                print(f"{remotePath} is a directory!")
                self.changeDirectoryMode(remotePath)
            elif (S_ISREG(mode)):
                self.__ftpConnection.chmod(remotePath, 0o777)
        # exit()
        # for root, dirs, files in os.walk(directoryPath):  
        #     for dir in dirs:  
        #         os.chmod(os.path.join(root, dir), 0o777)
        #     for file in files:
        #         os.chmod(os.path.join(root, file), 0o777)
        # for item in self.__ftpConnection.listdir():
        #     if (os.path.isfile(os.path.join(directoryPath, item))):
        #         print(directoryPath)
        #         self.__ftpConnection.chdir(directoryPath)
        #         self.__ftpConnection.chmod(os.path.join(self.__ftpConnection.getcwd(), item), 777)
        #     else:# (os.path.isdir(os.path.join(self.__ftpConnection.getcwd(), item))):
        #         # self.__ftpConnection.chdir(directoryPath)
        #         if (len(self.__ftpConnection.listdir()) == 0):
        #             break
        #         print(directoryPath)
        #         self.changeDirectoryMode(os.path.join(self.__ftpConnection.getcwd(), item))
    
    def runTomcats(self, tomcatPath: str, JAVA_HOME: None):
        self.__ftpConnection.chdir(None)
        self.__ftpConnection.chdir(tomcatPath)
        self.changeDirectoryMode(tomcatPath)
        if (self.checkIfWindows()):
            self.__ftpConnection.chdir(None)
            self.__ftpConnection.chdir(tomcatPath)
            self.__ftpConnection.chdir("bin")
            if (JAVA_HOME != None):
                stdin, stdout, stderr = self.__clientConnection.exec_command(f"set JAVA_HOME={JAVA_HOME} && set PATH=%PATH%;%JAVA_HOME%\\bin && {self.__ftpConnection.getcwd()}\\startup.bat")
            else:
                stdin, stdout, stderr = self.__clientConnection.exec_command(f"{self.__ftpConnection.getcwd()}\\startup.bat")
        else:
            self.__ftpConnection.chdir(None)
            self.__ftpConnection.chdir(tomcatPath)
            self.__ftpConnection.chdir("bin")
            if (JAVA_HOME != None):
                stdin, stdout, stderr = self.__clientConnection.exec_command(f"export JAVA_HOME={JAVA_HOME} ; export PATH=$PATH:$JAVA_HOME/bin ; sh {self.__ftpConnection.getcwd()}/startup.sh")
            else:
                stdin, stdout, stderr = self.__clientConnection.exec_command(f"sh {self.__ftpConnection.getcwd()}/startup.sh")
        return stdin, stdout, stderr

    # @staticmethod
    def getEnvVariable(self, win: bool):
        # self.__createSSHConnection(host, username, password)
        if (win):
            stdin, stdout, stderr = self.__clientConnection.exec_command("echo %UserProfile%")
        else:
            stdin, stdout, stderr = self.__clientConnection.exec_command("echo $HOME")
        return stdout.read().decode("utf-8").strip()

    def addEnvVariable(self, varialeName: str, value: str, win: bool):
        if (win):
            self.__clientConnection.exec_command()

    # @staticmethod
    def checkIfWindows(self) -> bool:
        # self.__createSSHConnection(host, username, password)
        stdin, stdout, stderr = self.__clientConnection.exec_command("ver")
        if (stderr.read().decode("utf-8") == '' and "windows" in stdout.read().decode("utf-8").strip().lower()):
            return True
        else:
            return False
    
    def execCommand(self, command: str):
        stdin, stdout, stderr = self.__clientConnection.exec_command(command=command)
        return stdin, stdout, stderr

    # @staticmethod
    def closeSSHConnection(self, stdin = None, stdout = None, stderr = None):
        stdin.close()
        stderr.close()
        stdout.close()
        self.__clientConnection.close()