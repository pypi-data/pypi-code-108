#!/usr/bin/env python3

import sys
import  queue
import  itertools
import  threading
import  asyncio
import  socket
import  os

from    datetime import datetime
from    functools import partial
from    time import time

from    p3lib.helper import getHomePath

from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models import Range1d
from bokeh.palettes import Category20_20 as palette

from bokeh.plotting import save, output_file
from bokeh.layouts import gridplot, column, row
from bokeh.models.widgets import CheckboxGroup
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import TextInput
from bokeh.models import Panel, Tabs
from bokeh.models import DataTable, TableColumn
from bokeh.models import CustomJS
from bokeh import events

class UpdateEvent(object):
    """@brief Responsible for holding the state of an event sent from a non GUI thread
              to the GUI thread context in order to update the GUI. The details of these
              updates will be specific to the GUI implemented. Therefore this class should
              be extended to include the events that are specific to the GUI implemented."""

    UPDATE_STATUS_TEXT = 1 # This is an example of an event. It is intended to be used to
                           # update the status line in the GUI to provide the user with
                           # some feedback as to the current state of the GUI.

    def __init__(self, id, argList=None):
        """@brief Constructor
           @param id An integer event ID
           @param argList A list of arguments associated with the event"""
        #As this is esentially a holding class we don't attempt to indicate provate attributes
        self.id = id
        self.argList = argList

class TimeSeriesPoint(object):
    """@brief Resonsible for holding a time series point on a trace."""
    def __init__(self, traceIndex, value, timeStamp=None):
        """@brief Constructor
           @param traceIndex The index of the trace this reading should be applied to.
                             The trace index starts at 0 for the top left plot (first
                             trace added) and increments with each call to addTrace()
                             on TimeSeriesPlotter instances.
           @param value The Y value
           @param timeStamp The x Value."""
        self.traceIndex = traceIndex
        if timeStamp:
            self.time = timeStamp
        else:
            self.time = datetime.now()
        self.value = value

class TabbedGUI(object):
    """@brief A Generalised class responsible for plotting real time data."""

    @staticmethod
    def GetFigure(title=None, yAxisName=None, yRangeLimits=None, width=400, height=400):
        """@brief A Factory method to obtain a figure instance.
                  A figure is a single plot area that can contain multiple traces.
           @param title The title of the figure.
           @param yAxisName The name of the Y axis.
           @param yRangeLimits If None then the Y azxis will auto range.
                               If a list of two numerical values then this
                               defines the min and max Y axis range values.
           @param width The width of the plot area in pixels.
           @param height The height of the plot area in pixels.
           @return A figure instance."""
        if yRangeLimits and len(yRangeLimits) == 2:
            yrange = Range1d(yRangeLimits[0], yRangeLimits[1])
        else:
            yrange = None

        fig = figure(title=title,
                     x_axis_type="datetime",
                     x_axis_location="below",
                     y_range=yrange,
                     plot_width=width,
                     plot_height=height)
        fig.yaxis.axis_label = yAxisName
        return fig

    def __init__(self, docTitle, bokehPort=9090):
        """@brief Constructor.
           @param docTitle The document title.
           @param bokehPort The port to run the server on."""
        self._docTitle=docTitle
        self._bokehPort=bokehPort
        self._doc = None
        self._tabList = []
        self._server = None

    def stopServer(self):
        """@brief Stop the bokeh server"""
        sys.exit()

    def isServerRunning(self):
        """@brief Check if the server is running.
           @param True if the server is running. It may take some time (~ 20 seconds)
                  after the browser is closed before the server session shuts down."""
        serverSessions = "not started"
        if self._server:
            serverSessions = self._server.get_sessions()

        serverRunning = True
        if not serverSessions:
                serverRunning = False

        return serverRunning

    def runBokehServer(self):
        """@brief Run the bokeh server. This is a blocking method."""
        apps = {'/': Application(FunctionHandler(self.createPlot))}
        self._server = Server(apps, port=self._bokehPort)
        self._server.show("/")
        self._server.run_until_shutdown()

    def _run(self, method, args=[]):
        """@brief Run a method in a separate thread. This is useful when
                  methods are called from gui events that take some time to execute.
                  For such methods the gui callback should call this method to execute
                  the time consuming methods in another thread.
           @param method The method to execute.
           @param A tuple of arguments to pass to the method.
                  If no arguments are required then an empty tuple should be passed."""
        thread = threading.Thread(target=method, args=args)
        thread.start()

    def _sendUpdateEvent(self, updateEvent):
        """@brief Send an event to the GUI context to update the GUI. When methods
                  are executing outside the gui thread but need to update the state
                  of the GUI, events must be sent to the gui context in order to update
                  the gui elements when they have the correct locks.
           @param updateEvent An UpdateEvent instance."""
        self._doc.add_next_tick_callback( partial(self._rxUpdateEvent, updateEvent)  )

    def _rxUpdateEvent(self, updateEvent):
        """@brief Receive an event into the GUI context to update the GUI.
           @param updateEvent An PSUGUIUpdateEvent instance. This method will
                              be specific to the GUI implemented and must therefore
                              be overridden in child classes."""
        raise Exception("BUG: The _rxUpdateEvent() method must be implemented by classes that are children of the TabbedGUI class.")

