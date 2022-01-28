"""
.. module:: fio
   :synopsis: file read/write module

"""

import vtk
import re
import numpy as np
from xml.etree.ElementTree import ElementTree, Element, SubElement
import json
import scipy.io as sio
from openpyxl import load_workbook



def readMocapFile(reader, fileName, sections, 
              removeSegmentNameFromMarkerNames=True,
              setMarkersZeroValuesToNaN=True,
              setMarkersDataFromMeterstoMillimeters=True
              ):
    """Read C3D file.

    Parameters
    ----------
    fileName : str
        Full path of the C3D file.

    sections : list
        List of strings indicating which section to read.
        It can contain the following: 'markers'.

    opts : dict
        Options dictionary that can contain the following keys:

        - setMarkersZeroValuesToNaN: if true, marker corrdinates exactly
          matching 0 will be replace with NaNs (e.g. Optitrack systems).
          Default is false.
         
        - removeSegmentNameFromMarkerNames: if true, marker names in the format
        "segment:marker" will be removed the "segment:" prefix.
        Default is false.

    Returns
    -------
    dict
        Collection of read data. It contains, as keys, the items contained
        in ``sections``:

        - markers: this is a dictionary where each key is a point label, and each
          value is a N x 3 np.ndarray of 3D coordinates (in *mm*), where N is the
          number of time frames.

    """

    # Open C3D pointer
    reader.readFromFile(fileName)

    # Initialize data structure
    data = {}
    
    # Correct for unit if necessary
    scaleFactor = 1.
    markerUnit = reader.getVectorUnit('marker')
    if markerUnit == 'm':
        if setMarkersDataFromMeterstoMillimeters:
            scaleFactor = 1000.
            markerUnit = 'mm'
    angleUnit = reader.getVectorUnit('angle')

    # Get relevant vector data (N x 3)
    markers = {}
    angles = {}
    for i in range(reader.getNVectors()):
        label, vecData, vecType = reader.getVector(i)
        if label is None:
            continue
        if vecType == 'marker':
            if removeSegmentNameFromMarkerNames:
                labelList = label.split(':')
                if len(labelList) > 1:
                    label = labelList[1]
            data_ = vecData * scaleFactor
            if setMarkersZeroValuesToNaN:
                data_[data_==0.] = np.nan # replace 0. with np.nan
            markers[label] = data_
        elif vecType == 'angle':
            data_ = vecData
            angles[label] = data_
            
    # Get events
    events = {}
    allList = []
    for i in range(reader.getNEvents()):
        label, context, frame = reader.getEvent(i)
        allList.append(frame)
    events['allMixedList'] = sorted(allList)
    print(events)
            
    freq = reader.getVectorFrequency()

    if 'markers' in sections:
        data['markers'] = {}
        data['markers']['data'] = markers
        data['markers']['unit'] = markerUnit
        data['markers']['freq'] = freq
        
    if 'angles' in sections:
        data['angles'] = {}
        data['angles']['data'] = angles
        data['angles']['unit'] = angleUnit
        data['angles']['freq'] = freq
        
    if 'events' in sections:
        data['events'] = {}
        data['events']['data'] = events

    # Return data
    return data
    
    
def writeMocapFile(writer, fileName, data, copyFromFile=None, reader=None):
    """Write to C3D file.

    Parameters
    ----------
    fileName : str
        Full path of the C3D file.

    data : dict
        Data dictionary that can contain the following keys:

        - markers or angles: this is vector-related data. This dictionary contains:
            - data: dictionary where each key is a vector label, and each
              value is a N x 3 np.ndarray of 3D coordinates, where N is
              the number of time frames. This field is always necessary.
            - framesNumber: number of data points per vector.
              This field is necessary when creating files from scratch.
            - unit: string indicating the vectors measurement unit.
              This field is necessary when creating files from scratch.
            - freq: number indicating the vectors acquisition frequency.
              This field is necessary when creating files from scratch.

    copyFromFile : str
        If None, it creates a new file from scratch.
        If str indicating the path of an existing C3D file, it adds/owerwrite data copied from that file.

    """

    markerUnit = 'mm'
    angleUnit = 'deg'
    translationUnit = 'mm'
    lengthUnit = 'mm'
    if copyFromFile is not None:
        # Open C3D pointer
        reader.readFromFile(copyFromFile)
        writer.setData(reader.getData())
        nVectorFrames = reader.getNVectorFrames()
        writer.setNVectorFrames(nVectorFrames)
        markerUnit = reader.getVectorUnit('marker')
        angleUnit = reader.getVectorUnit('angle')
    else:
        # Create new acquisition
        writer.initEmpty()
        for section in data:
            vecType = section[:-1]
            if section in ['markers', 'angles']:
                if 'framesNumber' in data[section]:
                    nVectorFrames = data[section]['framesNumber']
                else:
                    firstVectorName = list(data[section]['data'].keys())[0]
                    firstVector = data[section]['data'][firstVectorName]
                    nVectorFrames = firstVector.shape[0]
                writer.setNVectorFrames(nVectorFrames)
                writer.initSpaceForNVectorFrames()
                vectorUnit = data[section]['unit']
                if section == 'markers':
                    markerUnit = vectorUnit
                elif section == 'angles':
                    angleUnit = vectorUnit
                writer.setVectorUnit(vecType, vectorUnit)
                vectorFreq = data[section]['freq']
                writer.setVectorFrequency(vectorFreq)

    for section in data:
        if section in ['markers', 'angles', 'translations', 'lengths']:
            vecType = section[:-1]
            # Write vector data
            vectors = data[section]['data']
            for v in vectors:
                newVectorUnit = data[section]['unit']
                if section == 'markers':
                    if markerUnit == newVectorUnit:
                        vectorData = vectors[v].copy()
                    else:
                        if vectorUnit == 'm' and newVectorUnit == 'mm':
                            vectorData = vectors[v] / 1000.
                        else:
                            raise Exception('not solvable conflict between existing and new markers unit')
                elif section == 'angles':
                    if angleUnit == newVectorUnit:
                        vectorData = vectors[v].copy()
                    else:
                        raise Exception('not solvable conflict between existing and new angles unit')
                elif section == 'translations':
                    if translationUnit == newVectorUnit:
                        vectorData = vectors[v].copy()
                    else:
                        raise Exception('not solvable conflict between existing and new translations unit')
                elif section == 'lengths':
                    if lengthUnit == newVectorUnit:
                        vectorData = vectors[v].copy()
                    else:
                        raise Exception('not solvable conflict between existing and new lengths unit')
                writer.addVector(v, vectorData, vecType)

    # Write to C3D
    writer.writeToFile(fileName)
    

