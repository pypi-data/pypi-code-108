#!/usr/bin/env python3

import sys
import os
import re
import traceback
from   threading import Lock
from   socket import socket, AF_INET, SOCK_DGRAM
from   getpass import getpass, getuser
from   time import strftime, localtime
from   datetime import datetime
        
from   p3lib.netif import NetIF

class UIO(object):
    """@brief responsible for user output and input via stdout/stdin"""

    DISPLAY_ATTR_RESET          =   0
    DISPLAY_ATTR_BRIGHT         =   1
    DISPLAY_ATTR_DIM            =   2
    DISPLAY_ATTR_UNDERSCORE     =   4
    DISPLAY_ATTR_BLINK          =   5
    DISPLAY_ATTR_REVERSE        =   7
    DISPLAY_ATTR_HIDDEN         =   8

    DISPLAY_ATTR_FG_BLACK       =   30
    DISPLAY_ATTR_FG_RED         =   31
    DISPLAY_ATTR_FG_GREEN       =   32
    DISPLAY_ATTR_FG_YELLOW      =   33
    DISPLAY_ATTR_FG_BLUE        =   34
    DISPLAY_ATTR_FG_MAGNETA     =   35
    DISPLAY_ATTR_FG_CYAN        =   36
    DISPLAY_ATTR_FG_WHITE       =   37

    DISPLAY_ATTR_BG_BLACK       =   40
    DISPLAY_ATTR_BG_RED         =   41
    DISPLAY_ATTR_BG_GREEN       =   42
    DISPLAY_ATTR_BG_YELLOW      =   43
    DISPLAY_ATTR_BG_BLUE        =   44
    DISPLAY_ATTR_BG_MAGNETA     =   45
    DISPLAY_ATTR_BG_CYAN        =   46
    DISPLAY_ATTR_BG_WHITE       =   47

    DISPLAY_RESET_ESCAPE_SEQ    = "\x1b[0m"

    PROG_BAR_LENGTH             =   40

    USER_LOG_SYM_LINK           = "log.txt"
    DEBUG_LOG_SYM_LINK          = "debug_log.txt"
  
    @staticmethod
    def GetInfoEscapeSeq():
        """@return the info level ANSI escape sequence."""
        return "\x1b[{:01d};{:02d}m".format(UIO.DISPLAY_ATTR_FG_GREEN, UIO.DISPLAY_ATTR_BRIGHT)

    @staticmethod
    def GetDebugEscapeSeq():
        """@return the debug level ANSI escape sequence."""
        return "\x1b[{:01d};{:02d};{:02d}m".format(UIO.DISPLAY_ATTR_FG_BLACK, UIO.DISPLAY_ATTR_BG_WHITE, UIO.DISPLAY_ATTR_BRIGHT)

    @staticmethod
    def GetWarnEscapeSeq():
        """@return the warning level ANSI escape sequence."""
        return "\x1b[{:01d};{:02d}m".format(UIO.DISPLAY_ATTR_FG_RED, UIO.DISPLAY_ATTR_BRIGHT)

    @staticmethod
    def GetErrorEscapeSeq():
        """@return the warning level ANSI escape sequence."""
        return "\x1b[{:01d};{:02d}m".format(UIO.DISPLAY_ATTR_FG_RED, UIO.DISPLAY_ATTR_BLINK)

    @staticmethod
    def RemoveEscapeSeq(text):
        """@brief Remove ANSI escape sequences that maybe present in text.
           @param text A string that may contain ANSI escape sequences.
           @return The text with any ANSI escape sequences removed."""
        escapeSeq =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return escapeSeq.sub('', text)

    def __init__(self, debug=False, colour=True):
        self._debug                         = debug
        self._colour                        = colour
        self._logFile                       = None
        self._progBarSize                   = 0
        self._progBarGrow                   = True
        self._debugLogEnabled               = False
        self._debugLogFile                  = None
        self._symLinkDir                    = None
        self._sysLogEnabled                 = False
        self._sysLogHost                    = None

    def logAll(self, enabled):
        """@brief Turn on/off the logging of all output including debug output even if debugging is off."""
        self._debugLogEnabled = enabled

    def enableDebug(self, enabled):
        """@brief Enable/Disable debugging
           @param enabled If True then debugging is enabled"""
        self._debug = enabled

    def isDebugEnabled(self):
        """@return True if debuggin is eenabled."""
        return self._debug

    def info(self, text, highlight=False):
        """@brief Present an info level message to the user.
           @param text The line of text to be presented to the user."""
        if self._colour:
            if highlight:
                self._print('{}INFO:  {}{}'.format(UIO.GetInfoEscapeSeq(), text, UIO.DISPLAY_RESET_ESCAPE_SEQ))
            else:
                self._print('{}INFO{}:  {}'.format(UIO.GetInfoEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ, text))
        else:
            self._print('INFO:  {}'.format(text))
        self._update_syslog(PRIORITY.INFO, text)

    def debug(self, text):
        """@brief Present a debug level message to the user if debuging is enabled.
           @param text The line of text to be presented to the user."""
        if self._debug:
            if self._colour:
                self._print('{}DEBUG{}: {}'.format(UIO.GetDebugEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ, text))
            else:
                self._print('DEBUG: {}'.format(text))
        elif self._debugLogEnabled and self._debugLogFile:
            if self._colour:
                self.storeToDebugLog('{}DEBUG{}: {}'.format(UIO.GetDebugEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ, text))
            else:
                self.storeToDebugLog('DEBUG: {}'.format(text))
        self._update_syslog(PRIORITY.DEBUG, text)
        
    def warn(self, text):
        """@brief Present a warning level message to the user.
           @param text The line of text to be presented to the user."""
        if self._colour:
            self._print('{}WARN{}:  {}'.format(UIO.GetWarnEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ, text))
        else:
            self._print('WARN:  {}'.format(text))
        self._update_syslog(PRIORITY.WARNING, text)
        
    def error(self, text):
        """@brief Present an error level message to the user.
           @param text The line of text to be presented to the user."""
        if self._colour:
            self._print('{}ERROR{}: {}'.format(UIO.GetErrorEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ, text))
        else:
            self._print('ERROR: {}'.format(text))
        self._update_syslog(PRIORITY.ERROR, text)

    def _print(self, text):
        """@brief Print text to stdout"""
        self.storeToLog(text)
        if self._debugLogEnabled and self._debugLogFile:
            self.storeToDebugLog(text)
        print(text)
      
    def getInput(self, prompt, noEcho=False, stripEOL=True):
        """@brief Get a line of text from the user.
           @param noEcho If True then * are printed when each character is pressed.
           @param stripEOL If True then all end of line (\r, \n) characters are stripped.
           @return The line of text entered by the user."""
        if self._colour:
            if noEcho:
                prompt = "{}INPUT{}: ".format(UIO.GetInfoEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ) + prompt + ": "
                self.storeToLog(prompt, False)
                response = getpass(prompt, sys.stdout)

            else:
                prompt = "{}INPUT{}: ".format(UIO.GetInfoEscapeSeq(), UIO.DISPLAY_RESET_ESCAPE_SEQ) + prompt + ": "
                self.storeToLog(prompt, False)
                response = input(prompt)

        else:
            if noEcho:
                prompt = "INPUT: " + prompt + ": "
                self.storeToLog(prompt, False)
                response = getpass(prompt, sys.stdout)

            else:
                prompt = "INPUT: " + prompt + ": "
                self.storeToLog(prompt, False)
                response = input(prompt)

        if stripEOL:
            response = response.rstrip('\n')
            response = response.rstrip('\r')

        self.storeToLog(response)
        return response

    def getBoolInput(self, prompt, allowQuit=True):
        """@brief Get boolean repsonse from user (y or n response).
           @param allowQuit If True and the user enters q then the program will exit.
           @return True or False"""
        while True:
            response = self.getInput(prompt=prompt)
            if response.lower() == 'y':
                return True
            elif response.lower() == 'n':
                return False
            elif allowQuit and response.lower() == 'q':
                sys.exit(0)

    def getIntInput(self, prompt, allowQuit=True, radix=10):
      """@brief Get a decimal int number from the user.
         @param allowQuit If True and the user enters q then the program will exit.
         @param radix The radix of the number entered (default=10).
         @return True or False"""
      while True:
        response = self.getInput(prompt=prompt)
        try:
          return int(response, radix)
        except ValueError:
          self.warn("%s is not a valid integer value." % (response))

        if allowQuit and response.lower() == 'q':
          return None

    def errorException(self):
        """@brief Show an exception traceback if debugging is enabled"""
        if self._debug:
            lines = traceback.format_exc().split('\n')
            for l in lines:
                self.error(l)

    def getPassword(self, prompt):
        """@brief Get a password from a user.
           @param prompt The user prompt.
           @return The password entered."""
        return self.getInput(prompt, noEcho=True)

    def setSymLinkDir(self, symLinkDir):
        """@brief Set a shortcut location for symLink.
           @param symLinkDir The directory to create the simlink.
           @return None"""
        self._symLinkDir=symLinkDir

    def setLogFile(self, logFile):
        """@brief Set a logfile for all output.
           @param logFile The file to send all output to.
           @return None"""
        self._logFile=logFile
        self._debugLogFile = "{}.debug.txt".format(self._logFile)

    def storeToLog(self, text, addLF=True, addDateTime=True):
        """@brief Save the text to the main log file if one is defined.
           @param text The text to be saved.
           @param addLF If True then a line feed is added to the output in the log file.
           @return None"""
        self._storeToLog(text, self._logFile, addLF=addLF, addDateTime=addDateTime)

    def storeToDebugLog(self, text, addLF=True, addDateTime=True):
        """@brief Save the text to the debug log file if one is defined. This file holds all the
                  data from the main log file plus debug data even if debugging is not enabled.
           @param text The text to be saved.
           @param addLF If True then a line feed is added to the output in the log file.
           @return None"""
        self._storeToLog(text, self._debugLogFile, addLF=addLF, addDateTime=addDateTime, symLinkFile=UIO.DEBUG_LOG_SYM_LINK)

    def _storeToLog(self, text, logFile, addLF=True, addDateTime=True, symLinkFile=USER_LOG_SYM_LINK):
        """@brief Save the text to the log file if one is defined.
           @param text The text to be saved.
           @param logFile The logFile to save data to.
           @param addLF If True then a line feed is added to the output in the log file.
           @param symLinkFile The name of the fixed symlink file to point to the latest log file.
           @return None"""
        createSymLink = False
        if logFile:
            if addDateTime:
                timeStr = datetime.now().strftime("%d/%m/%Y-%H:%M:%S.%f")
                text = "{}: {}".format(strftime(timeStr, localtime()).lower(), text)

            # If the log file is about to be created then we will create a symlink
            # to the file.
            if not os.path.isfile(logFile):
                createSymLink = True

            fd = open(logFile, 'a')
            if addLF:
                fd.write("{}\n".format(text))
            else:
                fd.write(text)
            fd.close()

            if createSymLink:
                #This is helpful as the link will point to the latest log file
                #which can be useful when debugging. I.E  no need to find the
                #name of the latest file.
                dirName = self._symLinkDir
                # if the simlink has not been set then default to the logging file
                if dirName is None:
                    dirName = os.path.dirname(logFile)
                absSymLink = os.path.join(dirName, symLinkFile)
                if os.path.lexists(absSymLink):
                    os.remove(absSymLink)
                os.symlink(logFile, absSymLink)

    def showProgBar(self, barChar='*'):
        """@brief Show a bar that grows and shrinks to indicate an activity is occuring."""
        if self._progBarGrow:
            sys.stdout.write(barChar)
            self._progBarSize+=1
            if self._progBarSize > UIO.PROG_BAR_LENGTH:
                self._progBarGrow=False
        else:
            sys.stdout.write('\b')
            sys.stdout.write(' ')
            sys.stdout.write('\b')
            self._progBarSize-=1
            if self._progBarSize == 0:
                self._progBarGrow=True

        sys.stdout.flush()

    def clearProgBar(self):
        """@brief Clear any progress characters that maybe present"""
        sys.stdout.write('\b' * UIO.PROG_BAR_LENGTH)
        sys.stdout.write(' '*UIO.PROG_BAR_LENGTH)
        sys.stdout.write('\r')
        sys.stdout.flush()

    def getLogFile(self):
        """@return the name of the user output log file or None if not set"""
        return self._logFile

    def getDebugLogFile(self):
        """@return The name of the debug log file or None if not set."""
        return self._debugLogFile

    def getCurrentUsername(self):
        """Get the current users username or return unknown_user if not able to read it.
           This is required as getpass.getuser() does not always work on windows platforms."""
        username="unknown_user"
        try:
            username=getuser()
        except:
            pass
        return username

    def enableSyslog(self, enabled, host="localhost"):
        """@brief Enable/disable syslog.
           @param enabled If True then syslog is enabled."""
        self._sysLogEnabled = enabled
        self._sysLogHost = host
      
    def _update_syslog(self, pri, msg):
        """Send a message to syslog is syslog is enabled
        Syslog messages will have the following components
        0 = time/date stamp
        1 = hostname
        2 = main python file name
        3 = PID
        4 = username under which the program is being executed
        5 = The syslog message

        The syslog messages will be prefixed withj the application name
        """
        if self._sysLogEnabled:
            aMsg=msg
            #Ensure we have no zero characters in the message. 
            # syslog will throw an error if it finds any
            if "\x00" in aMsg:
                aMsg=aMsg.replace("\x00", "")
                
            #Attempt to get the src IP address for syslog messages.
            srcIP = ""
            try:
                netIF = NetIF()
                srcIP = netIF.getLocalNetworkAddress()
            except:
                pass

            try:
                #send aMsg to syslog with the current process ID and username
                syslog(pri, "%s %d %s: %s" % (srcIP, os.getpid(), str(self.getCurrentUsername()), str(aMsg) ), host=self._sysLogHost )
            #Ignore if se can't resolve address. We don't really syslog want errors to stop the user interface
            except:
                pass

