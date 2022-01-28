# -*- coding: utf-8 -*-

import btk

class BTKReader:
    
    def __init__(self):
        self.readerType = 'btk'
        self.fileName = None
        self.acq = None
        
    def readFromFile(self, fileName):
        self.fileName = fileName
        reader = btk.btkAcquisitionFileReader()
        reader.SetFilename(str(fileName))
        reader.Update()
        self.acq = reader.GetOutput()
    
    def getVectorUnit(self, vecType):
        if vecType == 'marker':
            type_ = btk.btkPoint.Marker
        elif vecType == 'angle':
            type_ = btk.btkPoint.Angle
        vecUnit = self.acq.GetPointUnit(type_)
        return vecUnit
    
    def getVectorFrequency(self):
        return self.acq.GetPointFrequency()
    
    def getNVectorFrames(self):
        nVectorFrames = self.acq.GetPointFrameNumber()
        return nVectorFrames
    
    def getNVectors(self):
        self.coll = self.acq.GetPoints()
        n = self.coll.GetItemNumber()
        return n
        
    def getVector(self, i):
        point = self.coll.GetItem(i)
        label = point.GetLabel()
        type_ = point.GetType()
        data = point.GetValues()
        if type_ == btk.btkPoint.Marker:
            vecType = 'marker'
        elif type_ == btk.btkPoint.Angle:
            vecType = 'angle'
        return label, data, vecType
    
    def getNEvents(self):
        n = self.acq.GetEventNumber()
        return n
    
    def getEvent(self, i):
        event = self.acq.GetEvent(i)
        label = event.GetLabel()
        context = event.GetContext()
        frame = int(event.GetFrame())
        return label, context, frame
    
    def getData(self):
        return self.acq, self.readerType
        

class BTKWriter:
    
    def __init__(self):
        self.writerType = 'btk'
        self.acq = None
        self.nVectorFrames = None
        
    def initEmpty(self):
        self.acq = btk.btkAcquisition()
        
    def initSpaceForNVectorFrames(self):
        self.acq.Init(0, self.nVectorFrames)
        
    def setNVectorFrames(self, nVectorFrames):
        self.nVectorFrames = nVectorFrames
        
    def setVectorUnit(self, vecType, unit):
        if vecType == 'marker':
            type_ = btk.btkPoint.Marker
        elif vecType == 'angle':
            type_ = btk.btkPoint.Angle
        self.acq.SetPointUnit(type_, unit)
        
    def setVectorFrequency(self, vecFreq):
        self.acq.SetPointFrequency(vecFreq)
        
    def addVector(self, label, data, vecType):
        newVector = btk.btkPoint(str(label), self.nVectorFrames)
        if vecType == 'marker':
            type_ = btk.btkPoint.Marker
        elif vecType == 'angle':
            type_ = btk.btkPoint.Angle
        newVector.SetType(type_)
        newVector.SetValues(data)
        self.acq.AppendPoint(newVector)
        
    def writeToFile(self, fileName):
        writer = btk.btkAcquisitionFileWriter()
        writer.SetInput(self.acq)
        writer.SetFilename(str(fileName))
        writer.Update()
        
    def setData(self, data):
        readerType = data[1]
        if readerType != self.writerType:
            raise Exception('reader and writer type must have the same type')
        self.acq = data[0]