class TimeSeriesPlotter(TabbedGUI):
    """@brief Responsible for plotting data on tab 0 with no other tabs."""

    def __init__(self, docTitle, bokehPort=9091, topCtrlPanel=True):
        """@Constructor
           @param docTitle The document title.
           @param bokehPort The port to run the server on.
           @param topCtrlPanel If True then a control panel is displayed at the top of the plot.
           """
        super().__init__(docTitle, bokehPort=bokehPort)
        self._statusAreaInput = None
        self._figTable=[[]]
        self._grid = None
        self._topCtrlPanel=topCtrlPanel
        self._srcList = []
        self._colors = itertools.cycle(palette)
        self._queue = queue.Queue()
        self._plottingEnabled = True

    def addTrace(self, fig, legend_label, line_color=None, line_width=1):
        """@brief Add a trace to a figure.
           @param fig The figure to add the trace to.
           @param line_color The line color
           @param legend_label The text of the label.
           @param line_width The trace line width."""
        src = ColumnDataSource({'x': [], 'y': []})

        #Allocate a line color if one is not defined
        if not line_color:
            line_color = next(self._colors)

        fig.line(source=src,
                 line_color = line_color,
                 legend_label = legend_label,
                 line_width = line_width)
        self._srcList.append(src)

    def _update(self):
        """@brief called periodically to update the plot traces."""
        if self._plottingEnabled:
            while not self._queue.empty():
                timeSeriesPoint = self._queue.get()
                new = {'x': [timeSeriesPoint.time],
                       'y': [timeSeriesPoint.value]}
                source = self._srcList[timeSeriesPoint.traceIndex]
                source.stream(new)

    def addValue(self, traceIndex, value, timeStamp=None):
        """@brief Add a value to be plotted. This adds to queue of values
                  to be plotted the next time _update() is called.
           @param traceIndex The index of the trace this reading should be applied to.
           @param value The Y value to be plotted.
           @param timeStamp The timestamp associated with the value. If not supplied
                            then the timestamp will be created at the time when This
                            method is called."""
        timeSeriesPoint = TimeSeriesPoint(traceIndex, value, timeStamp=timeStamp)
        self._queue.put(timeSeriesPoint)

    def addRow(self):
        """@brief Add an empty row to the figures."""
        self._figTable.append([])

    def addToRow(self, fig):
        """@brief Add a figure to the end of the current row of figues.
           @param fig The figure to add."""
        self._figTable[-1].append(fig)

    def createPlot(self, doc, ):
        """@brief create a plot figure.
           @param doc The document to add the plot to."""
        self._doc = doc
        self._doc.title = self._docTitle

        plotPanel = self._getPlotPanel()

        self._tabList.append( Panel(child=plotPanel,  title="Plots") )
        self._doc.add_root( Tabs(tabs=self._tabList) )
        self._doc.add_periodic_callback(self._update, 100)

    def _getPlotPanel(self):
        """@brief Add tab that shows plot data updates."""
        self._grid = gridplot(children = self._figTable, sizing_mode = 'scale_both',  toolbar_location='left')

        if self._topCtrlPanel:
            checkbox1 = CheckboxGroup(labels=["Plot Data"], active=[0, 1],max_width=70)
            checkbox1.on_change('active', self._checkboxHandler)

            self._fileToSave = TextInput(title="File to save", max_width=150)

            saveButton = Button(label="Save", button_type="success", width=50)
            saveButton.on_click(self._savePlot)

            shutDownButton = Button(label="Quit", button_type="success", width=50)
            shutDownButton.on_click(self.stopServer)

            self._statusBarWrapper = StatusBarWrapper()

            plotRowCtrl = row(children=[checkbox1, saveButton, self._fileToSave, shutDownButton])
            plotPanel = column([plotRowCtrl, self._grid, self._statusBarWrapper.getWidget()])
        else:
            plotPanel = column([self._grid])

        return plotPanel

    def _savePlot(self):
        """@brief Save plot to a single html file. This allows the plots to be
                  analysed later."""
        if self._fileToSave and self._fileToSave.value:
            if self._fileToSave.value.endswith(".html"):
                filename = self._fileToSave.value
            else:
                filename = self._fileToSave.value + ".html"
            output_file(filename)
            # Save all the plots in the grid to an html file that allows
            # display in a browser and plot manipulation.
            save( self._grid )
            self._statusBarWrapper.setStatus("Saved {}".format(filename))

    def _checkboxHandler(self, attr, old, new):
        """@brief Called when the checkbox is clicked."""
        if 0 in list(new):  # Is first checkbox selected
            self._plottingEnabled = True
            self._statusBarWrapper.setStatus("Plotting enabled")
        else:
            self._plottingEnabled = False
            self._statusBarWrapper.setStatus("Plotting disabled")

    def runNonBlockingBokehServer(self):
        """@brief Run the bokeh server in a separate thread. This is useful
                  if the we want to load realtime data into the plot from the
                  main thread."""
        self._serverThread = threading.Thread(target=self._runBokehServer)
        self._serverThread.setDaemon(True)
        self._serverThread.start()

    def _runBokehServer(self):
        """@brief Run the bokeh server. This is called when the bokeh server is executed in a thread."""
        apps = {'/': Application(FunctionHandler(self.createPlot))}
        #As this gets run in a thread we need to start an event loop
        evtLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(evtLoop)
        self._server = Server(apps, port=self._bokehPort)
        self._server.start()
        #Show the server in a web browser window
        self._server.io_loop.add_callback(self._server.show, "/")
        self._server.io_loop.start()