class ConsoleMenu(object):
    """@brief Responsible for presenting a list of options to the user on a
              console/terminal interface and allowing the user to select 
              the options as required."""
    def __init__(self, uio):
        """@brief Constructor
           @param uio A UIO instance."""
        self._uio = uio
        self._menuList = []
        
    def add(self, menuStr, menuMethod, args=None):
        """@brief Add a menu option.
           @param menuStr The String displayed as the menu option.
           @param menuMethod The method to be called when this option is selected.
           @param args An optional list or tuple of arguments to pass to the method."""
        self._menuList.append( (menuStr, menuMethod, args) )
        
    def show(self, showSelectedOption=False):
        """@brief Show the menu to the user and allow the user to interact with it.
           @param showSelectedOption If True then the option selected is displayed before executing the method."""
        while True:
            selectorId = 1
            for menuStr, _, _ in self._menuList:
                self._uio.info("{: >2}: {}".format(selectorId, menuStr))
                selectorId = selectorId + 1
            selectedID = self._uio.getIntInput("Select a menu option")
            if selectedID >= 1 and selectedID <= len(self._menuList):
                menuStr, selectedMethod, args = self._menuList[selectedID-1]
                if showSelectedOption:
                    self._uio.info(menuStr)
                if not args:
                    selectedMethod()
                else:
                    selectedMethod(*args)

