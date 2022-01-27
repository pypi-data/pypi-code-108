# #######################
# #      SIMULATORS     #
# #######################
from pymodbus.server.sync import ModbusTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
import opcua

class Simulator():
    ''' for inheritance a simulator should have:
    - inheritance of a Device children class
    - a function "serve" that starts the serveer
    - a function "writeInRegisters" to feed the data.
    - a function "shutdown_server" to shutdown the server.
    '''
    def __init__(self,speedflowdata=50,volatilitySimu=5):
        '''
        - speedflowdata : single data trigger event in ms
        - volatilitySimu : how much random variation (absolute units)
        '''
        self.volatilitySimu = volatilitySimu
        self.speedflowdata = speedflowdata
        # self.server_thread = threading.Thread(target=self.serve)
        # self.server_thread.daemon = True
        self.feed = True
        self.stopfeed = threading.Event()
        self.feedingThread = threading.Thread(target=self.feedingLoop)

    def stop(self):
        self.stopfeed.set()
        self.shutdown_server()
        print("Server stopped")

    def start(self):
        print("Start server...")
        self.server_thread.start()
        print("Server is online")
        self.feedingThread.start()
        print("Server simulator is feeding")

    def stopFeeding(self):
        self.feed=False

    def startFeeding(self):
        self.feed=True

    def feedingLoop(self):
        while not self.stopfeed.isSet():
            if self.feed:
                start=time.time()
                self.writeInRegisters()
                print('fed in {:.2f} milliseconds'.format((time.time()-start)*1000))
                sleep(self.speedflowdata/1000 + np.random.randint(0,1)/1000)

    def is_serving(self):
        return self.server_thread.is_alive()

class SimulatorModeBus(Simulator):
    ''' can only be used with a children class inheritating from a class that has
    attributes and methods of Device.
    ex : class StreamVisuSpecial(ComConfigSpecial,SimulatorModeBus)
    with class ComConfigSpecial(Device)'''

    def __init__(self,bo='=',*args,**kwargs):
        '''
        - bo : byteorder : bigendian >, littleendian <, native =, network(big endian) !
        '''
        self.bo = bo
        Simulator.__init__(self,*args,**kwargs)
        # initialize server with random values
        self.dfInstr['value']=self.dfInstr['type'].apply(lambda x:np.random.randint(0,100000))
        self.dfInstr['precision']=0.1
        self.dfInstr['FREQUENCE_ECHANTILLONNAGE']=1
        allTCPid = list(self.dfInstr['addrTCP'].unique())
        # Create an instance of ModbusServer
        slaves={}
        for k in allTCPid:
            slaves[k]  = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [k]*128))
            self.context = ModbusServerContext(slaves=slaves, single=False)
        self.server = ModbusTcpServer(self.context, address=("", self.port))
        self.server_thread = threading.Thread(target=self.serve)
        self.server_thread.daemon = True

    def start(self):
        print("Start server...")
        self.server_thread.start()
        print("Server is online")
        self.feedingThread.start()
        print("Server simulator is feeding")

    def generateRandomData(self,idTCP):
        ptComptage = self.dfInstr[self.dfInstr['addrTCP']==idTCP]
        byteflow=[]
        values=[]
        # te = ptComptage.iloc[[0]]
        for tag in ptComptage.index:
            te = ptComptage.loc[tag]
            # print(te)
            # address = te.index[0]
            typevar = te.type
            if typevar=='INT32':
                value = int(te.value + np.random.randint(0,value*self.volatilitySimu/100))
                # conversion of long(=INT32) into 2 shorts(=DWORD=word)
                valueShorts = struct.unpack(self.bo + '2H',struct.pack(self.bo + "i",value))
            if typevar=='INT64':
                value = int(te.value + np.random.randint(0,value*self.volatilitySimu/100))
                try:
                    # conversion of long long(=INT64) to 4 short(=DWORD=word)
                    valueShorts = struct.unpack(self.bo + '4H', struct.pack(self.bo + 'q',value))
                except:
                    print(value)
            if typevar=='IEEE754':
                value = te.value + np.random.randn()*te.value*self.volatilitySimu/100
                # value = 16.565
                # conversion of float(=IEEE7554O) to 2 shorts(=DWORD)
                valueShorts=struct.unpack(self.bo + '2H', struct.pack(self.bo+'f', value))
            byteflow.append(valueShorts)
            self.dfInstr.loc[tag,'value']=value
            # values.append(value)
        # return [l for k in byteflow for l in k],values
        return [l for k in byteflow for l in k]

    def writeInRegisters(self):
        feedingClient = ModbusClient(host='localhost',port=self.port)
        feedingClient.connect()

        for idTCP in self.allTCPid:
            # print(idTCP)
            ptComptage = self.dfInstr[self.dfInstr['addrTCP']==idTCP]

            # #######
            #                   IMPORTANT CHECK HERE
            #           block should have continuous adresses with no gap!
            # #######
            # ptComptage = ptComptage[ptComptage.intAddress<10000]
            try:
                byteflow = self.generateRandomData(idTCP)
                feedingClient.write_registers(ptComptage.intAddress[0],byteflow,unit=idTCP)
            except:
                print(dt.datetime.now().astimezone())
                print('***********************************')
                print(str(idTCP) + 'problem generating random Data')
                traceback.print_exc()
                print('***********************************')

        tagtest='C00000001-A003-1-kW sys-JTW'
        print(tagtest + ' : ',self.dfInstr.loc[tagtest,'value'])
        feedingClient.close()

    def serve(self):
        self.server.serve_forever()

    def shutdown_server(self):
        self.server.shutdown()
        print("Server simulator is shutdown")

