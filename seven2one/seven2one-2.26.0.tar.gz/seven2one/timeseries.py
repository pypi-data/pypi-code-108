import pandas as pd
import pytz
from gql import gql, Client#, AIOHTTPTransport, RequestsHTTPTransport # This is gql version 3
from gql.transport.requests import RequestsHTTPTransport
from loguru import logger
from numpy import nan, record

from seven2one.utils.ut_time import TimeUtils

from .utils.ut import Utils
from .utils.ut_timeseries import UtilsTimeSeries
from . import core

class TimeSeries():

    def __init__(self, accessToken:str, endpoint:str, client:object) -> None:
        global coreClient
        coreClient = client
            
        header = {
            'authorization': 'Bearer ' + accessToken
        }
        
        transport =  RequestsHTTPTransport(url=endpoint, headers=header, verify=True)
        self.client = Client(transport=transport, fetch_schema_from_transport=False)

        return

    def addTimeSeriesItems(self, inventoryName:str, timeSeriesItems:list) -> list:
        """
        Adds new time series and time series group items from a list of 
        dictionaires and returns a list of the created inventoryItemIds.

        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series item and the properties
            of the time series feature (unit, timeUnit and factor)

        Example:
        >>> timeSeriesItems = [
                {
                'meterId': 'XYZ123',
                'orderNr': 300,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:56Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh'
                },
                {
                'meterId': 'XYZ123',
                'orderNr': 301,
                'isRelevant': True,
                'dateTime': '2020-01-01T00:00:55Z',
                'resolution': {
                    'timeUnit': 'HOUR',
                    'factor': 1,
                    },
                'unit': 'kWh',
                },
            ]
        >>> client.TimeSeries.addTimeSeriesItems('meterData', timeSeriesItems)
        """
        
        properties = Utils._tsPropertiesToString(timeSeriesItems)
        if properties == None: return

        key = f'create{inventoryName}'
        graphQLString = f'''mutation addTimeSeriesItems {{
            {key} (input: 
                {properties}
            )
            {{
                inventoryItems {{
                    sys_inventoryItemId
                }}
                {Utils.errors}
            }}
        }} 
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)

        ids = result[key]['inventoryItems']
        idList = [item['sys_inventoryItemId'] for item in ids]
        logger.info(f"Created {len(idList)} time series items.")

        return idList

    def addTimeSeriesItemsToGroups(self, inventoryName:str, timeSeriesItems:list):
        """
        Adds new time series items to existing time series groups.
        
        Parameters:
        -----------
        inventoryName: str
            The name of the inventory.
        timeSeriesItems: list
            This list contains the properties of the time series items together 
            with the sys_inventoryItemId of the related group time series.

        Example:
        --------
        >>> items = [
                {
                    'issueDate':'2020-11-01T00:00+0200',
                    'name': 'forecast_wind_pro_de',
                    'sys_groupInventoryItemId': 'Sdin6tNl8S'
                }
            ]
        >>> client.TimeSeries.addTimeSeriesItemsToGroups('GroupInventory', instanceItems)
        """

        properties = Utils._propertiesToString(timeSeriesItems)
        if properties == None: return

        key = f'addTimeSeriesTo{inventoryName}'

        graphQLString = f'''mutation addTimeSeriesItemstoGroup {{
           {key} (input: 
                {properties}
            )
            {{
                inventoryItems {{
                    sys_inventoryItemId
                }}
                {Utils.errors}
            }}
        }}
        ''' 
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)

        try:
            ids = result[key]['inventoryItems']
            idList = [item['sys_inventoryItemId'] for item in ids]
            logger.info(f"Group instance(s) created.")
            return idList
        except:
            pass
            return   

    def setTimeSeriesData(self, inventoryName, inventoryItemId:str, timeUnit:str, factor:int, 
        unit:str, dataPoints:dict, chunkSize:int=10000) -> None:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryItemId of the time series is used. As 
        timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or DateTimeOffset 
        (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ---------
        inventoryName: str
            The name of the inventory to which the time series belong.
        inventoryItemId: str
            The inventoryItemId to which data is to be written.
        timeUnit: str
            Is the time unit of the time series item
        factor: int
            Is the factor of the time unit
        unit: str
            The unit of the values to be written. 
        dataPoints: dict
            Provide a dictionary with timestamps as keys.
        chunkSize:int = 10000
            Specifies the chunk size of time series values that are written in 
            a single transaction
        
        Example: 
        --------
        >>> inventory = 'meterData'
            inventoryItemId = 'TzdG1Gj2GW'
            tsData = {
                '2020-01-01T00:01:00Z': 99.91,
                '2020-01-01T00:02:00Z': 95.93,
            }
            
        >>> client.TimeSeries.setTimeSeriesData(inventory, inventoryItemId,
                'MINUTE', 1, 'W', tsData)
        """
        inventories = core.TechStack.inventories(coreClient, fields=['name', 'inventoryId'])
        inventoryId = Utils._getInventoryId(inventories, inventoryName)
        logger.debug(f"Found inventoryId {inventoryId} for {inventoryName}.")

        key = f'setTimeSeriesData'

        def _setTimeSeriesData(_dataPoints):
           
            graphQLString = f'''
                mutation setTimeSeriesData {{
                setTimeSeriesData(input: {{
                    sys_inventoryId: "{inventoryId}"
                    sys_inventoryItemId: "{inventoryItemId}",
                    data: {{
                        resolution: {{
                            timeUnit: {timeUnit}
                            factor: {factor}
                            }}
                        unit: "{unit}"
                        dataPoints: [
                            {_dataPoints}
                        ]
                    }}
                }})
                    {{
                        {Utils.errors}
                    }}
                }}
            '''
            try:
                result = Utils._executeGraphQL(self, graphQLString)
            except Exception as err:
                logger.error(err)
                return

            return result

        if len(dataPoints) < chunkSize:
            _dataPoints = UtilsTimeSeries._dataPointsToString(dataPoints)
            result = _setTimeSeriesData(_dataPoints)
            
            if result[key]['errors']:
                Utils._listGraphQlErrors(result, key)
            else:
                logger.info(f"{len(dataPoints)} data points set for time series {inventoryItemId}.")
            if result == None: return
            return

        else:
            dataPointsCount = 0
            for i in range(0, len(dataPoints), chunkSize):
                sliceDataPoints = UtilsTimeSeries._sliceDataPoints(dataPoints.items(), i, i + chunkSize)
                _sliceDataPoints = UtilsTimeSeries._dataPointsToString(sliceDataPoints)
                result = _setTimeSeriesData(_sliceDataPoints)
                if result == None: continue
                if result[key]['errors']:
                    Utils._listGraphQlErrors(result, key)
                
                dataPointsCount += len(sliceDataPoints)

            logger.info(f"{dataPointsCount} data points set for time series {inventoryItemId}.")

        return

    def setTimeSeriesDataCollection(self, timeSeriesData:list, chunkSize:int=1000) -> None:
        """
        Sets new time series data (timestamp & value) to an existing time series or 
        overwrites existing values. The sys_inventoryId and sys_inventoryItemId of the 
        time series is used. The dictionary represents the GraphQL format.
        As timestamp format you can use UTC (e.g. 2020-01-01T00:01:00Z) or 
        DateTimeOffset (e.g. 2020-01-01T00:00:00+01:00).

        Parameters
        ----------
        data: list
            A list of dictionaries defining inventory, inventoryItemId, resolution, 
            unit and time series values. Is used to write time series values for
            many time series in one single transaction.
        chunkSize: int = 10000
            Determines the packageSize of time series values that are written in 
            a single transaction

        Example: 
        --------
        >>> tsItems = [
                {
                    'sys_inventoryId': 'A6RGwtDbbk', 
                    'sys_inventoryItemId': 'TzdG1Gj2GW', 
                    'data': 
                        {
                            'resolution': {'timeUnit': 'MINUTE', 'factor': 15}, 
                            'unit': 'kW', 
                            'dataPoints': [
                                {
                                    'timestamp': '2021-12-10T07:40:00Z', 
                                    'value': 879.2
                                }
                            ]
                        }
                    },
                ] 
        >>> client.TimeSeries.setTimeSeriesDataCollection(tsItems)
        """
        try:
            _timeSeriesData = UtilsTimeSeries._tsCollectionToString(timeSeriesData)
        except Exception as err:
            logger.error(f"GraphQL string could not be created out of dictionary. Cause: {err}")
            return

        key = f'setTimeSeriesData'        
        graphQLString = f'''
            mutation {key} {{
            {key} (input: {_timeSeriesData})
                {{
                    {Utils.errors}
                }}
            }}
        '''
        try:
            result = Utils._executeGraphQL(self, graphQLString)
        except Exception as err:
            logger.error(err)
            return
           
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.debug(f"time series data points set.")
        if result == None: return
        return
   
    def timeSeriesData(self, inventoryName:str, fromTimepoint:str, toTimepoint:str, 
        fields:list=['sys_displayValue'], where:str=None, timeUnit:str=None, 
        factor:int=1, aggregationRule:str='AVG', timeZone:str=None, 
        displayMode:str='compressed',) -> pd.DataFrame:
        """
        Queries time series data and returns its values and properties 
        in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        fields: list|str = None
            Properties of the time series to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE intervall.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        displayMode: str = compressed 
            compressed: pivot display with dropping rows and columns that are NaN
            pivot-full: full pivot with all NaN columns and rows
            rows: row display

        Examples:
        ---------
        >>> timeSeriesData('meterData', '2020-10-01', '2020-10-01T:05:30:00Z')
        >>> timeSeriesData('meterData', fromTimepoint='2020-06-01', 
                toTimepoint='2020-06-15', fields=['meterId', 'phase'] 
                where='measure eq "voltage"')    
        """

        if timeZone != None:
            tz = timeZone
        else:
            tz = Utils.timeZone          

        _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, tz)
        _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, tz)

        if type(fields) != list:
            _fields = fields
        else:
            _fields = ''
            for header in fields:
                _fields += header + '\n'

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(where)

        if timeUnit != None:
            aggregation = f'''
                aggregation: {aggregationRule}
                resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                '''
        else:
            aggregation = ''

        key = inventoryName
        graphQLString = f'''query timeSeriesData {{
                {key}
                (pageSize: 500 {resolvedFilter})
                {{
                    {_fields}
                    _dataPoints (input:{{
                        from:"{_fromTimepoint}"
                        to:"{_toTimepoint}"
                        {aggregation}
                        }})
                    {{
                        timestamp
                        value
                        flag
                    }}
                }}
            }}'''
        
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pd.json_normalize(result[key], ['_dataPoints'], fields)
        if df.empty:
            logger.info('The query did not produce results.')
            return df
        df.loc[(df.flag == 'MISSING'), 'value'] = nan

        if displayMode == 'pivot-full':
            df = df.pivot_table(index='timestamp', columns=fields, values='value', dropna=False)
            columnNumber = len(result[key])
            dfColumnNumber = len(df.columns)
            if dfColumnNumber < columnNumber:
                logger.warning(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers.")
        elif displayMode == 'compressed':
            df = df.pivot_table(index='timestamp', columns=fields, values='value', dropna=True)
            columnNumber = len(result[key])
            dfColumnNumber = len(df.columns)
            if dfColumnNumber < columnNumber:
                logger.warning(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers or NaN-columns")
        elif displayMode == 'rows':
            pass
        

        df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S').tz_convert(pytz.timezone(tz))
                
        if Utils.useDateTimeOffset == False:
            df.index = df.index.tz_localize(tz=None)
        
        return df

    def timeSeriesGroupData(self, inventoryName:str, fromTimepoint:str, toTimepoint:str, 
        fields:list=['sys_displayValue'], instanceFields:list=['sys_displayValue'], 
        instancePrefix:str='instance.', where:str=None, whereInstance:str=None, 
        timeUnit:str=None, factor:int=1, aggregationRule:str='AVG', 
        timeZone:str=None, displayMode:str='compressed') -> pd.DataFrame:
        """
        Queries time series data from time series groups and returns its values and properties 
        for each time series instance in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        fields: list|str = None
            Properties of the time series group to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        instanceFields: list|str = None
            Properties of the time series instance to be used as header. Uses the displayValue as default. 
        instancePrefix: str = 'instance'
            Changes the prefix for all time series instance properties.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        whereInstance: str = None
            Use a string to add where criteria for time series instances.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE intervall.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        displayMode: str = compressed 
            compressed: pivot display with dropping rows and columns that are NaN
            pivot-full: full pivot with all NaN columns and rows
            rows: row display

        Examples:
        ---------
        >>> timeSeriesDataGroup('foreCastGroups', '2022-10-01', '2022-10-12')
        >>> timeSeriesDataGroup(
                inventoryName='foreCastGroups', 
                fromTimepoint='2022-10-01',
                toTimepoint='2022-10-12',
                fields=['region', 'measure'],
                instanceFields='issueDate',
                instancePrefix='',
                where='region in ["DE", "FR", "PL"],
                whereInstance='issueDate >= '2022-10-01',
                timeUnit:'DAY'
                )
        """

        if timeZone != None:
            tz = timeZone
        else:
            tz = Utils.timeZone          

        _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, tz)
        _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, tz)

        if type(fields) != list:
            _groupFields = fields
        else:
            _groupFields = ''
            for header in fields:
                _groupFields += header + '\n'

        if type(instanceFields) != list:
            _instanceFields = instanceFields
        else:
            _instanceFields = ''
            for header in instanceFields:
                _instanceFields += header + '\n'

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(where)

        resolvedInstanceFilter = ''
        if whereInstance != None: 
            resolvedInstanceFilter = Utils._resolveWhereString(whereInstance)

        if timeUnit != None:
            aggregation = f'''
                aggregation: {aggregationRule}
                resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                '''
        else:
            aggregation = ''

        if resolvedInstanceFilter == '':
            instanceInput = ''
        else:
            instanceInput = f'''({resolvedInstanceFilter})'''
           
        instanceDataPoints = f'''_dataPoints (input:{{
                        from:"{_fromTimepoint}"
                        to:"{_toTimepoint}"
                        {aggregation}
                        }})
                    {{
                        timestamp
                        value
                        flag
                    }}
        '''
        
        key = inventoryName
        graphQLString = f'''query timeSeriesData {{
                {key} (
                pageSize: 500 
                {resolvedFilter}
                )
                {{
                    {_groupFields}
                    timeSeriesInstances {instanceInput} {{
                        {_instanceFields}
                        {instanceDataPoints}
                    }}
                }}
            }}'''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        meta = [field for field in fields]
        meta += [['timeSeriesInstance', field] for field in instanceFields]

        df = pd.json_normalize(result[key], record_path = ['timeSeriesInstances', '_dataPoints'], 
            meta=meta)
        
        # rename columns
        reColumns = []
        for col in df.columns:
            if col.startswith('timeSeriesInstance'):
                col = col.replace('timeSeriesInstance.', instancePrefix)
            reColumns.append(col)
        df.columns = reColumns     

        if df.empty:
            logger.info('The query did not produce results.')
            return df
        df.loc[(df.flag == 'MISSING'), 'value'] = nan

        pivotColumns = list(df.columns)[3:]

        if displayMode == 'pivot-full':
            df = df.pivot_table(index='timestamp', columns=pivotColumns, values='value', dropna=False)
            columnNumber = len(result[key])
            dfColumnNumber = len(df.columns)
            if dfColumnNumber < columnNumber:
                logger.warning(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers.")
        elif displayMode == 'compressed':
            df = df.pivot_table(index='timestamp', columns=pivotColumns, values='value', dropna=True)
            columnNumber = len(result[key])
            dfColumnNumber = len(df.columns)
            if dfColumnNumber < columnNumber:
                logger.warning(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers or NaN-columns")
        elif displayMode == 'rows':
            pass

        df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S').tz_convert(pytz.timezone(tz))
                
        if Utils.useDateTimeOffset == False:
            df.index = df.index.tz_localize(tz=None)
        
        return df

    def timeSeriesGroupDataReduced(self, inventoryName:str, fromTimepoint:str, toTimepoint:str, 
        reduceFunction:str='LAST', fields:list=['sys_displayValue'], instanceFields:list=['sys_displayValue'], 
        where:str=None, whereInstance:str=None, 
        timeUnit:str=None, factor:int=1,
        timeZone:str=None, displayMode:str='compressed') -> pd.DataFrame:
        """
        Queries time series group data, reduces time series instances to a single array
        for each time series group and returns its values and properties 
        in a DataFrame.

        Parameter:
        --------
        inventoryName: str
            The name of the inventory.
        fromTimepoint: str
            The starting timepoint from where time series data will be retrieved. Different string
            formats as well as datetime.datetime and pandas.Timestamp objects are supported.
        toTimepoint: str
            The ending timepoint from where time series data will be retrieved
        reduceFunction: str = 'LAST'
            The function that determines how values from multiple time series instances should be reduced 
            to a single array.
        fields: list|str = None
            Properties of the time series group to be used as header. Uses the displayValue as default. 
            If fields are not unique for each column, duplicates will be omitted. If you use 
            multiple fields, a MultiIndex DataFrame will be created. Use inventoryProperties() 
            to find out which properties are available for an inventory. 
            To access MultiIndex use syntax like <df[header1][header2]>.
        instanceFields: list|str = None
            Properties of the time series instance to be used as header. Uses the displayValue as default. 
        instancePrefix: str = 'instance'
            Changes the prefix for all time series instance properties.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'
            Referenced items are not supported.
        whereInstance: str = None
            Use a string to add where criteria for time series instances.
        timeUnit: str = None
            The time unit if you want aggregate time series values. Use either 'MILLISECOND', 'SECOND'
            'MINUTE', 'HOUR', 'DAY', 'WEEK', 'MONTH', 'YEAR'.
        factor: int = 1
            A factor for time unit aggrergation, e.g. 15 for a 15 MINUTE intervall.
        aggregationRule: str = 'AVG'
            Choose between 'SUM', 'AVG', 'MIN' and 'MAX'.
        timeZone: str = None
            A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET'). Defaults
            to the local time zone or to a previously set default time zone.
        displayMode: str = compressed 
            compressed: pivot display with dropping rows and columns that are NaN
            pivot-full: full pivot with all NaN columns and rows
            rows: row display

        Examples:
        ---------
        >>> timeSeriesDataGroup('foreCastGroups', '2022-10-01', '2022-10-12')
        >>> timeSeriesDataGroup(
                inventoryName='foreCastGroups', 
                fromTimepoint='2022-10-01',
                toTimepoint='2022-10-12',
                fields=['region', 'measure'],
                instanceFields='issueDate',
                instancePrefix='',
                where='region in ["DE", "FR", "PL"],
                whereInstance='issueDate >= '2022-10-01',
                timeUnit:'DAY'
                )
        """

        if timeZone != None:
            tz = timeZone
        else:
            tz = Utils.timeZone          

        _fromTimepoint = TimeUtils._inputTimestamp(fromTimepoint, tz)
        _toTimepoint = TimeUtils._inputTimestamp(toTimepoint, tz)

        if type(fields) != list:
            _groupFields = fields
        else:
            _groupFields = ''
            for header in fields:
                _groupFields += header + '\n'

        if type(instanceFields) != list:
            _instanceFields = instanceFields
        else:
            _instanceFields = ''
            for header in instanceFields:
                _instanceFields += header + '\n'

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(where)

        resolvedInstanceFilter = ''
        if whereInstance != None: 
            resolvedInstanceFilter = Utils._resolveWhereString(whereInstance)

        if timeUnit != None:
            aggregation = f'''
                resolution: {{timeUnit: {timeUnit} factor: {factor}}}
                '''
        else:
            aggregation = ''

        if resolvedInstanceFilter == '':
            instanceInput = ''
        else:
            instanceInput = f'''({resolvedInstanceFilter})'''
           
        groupInput = f'''input:{{
                        from:"{_fromTimepoint}"
                        to:"{_toTimepoint}"
                        {aggregation}
                        reducer: {reduceFunction}
                        showMissing: true
                        }}
        '''
        
        key = inventoryName
        graphQLString = f'''query timeSeriesData {{
                {key} (
                pageSize: 500 
                {resolvedFilter}
                {groupInput}
                )
                {{
                    {_groupFields}
                    _dataPoints {{
                        timestamp
                        value
                        flag
                        }}
                    timeSeriesInstances {instanceInput} {{
                        sys_inventoryItemId
                    }}
                }}
            }}'''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pd.json_normalize(result[key], ['_dataPoints'], fields)

        print(df)

        if df.empty:
            logger.info('The query did not produce results.')
            return df
        df.loc[(df.flag == 'MISSING'), 'value'] = nan

        pivotColumns = list(df.columns)[3:]

        if displayMode == 'pivot-full':
            df = df.pivot_table(index='timestamp', columns=pivotColumns, values='value', dropna=False)
            columnNumber = len(result[key])
            dfColumnNumber = len(df.columns)
            if dfColumnNumber < columnNumber:
                logger.warning(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers.")
        elif displayMode == 'compressed':
            df = df.pivot_table(index='timestamp', columns=pivotColumns, values='value', dropna=True)
            columnNumber = len(result[key])
            dfColumnNumber = len(df.columns)
            if dfColumnNumber < columnNumber:
                logger.warning(f"{columnNumber-dfColumnNumber} columns omitted due to duplicate column headers or NaN-columns")
        elif displayMode == 'rows':
            pass

        df.index = pd.to_datetime(df.index, format='%Y-%m-%dT%H:%M:%S').tz_convert(pytz.timezone(tz))
                
        # if Utils.useDateTimeOffset == False:
        #     df.index = df.index.tz_localize(tz=None)
        
        return df

    def units(self) -> pd.DataFrame:
        """
        Returns a DataFrame of existing units.

        Examples:
        >>> units()
        """

        graphQLString = f'''query getUnits {{
        units
            {{
            name
            baseUnit
            factor
            isBaseUnit
            aggregation
            }}
        }}
        '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        return pd.json_normalize(result['units'])

    def createUnit(self, unit:str, baseUnit:str, factor:float, aggregation:str) -> None:
        """
        Creates a unit on basis of a base unit.

        Parameters:
        ----------
        unit : str
            The name of the unit to be created.
        baseUnit : str
            The name of an existing base unit.
        factor : float
            The factor related to the base unit.
        aggregation : str
            The enum value for default aggregation. Possible are 'SUM' and 'AVG' This 
            kind of aggregation is used for integral units (kW -> kWh), which are not supported 
            yet.

        Example:
        >>> createUnit('kW', 'W', 1000, 'AVG')
        """

        graphQLString = f'''
            mutation createUnit {{
                createUnit(input: {{
                    name: "{unit}"
                    baseUnit: "{baseUnit}"
                    factor: {factor}
                    aggregation: {aggregation}}})
                {{
                    {Utils.errors}
                }}
            }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        key = f'createUnit'
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"Unit {unit} created.")

        return

    def createBaseUnit(self, baseUnit:str, aggregation:str) -> None:
        """
        Creates a base unit.

        Parameters:
        ----------
        baseUnit : str
            The name of the base unit to be created.
        aggregation : str
            The enum value for default aggregation. Possible are 'SUM' and 'AVG' This 
            kind of aggregation is used for integral units (kW -> kWh), which are not supported 
            yet.

        Example:
        >>> createBaseUnit('W', 'AVG')
        """

        graphQLString = f'''
            mutation createBaseUnit {{
                createBaseUnit(input: {{
                    name: "{baseUnit}"
                    aggregation: {aggregation}}})
                {{
                    {Utils.errors}
                }}
            }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        key = f'createBaseUnit'
        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"Unit {baseUnit} created.")

        return

    def deleteUnit(self, unit:str, force=False) -> None:
        """
        Deletes a unit. Units can only be deleted if there are no Time Series that use this unit. 
        Base units can only be deleted, if no derived units exist.

        Parameters:
        ----------
        unit : str
            Name of the unit to be deleted.
        force : bool
            Optional, use True to ignore confirmation.
        
        Example:
        >>> deleteUnit('kW', force=True)
        """

        if force == False:
            confirm = input(f"Press 'y' to delete unit '{unit}'")
        else: confirm = 'y'

        graphQLString = f'''
        mutation deleteUnit{{
            deleteUnit (input: {{
                name: "{unit}"
                }})
                    {{
                    {Utils.errors}
                }}
            }}
            '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        logger.info(f"Unit {unit} deleted.")

        return

