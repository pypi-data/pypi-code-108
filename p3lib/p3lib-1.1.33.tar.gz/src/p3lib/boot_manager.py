#!/usr/bin/env python3

import  os
import  sys
import  platform

from    subprocess import check_call, DEVNULL, STDOUT, Popen, PIPE
from    datetime import datetime

class BootManager(object):
    """Responsible for adding and removing startup processes (python programs) when the computer boots.
       Currently supports the following platforms
       Linux"""

    LINUX_OS_NAME = "Linux"

    def __init__(self, uio=None, allowRootUser=False):
        """@brief Constructor
           @param uio A UIO instance to display user output. If unset then no output
                  is displayed to user.
           @param allowRootUser If True then allow root user to to auto start
                  programs. We do not do this by default because often a programs
                  configuration is stored in the users home path. E.G a config
                  file in ~/.<configfilename> or ~/.config/<configfolder or filename>.
                  If a program is started as root user then this config may not
                  be present in the /root folder and so when the program is started
                  it's config will not be found. If a program stores no config in
                  the home folder then this is not an issue."""
        self._uio = uio
        self._allowRootUser=allowRootUser
        self._osName = platform.system()
        self._platformBootManager = None
        if self._osName == BootManager.LINUX_OS_NAME:
            self._platformBootManager = LinuxBootManager(uio, self._allowRootUser)
        else:
            raise Exception("{} is an unsupported OS.".format(self._osName) )

    def add(self, user, argString=None, enableSyslog=False):
        """@brief Add an executable file to the processes started at boot time.
           @param exeFile The file/program to be executed. This should be an absolute path.
           @param user The user that will run the executable file.
           @param argString The argument string that the program is to be launched with.
           @param enableSyslog If True enable stdout and stderr to be sent to syslog."""
        if self._platformBootManager:
            self._platformBootManager.add(user, argString, enableSyslog)

    def remove(self):
        """@brief Remove an executable file to the processes started at boot time.
           @param exeFile The file/program to be removed. This should be an absolute path.
           @param user The Linux user that will run the executable file."""
        if self._platformBootManager:
            self._platformBootManager.remove()
            
    def getStatus(self):
        """@brief Get a status report.
           @return Lines of text indicating the status of a previously started process."""
        statusLines = []
        if self._platformBootManager:
            statusLines = self._platformBootManager.getStatusLines()
        return statusLines
        

