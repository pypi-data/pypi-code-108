import pandas
from re import match
from loguru import logger
from tzlocal import get_localzone
from datetime import datetime
import pytz

class UtilsProperty():
    def _getDataTypes(properties:dict) -> dict:
        """
        Sorts the property types and returns a dictionary of those properties 
        that are not of type STRING.
        """ 

        logger.debug(properties)
        propertyTypes = {'Boolean': [], 'Numeric': [], 'DateTime': [], 'String': [], 'Unknown': []}
        for property in properties:
            if property['dataType'] in ['DATE_TIME', 'DATE_TIME_OFFSET']:
                propertyTypes['DateTime'].append(property['name'])
            elif property['dataType'] == 'BOOLEAN':
                propertyTypes['Boolean'].append(property['name'])
            elif property['dataType'] in ['INT', 'LONG', 'DECIMAL']:
                propertyTypes['Numeric'].append(property['name'])
                
            elif property['dataType'] == 'STRING':
                propertyTypes['String'].append(property['name'])
            else: 
                propertyTypes['Unknown'].append(property['name'])
        return propertyTypes

    def _getArrays(properties:dict) -> list:
        """ Lists properties that are arrays (isArray) """

        p = [property['name'] for property in properties if property['isArray'] == True]
        return p

    def _getNullables(properties:dict) -> list:
        """ Lists properties that are nullable """

        p = [property['name'] for property in properties if property['nullable'] == True]
        return p

    def _transformBool(value:str):
        trueValues = ['ja', 'Ja', 'yes', 'Yes', 'True', 'true', 1]
        falseValues = ['nein', 'Nein', 'no', 'No', 'false','False',0]
        if value in trueValues:
            return True
        elif value in falseValues:
            return False
        return None

    def _isInt(n:str):
        return bool(match(r'-?\d+$', n))

    def _isFloat(n:str) -> bool:
        return bool(match(r'-?\d+(\.\d+)$', n))

    def _transformNumeric(value:str):
        if UtilsProperty._isInt(value):
            return int(value)
        elif UtilsProperty._isFloat(value):
            return float(value)
        else:
            logger.warning(f"'{value}' is not of numeric data type!")

    def _checkIsList(pythonList:str) -> bool:
        if pythonList[0] != '[':
            return False
        elif pythonList[-1] != ']':
            return False
        else:
            return True

    def _transformList(pythonList:str, propertyType:str) -> list:
        """ Transforms a String into a Python list"""
        if not UtilsProperty._checkIsList(pythonList):
            logger.warning(f"Value '{pythonList}' is not array type!")

        pythonList = pythonList[1:-1].split(',')
        pythonList = [element.strip() for element in pythonList]

        _pythonList = []
        for element in pythonList:
            if propertyType == 'Numeric':
                _pythonList.append(UtilsProperty._transformNumeric(element))
            elif propertyType == 'Boolean':
                _pythonList.append(UtilsProperty._transformBool(element))
            else:
                _pythonList.append(str(element))

        return _pythonList

