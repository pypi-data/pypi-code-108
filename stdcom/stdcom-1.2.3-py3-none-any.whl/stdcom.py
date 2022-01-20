import csv
import queue
import socket
import threading
from threading import Thread

"""

"""
class Subscription:
    """
        Class Passed Around by data coming from Multiverse, Note most of the time will be in its own thread, so copy the data before use

    """

    def __init__(self):
        self._name = None
        self._data = None

    def Name(self):
        """
            returns the name of the subscription
        """
        return self._name

    def Data(self):
        """
        Returns a list of the data
        """
        return  self._data

    def SetData(self, name, data):
        """
            Sets the class full of information
                :name: the name of the subscription
                :data: a list of the data
        """

        self._name = name
        self._data = data


class stdcom:

    """
        Threaded communication class to Multiverse, Standard Communication Class.  This is a stand alone class that does not retuire
        PyQt5

         :Host:  Name, or IP address where the Nextstep plugin is running
         :Port:  ServicePort where the NextStep plugin is listening
         :Connected: Callback  arg(Bool)
         :Data: Callback, where all the subscription comes in where it changes  Callback(Subscription)
         :Names: Call Back, where all possible names come in  Callabck(str)
         :Error: Callback  Callback()

    """


    _Callback = None
    _NCallback = None
    _ECallback = None

    nbrAcks = 1
    isopen = False

    def Start(self):
        """
        Start used interally when constructed starts the thread
        """

        self.conditionValue = threading.Condition()
        self.conditionValue = threading.Lock()
        self._t = Thread(target=self.run)
        self._t.start()

    def __init__(self, ipaddress, port, connectedFunction  =None, Callback=None, NCallback=None, ECallback = None):

        self._running = True
        self.activeData = {"": []} # todo need a way to stop collecting it down higher up
        self._outQueue = queue.Queue()
        self._outNameList = list()
        self.s = None
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            if self._ECallback != None :
                self._ECallback()

        self.HOST = ipaddress
        self.PORT = int(port)

        self._Callback = Callback
        self._NCallback = NCallback
        self._ECallback = ECallback
        self.connectedCallback = connectedFunction

        try:
            self.s.connect((self.HOST, self.PORT))


        except OSError as e:
            print("Caught exception socket.error : ", e)
            self.isopen = False
            self.s = None
            if self._ECallback != None :
                self._ECallback()

        if self.s is None:
            print("could not open socket")
            raise ConnectionError('Represents a hidden bug, do not catch this')
        else:
            self.isopen = True
            print("Connecting", self.HOST, ":", self.PORT)
            self.Start()
            if self.connectedCallback != None:
                self.connectedCallback(True)

    def UpDateMap(self, name, data):
        """
        Internal Use for stuffing data
            :name:  Subscription name
            :data:  Date coming from Multiverse
        """

        with self.conditionValue:
            self.activeData.update({name: data})

    def ReadValues(self, name):

        """
        Reads data for a given name, returns a list of data, the data that is cached from normal running operation to subscription changes.
            :name: The subscriber name
            :return:
        """

        data = []
        toDo = []
        with self.conditionValue:
            if name in self.activeData:
                data = self.activeData.get(name)
            else:
                toDo.append(name)

        if len(toDo):
            self.AddSubscriptions(toDo)
        return data

    def SetCallbacks(self, callback = None, namecallback = None):

        """
        SetCallbacks  sets the Data and
            :callback: Data Callback( Subscription)
            :namecallback: Name Callback(str)
        """
        with self.conditionValue:
            self._Callback = callback
            self._NCallback = namecallback

    def terminate(self):

        """
        Stops the thread,
        """

        with self.conditionValue:
            self._running = False
            self.s.close()
            self._t.join()
            print("Closing")

    def NamesOn(self):

        """
        Turns the names on in the Multiverse Plugin, allowing all possible names to come from Multiverse platform
        """

        command = "NAMES\n"
        with self.conditionValue:
            try:
                self.s.send(command.encode("ascii"))
            except OSError as e:
                print("Caught exception socket.error : ", e)
                self.isopen = False
                if self._ECallback != None:
                    self._ECallback()

    def GetErrors(self):
        """
        Returns the status of the socket
            :return: False is connection is ok
        """

        with self.conditionValue:
            return self.isopen

    def isConnected(self):
        """
        Returns the status of the socket, same as getErrors()
            :return: False is connection is ok
        """
        with self.conditionValue:
            return self.isopen

    def RemoveSub(self, who : str):
        """
        Remove a Subscription previously made
            :who:  the name of the subscrition
        """
        with self.conditionValue:
            if who in self.activeData:
                command = "REMOVESUB," + who
                command += "\n"
                try:
                    self.s.send(command.encode("ascii"))
                except OSError as e:
                    print("Caught exception socket.error : ", e)
                    self.isopen = False
                    if self._ECallback != None:
                        self._ECallback()

                del self.activeData[who]


    def Ping(self):

        """
        Pings the host, will except if socket in error or not open
        """

        command = "PING\n"
        with self.conditionValue:
            try:
                self.s.send(command.encode("ascii"))
            except OSError as e:
                print("Ping Caught exception socket.error : ", e)
                self.isopen = False
                if self._ECallback != None:
                    self._ECallback()

    def ReadData(self, who):
        """
        Reads data of a subscription directly from Multiverse
            :who: The name of the subscription
        """
        command = "READDATA," + who
        command += "\n"
        with self.conditionValue:
            try:
                self.s.send(command.encode("ascii"))
            except OSError as e:
                print("Caught exception socket.error : ", e)
                self.isopen = False
                if self._ECallback != None:
                    self._ECallback()

    def UpdateLocalData(self, name, data):
        # Usaed internally if the subscription is designed to be local

        sub = Subscription()
        sub.SetData(name, data)
        with self.conditionValue:
            CB = self._Callback
        if CB == None:
            self._outQueue.put(sub)
        if CB:
            CB(sub)

    def UpdateAsInt(self, who, what, index = 0):

        """
        Updates Data as int, to Multiverse no need for caller to recast to int..  ~/name will assume internal subscription does not participate with Multiverse
            :who:    Name of the subscription
            :what:   list[int]
            :where: to begin to change into the array,

        """

        if str(who).startswith('~/'):
            self.UpdateLocalData(who, what)
        else:
            command = "UPDATEI," + who + "," + str(index)
            for word in what:
                command += "," + str(word)
            command += "\n"
            with self.conditionValue:
                try:
                    self.s.send(command.encode("ascii"))
                except OSError as e:
                    print("Caught exception socket.error : ", e)
                    self.isopen = False
                    if self._ECallback != None:
                        self._ECallback()

    def UpdateAsBool(self, who, what, index):
        """
        Updates Data as Bool, to Multiverse no need for caller to recast to Bool..  ~/name will assume internal subscription does not participate with Multiverse
            :who:   Name of the subscription
            :what:  list[Bool]
            :where: to begin to change into the array,

        """

        if str(who).startswith('~/'):
            self.UpdateLocalData(who, what)
        else:
            command = "UPDATEB," + who + "," + str(index)
            for word in what:
                command += "," + str(word)
            command += "\n"
            with self.conditionValue:
                try:
                    self.s.send(command.encode("ascii"))
                except OSError as e:
                    print("Caught exception socket.error : ", e)
                    self.isopen = False
                    if self._ECallback != None:
                        self._ECallback()

    def UpdateAsFloat(self, who, what, index):

        """
        Updates Data as Float, to Multiverse no need for caller to recast to Float..  ~/name will assume internal subscription does not participate with Multiverse
            :who:  Name of the subscription
            :what: list[Float]
            :where: to begin to change into the array,

        """

        if str(who).startswith('~/'):
            self.UpdateLocalData(who, what)
        else:
            command = "UPDATEF," + who + "," + str(index)
            for word in what:
                command += "," + str(word)
            command += "\n"
            with self.conditionValue:
                try:
                    self.s.send(command.encode("ascii"))
                except OSError as e:
                    print("Caught exception socket.error : ", e)
                    self.isopen = False
                    if self._ECallback != None:
                        self._ECallback()

    def UpdateRaw(self, who, what, index):

        """
        Updates Data as when is passed, to Multiverse user should recast to desired type()  ~/name will assume internal subscription does not participate with Multiverse
            :who:   Name of the subscription
            :what:  list[type()]
            :where: to begin to change into the array,

        """

        if len(what):
            if isinstance(what[0], int):
                self.UpdateAsInt(who, what, index)
                return
            if isinstance(what[0], float):
                self.UpdateAsFloat(who, what, index)
                return
            if isinstance(what[0], bool):
                self.UpdateAsBool(who, what, index)
                return

        if str(who).startswith('~/'):
            self.UpdateLocalData(who, what)
        else:
            command = "UPDATE," + who + "," + str(index)
            for word in what:
                command += "," + str(word)
            command += "\n"
            with self.conditionValue:
                try:
                    self.s.send(command.encode("ascii"))
                except OSError as e:
                    print("Caught exception socket.error : ", e)
                    self.isopen = False
                    if self._ECallback != None:
                        self._ECallback()

    def GetNotifications(self):

        """
        If callback are not used, user can call this and it returns changed subsriptions, Use callbacks it makes more sense

            :return: list of subs that should be read if call backs are not used

        """


        with self.conditionValue:
            out = self._outQueue
            self._outQueue = queue.Queue()
            return out

    def AddSubscriptions(self, subs):
        """
        Adds a list of subscriptions
            :subs:  A list of str of subscriber names desired  subs : list[str]
         """
        data = [0]
        for word in subs:
            self.RemoveSub(word)
            with self.conditionValue:
                if word not in self.activeData:
                    self.activeData.update({word: data})
                    command = "NOTIFY," + word + "\n"
                    try:
                        self.s.send(command.encode("ascii"))
                    except OSError as e:
                        print("Caught exception socket.error : ", e)
                        self.isopen = False
                        if self._ECallback != None:
                            self._ECallback()

    def GetNames(self):
        """
        Gets the names all possible names possible to subscribe to
            :returns: List of possible names that are available at this time to subscribe to.
        """

        with self.conditionValue:
            out = self._outNameList
            return out

    def GetAcks(self):

        """
        Gets the number of Acks, used to see if the system is alive based on Pings or other actions, resets after it has been called

        :returns: Number of Acks to messages, including pings, since the last time read.
        """

        with self.conditionValue:
            nbrAcks = self.nbrAcks;
            self.nbrAcks = 1
            return  nbrAcks

    def run(self):

        """
         Internal use, thread running
        """

        self.s.settimeout(1)
        while self._running:
            scsv = None
            while self._running:
                try:
                    c = self.s.recv(1)

                except socket.error as e:
                    continue

                jv = c.decode('ascii')
                if scsv == None:
                    scsv = jv
                else:
                    scsv = scsv + jv

                if jv == '\n':
                    break


            # scsv = data.decode('ascii')
            if scsv == None:
                continue

            reader = list(csv.reader(scsv.split('\n'), delimiter=','))

            l = len(reader)

            if self._running and l >= 1:
                row = reader[0]
                if ('NAMESUP' in row[0]):
                    data = []
                    for x in range(1, len(row)):
                        data.append(row[x])
                    with self.conditionValue:
                        NCB = self._NCallback
                        if (NCB == None):
                            self._outNameList += data
                    if NCB:
                        NCB(data)

                elif 'READDATA' in row[0]:
                    if len(row) > 2:
                        name = row[1]
                        data = []
                        for x in range(2, len(row)):
                            data.append(row[x])

                        sub = Subscription()
                        sub.SetData(name, data)
                        self.UpDateMap(name, data)
                        with self.conditionValue:
                            CB = self._Callback

                            if CB == 0:
                                self._outQueue.put(sub)
                        if CB:
                            CB(sub)

                elif 'ACK' in row[0] :
                    with self.conditionValue:
                        self.nbrAcks = self.nbrAcks + 1


        self.s.close()


