import json
import binascii
from struct import *
from py_expression_eval import Parser

class BinaryParser:


    def __init__(self,event_data):
        self.configData = None
        self.event_data = event_data
        self.inValue = event_data["data_raw"] #data_raw from json

    def genMask(self, mask,dataArray):
        '''Creates a mask for each segment according to
            the segment format: a.b:c.d
            Then it can be used to get the value from the data_raw'''
        #mask: ["segment"]
        #mask => a.b:c.d
        interval = mask.split(":")
        byteStart = int(interval[0].split(".")[0])#byteStart = a 
        byteEnd = int(interval[1].split(".")[0])  #byteEnd = c
        bitStart = int(interval[0].split(".")[1]) #bitStart = b
        bitEnd = int(interval[1].split(".")[1])   #bitEnd = d
        maskArray = []

        if (byteStart != byteEnd): # if a is diferent to c
            #Here creates a mask from a to c when they're different
            for byteNum in range(len(dataArray)): #size of hexadecimal list
                if byteNum in range(byteStart, byteEnd+1):#range from a to c+1
                    if (byteNum ==  byteStart):
                        dataMaskByte = (0xff & (256-(2**(bitStart))))
                    if (byteNum ==  byteEnd):
                        dataMaskByte = (0xff & (2**(bitEnd+1) - 1))
                    maskArray.append(dataMaskByte)
                else:
                    maskArray.append(0)

        if (byteStart == byteEnd): # if a is equal to c
            for byteNum in range(len(dataArray)):
                if (byteNum == byteStart):
                    if (byteNum ==  byteStart):
                        dataMaskByteS = (0xff & (256-(2**(bitStart))) & (2**(bitEnd+1) - 1))
                    maskArray.append(dataMaskByteS)
                else:
                    maskArray.append(0)
        return maskArray

    def getDataBytes(self, dataArray, maskArray):
        '''
        Recieves a list of the raw_data values in decimal and a list with the values to mask 
        Returns a string with the hex values that
            have passed the mask'''
        #dataArray = list of numbers
        #maskArray = mask
        #both lists should have same len
        resultData = ""
        for dataIterator in range(len(dataArray)):
            if (maskArray[dataIterator]):
                resultData = resultData+str.format('{:02x}', (dataArray[dataIterator] & maskArray[dataIterator]))#sets decimal to hex
        resultData = bytearray.fromhex(resultData)#some bytes get lost, why?
        return resultData

    def masker(self, data, segment):
        '''
        Recieves the raw_data and the segment where the value is and removes
        everything out of that segment, mask the values that correspond
        Returns the string with the values from that segment
        '''
        #data: raw_data
        #mask: ["segment"]
        dataArrayHex = ([''.join(x) for x in zip(*[list(data[z::2]) for z in range(2)])])#separates the raw_data into bytes: a bytes list
        dataArray = [] #it will hold the numbers once they have been changed from hexadecimal to decimal
        for byteHex in dataArrayHex:
            data, = unpack("B",binascii.unhexlify(byteHex))#from "byte" to int
            dataArray.append(data)
        maskArray = self.genMask(segment,dataArray)#creates a mask for each segement
        dataCombined = self.getDataBytes(dataArray, maskArray)#masks the values
        return dataCombined

    def getValue(self, data, segment, type, post, output_format, maskerType):
        '''
        Revices the raw data, the segment where the value is in the raw data,
        the type of the value, post if a formula is needed to apply and a
        format if value needs a format
        Returns the value from the raw_data
        '''
        #data: raw_data
        #mask: ["segment"]
        #type: ["type"]
        #post: ["post"]
        #format: ["format"]
        if maskerType == 'binary':
            intData = int(data,16)
            formatSpec = '0{}b'.format(len(data)*4)
            splittedSegment = segment.split(':')
            binStrData = format(intData, formatSpec)
            if not splittedSegment[0] or not splittedSegment[1]:
                raise Exception("Incomplete segment: '{}'. You have to give a complete segment e.g: '0:1'".format(segment))
            value = binStrData[int(splittedSegment[0]):int(splittedSegment[1])+1]
            if type == 'int':
                try:
                    value = int(value,2)
                except:
                    value = None
            elif type == 'bytes':
                try:
                    list_value = list(value)
                    value = ''
                    while len(list_value) > 0:
                        tmp_value = ''
                        for x in range(4):
                            tmp_value = '{}{}'.format(tmp_value,list_value.pop(0))
                        value = '{}{}'.format(value,hex(int(tmp_value,2)).replace('0x','').rstrip("L").upper())
                except:
                    value = None
            elif type == 'bool':
                try:
                    value = bool(int(value,2))
                except:
                    value = None
        else:
            value, = unpack(type,self.masker(data, segment))#hex string with the value needed gotten from raw_data
        if post != " " and value != None:
            parser = Parser()
            value = parser.evaluate(post, {'x': value})#post contanis a formula to adjust value according to json
        if output_format != " ":
            value = output_format.format(value)#format contains the way to display the value if needed
        return value
 
    def replaceTemplate(self, obj, oValue):
        '''
        Replace the #tag for tag in the template
        If there's a unit that is not used, it is added
        '''
        for k, v in obj.items():#checks for nested dicts
            if isinstance(v, dict):
                obj[k] = self.replaceTemplate(v, oValue)
        for data in obj.keys():
            if isinstance(obj[data], str):
                if(obj[data] in oValue):
                    try:
                        obj[data] = eval(oValue[obj[data]])
                    except:
                        obj[data] = oValue[obj[data]]
                else:
                    for key in oValue.keys():
                        obj[data] = obj[data].replace(key, str(oValue[key]))
                    try:
                        obj[data] = (eval(obj[data]))
                    except:
                        obj[data] = obj[data]
        return obj

    def executeParser(self,key):
        '''
        It gets all the values from the data_raw (self.configData) and returns
        a dict with the formatted values and applied a formula if needed
        '''
        dataOut = {}
        dataValues = {}
        for variables in self.configData[key]["process"].keys():
            maskerType = self.configData[key]['process'][variables].get('maskerType','default')
            dataValues[variables] = self.getValue(self.inValue, 
                                            self.configData[key]["process"][variables]["segment"], 
                                            self.configData[key]["process"][variables]["type"], 
                                            self.configData[key]["process"][variables]["post"], 
                                            self.configData[key]["process"][variables]["format"],
                                            maskerType)

        dataOut = self.replaceTemplate(self.configData[key]["template"], dataValues)
        return dataOut

    def processParser(self):
        '''
        Applies and decides which parser to apply, the default way or a specific coming in the json
        returns the data in a dict way, empty other case
        '''
        #TODO Need add #default parser posibility
        #Have conditional data
        dataOut = {}
        if 'rawtype' in self.configData and type(self.configData['rawtype']) == dict: #there is conditional data, it does not have a default way
            maskerType = self.configData["rawtype"].get('maskerType','default')
            rawtype = self.getValue(self.inValue,    self.configData["rawtype"]["segment"], 
                                          self.configData["rawtype"]["type"], 
                                          self.configData["rawtype"]["post"], 
                                          self.configData["rawtype"]["format"],
                                          maskerType)#gets the flag at data_raw that indicates wich parser to take
            evalData = {}
            for evalConditions in self.configData["rawtype"]["conditions"].keys():
                #TODO Securized
                evalData['x']=rawtype  #save value
                if (eval('x'+evalConditions, {}, evalData)):#gets wich parser to process
                    parserName = self.configData["rawtype"]["conditions"][evalConditions]#take the parser
                    if parserName in self.configData:
                        dataOut = self.executeParser(parserName)#applies the parser
                    else:
                        dataOut = self.executeParser('#default')
                else:
                    dataOut = self.executeParser('#default')
        #Dont have conditional data
        elif 'rawtype' in self.configData and type(self.configData['rawtype']) == list: #there is conditional data, it does not have a default way
            for rawCondition in self.configData['rawtype']:
                evalData = {}
                if 'evaluations' in rawCondition:
                    evalData['raw_data'] = self.inValue
                    for evaluation in rawCondition['evaluations'].keys():
                        maskerType = rawCondition['evaluations'][evaluation].get('maskerType','default')
                        evalData[evaluation] = self.getValue(self.inValue,
                                                rawCondition['evaluations'][evaluation]['segment'],
                                                rawCondition['evaluations'][evaluation]["type"], 
                                                rawCondition['evaluations'][evaluation]["post"], 
                                                rawCondition['evaluations'][evaluation]["format"],
                                                maskerType)
                else:
                    evalData['raw_data'] = self.inValue
                    maskerType = rawCondition.get('maskerType','default')
                    evalData['x'] = self.getValue(self.inValue,
                                        rawCondition["segment"], 
                                        rawCondition["type"], 
                                        rawCondition["post"], 
                                        rawCondition["format"],
                                        maskerType)
                for condition in list(rawCondition['conditions'].keys()):
                    parsed = False
                    if eval(condition,{},evalData):
                        parserName = rawCondition["conditions"][condition]
                        if parserName in self.configData:
                            dataOut = self.executeParser(parserName)
                            parsed = True
                            break
                if not parsed:
                    dataOut = self.executeParser('#default')
        else:
            dataOut = self.executeParser('#default')
        return dataOut

    def execute(self):
        self.configData = self.event_data['parser']
        response = self.processParser()
        return {"data": response }