class StatusBarWrapper(object):
    """@brief Responsible for presenting a single status line of text in a GUI
              that runs the width of the page (normally at the bottom)."""
    def __init__(self):
        data = dict(
            status = [],
        )
        self.source = ColumnDataSource(data)

        columns = [
                TableColumn(field="status", title="Status"),
            ]
        self.statusBar = DataTable(source=self.source, columns=columns, header_row=True, index_position=None)

    def getWidget(self):
        """@brief return an instance of the status bar widget to be added to a layout."""
        return self.statusBar

    def setStatus(self, msg):
        """@brief Set the message iun the status bar.
           @param The message to be displayed."""
        self.source.data = {"status": [msg]}

class ReadOnlyTableWrapper(object):
    """@brief Responsible for presenting a table of values that can be updated dynamically."""
    def __init__(self, columnNameList, height=400, heightPolicy="auto", showLastRows=0, index_position=None):
        """@brief Constructor
           @param columnNameList A List of strings denoting each column in the 2 dimensional table.
           @param height The hieght of the table viewport in pixels.
           @param heightPolicy The height policy (auto, fixed, fit, min, max). default=fixed.
           @param showLastRows The number of rows to show in the table. If set to 2 then only
                  the last two rows in the table are displayed but they ate scrolled into view.
                  The default=0 which will display all rows and will not scroll the latest
                  into view..
           @param index_position The position of the index column in the table. 0 = the first
                  column. Default is None which does not display the index column."""
        self._columnNameList = columnNameList
        self._dataDict = {}
        self._columns = []
        for columnName in columnNameList:
            self._dataDict[columnName]=[]
            self._columns.append( TableColumn(field=columnName, title=columnName) )

        self._source = ColumnDataSource(self._dataDict)

        self._dataTable = DataTable(source=self._source, columns=self._columns, height=height, height_policy=heightPolicy, frozen_rows=-showLastRows, index_position=index_position)

    def getWidget(self):
        """@brief Return an instance of the DataTable widget to be added to a layout."""
        return self._dataTable

    def setRows(self, rowList):
        """@brief Set the rows in the table.
           @param rowList A list of rows of data. Each row must contain a list of values for each column in the table."""
        for _row in rowList:
            if len(_row) != len(self._columnNameList):
                raise Exception("{} row should have {} values.".format(_row, len(self._columnNameList)))
        dataDict = {}
        colIndex = 0
        for columnName in self._columnNameList:
            valueList = []
            for _row in rowList:
                valueList.append( _row[colIndex] )
            dataDict[columnName]=valueList

            colIndex = colIndex + 1
        self._source.data = dataDict

    def appendRow(self, _row):
        """@brief Set the rows in the table.
           @param rowList A list of rows of data. Each row must contain a list of values for each column in the table."""
        dataDict = {}
        colIndex = 0
        for columnName in self._columnNameList:
            valueList = [_row[colIndex]]
            dataDict[columnName]=valueList
            colIndex = colIndex + 1
        self._source.stream(dataDict)