class LinuxBootManager(object):
    """@brief Responsible for adding/removing Linux services using systemd."""

    LOG_PATH="/var/log"
    SERVICE_FOLDER = "/etc/systemd/system/"
    SYSTEM_CTL = "/bin/systemctl"

    def __init__(self, uio, allowRootUser):
        """@brief Constructor
           @param uio A UIO instance to display user output. If unset then no output is displayed to user.
           @param allowRootUser If True then allow root user to to auto start programs."""
        self._uio = uio
        self._logFile = None
        self._allowRootUser=allowRootUser

        if os.geteuid() != 0:
            self._fatalError("Please run this command with root level access.")

        self._info("OS: {}".format(platform.system()) )

        self._appName = None

    def _getInstallledStartupScript(self):
        """@brief Get the startup script full path. The startup script must be
                  named the same as the python file executed without the .py suffix.
           @return The startup script file (absolute path)."""""
        startupScript=None
        pythonFile = sys.argv[0] # The python file executed at program startup
        if pythonFile.startswith("./"):
            pythonFile=pythonFile[2:]
            
        envPaths = self._getPaths()

        # Search first for a file that does not have the .py suffix as 
        # this may be installed via a deb/rpm installation.
        exeFile=os.path.basename( pythonFile.replace(".py", "") )
        if envPaths and len(envPaths) > 0:
            for envPath in envPaths:
                _exeStartupScript = os.path.join(envPath, exeFile)
                if os.path.isfile(_exeStartupScript):
                    startupScript=_exeStartupScript
                    break 

        # If the script file has not been found then search for a file with 
        # the .py suffix.       
        if not startupScript:
            if envPaths and len(envPaths) > 0:
                for envPath in envPaths:
                    _startupScript = os.path.join(envPath, pythonFile)
                    if os.path.isfile(_startupScript):
                        startupScript=_startupScript
                        break     
                      
        if not startupScript:
            paths = self._getPaths()
            if len(paths):
                for _path in paths:
                    self._info(_path)
                self._fatalError("{} startup script not found using the PATH env var".format(pythonFile) )
            else:
                self._fatalError("No PATH env var found.")

        return startupScript

    def _getPaths(self):
        """@brief Get a list of the paths from the PATH env var.
           @return A list of paths or None if PATH env var not found."""
        pathEnvVar = os.getenv("PATH")
        envPaths = pathEnvVar.split(os.pathsep)
        return envPaths

    def _fatalError(self, msg):
        """@brief Record a fatal error.
           @param msg The message detailing the error."""
        raise Exception(msg)

    def _info(self, msg):
        """@brief Display an info level message to the user
           @param msg The message to be displayed."""
        self._log(msg)
        if self._uio:
            self._uio.info(msg)

    def _error(self, msg):
        """@brief Display an error level message to the user
           @param msg The message to be displayed."""
        self._log(msg)
        if self._uio:
            self._uio.error(msg)

    def _log(self, msg):
        """@brief Save a message to the log file.
           @param msg The message to save"""
        if self._logFile:
            timeStr = datetime.now().strftime("%d/%m/%Y-%H:%M:%S.%f")
            fd = open(self._logFile, 'a')
            fd.write("{}: {}\n".format(timeStr, msg) )
            fd.close()

    def _runLocalCmd(self, cmd):
        """@brief Run a command
           @param cmd The command to run.
           @return The return code of the external cmd."""
        self._log("Running: {}".format(cmd) )
        check_call(cmd, shell=True, stdout=DEVNULL, stderr=STDOUT)

    def _getApp(self):
        """@brief Get details of the app to run
           @return a tuple containing
                  0 = The name of the app
                  1 = The absolute path to the app to run"""
        exeFile = self._getInstallledStartupScript()
        exePath = os.path.dirname(exeFile)
        if len(exePath) == 0:
            self._fatalError("{} is invalid as executable path is undefined.".format(exeFile) )

        if not os.path.isdir(exePath):
            self._fatalError("{} path not found".format(exePath))

        appName = os.path.basename(exeFile)
        if len(appName) == 0:
            self._fatalError("No app found to execute.")

        absApp = os.path.join(exePath, appName)
        if not os.path.isfile( absApp ):
            self._fatalError("{} file not found.".format(absApp) )

        appName = appName.replace(".py", "")
        self._logFile = os.path.join(LinuxBootManager.LOG_PATH, appName)

        return (appName, absApp)

    def _getServiceFile(self, appName):
        """@brief Get the name of the service file.
           @param appName The name of the app to execute.
           @return The absolute path to the service file """
        serviceName = "{}.service".format(appName)
        serviceFile = os.path.join(LinuxBootManager.SERVICE_FOLDER, serviceName)
        return serviceFile

    def add(self, user, argString=None, enableSyslog=False):
        """@brief Add an executable file to the processes started at boot time.
                  This will also start the process. The executable file must be
                  named the same as the python file executed without the .py suffix.
           @param user The Linux user that will run the executable file.
                       This should not be root as config files will be be saved
                       to non root user paths on Linux systems and the startup
                       script should then be executed with the same username in
                       order that the same config file is used.
           @param argString The argument string that the program is to be launched with.
           @param enableSyslog If True enable stdout and stderr to be sent to syslog."""

        appName, absApp = self._getApp()

        serviceFile = self._getServiceFile(appName)

        lines = []
        lines.append("[Unit]")
        lines.append("After=network.target")
        lines.append("StartLimitIntervalSec=0")
        lines.append("")
        lines.append("[Service]")
        lines.append("Type=simple")
        lines.append("Restart=always")
        lines.append("RestartSec=1")
        if enableSyslog:
            lines.append("StandardOutput=syslog")
            lines.append("StandardError=syslog")
        else:
            lines.append("StandardOutput=null")
            lines.append("StandardError=journal")
        lines.append("User={}".format(user))

        #We add the home path env var so that config files (if stored in/under 
        # the users home dir) can be found by the prgram.
        if user and len(user) > 0:
            lines.append('Environment="HOME=/home/{}"'.format(user))
        if argString:
            lines.append("ExecStart={} {}".format(absApp, argString))
        else:
            lines.append("ExecStart={}".format(absApp))
        lines.append("")
        lines.append("[Install]")
        lines.append("WantedBy=multi-user.target")
        lines.append("")

        try:
            fd = open(serviceFile, 'w')
            fd.write( "\n".join(lines) )
            fd.close()
        except IOError:
            self._fatalError("Failed to create {}".format(serviceFile) )

        cmd = "{} daemon-reload".format(LinuxBootManager.SYSTEM_CTL)
        self._runLocalCmd(cmd)
        cmd = "{} enable {}".format(LinuxBootManager.SYSTEM_CTL, appName)
        self._info("Enabled {} on restart".format(appName))
        self._runLocalCmd(cmd)
        cmd = "{} start {}".format(LinuxBootManager.SYSTEM_CTL, appName)
        self._runLocalCmd(cmd)
        self._info("Started {}".format(appName))

    def remove(self):
        """@brief Remove the executable file to the processes started at boot time.
                  Any running processes will be stopped.  The executable file must be
                  named the same as the python file executed without the .py suffix."""
        appName, _ = self._getApp()

        serviceFile = self._getServiceFile(appName)
        if os.path.isfile(serviceFile):
            cmd = "{} disable {}".format(LinuxBootManager.SYSTEM_CTL, appName)
            self._runLocalCmd(cmd)
            self._info("Disabled {} on restart".format(appName))

            cmd = "{} stop {}".format(LinuxBootManager.SYSTEM_CTL, appName)
            self._runLocalCmd(cmd)
            self._info("Stopped {}".format(appName))

            os.remove(serviceFile)
            self._log("Removed {}".format(serviceFile))
        else:
            self._info("{} service not found".format(appName))

    def getStatusLines(self):
        """@brief Get a status report.
           @return Lines of text indicating the status of a previously started process."""
        statusLines = []
        appName, _ = self._getApp()
        cmd = "{} status {}".format(LinuxBootManager.SYSTEM_CTL, appName)
        p = Popen([LinuxBootManager.SYSTEM_CTL, 'status', appName], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate(b"input data that is passed to subprocess' stdin")
        response = output.decode() + "\n" + err.decode()
        lines = response.split("\n")
        return lines
            
            
            