cBridge = None

if __name__ == "__main__":
    from time import sleep
    import sys
    if "--version" in sys.argv :
        print("1.2.2")
        sys.exit()


    def _AddNames(lnames):
        for i in range(0, len(lnames)):
            item = str(lnames[i])
            print(item)
        print("Press Enter to exit...")


    def _AddValues(sub):
        name = sub.Name()
        data = sub.Data()
        for each in data:
            print(">>>>>> ", data)
        print("Press Enter to exit...")


    # this could be argv but we will weld it for now
    XHOST = "192.168.199.7"  # we talk to ourself
    XPORT = int(4897)  # service port for NextStep plugin

    XSUBS = ["Scanner1.moisture", "Scannner1.basiswt"]
    s1 = [11110, 0, 10, 100]

    try:
        cBridge = stdcom(XHOST,
                        XPORT)  # start the ball rolling make the communication class if it fails we will die a death in lib
        cBridge.SetCallbacks(_AddValues, _AddNames)
        cBridge.NamesOn()  # tell the communication class to turn all the names so we can get every name across Multiverse
        cBridge.AddSubscriptions(XSUBS)  # add our subscriptions to multiverse

        for i in range(0, len(XSUBS)):
            cBridge.UpdateAsFloat(XSUBS[i], s1, 0)



    except:
        print("Check IP or Ensure NextStep Plugin is running")

    sleep(1)
    cBridge.terminate()