class FileUtils(UtilsProperty):

    def _createItems(content:list, dataType:dict, isArray:list, nullable:list):
        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0: continue
            if len(row) < 1: continue
            else:
                item = {}
                for j, field in enumerate(row):
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else: 
                                item.setdefault(header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field,'Numeric'))
                            else:
                                item.setdefault(header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                #item.setdefault(header[j], FileUtils._convertTimestamp(field, timeZone, FileUtils._dateFormat(field)))
                                item.setdefault(header[j], field)
                        else:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'String'))
                            else:
                                item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    def _createInstanceItems(content:list, dataType:dict, isArray:list, nullable:list, idMapping:dict=None, 
        transpose:bool=False) -> list:

        if transpose == True:
            content = list(map(list, zip(*content)))

        for column in content:
            if column[0] in ['unit', 'timeUnit', 'factor']:
                del column

        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0: continue
            if len(row) < 1: continue
            else:
                if idMapping != None:
                    try:
                        groupInventoryItemId = idMapping[content[i][0]]
                    except:
                        logger.warning(f"ImportKeyProperty '{content[i][0]}' not found.")
                        continue
                else:
                    groupInventoryItemId = content[i][0]
                item = {'_groupInventoryItemId':groupInventoryItemId}
                for j, field in enumerate(row):
                    if j == 0: continue
                        
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else: 
                                item.setdefault(header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field,'Numeric'))
                            else:
                                item.setdefault(header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                #item.setdefault(header[j], UtilsProperty._convertTimestamp(field, timeZone))
                                item.setdefault(header[j], field)
                        else:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'String'))
                            else:
                                item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    def _createTimeSeriesItems(content:list, dataType:dict, isArray:list, nullable:list):
        itemList = []
        header = content[0]
        for i, row in enumerate(content):
            itemOkay = True # is changed to false, if certain criteria are not met -> warning message, next item
            if i == 0: continue
            if len(row) < 1: continue
            else:
                item = {'resolution': {}}
                for j, field in enumerate(row):
                    if not field:
                        if header[j] in nullable:
                            continue
                        elif header[j] not in nullable and len(field) > 0:
                            logger.warning(f"Value missing for non nullable {header[j]}. Item from line {i} not imported.")
                            itemOkay = False
                            break
                        else:
                            pass
                    else:
                        if header[j] in dataType['Boolean']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'Boolean'))
                            else: 
                                item.setdefault(header[j], UtilsProperty._transformBool(field))
                        elif header[j] in dataType['Numeric']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field,'Numeric'))
                            else:
                                item.setdefault(header[j], UtilsProperty._transformNumeric(field))
                        elif header[j] in dataType['DateTime']:
                            if header[j] in isArray:
                                item.setdefault(header[j], UtilsProperty._transformList(field, 'DateTime'))
                            else:
                                item.setdefault(header[j], UtilsProperty._convertTimestamp(field, timeZone))
                        else:
                            if header[j] == 'timeUnit':
                                item['resolution'].setdefault('timeUnit', field)
                            elif header[j] == 'factor':
                                item['resolution'].setdefault('factor', field)
                            else:
                                if header[j] in isArray:
                                    item.setdefault(header[j], UtilsProperty._transformList(field, 'String'))
                                else:
                                    item.setdefault(header[j], field)
                if itemOkay and len(item) > 0:
                    itemList.append(item)

        return itemList

    def _comparePropertiesBasic(properties:pandas.DataFrame, header:list) -> None:
        """ Compares header with requested properties from a basic inventory. """

        properties = set(properties['name'])
        header = set(header)
        return header.difference(properties)

    def _comparePropertiesTimeSeries(properties:pandas.DataFrame, header:list) -> None:
        """ Compares header with requested properties from a time series inventory. """

        properties = set(properties['name'])
        header = set(header)
        tsProperties = set(['timeUnit', 'factor', 'unit'])
        header = header - tsProperties
        return header.difference(properties)

    def _analyzeProperties(inventoryName:str, properties:pandas.DataFrame) -> tuple:
        """ Analyzes inventory properties and returns dictionaries to each property attribute """

        properties = properties[['name', 'dataType', 'isArray', 'nullable']].to_dict('records')
        dataType = UtilsProperty._getDataTypes(properties)
        isArray = UtilsProperty._getArrays(properties)
        nullable = UtilsProperty._getNullables(properties)

        logger.debug(f'Data types: {dataType}')
        logger.debug(f'Array properties: {isArray}')
        logger.debug(f'Nullable properties: {nullable}')

        return dataType, isArray, nullable

    def _timeZone(timeZone):
        if timeZone==None: 
            localTimeZone = get_localzone().zone
            return str(pytz.timezone(localTimeZone))
        else:
            return str(pytz.timezone(timeZone))

    def _timeZoneItems(timeZone):
        if timeZone==None: 
            localTimeZone = get_localzone().zone
            return str(pytz.timezone(localTimeZone))
        else:
            return str(pytz.timezone('UTC'))

    def _convertTimestamp(timestamp, timeZone, dateTimeFormat):

        timestamp = datetime.strptime(timestamp, dateTimeFormat)
        timestamp = pytz.timezone(timeZone).localize(timestamp).isoformat()
        return timestamp

    def _dateFormat(timestamp:str) -> str:

        # German
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%d.%m.%Y %H:%M:%S.%f'
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M:%S'
        if match(r'\d{2}.\d{2}.\d{4} \d{2}:\d{2}', timestamp):
            return '%d.%m.%Y %H:%M'
        if match(r'\d{2}.\d{2}.\d{4}', timestamp):
            return '%d.%m.%Y'

        # ISO
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f+00:00'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S+00:00'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%fZ'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%dT%H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', timestamp):
            return '%Y-%m-%dT%H:%M:%SZ'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}', timestamp):
            return '%Y-%m-%dT%H:%M'

        # English I
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f+00:00'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S+00:00'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y-%m-%d %H:%M:%S.%f'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M:%S'
        if match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', timestamp):
            return '%Y-%m-%d %H:%M'
        if match(r'\d{4}-\d{2}-\d{2}', timestamp):
           return '%Y-%m-%d'
               
        # English II
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}.\d{1,6}', timestamp):
            return '%Y/%m/%d %H:%M:%S.%f'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M:%S'
        if match(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', timestamp):
            return '%Y/%m/%d %H:%M'
        if match(r'\d{4}/\d{2}/\d{2}', timestamp):
            return '%Y/%m/%d'

        # English III
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M:%S'
        if match(r'\d{1,2}/\d{1,2}/\d{4} \d{2}:\d{2}', timestamp):
            return '%m/%d/%Y %H:%M'
        if match(r'\d{1,2}/\d{1,2}/\d{4}', timestamp):
            return '%m/%d/%Y'

        return None

    def _createInstanceItemContent(content):
        itemContent = []
        for row in content:
            if row[0] not in ['unit', 'timeUnit', 'factor']:
                itemContent.append(row)

        return itemContent
