
# This is the standard data format for dynamics data exchange inside and outside of BIFROST JOTUNN.
# 
# @module DataFrame
# @author Ralf Mosshammer <bifrost.at@siemens.com>, ported by Manuel Matzinger <manuel.matzinger@siemens.com>
# @copyright Ralf Mosshammer, Siemens AG, 2020, 2021

TYPEID = 'DATAFRAME'
import json
import uuid

"""
This is the standard data exchange format for BIFROST dynamics data. A data frame
 reflects the values of one or more dynamics across a common time vector (which can be one).

 dataFrame := {
   dataFrameId: ...                   An optional, unique frame ID
   time: [ ... ]                      Vector of times (in seconds), minimum length 1
   series: [ seriesEntry, ... ]       A collection of data series objects, minimum length 1
 }

 seriesEntry := {
   dynamicId: ...                     Dynamic ID as in the state
   type: ...                          One of the allowed data types
   values: [ ... ]                    A vector of values, indices and length corresponding to the time vector
   flags: [ [ ... ], ... ]            Data flags per value entry
   meta: { ... }                      Meta-data object (key, value) for the whole series
 }
"""
class DataFrame:


    """
    Create a new DataFrame, intially void of any data. When a time vector is set, either here or subsequently
    with setTime, the cardinality of the frame is thereby determined as the length of the time vector. Any data
    series added to the frame must correspond to this cardinality.
    @param {String} id (Optional) A predetermined ID. If none is given, a new one is generated.
    @param {Array} time (Optional) A time vector to initialize this frame with.
    """
    def __init__(self, id = None, time = None):
        self.dataFrameId    = id or DataFrame.createId()
        self.time           = None
        self.series         = []
        if time != None:
            self.setTime(time)

    """
    A DataFrame is considered empty if it has no time vector
    """
    def isEmpty(self):
        return (self.time == None or len(self.time) == 0)

    """
    Set the time vector for the data frame. This vector will determine the cardinality
    of the frame, i.e., the length of the values vector of each series element.
    @param {Array} time An array of time values (in seconds)
    @throws {Error} if an attempt is made to set the time after series data has been pushed
    """
    def setTime(self, time):
        if self.time != None or len(self.series) > 0:
            raise Exception('DataFrame time is immutable if there are any series entries (there are currently ('+str(len(self.series))+').')
        if not isinstance(time, list):
            time = [time]
        self.time = time
        return self

    """
    Add series data to a frame. If an entry for the given dynamic ID already exists,
    it will be purged from the frame prior to adding the new one (overwrite).
    
    @param {String} dynamicId The dynamic ID
    @param {Array} values Dynamic values. A vector with a minimum cardinality of 1.
    @param {String} type Type of the dynamic.
    @param {Array} flags A vector of flags relating to the value vector. If null, an empty vector will be inferred.
    @param {Object} meta Arbitrary key-value metadata.
    
    @throws {Error} if the time vector is not set
    @throws {Error} if the values parameter is not an array or has length 0
    @throws {Error} if a valid type was given, if any
    @throws {Error} if the value cardinality is not equivalent to the frame cardinality (time vector length)
    @throws {Error} if the flags array cardinality is not equivalent to the frame cardinality
    @throws {Error} if the first value element's inner type does not correspond to the declared type
    """
    def addSeries(self, dynamicId, values, datatype = None, flags = None, meta = dict()):
        # Check: is a time set?
        if (self.time == None):
            raise Exception('Attempt to push series data into frame before setting a time vector. Call setTime(time) first.')
        cardinality = len(self.time)
        
        # Check: is values a non-0 length array
        if isinstance(values, list) and len(values) == 0:
            raise Exception('Invalid "values" field for DataFrame: must be an Array with length > 0.')

        # Check: is the type valid, if given
        if datatype != None and not (datatype in self.types().values()):
            raise Exception('Invalid "type" field for DataFrame: must be one of '+str(self.types().values())+' (was '+str(datatype)+').')

        # Check: is the value series the same length as the time vector of this frame?
        if cardinality != len(values):
            raise Exception('Invalid "values" cardinality for DataFrame ('+str(len(values))+'): must be '+str(cardinality)+'.')

        # Check: same with flags, if given
        if flags != None:
            if len(flags) != cardinality:
                raise Exception('Invalid "flags" cardinality for DataFrame ('+str(len(flags))+'): must be '+str(cardinality)+'.')
        else:
            # Infer the flags array
            flags = [[] for i in range(cardinality)]

        #Try to automatically determine the type if none is given
        if not datatype:
            datatype = self.inferType(values[0])


        # Type verification
        if datatype != self.types()['UNKNOWN']:
            _v = values[0][0] if isinstance(values[0], list) else values[0]
            if _v != self.values()['NULL']:
                detectedType = type(_v)
                if detectedType is not self.pytypes()[datatype]:
                    raise Exception('Type mismatch: declared type is {'+str(datatype)+'}, but detected type is {'+str(detectedType)+'}.')
                
        # Existing elements are purged
        try:
            idx = -1
            idx = self.series.index(dynamicId)
            #idx = self.series.findIndex(entry => entry.dynamicId == dynamicId)
        except ValueError:
            pass 
        if idx > -1:
            self.series.pop(idx)

        self.series.append(self.createSeriesElement(dynamicId, values, datatype, flags, meta))

        return self


    """
    Create a series element for the DataFrame.
    
    @param {String} dynamicId The dynamic ID
    @param {Array} values Dynamic values. A vector with a minimum cardinality of 1.
    @param {String} type Type of the dynamic.
    @param {Array} flags A vector of flags relating to the value vector.
    @param {Object} meta Arbitrary key-value metadata.
    """
    def createSeriesElement(self, dynamicId, values, datatype, flags, meta):
        element = { 'dynamicId' : dynamicId,
                    'values'    : values,
                    'type'      : datatype,
                    'flags'     : flags,
                    'meta'      : meta 
                    }
        a = DataFrame.meta()['CARDINALITY']
        element['meta'][DataFrame.meta()['CARDINALITY']] = DataFrame.getValueCardinality(values[0])
        return element

    """
    Convert the data frame to a plain JavaScript object.
    """
    def toObject(self):
        return(
            {
                'time'    : self.time,
                'series'  : [ self.series ]
            }
        )

    """
    Convert the data frame to an array compatible with massUpdateDynamics
    """
    def toUpdateObject(self):
        result = []
        for idx in range(len(self.time)):
            for seriesElement in self.series:
                result.extend([{
                    'id': seriesElement['dynamicId'],
                    'time': self.time[idx],
                    'value': seriesElement['values'][idx]
                }])
        return result


    """
    Yield a JSON string representing this frame.
    """
    def toJSONString(self, pretty = False):
        if pretty:
            return json.dumps(self.toObject(), indent=2)
        return json.dumps(self.toObject())
    
    """
    String representation of the data frame header info.
    """
    def formatHeader(self):
        result = ''
        id = self.dataFrameId or '(anonymous)'
        if self.isEmpty():
            result = result + 'DataFrame ID '+str(id)+' (empty)'
        else:
            result = result + 'DataFrame ID '+str(id)+' ['+str(self.time[0])+'... '+str(self.time[len(self.time)-1])+'] ('+str(len(self.time))+') instants)'
        return result


    """
    String representation of the data frame as list of time instants.
    """
    def formatExpanded(self):
        result = ''
        seperator = '|'
        result = result + self.formatHeader() + '\n\n'
        if not self.isEmpty():
            for seriesElement in self.series:
                result =  result + '\t' + str(seriesElement['dynamicId'])
                for metaKey in seriesElement['meta'].keys():
                    result = result + '\n\t\t' + str(DataFrame.limit(metaKey, 15)) + str(seriesElement['meta'][metaKey])
                result = result + '\n\n'
            for i in range(len(self.time)):
                result = result + '\n\tInstant #'+str(i)+'  · T = '+str(self.time[i])+'\n'
                for seriesElement in self.series:
                    result = result + '\t' +  colors.lightgrey + DataFrame.limit(seriesElement['type'], 10) + DataFrame.limit(seriesElement['dynamicId'], 75) + DataFrame.formatValue(seriesElement['values'][i], DataFrame.get(seriesElement['meta'], DataFrame.meta()['CARDINALITY'], 1))
                    result = result + colors.lightgrey + str(seperator.join(seriesElement['flags'][i])) +'\n'
        return result


    """
    String representation of the data frame as compact time instant list.
    """
    def formatCompact(self):
        result = ''
        result = result + self.formatHeader() +'\n\n'
        if not self.isEmpty():
            result = result + '\tT [ '
            for i in range(len(self.time)):
                result = result + str(self.time[i])
                if i != (len(self.time) - 1) :
                    result = result + ' · '
            result = result + ' ]\n'
            for seriesElement in self.series:
                result = result + '\n\t' +colors.lightgrey+ DataFrame.limit(seriesElement['type'], 10) + DataFrame.limit(seriesElement['dynamicId'], 75)+'\t'
                for i in range(len(self.time)):
                    result = result + DataFrame.formatValue(seriesElement['values'][i], DataFrame.get(seriesElement['meta'], DataFrame.meta()['CARDINALITY'], 1))
                    if i != (len(self.time) - 1):
                        result = result + ' · '
                result = result +'\t{'
                for metaKey in seriesElement['meta'].keys():
                    result = result + str(metaKey)+ ' = ' + str(seriesElement['meta'][metaKey])
                result = result + ' }'
        return result

    """
    Generate a pretty string from the DataFrame
    """
    def prettyPrint(self):
        return self.formatCompact()



    """
    Valid value flags
    """
    @staticmethod 
    def flags():
        return {
            'VALID'           : 'DATA-FLAGS:VALID',
            'INTERPOLATED'    : 'DATA-FLAGS:INTERPOLATED',
            'PROJECTED'       : 'DATA-FLAGS:PROJECTED',
            'MISSING'         : 'DATA-FLAGS:MISSING'
        }

    
    """
    Special values
    """
    @staticmethod
    def values():
        return {
            'NULL' : None
        }

    """
    Allowed value types.
    """
    @staticmethod
    def types():
        return {
            'BOOLEAN' : 'boolean',
            'INTEGER' : 'integer',
            'FLOAT'   : 'float',
            'NUMBER'  : 'float',
            'STRING'  : 'string',
            'UNKNOWN' : 'unknown',
            'DEFAULT' : 'string'
        }
    
    """
    Python type equivalents.
    """
    @staticmethod
    def pytypes():
        return {
            DataFrame.types()['BOOLEAN'] : bool,
            DataFrame.types()['INTEGER'] : int,
            DataFrame.types()['FLOAT']   : float,
            DataFrame.types()['NUMBER']   : float,
            DataFrame.types()['STRING']  : str,
            DataFrame.types()['UNKNOWN'] : 'unknown',
            DataFrame.types()['DEFAULT'] : str
        }

    """
    Special metadata keys
    """
    @staticmethod
    def meta():
        return {
            'CARDINALITY' : 'cardinality',  # Value cardinality, i.e., the length of values[0]
            'AGGREGATION' : 'aggregation',
            'COMPRESSED'  : 'compressed'
        }

    """
    Required properties on the frame level.
    """
    @staticmethod
    def getRequiredFrameProps():
        return [
            'time',
            'series'
        ]

    """
    Required properties of the series object.
    """
    @staticmethod
    def getRequiredSeriesProps():
        return[
            'dynamicId',
            'values',
            'type',
            'flags'
        ]

    """
    Determine the value cardinality (1 for scalars, length for vectors).
    
    @param {any} value A single value of the values array
    """
    @staticmethod
    def getValueCardinality(value):
        if not isinstance(value, list):
            return 1
        else:
            return len(value)
    
    """
    Create a data frame from an array of dynamics. This functions does not check for potential
    duplicates.
    
    @param {Array} dynamicsArray An array of dynamics objects as formatted in the state
    @param {integer} time A time (in seconds) when these dynamics were recorded. This will be inferred from the
    first dynamic entries' updatedAt value if not given, but in this case, any deviant updatedAt values will throw
    and error.
    
    @throws {Error} if no time is given and an updatedBy value does not conform to the value of the first entry.
    """
    @staticmethod
    def fromDynamicsArray(dynamicsArray, _time = None):
        frame = DataFrame()

        if len(dynamicsArray) == 0:
            return frame

        time                = _time
        forceSameInstant    = False
        if _time == None:
            time             = dynamicsArray[0].updatedAt
            forceSameInstant = True

        frame.setTime(time)

        for dynamicObject in dynamicsArray:
            # old bug, would not allow to write dynamics which was gotten via subscriptions
            # if forceSameInstant and dynamicObject['updatedAt'] != time:
            #     raise Exception('Invalid updatedAt value ('+str(dynamicObject['updatedAt'])+') of dynamic '+str(dynamicObject['id'])+'. All updatedAt instants must conform to the frame instant ('+str(time)+').')
            valueType = DataFrame.inferType(dynamicObject.value)
            meta = {
                'ref'         : dynamicObject['ref'],
                'typeRef'     : dynamicObject['typeRef'],
                'childRef'    : dynamicObject['childRef'],
                'updatedAt'   : dynamicObject['updatedAt'],
                'updatedBy'   : dynamicObject['updatedBy'],
                'parentRefs'  : [DataFrame.get(dynamicObject, 'parentRefs', [])],
                DataFrame.meta()['CARDINALITY']: len(dynamicObject['value']) if isinstance(dynamicObject['value'], list) else 1
            }
            frame.addSeries(dynamicObject['id'], [dynamicObject['value']], valueType, None, meta)
        return frame

    """
    Create a DataFrame from a JSON object representation.
    @param {object} json JSON object representation of a valid DataFrame
    """
    @staticmethod
    def fromJSON(json):
        # Validate the JSON
        DataFrame.validate(json)
        result = DataFrame(json['dataFrameId'], json['time'])
        for seriesElement in json['series']:
            result.addSeries(
                DataFrame.get(seriesElement, 'dynamicId'),
                DataFrame.get(seriesElement, 'values'),
                DataFrame.get(seriesElement, 'type', None),
                DataFrame.get(seriesElement, 'flags', None),
                DataFrame.get(seriesElement, 'meta', None)
            )
        return result

    """
    Combine distinct frames into a single DataFrame object. Duplicate series dynamicIds will be purged (precendence for
    later array indices). 
    @param {Array} frames An array of valid DataFrames with the same frame cardinality.
    @param {Boolean} validate Check each frame fro validity before combining.
    """
    @staticmethod
    def combineFrames(frames, validate = False):
        result      = DataFrame(None, None)
        cardinality = None
        for frame in frames:
            if (validate):
                DataFrame.validate(frame)
            if (cardinality == None):
                cardinality = len(frame['time'])
                result.setTime(frame['time'])
            else:
                if len(frame['time']) != cardinality:
                    raise Exception('Attempt to combine frames with different cardinality ('+str(len(frame['time']))+'!= '+str(cardinality)+')')
            for seriesElement in frame['series']:
                result.addSeries(
                    DataFrame.get(seriesElement, 'dynamicId'),
                    DataFrame.get(seriesElement, 'values'),
                    DataFrame.get(seriesElement, 'type', None),
                    DataFrame.get(seriesElement, 'flags', None),
                    DataFrame.get(seriesElement, 'meta', None)
                )
        return result

    """
    Validate the grammar of the data frame.
    @param {DataFrame} frame A data frame to be validated
    """
    @staticmethod
    def validate(frame):
        id = DataFrame.get(frame, 'dataFrameId', 'Unknown ID')
        for prop in DataFrame.getRequiredFrameProps():
            if DataFrame.get(frame, prop, None) == None:
                raise Exception('Invalid DataFrame ('+str(id)+'). Required property '+str(prop)+' not found.')
        if not isinstance(frame['time'], list):
            raise Exception('Invalid DataFrame ('+str(id)+'). Property "time" must be an array.')
        i = 0
        for seriesEntry in DataFrame.get(frame, 'series', []):
            for prop in DataFrame.getRequiredSeriesProps():
                if DataFrame.get(seriesEntry, prop, None) == None:
                    raise Exception('Invalid series object in DataFrame ('+str(id)+'). Required property '+str(prop)+' not found in entry at position '+str(i)+' ('+str(json.dumps(seriesEntry))+'.')
            i = i + 1


    def createId():
        uniqueid = uuid.uuid4()
        return TYPEID + ':' + str(uniqueid)


    def formatValue(_value, cardinality = 1):
        result = ''
        sep = ', '
        if cardinality == 1:
            result = result + str(_value)
        else:
            result = result + '[ '
            result = result + sep.join([str(elem) for elem in _value])
            result = result + ' ]'
        return result


    def inferType(_value):
        value = _value
        if isinstance(value, list):
            if len(value) > 0:
                value = value[0]
            else:
                value = None
        if type(value) is int:
            return DataFrame.types()['INTEGER']

        if type(value) is float:
            return DataFrame.types()['FLOAT']

        if type(value) is bool:
            return DataFrame.types()['BOOLEAN']
        
        if type(value) is str:
            return DataFrame.types()['STRING']

        return DataFrame.types()['UNKNOWN']


    def limit(string, length):
        result = string
        if (len(string) > length):
            result = string[0:(len(string)-3)] + '...'
        return result.ljust(length)


    def get(objectp, path, default=None):
        try:
            return objectp[path]
        except Exception as e:
            print(e)
            if default:
                return default
            else:
                return False


