from dataclasses import dataclass
from gql import gql, Client#, AIOHTTPTransport, RequestsHTTPTransport # This is gql version 3
from gql.transport.requests import RequestsHTTPTransport
from loguru import logger
import base64

import pandas
import sys
import json
import os
import requests
import pytz
from tzlocal import get_localzone
import getpass

from .fileimport import FileImport
from .fileImportService import FileImportService
from .automation import Automation, Schedule
from .programming import Programming

from .utils.ut import Utils
from .utils.ut_meta import Meta
from .timeseries import TimeSeries


class TechStack(Utils, Meta):
    """
    Initializes a Seven2one TechStack client.

    Parameters:
    ----------
    host: str
        The host domain or ip address, e.g. 'app.organisation.com'
    user: str
        A username
    password: str = None
        The password belonging to the user. If None, it needs to
        be entered interactively.
    logLevel: str = 'WARNING'
        Change the highest log level. Available log levels are 
        'ERROR', 'WARNING', 'INFO' and 'DEBUG'.
    usePorts: bool = False
        A developer feature: if True, ports with prefix '8' for a
        developer ComposeStack will be used.
    timeZone: str = None
        A time zone provided in IANA or isoformat (e.g. 'Europe/Berlin' or 'CET').
        Defaults to the local timezone. 
    dateTimeOffset: bool = True
        Choose, if a Timestamp should be displayed as time zone naive (dateTimeOffset = False) 
        or with Offset information. 
    copyGraphQLString: bool = False
        A developer feature: if True, with each method execution, 
        the graphQL string is copied to the clipboard (Windows only).

    Examples:
    >>> client = TechStack('app.orga.com/', 'admin', logLevel='INFO')
    """

    def __init__(self, host:str, user:str, password:str=None, logLevel:str='WARNING', 
        usePorts:bool=False, timeZone:str=None, dateTimeOffset:bool=True, 
        copyGraphQLString:bool=False) -> object:
               
        try:
            logger.remove()
            logger.add(sys.stderr, format="{level:<10} {time} {message}", level=logLevel, colorize=True)
        except: pass

        if os.name == 'nt': 
            logger.debug('Dectected Windows, enabling pyperclip')
        else:
            logger.debug(f"Dectected platform: {os.name}")


        if password == None:
            password = getpass.getpass('Enter password: ')

        if usePorts == False:
            tokenUrl = f'https://{host}/authn/connect/token'
            dynEndpoint = f'https://{host}/dynamic-objects/graphql/'
            automationEndpoint = f'https://{host}/automation/graphql/'
            scheduleEndpoint = f'https://{host}/schedule/graphql/'
            programmingEndpoint = f'https://{host}/programming/graphql/'
            tsGatewayEndpoint = f'https://{host}/timeseries/graphql/'
            #fileImportServiceEndpoint = f'https://{host}/programming/graphql/'
        else: 
            tokenUrl = f'http://{host}:8040/connect/token'
            dynEndpoint = f'http://{host}:8050/graphql/'
            automationEndpoint = f'http://{host}:8120/graphql/'
            scheduleEndpoint = f'http://{host}:8130/graphql/'
            programmingEndpoint = f'http://{host}:8140/graphql/'
            tsGatewayEndpoint = f'http://{host}:8195/graphql/'
            fileImportServiceEndpoint = f'http://{host}:7200/graphql/'

        body = {
            'client_id': 'techstack-ui',
            'grant_type': 'password',
            'username': user,
            'password': password,
            'scope': 'dynamicobjectservice'
        }

        response = requests.post(tokenUrl, body, verify=True)
        try:
            response =  json.loads(response.text)
            token = response['access_token']
            logger.debug(f"Got Token: {token[:10]}...")
        except:
            logger.error(response)
            return

        header = {
            'authorization': 'Bearer ' + token
        }

        transport =  RequestsHTTPTransport(url=dynEndpoint, headers=header, verify=True)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)  
        self.accessToken = token
        self.scheme = self.client.introspection

        try:
            self.TimeSeries = TimeSeries(self.accessToken, tsGatewayEndpoint, self)
            self.FileImport = FileImport(self, self.TimeSeries)
        except Exception as err:
            logger.warning(f"Time series gateway not available")
            logger.debug(f"Reason: {err}")
            self.FileImport = FileImport(self)

        try:
            self.FileImportService = FileImportService(fileImportServiceEndpoint)
        except Exception as err:
            logger.debug(f"File import service not available")
            logger.debug(f"Reason: {err}")
        
        try:
            self.Automation = Automation(self.accessToken, automationEndpoint)
        except Exception as err:
            logger.warning(f"Automation service not available")
            logger.debug(f"Reason: {err}")
        
        try:
            self.Schedule = Schedule(self.accessToken, scheduleEndpoint)
        except Exception as err:
            logger.warning(f"Schedule service not available")
            logger.debug(f"Reason: {err}")

        try:
            self.Programming = Programming(self.accessToken, programmingEndpoint)
        except Exception as err:
            logger.warning(f"Programming service not available")
            logger.debug(f"Reason: {err}")

        # Defaults:
        if timeZone == None:
            Utils.timeZone = Utils._timeZone('local')
        else: 
            Utils.timeZone = timeZone
        Utils.useDateTimeOffset = dateTimeOffset
        Utils.copyGraphQLString = copyGraphQLString

        return

    def inventories(self, fields:list=None, where:str=None, orderBy:str=None, 
        asc:bool=True) -> pandas.DataFrame:
        """
        Returns a DataFrame of existing inventories.

        Parameters:
        ----------
        fields: list=None
            The list of fields to be queried, e.g.
            ['name', 'inventoryId, variant.name']
        where: str=None
            Use a string to add where criteria like 'name eq "meterData"'.
            The argument is momentarily very limited.
        orderBy: str=None
            Select one field to sort by.
        asc: bool=True
            Determines the sort order of items. Set to False to apply descending order.

        Examples:
        >>> getInventories()
        >>> getInventories(fields=['name', 'inventoryId'], 
                where='city eq "Hamburg"', 
                orderBy='variant', asc=True)
        """

        if fields == None:
            fields = ['name', 'inventoryId', 'variant.name', 'historyEnabled', 'hasValidityPeriods', 'isDomainUserType']
            _fields = Utils._queryFields(fields, recursive=True)
        else:
            try:
                _fields = Utils._queryFields(fields, recursive=True)
            except:
                logger.error("Fields must be provided as list, e.g. ['name', 'inventoryId, variant.name']")

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(where)

        if orderBy != None:
            if asc != True:
                _orderBy = f'order: {{ {orderBy}: DESC }}'
            else:
                _orderBy = f'order: {{ {orderBy}: ASC }}'
        else: _orderBy = ''

        graphQLString= f'''query getInventories {{
        inventories 
            (pageSize:1000 {_orderBy} {resolvedFilter})
            {{
            {_fields}
            }}
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pandas.json_normalize(result['inventories'])
        return df

    def items(self, inventoryName:str, references:bool=False, fields:list=None, where:str=None, 
        orderBy:str=None, asc:bool=True, pageSize:int=5000, 
        arrayPropertiesToPage:list=None, arrayPageSize:int=50) -> pandas.DataFrame:
        """
        Returns items of an inventory in a DataFrame.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        references: bool = False
            If True, items of referenced inventories will be added to the DataFrame. If
            the fields-parameter is used, this parameter is ignored.
        fields: list | str = None
            A list of all properties to be queried. If None, all properties will be queried.
            For referenced items use a '.' between inventory name and property.
        where: str = None
            Use a string to add where criteria like
            'method eq "average" and location contains "Berlin"'.
            Referenced items are not supported.
        orderBy: str = None
            Select a field to sort by.
        asc: bool = True
            Determines the sort order of items. If set to False, a descending order 
            is applied.
        pageSize: int = 5000
            The page size of items that is used to retrieve a large number of items.
        arrayPropertiesToPage:list = None
            Array (list) properties that should be paged. Real paging for array properties is 
            not yet supported. The properties listed here will just make use of of the arrayPageSize.
        arrayPageSize: int = 50
            The page size of list items that is used to page list items in an inventory item.

        Example:
        --------
        >>> items('appartments', references=True)
        """

        deleteId = False
        if fields != None:
            if type(fields) != list:
                fields = [fields]
            if 'sys_inventoryItemId' not in fields:
                deleteId = True
                fields += ['sys_inventoryItemId']
            _fields = Utils._queryFields(fields, recursive=True)
        else:
            properties = Utils._properties(self, inventoryName, recursive=True)
            properties = Utils._propertyList(properties, recursive=references)
            
            _fields = Utils._queryFields(properties, recursive=references)

        if len(_fields) == 0:
            logger.error(f"Inventory '{inventoryName}' not found.")
            return

        resolvedFilter = ''
        if where != None: 
            resolvedFilter = Utils._resolveWhereString(where)
        
        if orderBy != None:
            if asc != True:
                _orderBy = f'order: {{ {orderBy}: DESC }}'
            else:
                _orderBy = f'order: {{ {orderBy}: ASC }}'
        else: _orderBy = ''

        if arrayPropertiesToPage != None:
            listPagination = 'listPagination: [\n'
            for arrayProperty in arrayPropertiesToPage:
                listPagination += f'{{ from: 0, size: {arrayPageSize}, propertyPath: "{arrayProperty}" }}\n'
            listPagination += ']\n'
        else:
            listPagination = ''

        result = []
        count = 0
        lastId = ''

        while True:
            graphQLString= f''' query getItems {{
                    {inventoryName} (
                            pageSize: {pageSize} 
                            {listPagination}
                            {lastId}
                            {resolvedFilter}
                            {_orderBy}
                            ) {{
                        {_fields}
                    }}
                }}
                '''
            try:
                query = gql(graphQLString)
            except Exception as err:
                logger.error(err)
                return

            if count == 0:
                Utils._copyGraphQLString(graphQLString)

            try:
                _result = self.client.execute(query)
            except Exception as err:
                logger.error(err)
                return
            
            if _result[inventoryName]:
                result += _result[inventoryName]
                count += 1
            try:
                cursor = _result[inventoryName][-1]['sys_inventoryItemId']
                lastId = f'lastId: "{cursor}"'
            except: 
                break

        df = pandas.json_normalize(result)
        
        if fields != None: #sorts dataframe according to given fields
            try: # for array field this does not work
                df = df[fields]
            except:
                pass 
        if deleteId: del df['sys_inventoryItemId']

        return df

    def inventoryProperties(self, inventoryName, namesOnly=False):
        """
        Returns a DataFrame of a query of properties of an inventory.

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory.
        namesOnly : bool
            If True, only property names will be returned

        Example:
        --------
        >>> inventoryProperties('appartments') 


        """

        propertyFields = f'''
            name          
            ... Scalar
            isArray
            nullable
            ... Reference
            type
            propertyId
        '''

        graphQLString= f'''query Inventory {{
        inventory
            (inventoryName: "{inventoryName}")
            {{
            properties {{
                {propertyFields}
                }}
            }}
        }}
        fragment Scalar on IScalarProperty {{
            dataType
            }}
        fragment Reference on IReferenceProperty {{
            inventoryId
            inventoryName
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pandas.json_normalize(result['inventory']['properties'])

        if namesOnly == True:
            return list(df['name'])
        else:
            return df

    def propertyList(self, inventoryName, references=False, dataTypes=False):
        """
        Returns a list of properties of an inventory and its referenced inventories
        by reading out the scheme.

        Parameters:
        ----------
        inventoryName : str
            The name of the inventory.
        references : bool
            If True, properties of referenced inventories included.
        dataTypes : bool
            If True, result will be displayed as Series with properties as index and
            dataTypes as values.

        Example:
        --------
        >>> inventoryList('appartments') 

        """

        _properties = Utils._properties(self, inventoryName=inventoryName, recursive=references)

        if dataTypes == False:
            properties = Utils._propertyList(_properties, recursive=references)
        else:
            properties = pandas.Series(Utils._propertyTypes(_properties))

        return properties

    def addItems(self, inventoryName:str, items:list) -> str:
        """
        Adds from a list of dicts new items and returns a list
        of inventoryItemIds.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.

        Example:
        --------
        >>> items = [
                {
                'meterId': '86IEDD99',
                'dateTime': '2020-01-01T05:50:59Z'
                },
                {
                'meterId': '45IXZ52',
                'dateTime': '2020-01-07T15:41:14Z'
                }
            ]
        >>> addItems('meterData', items)
        """
        items = Utils._propertiesToString(items)
        key = f'create{inventoryName}'

        graphQLString= f'''mutation addItems {{
            {key} (input: 
                {items}
            )
                {{
                    {Utils.errors}           
                inventoryItems {{
                    sys_inventoryItemId
                }}
            }}
        }} 
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
        return result[key]['inventoryItems']

    def updateItems(self, inventoryName:str, items:list) -> None:
        """
        Updates from a list of dicts existing items. The 'sys_inventoryItemId'
        must be passed to each item.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list with dictionaries for each item.

        Example:
        --------
        >>> items = [
                {
                'sys_inventoryItemId':'118312438662692864',
                'meterId': '86IEDD99',
                'dateTime': '2020-01-01T05:50:59Z'
                },
                {
                'sys_inventoryItemId':'118312438662692864',
                'meterId': '45IXZ52',
                'dateTime': '2020-01-07T15:41:14Z'
                }
            ]
        >>> updateItems('meterData', items)
        """
        items = Utils._propertiesToString(items)
        #items = items.replace('"null"', 'null')
        key = f'update{inventoryName}'

        graphQLString= f'''mutation updateItems {{
            {key} (input: 
                {items}
            )
                {{
                    {Utils.errors}           
                    inventoryItems {{
                        sys_inventoryItemId
                }}
            }}
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)

        logger.info(f"{len(result[key]['inventoryItems'])} item(s) updated.")
        return

    def createInventory(self, name:str,  properties:list, variant:str=None, 
        propertyUniqueness:dict=None, historyEnabled:bool=False, 
        hasValitityPeriods:bool=False, isDomainUserType:bool=False) -> str:
        """
        Creates a new inventory. After creation, access rights must be set to add items.
        
        Parameters:
        ----------
        name : str
            Name of the new inventory (only alphanumeric characters allowed, 
            may not begin with a number)
        properties : list
            A list of dicts with the following mandatory keys: 
                name: str
                dataType: enum (STRING, BOOLEAN, DECIMAL, INT, LONG, DATE_TIME, 
                DATE_TIME_OFFSET)
            Optional keys:
                isArray: bool (Default = False)
                nullable: bool (Default = True)
                isReference: bool (Default = False)
                inventoryId: str (mandatory if hasReference = True)
        variant : str
            The inventory variant.
        propertyUniqueness : list
            A list of properties that should be unique in its combination. 
        historyEnabled : bool
            If True, changes in properties will be recorded in item history.
        hasValidityPeriods : bool
            If true, a validity period can be added to the item.    

        Example:
        --------
        >>> propertyDefinitions = [
            {
                'name': 'street',
                'dataType': 'STRING',
                'nullable': False,
            },
            {
                'name': 'postCode',
                'dataType': 'STRING',
                'nullable': False,
            },
            ]
            uniqueness = [{'uniqueKey': 'address', 'properties': ['street', 'postCode']}
        >>> createInventory('appartment', 'propertyDefinitions', propertyUniqueness=uniqueness) 
        """

        _properties = Utils._propertiesToString(properties)

        if variant != None:
            _variantId = f'{Utils._getVariantId(self.variants(), variant)}'
            logger.debug(f"Found variantId: {_variantId}")
            if type(_variantId) != str:
                logger.error(f"Variant name '{name}' not found")
                return
            _variant = f'variantId: "{_variantId}"'
        else: _variant = ''

        if propertyUniqueness != None:
            _propertyUniqueness = 'propertyUniqueness: ' + Utils._uniquenessToString(propertyUniqueness)
            logger.debug(_propertyUniqueness)
        else: _propertyUniqueness = ''

        _history = 'true' if historyEnabled != False else 'false'
        _validityPeriods = 'true' if hasValitityPeriods != False else 'false'
        _domainUser = 'true' if isDomainUserType != False else 'false'
        
        graphQLString= f'''
        mutation createInventory {{
            createInventory (input: {{
                name: "{name}"        
                properties: {_properties}
                {_variant}
                historyEnabled: {_history}
                hasValidityPeriods: {_validityPeriods}
                isDomainUserType: {_domainUser}
                {_propertyUniqueness}
                }})
                {{
                inventory {{
                    inventoryId
                    }}
                {Utils.errors}           
            }}
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result['createInventory']['errors']:
            Utils._listGraphQlErrors(result, 'createInventory')
            return

        logger.info(f"New inventory {name} created.")
 
        return result['createInventory']['inventory']['inventoryId']

    def deleteInventory(self, inventoryName:str, force:bool=False) -> str:
        """ 
        Deletes an inventory with all its containg items. 
        
        Parameters:
        -----------
        inventoryName : str
            The field name of the inventory.
        force : bool
            Use True to ignore confirmation.

        Example:
        ---------
        >>> deleteInventory('meterData', force=True)
        """

        inventory = self.inventories(where=f'name eq "{inventoryName}"')
        
        if inventory.empty:
            logger.error(f'Unknown inventory "{inventoryName}".')
            return
        inventoryId = inventory.loc[0, 'inventoryId']
        logger.debug(f'inventoryId: {inventoryId}')

        if force == False:
            confirm = input(f"Press 'y' to delete '{inventoryName}': ")

        key = 'deleteInventory'
        graphQLString= f'''mutation deleteInventory {{
            {key} (input:{{inventoryId: "{inventoryId}"}})
                {{
                    {Utils.errors}           
                }}
            }}
            '''

        if force == True: confirm = 'y'
        if confirm == 'y':
            result = Utils._executeGraphQL(self, graphQLString)
            if result == None: return
            if result[key]['errors']:
                Utils._listGraphQlErrors(result, key)
                return
            else: 
                logger.info(f"Inventory '{inventoryName}' deleted.")
        else: return

    def variants(self) -> pandas.DataFrame:
        """
            Returns a dataframe of available variants.
        """

        key = 'variants'
        graphQLString= f'''query getVariants {{
        {key} {{
            name
            variantId
            }}
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        df = pandas.json_normalize(result[key])
        return df

    def clearInventory(self, inventoryName:str, force=False):
        """
        Deletes all items from the inventory

        Parameters
        -----------
        inventoryName : str
            The name of the inventory.
        force : bool
            Use True to ignore confirmation.
        """

        _result = self.items(inventoryName, ['sys_inventoryItemId', 'inventoryId'])
        if _result.empty:
            logger.info(f"The inventory is empty.")
            return
        _inventoryItemIds = list(_result['sys_inventoryItemId'])

        _ids = ''
        for id in _inventoryItemIds:
            _ids += f'{{sys_inventoryItemId: "{id}"}}\n'    
      
        logger.debug(f"GraphQL Ids: {_ids}")
            
        if force == False:
            confirm = input(f"Press 'y' to delete  {len(_inventoryItemIds)} items: ")

        key = f'delete{inventoryName}'
        graphQLString= f'''
            mutation deleteItems {{
                {key} ( input: 
                    [{_ids}]
                )
                {{
                    {Utils.errors}           
                }}
            }}
            '''

        if force == True: confirm = 'y'
        if confirm == 'y':
            result = Utils._executeGraphQL(self, graphQLString)
            if result == None: return
        else:
            return

        if result[key]['errors'] != None:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"{len(_inventoryItemIds)} items deleted.")

    def deleteItems(self, inventoryName:str, inventoryItemIds:list=None, where:str=None, force=False):
        """
        Deletes inventory items from a list of inventoryItemIds or by where-criteria. 

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory.
        items : list
            A list of inventoryItemIds that should be deleted.
        where : str
            Filter criteria to select items that should be deleted.
            Referenced items are not supported.
        all : bool
            All items of the inventory will be deleted
        force : bool
            Use True to ignore confirmation.

        Examples:
        ---------
        >>> deleteItems('meterData', where='changeDate gt "2020-12-01"', force=True)
        >>> deleteItems('meterData', inventoryItemIds=['ef73d6d5-d1d7-459a-b079-ec640cbb310e'])
        """

        if inventoryItemIds == None and where == None:
            logger.error(f"No list of items and no where-criteria were provided.")
        if inventoryItemIds != None and where != None:
            logger.warning(f"List of items and where-criteria has been provided. Item list is used.")

        if where != None:
            _result =self.items(inventoryName, ['sys_inventoryItemId', 'inventoryId'], 
                where=where)
            if _result.empty:
                logger.info(f"The where criteria '{where}' led to no results.")
                return

            _inventoryItemIds = list(_result['sys_inventoryItemId'])
            
        if inventoryItemIds != None:
            _inventoryItemIds = inventoryItemIds

        _ids = ''
        for id in _inventoryItemIds:
            _ids += f'{{sys_inventoryItemId: "{id}"}}\n'    
      
        logger.debug(f"GraphQL Ids: {_ids}")
            
        if force == False:
            confirm = input(f"Press 'y' to delete  {len(_inventoryItemIds)} items: ")

        key = f'delete{inventoryName}'
        graphQLString= f'''
            mutation deleteItems {{
                {key} ( input: 
                    [{_ids}]
                )
                {{
                    {Utils.errors}           
                }}
            }}
            '''
        

        if force == True: confirm = 'y'
        if confirm == 'y':
            result = Utils._executeGraphQL(self, graphQLString)
            if result == None: return
        else:
            return

        if result[key]['errors'] != None:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"{len(_inventoryItemIds)} items deleted.")

    def updateVariant(self, variantName, newName=None, icon=None) -> None:
        """Updates a variant"""

        _variantId = Utils._getVariantId(self.variants(), variantName) 
        logger.debug(f"Found variantId: {_variantId}")

        if newName != None:
            _name = f'name: "{newName}"'
        else:
            _name = 'null'

        if icon != None:
            _icon =f'icon: "{icon}"'
        else:
            _icon = 'null'

        key = 'updateVariant'
        graphQLString = f'''mutation updateVariant {{
            {key} (input:{{
                variantId: "{_variantId}"
                {_name}
                {_icon}
                }})
                {{
                    {Utils.errors}           
                }}
            }}
            '''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        return

    def updateArrayProperty(self, inventoryName:str, inventoryItemId:str, arrayProperty:str, 
        operation:str, arrayItems:list=None, cascadeDelete:bool=False) -> None:
        """
        Updates a single array property of a single inventoryItemId. Arrays with and without 
        references are supported.

        Parameters:
        -----------
        inventoryName : str
            The name of the inventory where the item is located.
        inventoryItemId : str
            The sys_inventoryItemId of the item.
        arrayProperty : str
            The name of the property whose array items are to be updated.
        operation : str
            The update operation to be performed. Options:
            insert: inserts a list of array items.
            removeById: removes array items by a list of given ids.
            removeByIndex: removes array items by a list of given indices.
            removeAll: removes all array items
        cascadeDelete : bool (False)
            If array items are refencences, True will delete also the reference items. 

        Examples:
        ---------
        >>> client.updateArrayProperty('meterData', 'A5N45hOOmm',
                'timeSeries', action='insert', arrayItems=['A5FdSjehbE'])
        >>> client.updateArrayProperty('meterData', 'A5N45hOOmm',
                'timeSeries', action='removeByIndex', arrayItems=[0,1], cascadeDelete=True)
        """

        operations = ['insert', 'removeById', 'removeByIndex', 'removeAll']
        if operation not in operations:
            logger.error(f"Action '{operation}' allowed. Possible update operations: {operations} ")

        if operation == 'removeAll':
            try:
                propertyDf = TechStack.inventoryProperties(self, 'volueGroups')
                arrayProps = propertyDf[propertyDf['name'] == arrayProperty]
                logger.debug(f"Properties of array: {arrayProps}")
                if arrayProps['type'].item() == 'reference':
                    arrDf = TechStack.items(self, inventoryName, 
                        where=f'sys_inventoryItemId eq "{inventoryItemId}"', fields=[f'{arrayProperty}.sys_inventoryItemId'],
                        arrayPropertiesToPage=[arrayProperty], arrayPageSize=5000)
                else:
                    arrDf = TechStack.items(self, inventoryName, fields=[{arrayProperty}],
                        where=f'sys_inventoryItemId eq "{inventoryItemId}"', listPageSize=5000)
            except Exception as err:
                logger.error(err)
                return
            countArray = len(arrDf[arrayProperty].item())
            arrayItems = [num for num in range(countArray)]
            logger.debug(f"Array Items: {arrayItems}")
        _arrayItems = Utils._arrayItemsToString(arrayItems, operation, cascadeDelete)
        logger.debug(f"Array Items as String: {_arrayItems}")

        key = f'update{inventoryName}ArrayProperties'
        graphQLString = f'''mutation updateArray {{
            {key} (
                input: {{
                sys_inventoryItemId: "{inventoryItemId}"
                {arrayProperty}: {{
                    {_arrayItems}
                    }}
                }}
            ) 
            {{
                {Utils.errors}           
            }}
        }}'''

        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors'] != None:
            Utils._listGraphQlErrors(result, key)
        else:
            logger.info(f"Array property {arrayProperty} for item {inventoryItemId} updated.")

    def addInventoryProperties(self, inventoryName:str, properties:list) -> None:
        """
        Adds one or more inventory properties to an existing inventory.

        Parameters:
        ----------
        inventoryName: str
            Name of inventory
        properties: list
            A list of dicts with the following mandatory keys: 
                name: str
                dataType: enum (STRING, BOOLEAN, DECIMAL, INT, LONG, DATE_TIME, 
                DATE_TIME_OFFSET)
            Optional keys:
                isArray: bool (Default = False)
                nullable: bool (Default = True)
                isReference: bool (Default = False)
                inventoryId: str (mandatory if hasReference = True)
        """

        key = 'addProperty' 
        inventory = self.inventories(where=f'name eq "{inventoryName}"')
        
        if inventory.empty:
            logger.error(f'Unknown inventory "{inventoryName}".')
        inventoryId = inventory.loc[0, 'inventoryId']
        _properties = Utils._propertiesToString(properties)

        graphQLString= f'''
        mutation {key} {{
        {key} (input: {{
            inventoryId: "{inventoryId}"	
            properties: {_properties}
            }}) 
            {{
                {Utils.errors}           
            }}
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
            return
        else:
            logger.info(f"New property(ies) added.")

    def updateDisplayValue(self, inventoryName, displayValue) -> None:

        inventory = self.inventories(where=f'name eq "{inventoryName}"')
        
        if inventory.empty:
            logger.error(f'Unknown inventory "{inventoryName}".')
            return
        inventoryId = inventory.loc[0, 'inventoryId']
        logger.debug(f'inventoryId: {inventoryId}')

        key = 'updateInventory'
        graphQLString= f'''mutation updateDisplayValue {{
            {key} (input: {{
                inventoryId: "{inventoryId}"
                displayValue: "{displayValue}"
                }}) {{
                {Utils.errors}
            }}
        }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        if result[key]['errors']:
            Utils._listGraphQlErrors(result, key)
            return
        else:
            logger.info(f"Display value updated.")

    def resync(self) -> None:
        """Resynchornizes read databases"""

        key = 'reSyncReadDatabase'
        graphQLString= f'''mutation resync{{
            {key}
            }}
        '''
        result = Utils._executeGraphQL(self, graphQLString)
        if result == None: return

        return result
    
    def defaultDataFrame(self, maxRows, maxColumns):
        """Sets default sizes for a DataFrame for the current session"""
        pandas.options.display.max_rows = maxRows
        pandas.options.display.max_columns = maxColumns
        return

    def defaults(self):
        """Shows default values"""
        defaults = {
            'Time zone': Utils.timeZone,
            'Use DateTimeOffset format': Utils.useDateTimeOffset,
            'Copy graphQL string': Utils.copyGraphQLString
            }

        return defaults

# Some stand alone functions

def encodeBase64(file:str):
    with open(file) as file:
        content = file.read()
        content = base64.b64encode(content.encode('ascii'))
        return content.decode('UTF8')
        
def decodeBase64(content:str):
    return base64.b64decode(content)