#!/usr/bin/env python3

"""This file is responsible for providing general helper functionality not
   associated with particular objects"""

import sys
import os
import platform
import json
import traceback
import  socket

def initArgs(parser, lastCmdLineArg=None, checkHostArg=True):
    """This method is responsible for
        - Ensure that the host argument has been defined by the user on the command line
        - Set the debug level as defined on the command line.
        - If lastCmdLineArg is defined then ensure that this is the last arguemnt on the
          command line. If we don't do this then the user may define some arguments on
          the command line after the action (callback) command line option but as
          the arguments are processed in sequence the args following the action
          arg will not be used.
    """

    if checkHostArg:
        if parser.values.host == None or len(parser.values.host) == 0:
            raise Exception("Please define the RFeye host on the command line.")

    parser.uio.debugLevel = parser.values.debug

    # Check that the argument that invoked tha action (callback) is the last on the command line
    argOk = False
    if len(sys.argv) > 0:
        lastArg = sys.argv[len(sys.argv) - 1]
        if lastArg == lastCmdLineArg:
            argOk = True

    if not argOk:
        raise Exception("Please ensure %s (if used) is the last argument on the command line." % (lastCmdLineArg))


def ensureBoolInt(value, arg):
    """We expect value to be a boolean (0 or 1)
       raise an error if not
    """
    if value not in [0, 1]:
        raise Exception("The %s arg should be followed by 0 or 1. Was %s." % (str(arg), str(value)))


def getLines(text):
    """Split the text into lines"""
    lines = []
    if len(text) > 0:
        elems = text.split("\n")
        lines = stripEOL(elems)
    return lines


def stripEOL(lines):
    """Strip the end of line characters from the list of lines of text"""
    noEOLLines = []
    for l in lines:
        l = l.rstrip("\n")
        l = l.rstrip("\r")
        noEOLLines.append(l)
    return noEOLLines


def getLinesFromFile(f):
    """Get Lines from file"""
    fd = open(f, "r")
    lines = fd.readlines()
    fd.close()
    return stripEOL(lines)


def _removeInvalidChars(line):
    """Return a copy of line with each ASCII control character (0-31),
    and each double quote, removed."""
    output = ''
    for c in line:
        if c >= ' ' and c != '"':
            output = output + c
    return output


def _addEntry(line, dict):
    """Parse line into a key and value, adding the result to dict, as in
    getDict."""
    # check for a parameter
    fields = line.split('=')
    # if at least 2 fields exist
    if len(fields) > 1:
        # add the key,value pair to the dictionary
        key = _removeInvalidChars(fields[0])
        value = _removeInvalidChars(fields[1])
        dict[key] = value


def getDict(filename, jsonFmt=False):
    """@brief Load dict from file
       @param jsonFmt If True then we expect the file to be in json format.

           if json is True we expect the file to be in json format

           if json is False
            We key=value pairs (= is the separate character).
            Lines containing a hash sign as the first non-whitespace character are
            ignored. Leading and trailing whitespace is ignored.

            Lines not containing an equals sign are also silently ignored.

            Lines not ignored are assumed to be in the form key=value, where key
            does not contain an equals sign;
            Control characters and double quotes in both key and value are silently
            discarded. value is also truncated just before the first whitespace or
            equals sign it contains.

       @return Return the dict loaded from the file.

    """
    dictLoaded = {}

    if jsonFmt:
        fp = open(filename, 'r')
        dictLoaded = json.load(fp)
        fp.close()

    else:

        lines = getLinesFromFile(filename)
        for line in lines:
            # strip leading and trailing whitespaces
            line = line.strip()
            # if a comment line then ignore
            if line.find('#') == 0:
                continue
            # add an entry to the dict
            _addEntry(line, dictLoaded)

    return dictLoaded


def saveDict(dictToSave, filename, jsonFmt=False):
    """@brief Save dict to a file.
       @param jsonFmt If True then we expect the file to be in json format.

       if json is True we expect the file to be in json format

       if json is False the file is saved as key = value pairs
       Each key in dict produces a line of the form key=value. Output will be
       ambiguous if any keys contain equals signs or if any values contain
       newlines.

    """

    if jsonFmt:
        try:

            with open(filename, "w") as write_file:
                json.dump(dictToSave, write_file)

        except IOError as i:
            raise IOError(i.errno, 'Failed to write file \'%s\': %s'
                          % (filename, i.strerror), i.filename).with_traceback(sys.exc_info()[2])
    else:
        lines = []
        # build config file lines
        for key in list(dictToSave.keys()):
            lines.append(str(key) + '=' + str(dictToSave.get(key)) + '\n')
        try:
            f = open(filename, 'w')
            f.writelines(lines)
            f.close()
        except IOError as i:
            raise IOError(i.errno, 'Failed to write file \'%s\': %s'
                          % (filename, i.strerror), i.filename).with_traceback(sys.exc_info()[2])


def getAddrPort(host):
    """The host address may be entered in the format <address>:<port>
       Return a tuple with host and port"""
    elems = host.split(":")

    if len(elems) > 1:
        host = elems[0]
        port = int(elems[1])
    else:
        port = 22

    return [host, port]


