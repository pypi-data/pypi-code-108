import json
import time
import sys
import re
try:
    import httplib as http # python 2.x
except ImportError:
    import http.client as http # python 3.x

class SynapseAPI:
    Modes = ('Idle', 'Standby', 'Preview', 'Record') #, 'Unknown'
    Persist = ('Last', 'Best', 'Fresh')

    def __init__(self, server = "localhost", port = 24414):
        self.synCon = http.HTTPConnection(server, port)
        self.lastReqStr = ''
        self.lastReqData = ''
        self.sizeTable = {}
        self.reSueTank = re.compile('subject|user|experiment|tank|block')
        self.demoExperiments = ['demoAudioStim1','demoUser1','demoPCSort','demoBoxSort','demoTetSort','demoChanMap','demoSigSelector','demoSigInjector','demoElecStim','demoFileStim','demoParSeq']
        self.demoRequiredGizmos = {'demoAudioStim1':'aStim1','demoUser1':'TagTest1','demoPCSort':'Neu1','demoBoxSort':'Box1','demoTetSort':'Tet1','demoChanMap':'Map1','demoSigSelector':'Sel1','demoSigInjector':'Inj1','demoElecStim':'eStim1','demoFileStim':'fStim1','demoParSeq':'ParSeq1'}

    def __del__(self):
        self.synCon.close()

    def connect(self):
        self.synCon.close()
        try:
            self.synCon.connect()
        except Exception as e:
            if type(e) is ConnectionRefusedError:
                print('Connection Error: make sure Synapse Server is enabled and Synapse is running.')
            else:
                raise Exception('failed to connect to Synapse\n' + str(e))

    def checkMode(self):
        if self.getMode() < 2:
            print('Synapse is not in a run-time mode')

    def cleanStruct(self, s):
        if '_return_code_' in s:
            s.pop('_return_code_')
        if '_return_msg_' in s:
            s.pop('_return_msg_')
        return s

    def exceptMsg(self):
        retval = ''

        if 'params' in self.lastReqStr:
            retval = '\nSynapse may need to be in non-Idle mode'
        elif self.reSueTank.search(self.lastReqStr) is not None:
            retval = '\nSynapse may need to be in Idle mode'

        return retval

    def getResp(self):
        retval = None

        try:
            resp = self.synCon.getresponse()

            # success
            if resp.status == 200:
                try:
                    retval = json.loads(resp.read().decode('utf-8'))

                    if '_return_code_' in retval:
                        resp.status = retval['_return_code_']

                except:
                    # no particular meaning to 404 at the moment. just want something != 200
                    resp.status = 404

            if resp.status != 200:
                print('error received from Synapse')

                if retval is not None and '_return_msg_' in retval and len(retval['_return_msg_']) > 0:
                    print(' {0} {1} {2}'.format(
                                                self.lastReqData,
                                                retval['_return_code_'],
                                                retval['_return_msg_'])
                    )
                retval = None

        except:
            print('failed to retrieve response from Synapse' + self.exceptMsg())
            self.connect()

        return retval

    def sendRequest(self, reqTypeStr, reqStr, reqData = None):
        '''
        reqTypeStr = HTTP methods, e.g. 'GET', 'PUT', 'OPTIONS'
        reqData = JSON formatted data
        '''

        try:
            if reqData is None:
                self.lastReqData = ''
                self.synCon.request(reqTypeStr, reqStr)
            else:
                self.lastReqData = repr(reqData)
                self.synCon.request(reqTypeStr, reqStr, reqData, {'Content-type' : 'application/json'})

            self.lastReqStr = reqStr

        except:
            print('failed to send %s %s to Synapse' % (reqTypeStr, reqStr))
            self.connect()
            return None
        
        return 1

    def sendGet(self, reqStr, respKey = None, reqData = None):
        if reqData is None:
            self.lastReqData = ''
        else:
            self.lastReqData = repr(reqData)
        
        x = self.sendRequest('GET', reqStr, reqData)
        if x is None:
            return None
        resp = self.getResp()

        try:
            if respKey is None:
                retval = resp
            else:
                retval = resp[respKey]

        except:
            retval = None

        return retval

    def sendPut(self, reqStr, reqData):
        self.sendRequest('PUT', reqStr, reqData)
        # we must read and 'clear' response
        # otherwise subsequent HTTP request may fail
        x = self.getResp()
        if x is None:
            if 'RecordingNotes' in reqStr:
                if self.getMode() < 3:
                    print('Recording Notes only work in Record mode')
            retval = 0
        elif x == '':
            retval = 0
        else:
            if x is float:
                retval = x
            else:
                retval = 1
        return retval

    def sendOptions(self, reqStr, respKey, reqData = None):
        x = self.sendRequest('OPTIONS', reqStr, reqData)
        
        if x is None:
            return []
        
        return self.getResp()[respKey]

    def parseJsonString(self, jsonData):
        try:
            retval = str(jsonData)
        except:
            retval = ''

        return retval

    def parseJsonStringList(self, jsonData):
        retval = []

        try:
            for value in jsonData:
                retval.append(self.parseJsonString(value))
        except:
            retval = []
            return retval

        return retval

    def parseJsonFloat(self, jsonData, result = []):
        try:
            retval = float(jsonData)
        except:
            retval = 0.0
            # notify caller if interested
            if len(result) > 0:
                result[0] = False

        return retval

    def parseJsonFloatList(self, jsonData, result = []):
        retval = []

        try:
            for value in jsonData:
                retval.append(self.parseJsonFloat(value, result))
        except:
            retval = []
            return retval

        return retval

    def parseJsonInt(self, jsonData):
        return int(self.parseJsonFloat(jsonData))

    def getMode(self):
        '''
        -1: Error
         0: Idle
         1: Standby
         2: Preview
         3: Record
        '''

        x = self.sendGet('/system/mode', 'mode')
        if x is None:
            return -1
        return self.Modes.index(x)

    def getModeStr(self):
        '''
        '' (Error)
        'Idle'
        'Standby'
        'Preview'
        'Record'
        '''

        retval = self.getMode()
        if retval == -1:
            retval = ''
        else:
            retval = self.Modes[retval]

        return retval

    def setMode(self, mode):
        '''
        mode must be an integer between 0 and 3, inclusive
        '''

        if mode in range(len(self.Modes)):
            return self.sendPut('/system/mode', json.dumps({'mode' : self.Modes[mode]}))
        else:
            raise Exception('Invalid input to setMode, must be integer between 0 and 3')

    def setModeStr(self, modeStr):
        '''
        string equivalent of setMode()
        '''

        try:
            mode = self.Modes.index(modeStr)
        except:
            raise Exception('invalid call to setModeStr()')

        return self.setMode(mode)

    def issueTrigger(self, id):
        return self.sendPut('/trigger/' + str(id), None)

    def getSystemStatus(self):
        retval = {'sysLoad' : 0, 'uiLoad' : 0, 'errorCount' : 0, 'rateMBps' : 0, 'recordSecs' : 0}
        resp = self.sendGet('/system/status')

        sysStat = {'sysLoad' : '', 'uiLoad' : '', 'errors' : '', 'dataRate' : '', 'recDur' : ''}
        # to catch if resp is somehow not iterable
        try:
            for key in resp:
                # to catch if this assignment is somehow invalid
                try:
                    sysStat[key] = resp[key]
                except:
                    continue
        except:
            pass

        # Synapse internal keys : user friendly keys
        keyMap = {'sysLoad' : 'sysLoad', 'uiLoad' : 'uiLoad', 'errors' : 'errorCount', 'dataRate' : 'rateMBps', 'recDur' : 'recordSecs'}
        for key in sysStat:
            try:
                if key == 'dataRate':
                    # '0.00 MB/s'
                    retval[keyMap[key]] = float(sysStat[key].split()[0])
                elif key == 'recDur':
                    # 'HH:MM:SSs'
                    recDur = sysStat[key][:-1].split(':')
                    retval[keyMap[key]] = int(recDur[0]) * 3600 + int(recDur[1]) * 60 + int(recDur[2])
                else:
                    retval[keyMap[key]] = int(sysStat[key])

            except:
                continue

        return retval

    def getPersistModes(self):
        return self.parseJsonStringList(self.sendOptions('/system/persist', 'modes'))

    def getPersistMode(self):
        return self.parseJsonString(self.sendGet('/system/persist', 'mode'))

    def setPersistMode(self, modeStr):
        if modeStr not in self.Persist:
            raise Exception("Allowed persistences are: 'Best', 'Last', or 'Fresh'")
            
        x = self.sendPut('/system/persist', json.dumps({'mode' : modeStr}))
        if x == 0:
            if self.getMode() > 0:
                print('Synapse is not in idle mode')
        return x

    def getSamplingRates(self):
        retval = {}
        resp = self.sendGet('/processor/samprate')

        if resp is not None:
            resp = self.cleanStruct(resp)
            for proc in list(resp.keys()):
                retval[self.parseJsonString(proc)] = self.parseJsonFloat(resp[proc])

        return retval

    def getGizmoParent(self, gizmoName):
        x = self.sendGet('/experiment/processor/' + gizmoName, 'processor')
        if x is None:
            return ''
        return self.parseJsonString(x)

    def getKnownSubjects(self):
        return self.parseJsonStringList(self.sendOptions('/subject/name', 'subjects'))

    def getKnownUsers(self):
        return self.parseJsonStringList(self.sendOptions('/user/name', 'users'))

    def getKnownExperiments(self):
        return self.parseJsonStringList(self.sendOptions('/experiment/name', 'experiments'))

    def getKnownTanks(self):
        return self.parseJsonStringList(self.sendOptions('/tank/name', 'tanks'))

    def getKnownBlocks(self,):
        return self.parseJsonStringList(self.sendOptions('/block/name', 'blocks'))

    def getCurrentSubject(self):
        return self.parseJsonString(self.sendGet('/subject/name', 'subject'))

    def getCurrentUser(self):
        return self.parseJsonString(self.sendGet('/user/name', 'user'))

    def getCurrentExperiment(self):
        return self.parseJsonString(self.sendGet('/experiment/name', 'experiment'))

    def getCurrentTank(self):
        return self.parseJsonString(self.sendGet('/tank/name', 'tank'))

    def getCurrentBlock(self):
        x = self.sendGet('/block/name', 'block')
        if x is None:
            self.checkMode()
            return 0
        return self.parseJsonString(x)

    def setCurrentSubject(self, name):
        result = self.sendPut('/subject/name', json.dumps({'subject' : name}))
        time.sleep(.5)
        return result

    def setCurrentUser(self, name, pwd = ''):
        result = self.sendPut('/user/name', json.dumps({'user' : name, 'pwd' : pwd}))
        time.sleep(.5)
        return result

    def setCurrentExperiment(self, name):
        result = self.sendPut('/experiment/name', json.dumps({'experiment' : name}))
        time.sleep(2)
        return result

    def setCurrentTank(self, name):
        result = self.sendPut('/tank/name', json.dumps({'tank' : name}))
        time.sleep(.5)
        return result

    def setCurrentBlock(self, name):
        result = self.sendPut('/block/name', json.dumps({'block' : name}))
        if result == 0:
            if self.getMode() > 0:
                print('Synapse is not in idle mode')
            else:
                print("Check that Synapse Menu > Preferences > Data Saving > Block Naming is set to 'Prompt'")
        time.sleep(.5)
        return result

    def createTank(self, path):
        result = self.sendPut('/tank/path', json.dumps({'tank' : path}))
        time.sleep(.5)
        return result

    def createSubject(self, name, desc = '', icon = 'mouse'):
        result = self.sendPut('/subject/name/new', json.dumps({'subject' : name, 'desc' : desc, 'icon' : icon}))
        time.sleep(.5)
        return result

    def getGizmoNames(self, synApiOnly = False):
        '''
        if synApiOnly == True:
            return names of objects with any SynapseAPI parameter enabled
        '''
        if synApiOnly:
            return self.parseJsonStringList(self.sendOptions('/gizmos/api', 'gizmos'))
        else:
            return self.parseJsonStringList(self.sendOptions('/gizmos', 'gizmos'))
    
    def getGizmoInfo(self, gizmoName):
        # info should have type, desc, cat and icon
        # icon is a string of base64-encoded text
        info = self.sendGet('/gizmos/' + gizmoName)
        if info is not None:
            info = self.cleanStruct(info)
            retval = {}
            for key in info.keys():
                retval[self.parseJsonString(key)] = self.parseJsonString(info[key])
            return retval
        return {}
    
    def getParameterNames(self, gizmoName):
        return self.parseJsonStringList(self.sendOptions('/params/' + gizmoName, 'parameters'))

    def getParameterInfo(self, gizmoName, paramName):
        info = self.parseJsonStringList(self.sendGet('/params/info/%s.%s' % (gizmoName, paramName), 'info'))
        keys = ('Name', 'Unit', 'Min', 'Max', 'Access', 'Type', 'Array')

        if len(info) == 0:
            return {}
        
        retval = {}
        for i in range(len(keys)):
            key = keys[i]

            try:
                retval[key] = info[i]

                if key == 'Array' and info[i] != 'No' and info[i] != 'Yes':
                    retval[key] = int(info[i])
                elif key == 'Min' or key == 'Max':
                    retval[key] = float(info[i])

            except:
                retval[key] = None

        return retval

    def getParameterSize(self, gizmoName, paramName):
        return self.parseJsonInt(self.sendGet('/params/size/%s.%s' % (gizmoName, paramName), 'value'))

    def getParameterValue(self, gizmoName, paramName):
        value = self.sendGet('/params/%s.%s' % (gizmoName, paramName), 'value')
        if value is None:
            self.checkMode()
            return None

        didConvert = [True]
        retval = self.parseJsonFloat(value, didConvert)
        
        if not didConvert[0]:
            retval = self.parseJsonString(value)

        return retval

    def getParameterValues(self, gizmoName, paramName, count = -1, offset = 0):
        '''
        if count == -1:
            count = getParameterSize(gizmoName, paramName)
        '''

        count = int(count)
        offset = int(offset)

        if count == -1:
            lookup = gizmoName + '.' + paramName
            if lookup in self.sizeTable:
                count = self.sizeTable[lookup]
            else:
                count = self.getParameterSize(gizmoName, paramName)
                self.sizeTable[lookup] = count
            if count == 1:
                # catch if getParameterValues was used to read a single parameter
                print('{0} {1}: calling getParameterValue instead of getParameterValues'.format(
                    gizmoName,
                    paramName)
                )
                return self.getParameterValue(gizmoName, paramName)
        
        values = self.sendGet('/params/%s.%s' % (gizmoName, paramName),
                              'values',
                              json.dumps({'count' : count, 'offset' : offset}))
        if values is None:
            return values

        # HACK to pass variable by reference
        didConvert = [True]
        retval = self.parseJsonFloatList(values, didConvert)
        
        if not didConvert[0]:
            retval = self.parseJsonStringList(values)
            
        return retval[:min(count, len(retval))]

    def setParameterValue(self, gizmoName, paramName, value):
        try:
            len(value)
            if type(value) is not str:
                print('Input value is an array, using setParameterValues instead')
                return self.setParameterValues(gizmoName, paramName, value)
        except:
            pass
        return self.sendPut('/params/%s.%s' % (gizmoName, paramName), json.dumps({'value' : value}))

    def setParameterValues(self, gizmoName, paramName, values, offset = 0):
        jjj = json.dumps({'offset' : offset, 'values' : values})
        
        # if its a single value add brackets so Synapse treats it like a list
        # note: if its a ParSeq parameter list, this does not work - the whole list needs to be replaced
        try:
            len(values)
        except:
            colon = jjj.rfind(':')
            jjj = jjj[:colon+1] + '[' + jjj[(colon+2):-1] + ']}'
        x = self.sendPut('/params/%s.%s' % (gizmoName, paramName), jjj)
        if x == 0:
            self.checkMode()
        return x

    def getExperimentMemos(self, experiment, memoNum = -1, startNum = -1, endNum = -1, startTime = '-1', endTime = '-1'):
        '''
        memoNum:             return single memo (1 based index)
        startNum / endNum:   filter by log number (nonnegative)
        startTime / endTime: filter by log time stamp (%Y%m%d%H%M%S)

        filtering is inclusive
        startNum / endNum is prioritized over startTime / endTime
        if startNum / startTime > endNum / endTime and endNum / endTime != -1 / '', endNum / endTime is ignored

        all memos for experiment are returned if no filter given
        '''
        startTime = str(startTime)
        endTime = str(endTime)
        reqStr = '/experiment/notes/' + experiment
        if memoNum > -1:
            reqStr += '/%d' % memoNum
        elif startNum > -1 or endNum > -1:
            reqStr += '/range/%d/%d' % (startNum, endNum)
        elif len(startTime) == 14 or len(endTime) == 14:
            reqStr += '/range/%s/%s' % (startTime.replace('-1', '00000000000000'), endTime.replace('-1', '00000000000000'))

        return self.parseJsonStringList(self.sendGet(reqStr, 'notes'))

    def getSubjectMemos(self, subject, memoNum = -1, startNum = -1, endNum = -1, startTime = '-1', endTime = '-1'):
        '''
        memoNum:             return single memo (1 based index)
        startNum / endNum:   filter by log number (nonnegative)
        startTime / endTime: filter by log time stamp (%Y%m%d%H%M%S)

        filtering is inclusive
        startNum / endNum is prioritized over startTime / endTime
        if startNum / startTime > endNum / endTime and endNum / endTime != -1 / '', endNum / endTime is ignored

        all memos for subject are returned if no filter given
        '''

        reqStr = '/subject/notes/' + subject
        if memoNum > -1:
            reqStr += '/%d' % memoNum
        elif startNum > -1 or endNum > -1:
            reqStr += '/range/%d/%d' % (startNum, endNum)
        elif len(startTime) == 14 or len(endTime) == 14:
            reqStr += '/range/%s/%s' % (startTime.replace('-1', '00000000000000'), endTime.replace('-1', '00000000000000'))

        return self.parseJsonStringList(self.sendGet(reqStr, 'notes'))

    def getUserMemos(self, user, memoNum = -1, startNum = -1, endNum = -1, startTime = '-1', endTime = '-1'):
        '''
        memoNum:             return single memo (1 based index)
        startNum / endNum:   filter by log number (nonnegative)
        startTime / endTime: filter by log time stamp (%Y%m%d%H%M%S)

        filtering is inclusive
        startNum / endNum is prioritized over startTime / endTime
        if startNum / startTime > endNum / endTime and endNum / endTime != -1 / '', endNum / endTime is ignored

        all memos for user are returned if no filter given
        '''

        reqStr = '/user/notes/' + user
        if memoNum > -1:
            reqStr += '/%d' % memoNum
        elif startNum > -1 or endNum > -1:
            reqStr += '/range/%d/%d' % (startNum, endNum)
        elif len(startTime) == 14 or len(endTime) == 14:
            reqStr += '/range/%s/%s' % (startTime.replace('-1', '00000000000000'), endTime.replace('-1', '00000000000000'))

        return self.parseJsonStringList(self.sendGet(reqStr, 'notes'))

    def appendExperimentMemo(self, experiment, memo):
        return self.sendPut('/experiment/notes', json.dumps({'experiment' : experiment, 'memo' : memo}))

    def appendSubjectMemo(self, subject, memo):
        return self.sendPut('/subject/notes', json.dumps({'subject' : subject, 'memo' : memo}))

    def appendUserMemo(self, user, memo):
        return self.sendPut('/user/notes', json.dumps({'user' : user, 'memo' : memo}))

    def startDemo(self, name):
        if name not in self.demoExperiments:
            raise Exception('%s is not a valid demo experiment' % name)
        if self.getCurrentExperiment() != name:
            if name not in self.getKnownExperiments():
                raise Exception('Experiment %s not found' % name)
            if self.getModeStr() != 'Idle':
               self.setModeStr('Idle')
            try:
                self.setCurrentExperiment(name)
            except:
                raise Exception('Experiment %s not selected' % name)

        if self.demoRequiredGizmos[name] not in self.getGizmoNames():
            raise Exception('Required gizmo %s not found' % self.demoRequiredGizmos[name])

        if self.getModeStr() == 'Idle':
            self.setPersistMode('Fresh')
            self.setModeStr('Record')