class AlertButtonWrapper(object):
    """@brief Responsible for presenting a button that when clicked displayed an alert dialog."""
    def __init__(self, buttonLabel, alertMessage, buttonType="default", onClickMethod=None):
        """@brief Constructor
           @param buttonLabel The text displayed on the button.
           @param alertMessage The message displayed in the alert dialog when clicked.
           @param buttonType The type of button to display (default, primary, success, warning, danger, light)).
           @param onClickMethod An optional method that is called when the alert OK button has been clicked.
        """
        self._button = Button(label=buttonLabel, button_type=buttonType)
        if onClickMethod:
            self.addOnClickMethod(onClickMethod)

        source = {"msg": alertMessage}
        callback1 = CustomJS(args=dict(source=source), code="""
            var msg = source['msg']
            alert(msg);
        """)
        self._button.js_on_event(events.ButtonClick, callback1)

    def addOnClickMethod(self, onClickMethod):
        """@brief Add a method that is called after the alert dialog has been displayed.
           @param onClickMethod The method that is called."""
        self._button.on_click(onClickMethod)

    def getWidget(self):
        """@brief return an instance of the button widget to be added to a layout."""
        return self._button

class ShutdownButtonWrapper(object):
    """@brief Responsible for presenting a shutdown button. When the button is clicked
              an alert message is displayed instructing the user to close the browser
              window. When the OK button in the alert dialog is clicked the
              application is shutdown."""
    def __init__(self, shutDownMethod):
        """@brief Constructor
           @param shutDownMethod The method that is called to shutdown the application.
        """
        self._alertButtonWrapper = AlertButtonWrapper("Quit",\
                                                      "The application is shutting down. Please close the browser window",\
                                                      buttonType="danger",\
                                                      onClickMethod=shutDownMethod)

    def getWidget(self):
        """@brief return an instance of the shutdown button widget to be added to a layout."""
        return self._alertButtonWrapper.getWidget()

class SingleAppServer(object):
    """@brief Responsible for running a bokeh server containing a single app.
              The server may be started by calling either a blocking or a non
              blocking method. This provides a basic parennt class with
              the freedom to define your app as required."""

    @staticmethod
    def GetNextUnusedPort(basePort=1024, maxPort = 65534, bindAddress="localhost"):
        """@brief Get the first unused above the base port.
           @param basePort The port to start checking for available ports.
           @param maxPort The highest port number to check.
           @param bindAddress The address to bind to.
           @return The TCP port or -1 if no port is available."""
        port = basePort
        while True:
            try:
                sock = socket.socket()
                sock.bind((bindAddress, port))
                sock.close()
                break
            except:
                port = port + 1
                if port > maxPort:
                    port = -1
                    break

        return port

    def __init__(self, bokehPort=0):
        """@Constructor
           @param bokehPort The TCP port to run the server on. If left at the default
                  of 0 then a spare TCP port will be used.
           """
        if bokehPort == 0:
            bokehPort = SingleAppServer.GetNextUnusedPort()
        self._bokehPort=bokehPort

    def getServerPort(self):
        """@return The bokeh server port."""
        return self._bokehPort

    def runBlockingBokehServer(self, appMethod=None):
        """@brief Run the bokeh server. This method will only return when the server shuts down.
           @param appMethod The method called to create the app."""
        if appMethod is None:
            appMethod = self.app
        apps = {'/': Application(FunctionHandler(appMethod))}
        #As this gets run in a thread we need to start an event loop
        evtLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(evtLoop)
        self._server = Server(apps, port=self._bokehPort)
        self._server.start()
        #Show the server in a web browser window
        self._server.io_loop.add_callback(self._server.show, "/")
        self._server.io_loop.start()

    def runNonBlockingBokehServer(self, appMethod=None):
        """@brief Run the bokeh server in a separate thread. This is useful
                  if the we want to load realtime data into the plot from the
                  main thread.
           @param appMethod The method called to create the app."""
        if appMethod is None:
            appMethod = self.app
        self._serverThread = threading.Thread(target=self.runBlockingBokehServer, args=(appMethod,))
        self._serverThread.setDaemon(True)
        self._serverThread.start()
        
    def app(self, doc):
        """@brief Start the process of creating an app.
           @param doc The document to add the plot to."""
        raise NotImplementedError("app() method not implemented by {}".format(self.__class__.__name__))
    