class SimulatorOPCUA(Simulator):
    ''' can only be used with a children class inheritating from a class that has
    attributes and methods of Device.
    ex : class StreamVisuSpecial(ComConfigSpecial,SimulatorOPCUA)
    with class ComConfigSpecial(Device)
    '''
    def __init__(self,*args,**kwargs):
        self.server=opcua.Server()
        self.server.set_endpoint(self.endpointUrl)
        self.nodeValues = {}
        self.nodeVariables = {}
        self.createNodes()
        Simulator.__init__(self,*args,**kwargs)

    def serve(self):
        print("start server")
        self.server.start()
        print("server Online")

    def shutdown_server(self):
        self.server.stop()

    def createNodes(self):
        objects=self.server.get_objects_node()
        self.beckhoff = objects.add_object(self.nameSpace,"Beckhoff")
        valueInits = self.createRandomInitalTagValues()
        for tag,val in valueInits.items():
            self.nodeValues[tag]    = val
            self.nodeVariables[tag] = self.beckhoff.add_variable(self.nameSpace+tag,tag,val)

    def writeInRegisters(self):
        for tag,var in self.nodeVariables.items():
            tagvar=self.dfPLC.loc[tag]
            if tagvar.DATATYPE=='REAL':
                newValue = self.nodeValues[tag] + self.volatilitySimu*np.random.randn()*tagvar.PRECISION
                self.nodeVariables[tag].set_value(newValue)
            if tagvar.DATATYPE=='BOOL':
                newValue = np.random.randint(0,2)
                self.nodeVariables[tag].set_value(newValue)
            self.nodeValues[tag] = newValue
        # tagTest = 'SEH1.STB_STK_03.HER_01_CL01.In.HR26'
        tagTest = 'SEH1.GWPBH_PMP_05.HO00'
        # tagTest = 'SEH1.STB_GFC_00_PT_01_HC21'
        # tagTest = 'SEH1.STB_STK_01.SN'
        # tagTest = 'SEH1.HPB_STG_01a_HER_03_JT_01.JTVAR_HC20'
        print(tagTest + ': ',self.nodeVariables[tagTest].get_value())