def readMimics(fileName, sections):
    """Read points coordinates from ASCII file exported from Materialise
    Mimics. An example of file content is:
    
    Point:
    Name  	X1       	Y1        	Z1       	
    FKC   	 46.6870 	 -92.0609 	958.0264 	
    FLE   	 40.2380 	 -46.8351 	984.0000 	
    FME   	 36.3195 	-138.6404 	976.5000 	
    TKC   	 31.8037 	 -88.4758 	950.2433 	
    TAC   	-21.8975 	 -77.1526 	552.5607 	
    
    Circle:
    Name  	X1      	Y1        	Z1       	R       	D      	
    TLCC  	32.9836 	 -67.3573 	943.2257 	23.6281 	0.0000 	
    TMCC  	31.8691 	-102.0591 	940.1147 	27.6284 	0.0000 	
    
    Sphere:
    Name  	X1       	Y1        	Z1        	R       	D      	
    FHC   	 11.1663 	-134.8308 	1403.1165 	27.2839 	0.0000 	
    FMCC  	 27.4416 	-116.3681 	 965.6003 	22.9368 	0.0000 	
    FLCC  	 39.0764 	 -61.9340 	 976.9134 	24.7792 	0.0000 	
    mF1   	 33.6330 	-280.7724 	1133.2573 	 6.0216 	0.0000 	
    mF2   	 73.3282 	-237.5155 	1183.1842 	 6.1986 	0.0000 	
    mF3   	 91.7198 	-238.5893 	1091.9640 	 6.2495 	0.0000 	
    mF4   	-38.4368 	-232.0098 	1126.2762 	 6.1103 	0.0000 	
    mT1   	  5.1893 	-280.0224 	 807.6139 	 6.0960 	0.0000 	
    mT2   	 74.2126 	-260.8282 	 841.1344 	 6.0205 	0.0000 	
    mT3   	 42.6394 	-246.6916 	 751.9938 	 6.2438 	0.0000 	
    mT4   	-48.0996 	-208.2864 	 826.2371 	 6.3594 	0.0000 	
    

    Parameters
    ----------
    fileName : str
        Full path of the ASCII file.

    sections : list
        (To be implemented, not used yet).

    Returns
    -------
    dict
        Collection of read data. It contains, as keys, the items contained
        in ``sections``:

        - markers: this is a dictionary where each key is a point label, and each
          value is a N x 3 np.ndarray of 3D coordinates (in *mm*), where N is the
          number of time frames.

    """
    
    # Read file
    with open(fileName) as f:
        content = f.readlines()
        
    # Parse content
    state = 'skip'
    data = {}
    data['markers'] = {}
    for line in content:
        if re.match('Name\s*\t*X1\s*\t*Y1\s*\t*Z1\s*\t*', line):
            state = 'parse'
        elif state == 'parse':
            line = line.strip()
            if line == '':
                state = 'skip'
            else:
                p = line.split('\t')
                name = p[0].strip()
                x = float(p[1])
                y = float(p[2])
                z = float(p[3])
                data['markers'][name] = [x, y, z]
            
    return data
    
    
