from PyQt5.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot, QSettings
from stdcom import *

"""
    This is where Stec QObject are kept, this are not QWidgets
"""
class VSettings(QSettings):
    """
    Used to save setup data
    """
    def __init__(self, project : str = "stec-opcua"):
        """
        :param project:   default is "stec-opc" Should be the Project you or instance of the Project
        """
        super().__init__( project, QSettings.IniFormat)


class stdcomPyQt(QObject):
    """
    The stdcomPyQt class is a PyQt5 version that sits on top of stdcom, can has signals, slots, and auto restart capabilities build into it.
        :uiparent: QObject = None default, or the parent QObject
    """


    sigNewData = pyqtSignal(str, list)
    sigNames = pyqtSignal(list)
    sigConnect = pyqtSignal()
    sigNoConnect = pyqtSignal()
    sigBalanceTable = pyqtSignal()

    cBridge = None
    Parent = None
    liveSubnames = []

    watchDogSeconds = 5

    # this is a duplicate, but it allows us to stay running if the Links to Multiverse is down..
    liveData = {}
    timer = None
    MultiverseHostname = "192.168.199.7"
    MultiversePort = 4897

    def __init__(self, uiparent: QObject = None):
        """

        :param uiparent: QObject of the parent or None
        """
        if uiparent is not None:
            super().__init__(uiparent)
        else:
            super().__init__()

        self.Parent = uiparent
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.RestartAttmepts)
        self.timer.setInterval(self.watchDogSeconds * 1000)

    def setWatchDogIntervalSec(self, seconds: int = 5):
        """
        Sets the watchdog timer in seconds. This can be adjusted if the Multiverse in on the internet and thousands of miles away.
            :seconds: Default is 5 seconds, make this longer if huge internet delay
        """

        self.watchDogSeconds = seconds
        self.timer.setInterval(self.watchDogSeconds * 1000)

    def readValues(self, Name: str):
        """
        Reads values cached for a single subscription name that is given and has been subscribed to.
            :Name: Name of the subscription
            :return: list of data for a given subscrition, or None if not available
        """
        if Name in self.liveData.keys():
            return self.liveData.get(Name)
        return None

    def writeValues(self, Name: str, Data: list):

        """
        WritesValues to multiverse if subcription is made, or local data is ~/ is the prefix
            :Name: The name of the subscription, if ~/ is the prefix, then data is local.
            :Data: Is a list[] of data

        """
        if Name in self.liveData.keys():
            self.liveData.update({Name: Data})
            if self.cBridge is not None and Data is not None:
                Data = list(Data)
                if len(Data):
                    self.cBridge.UpdateRaw(Name, Data, 0)

            # allow the system to operate without Multiverse
            else:
                self.sigNewData.emit(Name, Data())

    def subscribe(self, Name: str):
        """
        Subscribe to a give Name
            :Name: The subscription name

        """
        if Name not in self.liveData.keys():
            self.liveData.update({Name: []})
            if self.cBridge is not None:
                self.cBridge.AddSubscriptions([Name])

    def getPossibleSubscribesr(self):
        """
        All the possible subscription names possible
           :return: list of names of all possible subscritions
        """

        return self.liveSubnames

    def getSubscribers(self):
        """
        All the stuff subscribed to
            :return: A list of all the subscription names we have subscribed to
        """
        return list(self.liveData.keys())

    def unsubscribe(self, Name):
        """
        UnSubscribe to something previously subscribed to.
            :Name: The name of the Subscription to delete
        """
        if Name in self.liveData.keys():
            del self.liveData[Name]
            if self.cBridge is not None:
                self.cBridge.RemoveSub(Name)

    def AddValues(self, sub):
        """
        Internal use, updates makes and notfies by signal data has changed for a subcription
            :sigNewData.emit: Name, Data
        """
        self.liveData.update({sub.Name(): sub.Data()})
        self.sigNewData.emit(sub.Name(), sub.Data())


    def AddNames(self, values):
        """
        Internal use tell when a new name is found, with emit
            : sigNames.emit: list[str] of new names entering the picture that can be subscribed to
        """
        print("AddNames")
        self.sigNames.emit(values)

    def ConnectSocket(self, v):
        """
        Socket connection call back, for internal use
            :sigConnect.emit: emits the signal if connection happens
        """
        self.sigConnect.emit()
        print(v)

    def ConnectionError(self):
        """
         Socket error connection call back, for internal use
            :sigNoConnect.emit: emits the signal if connection error or close happens
        """
        self.sigNoConnect.emit()
        print("Connection Error")

    def setDestination(self, dest, port):
        """
        Sets a new Destination and port, the user must terminate amd loadbridge again after changing is connected.
        """
        self.MultiverseHostname = dest
        self.MultiversePort = port

    def LoadcBridge(self):
        """
        User calls this to start the ball rolling to the connection to multiverse providing the destination and port are set correctly.
        """

        if self.cBridge is not None:
            self.liveSubnames = []
            self.cBridge.terminate()
            self.sigNames.disconnect(self.NewLiveTags)

        try:

            self.cBridge = stdcom(self.MultiverseHostname, self.MultiversePort, self.ConnectSocket, None, None,
                                  self.ConnectionError)

            self.cBridge.SetCallbacks(self.AddValues, self.AddNames)
            self.cBridge.NamesOn()  # tell the communication class to tu
            self.sigNames.connect(self.NewLiveTags)
            self.sigConnect.emit()

            subs = list(self.liveData.keys())

            if subs is not None and len(subs) > 0:
                self.cBridge.AddSubscriptions(subs)
            else:
                print("No Subscriptions to Add")

            self.timer.start()

        except  ConnectionError as e:
            print("Need To Set Correct IP and Port")
            self.cBridge = None
            self.sigNoConnect.emit()

    # ----- from threads
    def terminate(self):
        """
        Cridical the user called this function when leaving .. I closes down the thread connected to multiverse
        """
        if self.cBridge is not None:
            self.timer.stop()
            self.cBridge.terminate()
            self.cBridge = None
            self.sigNoConnect.emit()

    @pyqtSlot(str, list)
    def slotUpdateData(self, Name, Data):
        self.writeValues(Name, Data)

    @pyqtSlot(list)
    def NewLiveTags(self, names):
        self.liveSubnames = self.liveSubnames + names

    @pyqtSlot()
    def RestartAttmepts(self): # todo needs better logic, this works but logic is weak and needs something besides order and 1 default
        if self.cBridge is None or self.cBridge.isConnected() is False:
            self.LoadcBridge()
        elif self.cBridge != None:
            acks = self.cBridge.GetAcks()
            print("ACKS: ", acks)
            if acks == 0:
                self.LoadcBridge()
            else:
                self.cBridge.Ping()


if __name__ == "__main__":

    from PyQt5.QtCore import QCoreApplication
    import sys

    if "--version" in sys.argv:
        print("1.2.2")
        sys.exit()

    app = QCoreApplication(sys.argv)
    w = stdcomPyQt()
    w.LoadcBridge()
    app.exec_()
    w.terminate()
    sys.exit(0)
