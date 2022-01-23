import subprocess
from shutil import which
from sys import stderr, stdout
from PSAPP.DB.dbConnection import DBConnection
from PSAPP.Logging.loggingModule import Logging
from PSAPP.DB.sshConnection import SSHConnection, SSHClient

class ImportDumps:

    def __init__(self, dbConnection: DBConnection, mainLogger: Logging = None) -> None:
        self.__dbConnection: DBConnection = dbConnection
        self.__dumpPath: str = ''

    def importDump(self, dbIP: str, dbPort: int, dbSID: str, dumpPath: str, schemas: list, userPass: str, user: str = "system", dataPump: bool = True, content: str =  "ALL", tableExistAction: str =  "APPEND", logFile: str = "logs.log", ignore: str = 'y', grants: str = 'n', parFilePath: str = None, remapSchemas: dict = None, directory: str = "", version: float = -1, osUsername: str = "", osPassword: str = "") -> list:
        statementElements: list = ["impdp", f"{user}/{userPass}@{dbIP}:{dbPort}/{dbSID}", f"dumpfile={dumpPath}", f"schemas={','.join(schemas)}", f"table_exists_action={tableExistAction}", f"logfile={logFile}", f"content={content}", f"grants={grants}", f"ignore={ignore}"]
        if (remapSchemas != None):
            for tempSchema in remapSchemas.keys():
                tempRemapSchemas = tempSchema + ":" + remapSchemas[tempSchema]
                statementElements.append(f"remap_schema={tempRemapSchemas}")
        if (parFilePath != None):
            statementElements.append(f"parfile={parFilePath}")
        if (directory != ""):
            statementElements.append(f"directory={directory}")
        if (version != -1):
            statementElements.append(f"version={version}")
        if (self.__checkIfSSH()):
            print(" ".join(statementElements))
            importProcess = subprocess.Popen(statementElements, stdout=subprocess.PIPE, encoding="utf8")
            while True:
                output = importProcess.stdout.readline()
                if (output == '' and importProcess.poll() is not None):
                    break
                if (output):
                    print(output.strip())
            rc = importProcess.poll()
        else:
            print(dbIP)
            clientConnection: SSHConnection = SSHConnection(dbIP, osUsername, osPassword)
            # clientConnection: SSHClient = SSHConnection.createSSHConnection(dbIP, osUsername, osPassword)
            print(" ".join(statementElements))
            stdin, stdout, stderr = clientConnection.execCommand(" ".join(statementElements))
            print(stdout.read().decode("utf-8"))
            print(stderr.read().decode("utf-8"))
            clientConnection.closeSSHConnection(stdin, stdout, stderr)
        return statementElements

    def __checkIfSSH(self) -> bool:
        if (which("impdp") != None and which("imp") != None):
            print("test")
            return True
        else:
            print("Not true")
            return False