def readSplinesMimics(fileName):
    
    # Read file
    with open(fileName) as f:
        content = f.readlines()
        
    # Parse content
    state = 'skip'
    data = {}
    data['splines'] = {}
    for line in content:
        if state == 'skip':
            if re.match('Spline:', line):
                state = 'parse-name'
        elif state == 'parse-name':
            name = line.split('Name:')[1].strip()
            data['splines'][name] = []
            state = 'parse'
        else:
            if line.strip() == '':
                state = 'skip'
                continue
            p = line.split(':')
            if (re.match('Xp,Yp,Zp', p[0])):
                data['splines'] = {}
                state = 'skip'
                continue
            v = p[1].strip().split()
            x = float(v[0])
            y = float(v[1])
            z = float(v[2])
            data['splines'][name].append([x, y, z])
            
    return data

    
def readSTL(filePath):
    """Read C3D file.

    Parameters
    ----------
    filePath : str
        Full path of the STL file.

    Returns
    -------
    vtkPolyData
        returned by ``vtk.vtkSTLReader()``.

    """
    
    reader = vtk.vtkSTLReader()
    reader.SetFileName(filePath)
    reader.Update()
    vtkData = reader.GetOutput()
    return vtkData
    

def writeSTL(filePath, vtkData):
    writer = vtk.vtkSTLWriter()
    writer.SetFileTypeToASCII()
    writer.SetInputData(vtkData)
    writer.SetFileName(filePath)
    writer.Write()

    
def writeXML3Matic(filePath, data):
    """Write to XML schema useable by Meterialise 3-matic.
    Example schema:
    
    <Entities xmlns:mat="urn:materialise">
        <Point>
            <Name>S1G1B</Name>
            <Coordinate>
                16.940976647370583 -85.358029123743265 899.51227236399541
            </Coordinate>
        </Point>
        <Line>
            <Name>Line-001</Name>
            <StartPoint>
                45.577666130142411 -100.89681849251893 904.83454568666582
            </StartPoint>
            <EndPoint>
                43.866504322409831 -101.87987025530371 904.48405949547521
            </EndPoint>
        </Line>
    </Entities>

    Parameters
    ----------
    filePath : str
        Full path of the XML file.
        
    data : list
        List of dictionaries, that must contain the following fields:
        
        - name: name of the entity;
        - type: type of the entity;
        it can be: 'point', 'line';
        - coords: Nx3 (line) or 3-elem (point) array of coordinates

    """
    
    entities = Element('Entities', attrib={'xmlns:mat': 'urn:materialise'})
    for item in data:
        if item['type'] == 'point':
            point = SubElement(entities, 'Point')
            name = SubElement(point, 'Name')
            name.text = item['name']
            coordinate = SubElement(point, 'Coordinate')
            coordinate.text = "%2.15f  %2.15f  %2.15f " % tuple(item['coords'])
        if item['type'] == 'line':
            line = SubElement(entities, 'Line')
            name = SubElement(line, 'Name')
            name.text = item['name']
            startPoint = SubElement(line, 'StartPoint')
            startPoint.text = "%2.15f  %2.15f  %2.15f " % tuple(item['coords'][0,:])
            endPoint = SubElement(line, 'EndPoint')
            endPoint.text = "%2.15f  %2.15f  %2.15f " % tuple(item['coords'][-1,:])
    ElementTree(entities).write(
        filePath,
        xml_declaration = True,
        encoding = 'utf-8',
    )
        
        


def readORParamsFile(fileName):
    """Read Oxford-Rig (IORT UZLeuven) parameters file.

    Parameters
    ----------
    filePath : str
        Full path of the parameters file.

    Returns
    -------
    dict
        Parameters parsed.

    """
    
    with open(fileName) as fn:
        data = json.load(fn)
    return data


def writedORParamsFile(fileName, params):
    with open(fileName, 'w') as fn:
        fn.write(json.dumps(params, indent=4))
    
    
def writeMATFile(fileName, data):
    sio.savemat(fileName, {'data': data})
    
    
def readXLSFile(fileName, sheet):
    wb = load_workbook(filename=fileName, read_only=True)
    ws = wb[sheet]
    
    sheetData = []
    for row in ws.rows:
        rowData = []
        for cell in row:
            rowData.append(cell.value)
        sheetData.append(rowData)
        
    return sheetData
    
    
def readIORTPointsFile(fileName):
    data = readXLSFile(fileName, 'Measurements export')
    points = {}
    for i in range(1, len(data)):
        row = data[i]
        if all(v is None for v in row):
            continue
        pointName = row[1]
        x, y, z = row[2], row[3], row[4]
        points[pointName] = [x, y, z]
        
    return points
    
    
def readStringListMapFile(fileName):
    with open(fileName) as f:
        content = f.read().splitlines()
    data = {}
    for line in content:
        t = line.split(': ')
        key = t[0]
        values = t[1].split(', ')
        for i, v in enumerate(values):
            try:
                values[i] = float(v)
            except:
                pass
        data[key] = values
    
    return data
    
    
        