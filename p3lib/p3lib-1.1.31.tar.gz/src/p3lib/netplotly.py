#!/usr/bin/env python3

import os
import plotly
import tarfile
import tempfile
import shutil

from   pathlib import Path
try:
    from   .ssh import SSH
    from   .helper import getHomePath
except:
    #We get here if running netplotly_demo.py as it sits in the same folder
    #as netplotly.py
    from   ssh import SSH
    from   helper import getHomePath

class NetPlotly(object):
    """@brief Manage plotly graphs on a webserver and allow them to be transferred over a network via ssh.
              Plots are saved to a local folder. The local folder maybe served via a web server.
              The contents of the local folder maybe transferred to a remote machine via ssh.
              The contents of the remote folder maybe served via a web server.

              The local and remote folders will contain an index.html file. This displays a table of
              all the available plots. Each plot name in the table maybe clicked which will display
              the plotly plot."""
    INDEX_HTML_FILE         = "netplotly_index.html"
    DEFAULT_LOCAL_ROOT      = "~/.netplotly"
    ASSETS_FOLDER           = "assets"
    PLOT_LIST_FILE          = "plot_list.txt"

    @staticmethod
    def GetTarBallFile():
        """@brief Get the tarball file path
           @return The abs file path"""
        return os.path.join( tempfile.gettempdir(), "netplotly.tgz" )

    def __init__(self, localRoot=DEFAULT_LOCAL_ROOT, serverRoot=DEFAULT_LOCAL_ROOT, host=None, username=None, password=None, port=22, uio=None):
        """@brief Constructor
           @param localRoot The local folder to store the plots in.
                  A web server may serve files directly from here or they maybe
                  uploaded (via ssh) to a webserver using the API's provided
                  by this class.
           @param serverRoot The folder to store html files in on the server.
           @param host The address of the ssh server to upload files to.
           @param username The SSH server username
           @param password The SSH server password. Not required if auto login via public
                           key is enabled for the ssh server.
           @param port The ssh server port (default=22).
           @param uio A UIO instance for displaying messages to the user."""
        self._localRoot = localRoot
        self._serverRoot = serverRoot
        self._host       = host
        self._username  = username
        self._password  = password
        self._port      = port
        self._uio       = uio
        self._ssh       = None

        self._updateLocalRoot()

    def _updateLocalRoot(self):
        """@brief Set the local _rootp attr"""
        if self._localRoot.startswith("~"):
            self._localRoot = getHomePath() + self._localRoot.replace("~", "")

    def info(self, msg):
        """@brief Display an info level message if we have been provided with a uio object"""
        if self._uio:
            self._uio.info(msg)

    def _getPlotListFile(self):
        """@return The plot list file"""
        return os.path.join(self._localRoot, NetPlotly.PLOT_LIST_FILE)

    def _updatePlotList(self, plotTitle):
        """@brief Update the plot title log file. This file is read by the javascript to
                  present a table of available plots to the user. The PLOT_LIST_FILE
                  simply contains a number of lines each lines text is the name of the plot.
           @param plotTitle The plot title
           @return None"""
        alreadyAdded = False
        plotListFile = self._getPlotListFile()
        if os.path.isfile(plotListFile):
            fd = open(plotListFile, 'r')
            lines = fd.readlines()
            fd.close()
            for line in lines:
                line=line.rstrip("\n")
                if line == plotTitle:
                    alreadyAdded=True
        if not alreadyAdded:
            fd = open(plotListFile, 'a')
            fd.write("{}\n".format(plotTitle))
            fd.close()

    def _removePlotList(self, plotTitle):
        """@brief Remove a file from the plot list.
           @param plotTitle The plot title
           @return None"""
        plotListFile = self._getPlotListFile()
        newLines = []
        if os.path.isfile(plotListFile):
            fd = open(plotListFile, 'r')
            lines = fd.readlines()
            fd.close()

            for line in lines:
                if not line.startswith(plotTitle):
                    newLines.append(line)

            fd = open(plotListFile, 'w')
            for l in newLines:
                fd.write(l)

            fd.close()

    def save(self, fig, htmlFile=None, autoOpen=False):
        """@brief Save a plotly figure to an html file in the local home folder.
           @param fig The plotly figure
           @param htmlFile The name of the htmlfile to save. If not provided the name of the plot
                           with the .html suffix is used as the filename.
           @param autoOpen If True then a browser window is launched to show the plot"""
        #don't allow index.html as this is usd for the table of plots
        if htmlFile == NetPlotly.INDEX_HTML_FILE:
            raise Exception("save(): {} is a reserved html file name.".format(NetPlotly.INDEX_HTML_FILE))

        #If no html file provided then use the name of the plot
        if not htmlFile:
            htmlFile = "{}.html".format( fig["layout"]["title"]["text"] )

        if not os.path.isdir(self._localRoot):
            os.makedirs(self._localRoot)
            self.info("Created {}".format(self._localRoot))

        plotName = htmlFile.replace(".html", "")
        self._updatePlotList(plotName)

        fileToSave = os.path.join(self._localRoot, htmlFile)
        plotly.offline.plot(fig, filename=fileToSave, auto_open = autoOpen)
        self.info("Saved {}".format(fileToSave))

    def _createTarBall(self, opFile, srcFolder):
        self.info("Creating {} from {}".format(opFile, srcFolder))
        with tarfile.open(opFile, "w:gz") as tar:
            tar.add(srcFolder, arcname=os.path.basename(srcFolder))

    def connect(self):
        """@brief connect to the server vis ssh"""
        if not self._host:
            raise Exception("No SSH server defined to connect to")

        if not self._ssh:
            self.info("Connecting to {}:{} as {}".format(self._host, self._port, self._username))
            self._ssh = SSH(self._host, username=self._username, password=self._password, port=self._port)
            self._ssh.connect(connectSFTPSession=True)
            self.info("Connected")

    def disconnect(self):
        """@brief Close the connection to the server."""
        if self._ssh:
            self._ssh.close()
            self._ssh = None
            self.info("Closed server connection")

    def upload(self, purge=False):
        """@brief Upload the plot to the server.
           @param purge If True (default is False) then all html files are removed from the server before uploading
                        from the local path. If True the caller must be careful to set serverRoot (in Constructor)
                        as all files in this location are purged before files are uploaded."""
        if self._host and self._username:
            tarBallFile = NetPlotly.GetTarBallFile()
            self._createTarBall(tarBallFile, self._localRoot)
            self.connect()

            if purge:
                #Remove all the files in the server folder
                cmd = "rm -f {}/*".format(self._serverRoot)
                self._ssh.runCmd(cmd)

            self.info("Uploading {} to {}:{}".format(tarBallFile, self._host, self._port))
            self._ssh.putFile(tarBallFile, tarBallFile)

            self.info("Decompressing {} into {} on the server.".format(tarBallFile, self._serverRoot))
            rPath = Path(self._serverRoot)
            cmd = "tar zxvf {} -C {}".format(tarBallFile, rPath.parent)
            self._ssh.runCmd(cmd)

            self.disconnect()

    def getPlotNameList(self):
        """@brief Get a list of the names of all the plots currently stored in the local root folder.
           @return a list of plot names."""
        plotList = []
        plotListFile = self._getPlotListFile()
        if os.path.isfile(plotListFile):
            fd = open(plotListFile, 'r')
            plotList = fd.read().splitlines()
            fd.close()

        return plotList

    def getPlotFileList(self):
        """@brief Get a list of the plot file names of all the plots currently stored in the local root folder.
           @return a list of plot file names."""
        plotList = self.getPlotNameList()
        plotFileList = ["{}.html".format(plotName) for plotName in plotList]
        return plotFileList

    def remove(self, plotName):
        """@brief Remove a plot by it's name from the plot list.
           @return None"""
        fileToRemove = os.path.join(self._localRoot, "{}.html".format(plotName))
        if os.path.isfile(fileToRemove):
            os.remove(fileToRemove)
        self._removePlotList(plotName)

    def removeLocalRoot(self):
        """@brief Remove all plots from the list of plots. Be sure you have _localRoot set
                  correctly before calling this method.
           @return None"""
        shutil.rmtree(self._localRoot)