if __name__ == '__main__':

    syn = SynapseAPI()
    #x = syn.appendExperimentMemo('SpikeCount', 'test')
    #print(x)
    #x = syn.appendExperimentMemo('SpikeCount444', 'test') # return 500 Unknown error 
    #print(x)
    #x = syn.appendSubjectMemo('Subject1', 'test')
    #print(x)
    #x = syn.appendSubjectMemo('SpikeCount444', 'test') # return 500 Unknown error 
    #print(x)
    #x = syn.appendUserMemo('User1', 'test')
    #print(x)
    #x = syn.appendUserMemo('SpikeCount444', 'test') # return 500 Unknown error 
    #print(x)

    #x = syn.createSubject('testSub4412', 'testDesc', 'human')
    #print(x)
    #y = syn.createSubject('testSub4412', 'testDesc', 'human') # return 404 Not found (because it exists)
    #print(y)
    #z = syn.createSubject('testSub21', 'testDesc2', 'human2')
    #print(z)

    #x = syn.createSubject('testSub55', 'testDesc', 'human')
    #print(x)
    #y = syn.createSubject('testSub55', 'testDesc', 'human') # return 404 Not found (because it exists)
    #print(y)
    #z = syn.createSubject('testSub255', 'testDesc2', 'human2')
    #print(z)

    #x = syn.createTank('N:\\TEMP\\_SynTank22') # createTank returns 404 Not Found if already exists or can't make path
    #print(x)
    #y = syn.createTank('G:\\TEMP\\AAA\\SynTank33')
    #print(y)
    #x = syn.getCurrentBlock() # returns 404 Not Found if Synapse is Idle, caught later
    #print(x)

    #x = syn.getCurrentExperiment() # never fails
    #print(x)
    #y = syn.getCurrentSubject() # never fails
    #print(y)
    #z = syn.getCurrentTank() # never fails
    #print(z)
    #a = syn.getCurrentUser() # never fails
    #print(a)

    #x = syn.getExperimentMemos('SpikeCount') # never fails
    #print(x)
    #y = syn.getExperimentMemos('SpikeCount', endTime = 20200811153000)
    #print(y)
    #z = syn.getExperimentMemos('SpikeCount', startTime = 20210811153000) # empty list
    #print(z)
    #    startTime  double, filter by log time stamp (%Y%m%d%H%M%S)
    #    endTime    double, filter by log time stamp (%Y%m%d%H%M%S)

    #x = syn.getGizmoNames(True) # never fails
    #print(x)
    #y = syn.getGizmoNames(False) # never fails
    #print(y)

    x = syn.getGizmoInfo('aStim1')
    print(x)
    y = syn.getGizmoInfo('StStore1')
    print(y)
    z = syn.getGizmoInfo('test')  # 404 Not Found if gizmo doesn't exist
    print(z)
    a = syn.getGizmoInfo('Accum1')
    print(a)

    #z = syn.getGizmoParent('test')  # 404 Not Found if parent doesn't exist
    #print(z)
    #x = syn.getGizmoParent('aStim1')
    #print(x)
    #y = syn.getGizmoParent('StStore1')
    #print(y)

    #x = syn.getKnownBlocks() # never fails
    #print(x)
    #x = syn.getKnownExperiments() # never fails
    #print(x)
    #x = syn.getKnownSubjects() # never fails
    #print(x)
    #x = syn.getKnownTanks() # never fails
    #print(x)
    #x = syn.getKnownUsers() # never fails
    #print(x)

    #x = syn.getMode() # never fails
    #print(x)
    #x = syn.getModeStr() # never fails
    #print(x)

    #x = syn.getParameterInfo('aStim1', 'PulsePeriod')
    #print(x)
    #y = syn.getParameterInfo('aStim1', 'PulsePeriod2') # returns empty dict with no error for missing gizmo or parameter
    #print(y)
    #z = syn.getParameterInfo('aStim2', 'PulsePeriod') # returns empty dict with no error for missing gizmo or parameter
    #print(z)

    #x = syn.getParameterNames('aStim1')
    #print(x)
    #y = syn.getParameterNames('aStim2') # returns empty array if gizmo not found
    #print(y)

    #x = syn.getParameterSize('aStim1', 'PulsePeriod')
    #print(x)
    #y = syn.getParameterSize('aStim1', 'PulsePeriod2') # returns 0 if gizmo or parameter not found
    #print(y)
    #z = syn.getParameterSize('aStim2', 'PulsePeriod2')
    #print(z)
    #a = syn.getParameterSize('aStim1', 'ParameterList')
    #print(a)
    #b = syn.getParameterSize('aStim2', 'ParameterList')
    #print(b)

    #x = syn.getParameterValue('aStim1', 'PulsePeriod')
    #print(x)
    #y = syn.getParameterValue('aStim1', 'PulsePeriod2') # returns 422 Ill-formed request packet if not found
    #print(y)
    #z = syn.getParameterValue('aStim2', 'PulsePeriod')
    #print(z)

    #x = syn.getParameterValues('aStim1', 'PulsePeriod') # calls getParameterValue instead
    #print(x)
    #y = syn.getParameterValues('aStim1', 'PulsePeriod2') # returns 422 Ill-formed request packet if parameter not found
    #print(y)
    #z = syn.getParameterValues('aStim2', 'PulsePeriod') # returns 422 Ill-formed request packet if gizmo not found
    #print(z)
    #a = syn.getParameterValues('aStim1', 'ParameterList')
    #print(a)
    #b = syn.getParameterValues('aStim2', 'ParameterList') 
    #print(b)

    #x = syn.getPersistMode() # never fails
    #print(x)
    #x = syn.getPersistModes() # never fails
    #print(x)
    #x = syn.getSamplingRates() # never fails
    #print(x)

    #x = syn.getSubjectMemos('Subject1')
    #print(x)
    #y = syn.getSubjectMemos('asdfexwdf') # returns empty list when subject doesn't exist
    #print(y)

    #x = syn.getSystemStatus() # never fails
    #print(x)

    #x = syn.getUserMemos('User1')
    #print(x)
    #y = syn.getUserMemos('User2') # returns empty array if not found
    #print(y)

    #x = syn.issueTrigger(1)
    #print(x)
    #y = syn.issueTrigger(55) # returns 404 Not found if trigger outside bounds
    #print(y)

    #x = syn.setCurrentBlock('test') # returns 404 if already recording, or Block Naming is not set to 'Prompt'
    #print(x)

    #x = syn.setCurrentExperiment('SpikeCount')
    #print(x)
    #y = syn.setCurrentExperiment('tedsdfest') # returns 400 Invalid syntax if experiment doesn't exist
    #print(y)

    #x = syn.setCurrentSubject('Subject1')
    #print(x)
    #y = syn.setCurrentSubject('tesd') # returns 400 Invalid syntax if experiment doesn't exist
    #print(y)

    #x = syn.setCurrentTank('F:\TDT\MYSYNTANK8') # returns 404 Not found if auto tank naming is turned on
    #print(x)
    #y = syn.setCurrentTank('G:\TEMP\AAA\test555') # it also doesn't care if it's a legit tank or not, it just creates the folder and returns 0 - make sure you create the tank first
    #print(y)

    #x = syn.setCurrentUser('User1')
    #print(x)
    #y = syn.setCurrentUser('User2', 'badpass2') # returns 404 Not found if password is bad
    #print(y)
    #z = syn.setCurrentUser('User2', 'test') 
    #print(z)
    #a = syn.setCurrentUser('User3') # returns 400 Invalid syntax if user doesn't exist
    #print(a)

    #x = syn.setMode(1) # 404 Not found if Standby isn't enabled
    #print(x)
    #y = syn.setMode(1) # 404 Not found if already in desired mode
    #print(y)
    #z = syn.setMode(55) # hard exception
    #print(z)

    #x = syn.setModeStr('Standby')
    #print(x)
    #y = syn.setModeStr('Standby') # 404 Not found if already in desired mode
    #print(y)
    #z = syn.setModeStr('ttt') # hard exception
    #print(z)

    #a = syn.setParameterValue('aStim1', 'PulsePeriod', 6)  # returns 1
    #print(a)
    #x = syn.setParameterValue('aStim1', 'PulsePeriod', 'test')  # returns 1 for some reason? TODO
    #print(x)
    #y = syn.setParameterValue('aStim1', 'PulsePeriod2', 5)  # 404 Not Found if can't edit or doesn't exist or not in runtime
    #print(y)
    #z = syn.setParameterValue('ParSeq1', 'PulseCount', list(range(1, 11)))  # catches that it's an array and use setParameterValues instead
    #print(z)

    #x = syn.setParameterValue('RecordingNotes', 'Button', 0) # log note associated with first button
    #print(x)
    #x = syn.setParameterValue('RecordingNotes', 'Button', 'test') # doesn't fail but should
    #print(x)
    #x = syn.setParameterValue('RecordingNotes', 'Note', 'My Custom Note') # write a custom note
    #print(x)

    #x = syn.setParameterValues('aStim1', 'PulsePeriod', 6)  # 422 Ill-formed request packet if can't talk to it that way
    #print(x)
    #y = syn.setParameterValues('ParSeq1', 'PulseCount', list(range(1, 11)))
    #print(y)
    #z = syn.setParameterValues('ParSeq1', 'PulseCount2', list(range(1, 11)))  # 422 Ill-formed request packet if not a parameter
    #print(z)
    #a = syn.setParameterValues('ParSeq1', 'PulseCount', 55)
    #print(a)
    
    #syn.setParameterValue('TagTest1', 'Enable', 1)
    #c = syn.setParameterValues('TagTest1', 'MyArray', [x/100. for x in range(1, 101)]);
    #print(c)
    #d = syn.setParameterValues('TagTest1', 'MyArray', 10, 85);
    #print(d)
    #a = syn.setParameterValues('ParSeq1', 'PulseCount', 55, 3)
    #print(a)

    #x = syn.setPersistMode('Best') # 503 Could not process request in time if in a runtime mode
    #print(x)
    #y = syn.setPersistMode('ttt') # hard exception
    #print(y)