# -------------------------------------------------------------------
# @brief An implementation to allow syslog messages to be generated.
# 
class FACILITY:
  KERN=0
  USER=1
  MAIL=2
  DAEMON=3
  AUTH=4
  SYSLOG=5
  LPR=6
  NEWS=7
  UUCP=8
  CRON=9
  AUTHPRIV=10
  FTP=11
  LOCAL0=16
  LOCAL1=17
  LOCAL2=18
  LOCAL3=19
  LOCAL4=20
  LOCAL5=21
  LOCAL6=22
  LOCAL7=23
 
class PRIORITY:
  EMERG=0
  ALERT=1
  CRIT=2
  ERROR=3
  WARNING=4
  NOTICE=5
  INFO=6
  DEBUG=7

syslogSocket=None
lock = Lock()
  
def syslog(priority, message, facility=FACILITY.LOCAL0, host='localhost', port=514):
    """
	  @brief Send a syslog message.
      @param priority The syslog priority level.
      @param message The text message to be sent.
      @param facility The syslog facility 
      @param host The host address for the systlog server.
      @param port The syslog port.
	"""
    global lock, timer, syslogSocket
	
    try:
        lock.acquire()
        if not syslogSocket:
            syslogSocket = socket(AF_INET, SOCK_DGRAM)

        smsg = '<%05d>%s' % ( (priority + facility*8), message )
        syslogSocket.sendto(smsg.encode('ascii', 'ignore'), (host, port))

    finally:
        lock.release()
