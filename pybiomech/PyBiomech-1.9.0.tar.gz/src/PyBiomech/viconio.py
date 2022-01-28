# -*- coding: utf-8 -*-

import numpy as np
from ViconNexus import ViconNexus

class ViconReader:
    
    def __init__(self):
        self.readerType = 'vicon'
        self.fileName = None
        self.vicon = ViconNexus()
        
    def readFromFile(self, fileName):
        pass
    
    def getVectorUnit(self, vecType):
        if vecType == 'marker':
            unit = 'mm'
        elif vecType == 'angle':
            unit = 'deg'
        return unit
    
    def getVectorFrequency(self):
        return self.vicon.GetFrameRate()
    
    def getNVectorFrames(self):
        self.nVectorFrames = self.vicon.GetFrameCount()
        return self.nVectorFrames
    
    def getNVectors(self):
        self.subjects = self.vicon.GetSubjectNames()
        self.markers = []
        self.modOutputs = []
        self.assoc = {}
        for subject in self.subjects:
            markers = self.vicon.GetMarkerNames(subject)
            for m in markers:
                self.assoc[m] = subject
            self.markers += markers
            modOutputs = self.vicon.GetModelOutputNames(subject)
            for m in modOutputs:
                self.assoc[m] = subject
            self.modOutputs += modOutputs
        self.NMarkers = len(self.markers)
        self.NModOutputs = len(self.modOutputs)
        self.NVectors = self.NMarkers + self.NModOutputs
        return self.NVectors
        
    def getVector(self, i):
        skip = False
        if i < self.NMarkers:
            label = self.markers[i]
            trajX, trajY, trajZ, trajExists = self.vicon.GetTrajectory(self.assoc[label], label)
            data = np.array([trajX, trajY, trajZ]).T
            data[data==0.] = np.nan
            vecType = 'marker'
            if data.shape[0] == 0:
                skip = True
        else:
            label = self.modOutputs[i - self.NMarkers]
            group, components, types = self.vicon.GetModelOutputDetails(self.assoc[label], label)
            [data, exists] = self.vicon.GetModelOutput(self.assoc[label], label)
            if group in ['Modeled Markers','Angles']:
                trajX, trajY, trajZ = data
                data = np.array([trajX, trajY, trajZ]).T
                data[data==0.] = np.nan
                if group == 'Modeled Markers':
                    vecType = 'marker'
                elif group == 'Angles':
                    vecType = 'angle'
            else:
                skip = True
        if skip:
            label = None
            data = None
            vecType = None
        return label, data, vecType
    
    def getNEvents(self):
        self.events = []
        fr1, fr2 = self.vicon.GetTrialRange()
        for context in ['Right', 'Left', 'General']:
            for label in ['Foot Off', 'Foot Strike', 'Event']:
                for subject in self.subjects:
                    eventFrames, eventOffsets = self.vicon.GetEvents(subject, context, label)
                    for i in range(len(eventFrames)):
                        event = {}
                        event['label'] = label
                        event['context'] = context
                        event['frame'] = int(eventFrames[i] - fr1)
                        self.events.append(event)
        return len(self.events)
    
    def getEvent(self, i):
        event = self.events[i]
        label = event['label']
        context = event['context']
        frame = event['frame']
        return label, context, frame
    
    def getData(self):
        return self.readerType
    
    
class ViconWriter:
    
    def __init__(self):
        self.writerType = 'vicon'            
        self.vicon = ViconNexus()
        self.nVectorFrames = None
        
    def initEmpty(self):
        pass
        
    def initSpaceForNVectorFrames(self):
        pass
        
    def setNVectorFrames(self, nVectorFrames):
        self.nVectorFrames = nVectorFrames
        
    def setVectorUnit(self, vecType, unit):
        pass
        
    def setVectorFrequency(self, vecFreq):
        pass
        
    def addVector(self, label, data, vecType):
        self.subjects = self.vicon.GetSubjectNames()
        subject = self.subjects[0]
        existingMarkerNames = self.vicon.GetMarkerNames(subject)
        existingModelOutputNames = self.vicon.GetModelOutputNames(subject)
        if vecType in ['marker', 'angle', 'translation', 'length']:
            Nf = data.shape[0]
            exists = np.array([True] * Nf)
            data_ = np.zeros((Nf, 3))
            if len(data.shape) < 2:
                data_[:,2] = data
            else:
                data_ = data
            exists[np.isnan(data_[:,2])] = False
            data_[np.isnan(data_)] = 0.
            dataList = data_.T.tolist()
            exists = exists.tolist()
            isOrigMarker = True
            if vecType == 'marker':
                if label not in existingMarkerNames:
                    isOrigMarker = False
                    if label not in existingModelOutputNames:
                        self.vicon.CreateModeledMarker(subject, label)
            elif vecType == 'angle':
                isOrigMarker = False
                if label not in existingModelOutputNames:
                    XYZNames = ['X','Y','Z']
                    anglesTypes = ['Angle'] * 3
                    self.vicon.CreateModelOutput(subject, label, 'Angles', XYZNames, anglesTypes)
            elif vecType == 'translation':
                isOrigMarker = False
                if label not in existingModelOutputNames:
                    XYZNames = ['X','Y','Z']
                    translationsTypes = ['Length'] * 3
                    self.vicon.CreateModelOutput(subject, label, 'Lengths', XYZNames, translationsTypes)
            elif vecType == 'length':
                isOrigMarker = False
                if label not in existingModelOutputNames:
                    XYZNames = ['X','Y','Z']
                    lengthsTypes = ['Length'] * 3
                    self.vicon.CreateModelOutput(subject, label, 'Lengths', XYZNames, lengthsTypes)
            if isOrigMarker:
                x, y, z = dataList
                self.vicon.SetTrajectory(subject, label, x, y, z, exists)
            else:
                self.vicon.SetModelOutput(subject, label, dataList, exists)
        
    def writeToFile(self, fileName):
        pass
        
    def setData(self, data):
        readerType = data[0]
        if readerType != self.writerType:
            raise Exception('reader and writer type must have the same type')