class safepointer:
     def has(obj,path):
          return pointerclass.hasp(obj,path)

     def get(obj,path, defn = None):
          if (pointerclass.hasp(obj,path)): # anderes has
               return pointerclass.getp(obj,path)
          return defn

class pointerclass:
     # Converts a json pointer into a array of reference tokens
     def parse(pointer):
          if (pointer == ''):
               return []
          if (pointer[0] != '/'):
               raise Exception('Invalid JSON pointer: ' + pointer)
          # removes first char which should be / and then splits the rest
          return pointer[1:].split("/")

     def getp(obj, pointer):
          if (isinstance(pointer,list)):
               refTokens = pointer
          else:
               refTokens = pointerclass.parse(pointer)
          for i in range(len(refTokens)):
               tok = refTokens[i]
               if not ((type(obj) is dict and tok in obj)):
                    raise Exception('Invalid reference token: ' + tok)
               obj = obj[tok]
          return obj

     def hasp(obj, pointer):
          try:
               pointerclass.getp(obj, pointer)
          except Exception as e:
               print(e)
               return False
          return True

class colors: 
    black='\033[30m'
    red='\033[31m'
    green='\033[32m'
    orange='\033[33m'
    blue='\033[34m'
    purple='\033[35m'
    cyan='\033[36m'
    lightgrey='\033[37m'
    darkgrey='\033[90m'
    lightred='\033[91m'
    lightgreen='\033[92m'
    yellow='\033[93m'
    lightblue='\033[94m'
    pink='\033[95m'
    lightcyan='\033[96m'