class GUIModel_A(SingleAppServer):
    """@brief This class is responsible for providing a mechanism for creating a GUI as
              simply as possible with some common features that can be updated dynamically.

              These common features are currently.
              1 - A widget at the bottom of the page for saving the state of the page to an
                HTML file. This is useful when saving the states of plots as the HTML files
                can be distributed and when recieved opened by users with their web browser.
                When opened the plots can be manipulated (zoom etc).
              2 - A status bar at the bottom of the page."""

    UPDATE_POLL_MSECS               = 100
    BOKEH_THEME_CALIBER             = "caliber"
    BOKEH_THEME_DARK_MINIMAL        = "dark_minimal"
    BOKEH_THEME_LIGHT_MINIMAL       = "light_minimal"
    BOKEH_THEME_NIGHT_SKY           = "night_sky"
    BOKEH_THEME_CONTRAST            = "contrast"
    BOKEH_THEME_NAMES               = (BOKEH_THEME_CALIBER,
                                       BOKEH_THEME_DARK_MINIMAL,
                                       BOKEH_THEME_DARK_MINIMAL,
                                       BOKEH_THEME_NIGHT_SKY,
                                       BOKEH_THEME_CONTRAST)
    DEFAULT_BOKEH_THEME             = BOKEH_THEME_NAMES[0]

    def __init__(self, docTitle, 
                 bokehServerPort=SingleAppServer.GetNextUnusedPort(),
                 includeSaveHTML=True,
                 theme=DEFAULT_BOKEH_THEME,
                 updatePollPeriod=UPDATE_POLL_MSECS):
        """@Constructor.
           @param docTitle The title of the HTML doc page.
           @param includeSaveHTML If True include widgets at the bottom of the web page for saving it as an HTML file.
           @param theme The theme that defines the colours used by the GUI (default=caliber). BOKEH_THEME_NAMES defines the
                        available themes.
           @param updatePollPeriod The GUI update poll period in milli seconds. 
           @param bokehServerPort The TCP port to bind the server to."""
        super().__init__(bokehPort=bokehServerPort)
        self._docTitle              = docTitle          # The HTML page title shown in the browser window.
        self._includeSaveHTML       = includeSaveHTML   # If True then the save HTML page is displayed at the bottom of the web page.
        self._theme                 = theme             # The theme that defines the colors used by the GUI.
        self._updatePollPeriod      = updatePollPeriod  # The GUI poll time in milli seconds.
        self._appInitComplete       = False             # True when the app is initialised
        self._lastUpdateTime        = time()            # A timer used to show the user the status of the data plot as it can take a while for bokeh to render it on the server.
        self._plotDataQueue         = queue.Queue()     # The queue holding rows of data to be plotted and other messages passed into the GUI thread inside _update() method.
        self._guiTable              = []                # A two dimensional table that holds the GUI components in a grid.
        self._uio                   = None              # A UIO instance for displaying update messages on stdout. If left at None then no messages are displayed.
        self._updateStatus          = True              # Flag to indicate if the status bar should be updated.
        self._htmlFileName          = "plot.html"       # The default HTML file to save.

    def send(self, theDict):
        """@brief Send a dict to the GUI. This method must be used to send data to the GUI
                  thread as all actions that change GUI components must be performed inside
                  the GUI thread. The dict passed here is the same dict that gets passed
                  to the self._processDict(). This allows subclasses to receive these
                  dicts and update the GUI based on the contents.
           @param theDict A Dict containing data to update the GUI."""
        self._plotDataQueue.put(theDict)

    def setUIO(self, uio):
        """@brief Set a UIO instance to display info and debug messages on std out."""
        self._uio = uio

    def setHTMLSaveFileName(self, defaultHTMLFileName):
        """@brief Set the HTML filename to save.
           @param defaultHTMLFileName The default HTML filename to save."""
        self._htmlFileName = defaultHTMLFileName

    def app(self, doc):
        """@brief Start the process of creating an app.
           @param doc The document to add the plot to."""
        self._doc = doc
        self._doc.title = self._docTitle
        self._doc.theme = self._theme
        # The status bar can be added to the bottom of the window showing status information.
        self._statusBar = StatusBarWrapper()
        #Setup the callback through which all updates to the GUI will be performed.
        self._doc.add_periodic_callback(self._update, self._updatePollPeriod)

    def _info(self, msg):
        """@brief Display an info level message on the UIO instance if we have one."""
        if self._uio:
            self._uio.info(msg)

    def _debug(self, msg):
        """@brief Display a debug level message on the UIO instance if we have one."""
        if self._uio:
            self._uio.debug(msg)

    def _internalInitGUI(self):
        """@brief Perform the GUI initalisation if not already performed."""
        if not self._appInitComplete:
            self._initGUI()
            if self._includeSaveHTML:
                self._addHTMLSaveWidgets()
            self._guiTable.append([self._statusBar.getWidget()])
            gp = gridplot( children = self._guiTable, sizing_mode='stretch_width', toolbar_location="above", merge_tools=True)
            self._doc.add_root( gp )
            self._appInitComplete = True

    def _initGUI(self):
        """@brief Setup the GUI before the save HTML controls and status bar are added.
           This should be implemented in a subclass to setup the GUI before it's updated.
           The subclass must add GUI components/widgets to self._guiTable as this is added
           to a gridplot before adding to the root pane."""
        raise NotImplementedError("_initGUI() method not implemented by {}".format(self.__class__.__name__))

    def _processDict(self, theDict):
        """@brief Process a dict received from the self._plotDataQueue inside the GUI thread.
                  This should be implemented in a subclass to update the GUI. Typically to add
                  data to a plot in realtime. """
        raise NotImplementedError("_processDict() method not implemented by {}".format(self.__class__.__name__))

    def _update(self, maxBlockSecs=1):
        """@brief called periodically to update the plot traces.
           @param maxBlockSecs The maximum time before this method returns."""
        callTime = time()

        self._internalInitGUI()

        self._showStats()

        #While we have data to process
        while not self._plotDataQueue.empty():

            #Don't block the bokeh thread for to long while we process dicts from the queue or it will crash.
            if time() > callTime+maxBlockSecs:
                self._debug("Exit _update() with {} outstanding messages after {:.1f} seconds.".format( self._plotDataQueue.qsize(), time()-callTime ))
                break

            objReceived = self._plotDataQueue.get()

            if isinstance(objReceived, dict):
                self._processDict(objReceived)

        #If we have left some actions unprocessed we'll handle them next time we get called.
        if self._plotDataQueue.qsize() > 0:
            self._setStatus( "Outstanding GUI updates: {}".format(self._plotDataQueue.qsize()) )
            self._updateStatus = True

        elif self._updateStatus:
            self._setStatus( "Outstanding GUI updates: 0" )
            self._updateStatus = False

    def _addHTMLSaveWidgets(self):
        """@brief Add the HTML save field and button to the bottom of the GUI."""
        saveButton = Button(label="Save HTML File", button_type="success", width=50)
        saveButton.on_click(self._savePlot)

        self.fileToSave = TextInput(title="HTML file to save")

        self.fileToSave.value = os.path.join(getHomePath(), self._htmlFileName)

        self._guiTable.append([self.fileToSave])
        self._guiTable.append([saveButton])

    def _savePlot(self):
        """@brief Save an html file with the current GUI state."""
        try:
            if len(self.fileToSave.value) > 0:
                fileBasename = os.path.basename(self.fileToSave.value)
                filePath = self.fileToSave.value.replace(fileBasename, "")
                if os.path.isdir(filePath):
                    if os.access(filePath, os.W_OK):
                        msg = "Saving {}. Please wait...".format(self.fileToSave.value)
                        self._info(msg)
                        self._setStatus(msg)
                        output_file(filename=self.fileToSave.value, title="LPTest Static HTML file")
                        save(self._doc)
                        self._setStatus( "Saved {}".format(self.fileToSave.value) )
                    else:
                        self._setStatus( "{} exists but no write access.".format(filePath) )
                else:
                    self._setStatus( "{} path not found.".format(filePath) )
            else:
                self._statusBar.setStatus("Please enter the html file to save.")
        except Exception as ex:
            self._statusBar.setStatus( str(ex) )

    def _setStatus(self, msg):
        """@brief Set the display message in the status bar at the bottom of the GUI.
           @param msg The message to be displayed."""
        self._statusMsg = msg
        self._statusBar.setStatus(self._statusMsg)

    def _showStats(self):
        """@brief Show the current outstanding message count so that user user is aware if the GUI
                  is taking some time to update."""
        if time() > self._lastUpdateTime+10:
            self._debug("Updating GUI: Outstanding messages = {}".format( self._plotDataQueue.qsize()) )
            self._lastUpdateTime = time()
