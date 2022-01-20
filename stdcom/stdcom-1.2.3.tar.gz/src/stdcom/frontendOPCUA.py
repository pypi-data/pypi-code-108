#!/usr/bin/python3

#  Copyright (C) 2021 Vremsoft LLC and/or its subsidiary(-ies).
#  All rights reserved.
#  Contact: Laura Chapman  (edc@vremsoft.com)
#  Commercial Usage
#  Licensees holding valid Vremsoft LLC licenses may use this file in
#  accordance with the License Agreement provided with the
#  Software or, alternatively, in accordance with the terms contained in+`
#  a written agreement between you and Vremsoft. LLC
#
import sys, re
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None

from frontend import *
from PyQt5.QtWidgets import QDialog, QApplication, QTabWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtCore import QSettings, QVariant, Qt, QEvent
from PyQt5.Qt import pyqtSlot, pyqtSignal
from stdcomqt5 import *
from opcua import ua, Server, uamethod
#from opcua.common.callback import CallbackType
#import copy


class Tree (object) :
    """
    Simple Itor functionallity for traversing names or data
    """

    cb = None

    def __init__(self, cb):
        super().__init__()
        self.cb = cb

    def addname(self, name, data = None):
        """

        :param name:  Names coming in
        :param data:  Data if uses as data itor
        :return:
        """
        key = re.split(r'[.;:,\s]\s*', name)

        if len(key) >= 0:
            word = key[0]
            parent = None

            try:
                idx = word.index('//')
                if idx == 0:
                    rdx = word.rindex('/')
                    word = word[idx:rdx]
                    if self.cb is not None:
                        newname = name.replace('/', '.')
                        self.cb(word, name, newname, data)
                else:
                    if self.cb is not None :
                        self.cb(key[0], name, name, data )
            except:
                if self.cb is not None :
                    self.cb(key[0], name, name, data )


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    """
    data  = None
    firstTime = True

    def __init__(self,  name : str, cBridge : stdcomPyQt ) :
        """

        :param name: Name of the publication
        :param cBridge:    The cBridge
        """
        self.Name = name
        self.cBridge = cBridge
        self.data = []
        firstTime = True

    def Same(self, l1: [], l2: []):
        """
        Determines if 2 lists are the same
        :param l1:  List 1
        :param l2:  List 2
        :return:  True is same, False if not
        """
        if len(l1) is not len(l2):
            return False
        if len(l1) == 0 or len(l2) == 0:
            return False

        for i in range(0, len(l1)):
            if l1[i] is not l2[i]:
                return False

        return True


    def write_from_multiverse(self, name : str, data : list ):
        """

        :param name: Name of publication
        :param data:   Data coming from multiverse
        :return:
        """
        self.just_in_from_multiverse = True

    def datachange_notification(self, node, val, data):

        """
        Called when opc changes data
        :param node:
        :param val:
        :param data:
        :return:
        """
        if self.firstTime == True :
            self.firstTime = False
            return

        val = list(val)
        if self.Same(val, self.data) == False :
            self.cBridge.writeValues(self.Name,val)

    def event_notification(self, event):
        print("Python: New event", event)


class StecMultiverseOPCUA(QDialog):

    """
    Stec OPCUA Server used fpr anyone whishing use or make a OPCUA Server to Multiverse
    """

    MultiverseHostname = None
    MultiversePort = None
    OPCUAEndpoint = None
    OPCUAEndpointPort = 4840
    OPCUrl = None
    OPCDest = None
    adaptor = None
    cBridge = None

    server = None

    OurUaVars = None
    OurFolders = None
    OurSubs = None
    OurClientHandlers = {}

    def __init__(self, cBridge : stdcomPyQt = None):
        """

        :param cBridge: If you are passing a cBridge and it is controlled here, pass it else it will make one
        """
        self.cBridge = cBridge
        super().__init__()
        self.ui = Ui_FrontendOPCUA()
        self.ui.setupUi(self)
        self.show()

        self.MultiverseHostname = self.ui.lineEditMultiverseHost.text()
        self.MultiversePort = int(self.ui.lineEditMultiversePort.text())
        self.OPCUAEndpointPort = int(self.ui.lineEditOpcUAPort.text())
        self.OPCUAEndpoint = self.ui.lineEditOPCUAEndpoint.text()
        self.OPCUrl = self.ui.lineEditUrl.text()

        self.ui.pushButtonSave.clicked.connect(self.SaveConfig)
        self.ui.pushButtonClose.clicked.connect(self.slotButtonClose)
        self.ui.pushButtonDelete.clicked.connect(self.DeleteRows)

        self.adaptor = Tree(self.EachName)
        self.adaptorData = Tree(self.EachData)
        if self.cBridge is None :
            self.cBridge = stdcomPyQt()

        self.cBridge.sigNames.connect(self.slotNames)
        self.cBridge.sigNewData.connect(self.slotNewData)
        self.LoadConfig()
        self.resetAll()



    def resetAll(self):
        """
        Internal Use
        :return:
        """
        if self.server is not None:
            self.server.stop()
            del self.server

        if self.OurFolders is not None :
            self.OurFolders.clear()

        if self.OurUaVars is not None :
            self.OurUaVars .clear()

        if self.OurSubs is not None :
            self.OurSubs.clear()

        if self.OurClientHandlers is not None :
            self.OurClientHandlers.clear()

        self.LoadConfig()
        self.server = Server()
        endPoint = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
        endPoint = self.OPCDest

        self.server.set_endpoint(endPoint)

        # setup our own namespace, not really necessary but should as spec
        uri = "http://examples.freeopcua.github.io"
        uri = self.OPCUrl
        self.idx = self.server.register_namespace(uri)

        # set all possible endpoint policies for clients to connect through
        self.server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign])

        self.server.set_server_name("Multiverse NextStep Server")

        # get Objects node, this is where we should put our nodes
        self.objects = self.server.get_objects_node()

        self.myobj = self.objects.add_object(self.idx, "Stec Multiverse")
        self.myvar1 = self.myobj.add_variable(self.idx, "NextStep Configuration", [ str(self.MultiverseHostname), str(self.MultiversePort)  ])
   #     self.myvar1.set_writable()  # Set MyVariable to be writable by clients

        # starting!
        self.server.start()

        if self.cBridge is not None:
            self.cBridge.terminate()

        self.cBridge.setDestination(self.MultiverseHostname, self.MultiversePort)
        self.cBridge.LoadcBridge()

    def createEndpoint(self):
        """
        Builds an endpoint from ip and name internal use
        :return:
        """
        self.OPCDest = "opc.tcp://" + str(self.OPCUAEndpoint) + ":" + str(self.OPCUAEndpointPort)  +"/freeopcua/server/"
        self.ui.lineEditEndPointFull.setText( self.OPCDest )

    def closeEvent(self, event: QEvent = None):
        """
        internal use
        :param event:
        :return:
        """
        if self.cBridge is not None:
            self.Terminate()
            self.cBridge = None
        event.accept()

    def allowed(self, name : str ):
        """
        :param name: Name from setup to determine if we can use it
        :return:
        """
        if name in self.OurUaVars.keys():
            vals = self.OurUaVars[name]
            return str(vals[0]), str(vals[1]), str(vals[2])

        return None, None, None

    def EachName(self, key, name, nameCorrected, data):

        """
        The itor function for each name when it comes it
        :param key:
        :param name:
        :param nameCorrected:
        :param data:
        :return:
        """
        if self.OurUaVars is None:
            self.OurUaVars = {name: [False, True, None]}
            self.InsertRow(name)

        elif name not in self.OurUaVars:
            self.OurUaVars.update({name: [False, True, None]})
            self.InsertRow(name)

        if self.OurFolders is None :
            myfolder = self.objects.add_folder(self.idx, key)
            self.OurFolders = {key : myfolder}

        elif key not in self.OurFolders.keys() :
            myfolder = self.objects.add_folder(self.idx, key)
            self.OurFolders.update( {key : myfolder })

        else :
            myfolder = self.OurFolders[key]

        myvar = None
        subscribe, readOnly, freq = self.allowed(name)

        if subscribe is None or readOnly is None:
            return

        if str(subscribe.upper()) == "TRUE":
            self.cBridge.subscribe(name)
            myvar = myfolder.add_variable(self.idx, nameCorrected, ["Waiting"])

            if self.OurSubs is None :
                self.OurSubs = {name : [myvar, None]}
            else :
                self.OurSubs.update( {name: [myvar, None]} )

            if readOnly.upper() == "FALSE":
                myvar.set_writable()
                handler = SubHandler(name,self.cBridge)
                sub = self.server.create_subscription(5, handler)
                handle = sub.subscribe_data_change(myvar)
                self.OurClientHandlers.update({name:handler })


    def EachData(self, key, name, nameCorrected, data ):

        """
        Data itor when data comes in from multiverse that we are subscribed to
        :param key:
        :param name:
        :param nameCorrected:
        :param data:
        :return:
        """
        if self.OurFolders is None or key not in self.OurFolders.keys():
            self.EachName( key, name, nameCorrected, data )


        if name in self.OurClientHandlers :
            handle = self.OurClientHandlers[name].data = data


        if name in self.OurSubs and data is not None :
            vars = self.OurSubs[name]
            myvar = vars[0]
            myvar.set_value(data)


    def InsertRow(self, name,  enabled : str = "False",  readonly : str = "True", freq = str(5)):

        """
        Inserts a row with a subscription possibility to the table
        :param name:
        :param enabled:
        :param readonly:
        :param freq:
        :return:
        """
        rows = self.ui.tableWidgetAllowable.rowCount()
        self.ui.tableWidgetAllowable.insertRow(rows )

        itm1 = QTableWidgetItem()
        itm1.setText(name)

        itm4 = QTableWidgetItem()
        itm4.setText(str(freq))


        bxt1 = QCheckBox( str(enabled))
        if str(enabled).upper() == "TRUE" :
            bxt1.setChecked(True)

        bxt2 =  QCheckBox(str(readonly))
        if str(readonly).upper() == "TRUE":
            bxt2.setChecked(True)

        self.ui.tableWidgetAllowable.setItem(rows, 0, itm1)
        self.ui.tableWidgetAllowable.setItem(rows, 3, itm4)

        self.ui.tableWidgetAllowable.setCellWidget(rows, 1,bxt1)
        self.ui.tableWidgetAllowable.setCellWidget(rows, 2, bxt2)


    def UpdateAllowedScreen(self):
        """
        Tells the screen what should be allowed
        :return:
        """
        self.ui.tableWidgetAllowable.setRowCount(0)
        self.ui.tableWidgetAllowable.setHorizontalHeaderLabels(["Subscription", "Allowed", "ReadOnly","Freq"])
        keys = self.OurUaVars.keys()
        for key in keys:
            val = self.OurUaVars[key]
            if len(val) >= 3 :
                if val[2] is None :
                    val[2] = 5

                self.InsertRow(str(key), val[0], val[1], val[2])

    def RebuildAllowed(self):

        """
        gets data from the screen and makes a maps of what to subscribe to
        :return:
        """
        rows = self.ui.tableWidgetAllowable.rowCount()
        allowed = {}
        for r in range(0, rows) :
            name = self.ui.tableWidgetAllowable.item(r,0).text()

            bxt1 = self.ui.tableWidgetAllowable.cellWidget(r,1)
            if bxt1.isChecked() :
                allow = "True"
            else:
                allow = "False"

            bxt2 = self.ui.tableWidgetAllowable.cellWidget(r, 2)
            if bxt2.isChecked():
                readonly = "True"
            else:
                readonly = "False"


            timeing = self.ui.tableWidgetAllowable.item(r, 3).text()
            allowed.update( { name: [allow,readonly,None ]})

        self.OurUaVars = allowed

    @pyqtSlot()
    def Terminate(self):
        """
        terminated thread and shuts it all down
        :return:
        """
        if self.cBridge is not None:
            self.cBridge.terminate()
            self.cBridge = None

        if self.server is not None:
            self.server.stop()
            self.server = None

    @pyqtSlot(list)
    def slotNames(self, names):
        """

        :param names: names as they come in from multiverse
        :return:
        """
        for name in names :
            self.adaptor.addname(name, None)

    @pyqtSlot(str, list)
    def slotNewData(self, name, data):
        """
        data as it comes in from Multiverse
        :param name:
        :param data:
        :return:
        """
        self.adaptorData.addname(name,data)


    @pyqtSlot()
    def slotButtonClose(self):
        """
        Close from screen
        :return:
        """
        if self.cBridge is not None :
            self.Terminate()
            self.cBridge = None
        self.deleteLater()

    @pyqtSlot()
    def SaveConfig(self):

        """
        Saves all setup data
        :return:
        """

        self.RebuildAllowed()
        settings = VSettings()

        self.MultiverseHostname = self.ui.lineEditMultiverseHost.text()
        self.MultiversePort = int(self.ui.lineEditMultiversePort.text())
        self.OPCUAEndpointPort = int(self.ui.lineEditOpcUAPort.text())
        self.OPCUAEndpoint = self.ui.lineEditOPCUAEndpoint.text()
        self.OPCUrl = self.ui.lineEditUrl.text()

        settings.setValue( 'MultiverseHostname', self.MultiverseHostname)
        settings.setValue( 'MultiversePort', self.MultiversePort)
        settings.setValue( "Endpoint", self.OPCUAEndpoint)
        settings.setValue( "EndpointPort", self.OPCUAEndpointPort )
        settings.setValue( 'OurAllows', self.OurUaVars )
        settings.setValue("URL", self.OPCUrl)
        settings.sync()
        self.cBridge.terminate()
        self.UpdateAllowedScreen()
        self.cBridge.setDestination(self.MultiverseHostname, self.MultiversePort)
        self.createEndpoint()
        self.resetAll()

    @pyqtSlot()
    def LoadConfig(self):
        """
        loads all configurations
        :return:
        """
        settings = VSettings()
        self.MultiverseHostname = str(settings.value("MultiverseHostname", self.MultiverseHostname))
        self.MultiversePort = int(settings.value("MultiversePort", self.MultiversePort))
        self.OPCUAEndpoint =  str(settings.value("Endpoint", self.OPCUAEndpoint))
        self.OPCUAEndpointPort = int(settings.value("EndpointPort", self.OPCUAEndpointPort))
        self.OPCUrl =  str(settings.value("URL", self.OPCUrl))

        if self.OurUaVars is None :
            self.OurUaVars = {"None": [False, True, 5]}


        self.OurUaVars = settings.value('OurAllows', self.OurUaVars)

        self.ui.lineEditMultiverseHost.setText(self.MultiverseHostname)
        self.ui.lineEditMultiversePort.setText(str(self.MultiversePort))
        self.ui.lineEditOpcUAPort.setText(str(self.OPCUAEndpointPort))
        self.ui.lineEditOPCUAEndpoint.setText(self.OPCUAEndpoint)

        self.UpdateAllowedScreen()
        self.ui.lineEditUrl.setText( self.OPCUrl)
        self.createEndpoint()

    @pyqtSlot()
    def DeleteRows(self):
        """
        deletes a selected row
        :return:
        """
        index_list = []
        for model_index in self.ui.tableWidgetAllowable.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index.row())

        for index in index_list:
            self.ui.tableWidgetAllowable.removeRow(index)


if __name__ == "__main__":
    """
    bumped version
    """
    if "--version" in sys.argv:
        print("1.2.3")
        sys.exit()

    show = True
    nextProject = False
    project = None

    app = QApplication(sys.argv)

    window = StecMultiverseOPCUA(project)
    window.setWindowTitle("Stec OPCUA Server")

    if '--hide' in sys.argv:
        print("Hidden Display")
        window.hide()
    else:
        window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec_()
    window.Terminate()