def getProgramName():
    """Get the name of the currently running program."""
    progName = sys.argv[0].strip()
    if progName.startswith('./'):
        progName = progName[2:]
    if progName.endswith('.py'):
        progName = progName[:-3]

    # Only return the name of the program not the path
    pName = os.path.split(progName)[-1]
    if pName.endswith('.exe'):
        pName = pName[:-4]
    return pName


def getBoolUserResponse(uio, prompt, allowQuit=True):
    """Get boolean (Y/N) repsonse from user.
       If allowQuit is True and the user enters q then the program will exit."""
    while True:
        response = uio.getInput(prompt=prompt)
        if response.lower() == 'y':
            return True
        elif response.lower() == 'n':
            return False
        elif allowQuit and response.lower() == 'q':
            sys.exit(0)


def getIntUserResponse(uio, prompt, allowQuit=True):
    """Get int repsonse from user.
       If allowQuit is True and the user enters q then None is returned to
       indicate that the user selected quit."""
    while True:
        response = uio.getInput(prompt=prompt)

        try:

            return int(response)

        except ValueError:

            uio.info("%s is not a valid integer value." % (response))

        if allowQuit and response.lower() == 'q':
            return None


def getIntListUserResponse(uio, prompt, minValue=None, maxValue=None, allowQuit=True):
    """Get int repsonse from user as a list of int's
       If allowQuit is True and the user enters q then the program will exit."""
    while True:
        response = uio.getInput(prompt=prompt)
        try:
            elems = response.split(",")
            if len(elems) > 0:
                intList = []
                errorStr = None
                for vStr in elems:
                    v = int(vStr)
                    if minValue != None and v < minValue:
                        errorStr = "The min value that may be entered is %d." % (minValue)
                        break
                    elif maxValue != None and v > maxValue:
                        errorStr = "The max value that may be entered is %d." % (maxValue)
                        break
                    else:
                        intList.append(v)

                if errorStr != None:
                    uio.error(errorStr)

            return intList
        except ValueError:
            pass
        if allowQuit and response.lower() == 'q':
            sys.exit(0)


def getHomePath():
    """Get the user home path as this will be used to store config files"""
    if "HOME" in os.environ:
        return os.environ["HOME"]

    elif "HOMEDRIVE" in os.environ and "HOMEPATH" in os.environ:
        return os.environ["HOMEDRIVE"] + os.environ["HOMEPATH"]

    elif "USERPROFILE" in os.environ:
        return os.environ["USERPROFILE"]

    return None


def setHomePath(homePath):
    """Seth the env variable HOME"""
    # Do some sanity/defensive stuff
    if homePath == None:
        raise Exception("homePath=None.")
    elif len(homePath) == 0:
        raise Exception("len(homePath)=0.")

    # We do some special stuff on windows
    if platform.system() == "Windows":

        os.environ["HOME"] = homePath

        if "USERPROFILE" in os.environ:
            os.environ["USERPROFILE"] = os.environ["HOME"]

        if "HOMEPATH" in os.environ:
            os.environ["HOMEPATH"] = os.environ["HOME"]

        if not os.path.isdir(os.environ["HOME"]):
            raise Exception(os.environ["HOME"] + " path not found.")

    else:
        # Not windows set HOME env var
        os.environ["HOME"] = homePath

        if not os.path.isdir(os.environ["HOME"]):
            raise Exception(os.environ["HOME"] + " path not found.")

def printDict(uio, theDict, indent=0):
    """@brief Show the details of a dictionary contents
       @param theDict The dictionary
       @param indent Number of tab indents
       @return None"""
    for key in theDict:
        uio.info('\t' * indent + str(key))
        value = theDict[key]
        if isinstance(value, dict):
            printDict(uio, value, indent + 1)
        else:
            uio.info('\t' * (indent + 1) + str(value))

def logTraceBack(uio):
    """@brief Log a traceback using the uio instance to the debug file.
       @param uio A UIO instance
       @return None"""
    # Always store the exception traceback in the logfile as this makes
    # it easier to diagnose problems with the testing
    lines = traceback.format_exc().split("\n")
    for line in lines:
        uio.storeToDebugLog(line)

def GetFreeTCPPort():
    """@brief Get a free port and return to the client. If no port is available
              then -1 is returned.
       @return the free TCP port number or -1 if no port is available."""
    tcpPort=-1
    try:
        #Bind to a local port to find a free TTCP port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        tcpPort = sock.getsockname()[1]
        sock.close()
    except socket.error:
        pass
    return tcpPort

def appendCreateFile(uio, aFile, quiet=False):
    """@brief USer interaction to append or create a file.
       @param uio A UIO instance.
       @param quiet If True do not show uio messages (apart from overwrite prompt.
       @param aFile The file to append or delete."""
    createFile = False
    if os.path.isfile(aFile):
        if uio.getBoolInput("Overwrite {} y/n".format(aFile)):
            os.remove(aFile)
            if not quiet:
                uio.info("Deleted {}".format(aFile))
            createFile = True
        else:
            if not quiet:
                uio.info("Appending to {}".format(aFile))

    else:
        createFile = True

    if createFile:
        fd = open(aFile, 'w')
        fd.close()
        if not quiet:
            uio.info("Created {}".format(aFile))
