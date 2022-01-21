from __future__ import annotations
from typing import Optional, Any, Union

import requests
import json

from filters import Filter

__all__ = (
    'Client',
)

class Client:
    '''
    A client that communicates with SupaBase API servers.
    '''

    def __init__(self, db_url: str, api_key: str, table: Optional[str]=None) -> None:
        '''
        Initialize a client.
        anon_key or service_key can be used to specify the API key.
        db_url represents the unique portion or the URL of the database.
        Example: 
        For this URL -> https://ythwdmythxedmuaprwff.supabase.co/rest/v1/main
        'ythwdmythxedmuaprwff' is the database url.
        '''

        self.base: str = f"https://{db_url}.supabase.co/rest/v1/" if not db_url.startswith('https') else db_url
        self.table: Optional[str] = table
        self.headers: dict[str,str] = {
            'apikey' : api_key,
            'Authorization' : "Bearer " + api_key
        }
        self.application_headers: dict[str,str] ={
            "Content-Type": "application/json",
        }

    def read(self, query: Any, range: Union[tuple[int],list[int]]=[]) -> dict[str,Any]:
        '''
        Read data from the database with the option of filtering and paginating.
        Set query to '*' to read all data.
        Set query to a row name to read from the row.
        Set query to a list of row names to read from the specified rows.

        Making use of PostgREST syntax, you can also use the following operators to filter:
        - 'lt' for less than
        - 'lte' for less than or equal to
        - 'ge' for greater than
        - 'gte' for greater than or equal to
        - 'eq' for equal to
        - 'neq' for not equal to
        - 'in' for in
        - 'is' for is
        - 'fts' for full text search
        Syntax: row_name=operator.search_value
        Example: name=eq.John
        Example: age=gte.18

        Set range to a tuple or list of two integers to specify the range of rows to read.
        Example: range=(0,9), means read the first 10 rows.

        Returns a dictionary of the data queried for.
        '''
        
        pagination: dict[str, str] = {}
        if range != []:
            assert len(range) in [2] and type(range) in [list,tuple], "Range must be a tuple or list of two integers"
            pagination = {"Range": f"{range[0]}-{range[1]}"}
        # All Rows
        if query == "all" or query == "*":
            result: dict[str,Any] = self.send({'select':'*'}, extra_headers=pagination).json()
        elif isinstance(query, list):
            # List of Row Names
            if all(True if type(i)==str else False for i in query):
                result: dict[str,Any] = self.send({'select': ','.join(query)}, extra_headers=pagination).json()
            # List of Filters
            elif all(True if type(i)==Filter else False for i in query):
                filters = {k: v for d in query for k, v in d.to_dict().items()}
                result: dict[str,Any] = self.send(filters, extra_headers=pagination).json()
            else:
                raise Exception("Query must be a list of row names or a list of filters")
        # Single row name
        elif isinstance(query, str):
            result: dict[str,Any] = self.send({'select': query}, extra_headers=pagination).json()
        # Single Filter
        elif isinstance(query, Filter):
            result: dict[str,Any] = self.send(query.to_dict(), extra_headers=pagination).json()
        else:
            raise Exception("Query must be a row name, a list of row names, a filter")
        return result

    def insert(self, new_row: Union[dict[str, Any], list[dict[str, Any]], tuple[dict[str, Any]]], filters: Union[Filter, list[Filter], None]=None, upsert: bool=False) -> Optional[dict[str, Any]]:
        '''
        Insert a new row or multiple rows into the database. 
        new_row should be a dictionary or a list/tuple of dictionaries.
        Upsert is supported, set upsert to True to update if exists and create if not. Defaults to False.
        Returns upserted row(s) or None if upsert is False.
        '''
        if upsert:
            prefer = {"Prefer": "resolution=merge-duplicates"}
        else:
            prefer = {"Prefer": "return=representation"}
        if isinstance(filters, list):
            filters = {k: v for d in filters for k, v in d.to_dict().items()}
        elif filters != None:
            filters = filters.to_dict()
        return self.send(filters, new_row, method="post", extra_headers=self.application_headers | prefer).text

    def update(self, new_row: dict[str, Any], filters: Union[Filter, list[Filter]]) -> Optional[dict[str, Any]]:
        '''
        Update a row in the database.
        use filter to select the rows to update.
        new_row is a dictionary of new values.
        Returns the replaced values.
        '''
        if isinstance(filters, list):
            filters = {k: v for d in filters for k, v in d.to_dict().items()}
        else:
            filters = filters.to_dict()
        return self.send(filters, new_row, method="patch", extra_headers=self.application_headers | {"Prefer": "return=representation"})

    def delete(self, filters: Union[Filter, list[Filter]]) -> None:
        '''
        Delete a row in the database.
        use filter to select the rows to delete.
        '''
        if isinstance(filters, list):
            filters = {k: v for d in filters for k, v in d.to_dict().items()}
        else:
            filters = filters.to_dict()
        return self.send(filters, method="delete")

    def send(self, params: dict[str,Any], data: dict[str,Any]={}, extra_headers: dict[str,Any]={}, method="get") -> dict[str,Any]:
        '''
        Should not be called directly, rather, invoked by other methods.
        '''
        
        assert self.table!=None, "Table name is required"
        response: requests.models.Response = requests.request(method, self.base + self.table, headers=self.headers | extra_headers, params=params, data=json.dumps(data))
        if not response.ok:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response

    async def async_read(self, query: Any, range: Union[tuple[int], list[int]] = []) -> dict[str, Any]:
        '''
        Read data from the database with the option of filtering and paginating.
        Set query to '*' to read all data.
        Set query to a row name to read from the row.
        Set query to a list of row names to read from the specified rows.

        Making use of PostgREST syntax, you can also use the following operators to filter:
        - 'lt' for less than
        - 'lte' for less than or equal to
        - 'ge' for greater than
        - 'gte' for greater than or equal to
        - 'eq' for equal to
        - 'neq' for not equal to
        - 'in' for in
        - 'is' for is
        - 'fts' for full text search
        Syntax: row_name=operator.search_value
        Example: name=eq.John
        Example: age=gte.18

        Set range to a tuple or list of two integers to specify the range of rows to read.
        Example: range=(0,9), means read the first 10 rows.

        Returns a dictionary of the data queried for.
        '''

        pagination: dict[str, str] = {}
        if range != []:
            assert len(range) in [2] and type(range) in [
                list, tuple], "Range must be a tuple or list of two integers"
            pagination = {"Range": f"{range[0]}-{range[1]}"}
        # All Rows
        if query == "all" or query == "*":
            result = await self.send({'select': '*'}, extra_headers=pagination)
        elif isinstance(query, list):
            # List of Row Names
            if all(True if type(i) == str else False for i in query):
                result = await self.send({'select': ','.join(query)}, extra_headers=pagination)
            # List of Filters
            elif all(True if type(i) == Filter else False for i in query):
                filters = {k: v for d in query for k, v in d.to_dict().items()}
                result = await self.send(filters, extra_headers=pagination)
            else:
                raise Exception(
                    "Query must be a list of row names or a list of filters")
        # Single row name
        elif isinstance(query, str):
            result = await self.send({'select': query}, extra_headers=pagination)
        # Single Filter
        elif isinstance(query, Filter):
            result = await self.send(query.to_dict(), extra_headers=pagination)
        else:
            raise Exception(
                "Query must be a row name, a list of row names, a filter")
        return result.json()

    async def async_insert(self, new_row: Union[dict[str, Any], list[dict[str, Any]], tuple[dict[str, Any]]], filters: Union[Filter, list[Filter], None] = None, upsert: bool = False) -> Optional[dict[str, Any]]:
        '''
        Insert a new row or multiple rows into the database. 
        new_row should be a dictionary or a list/tuple of dictionaries.
        Upsert is supported, set upsert to True to update if exists and create if not. Defaults to False.
        Returns upserted row(s) or None if upsert is False.
        '''
        if upsert:
            prefer = {"Prefer": "resolution=merge-duplicates"}
        else:
            prefer = {"Prefer": "return=representation"}
        if isinstance(filters, list):
            filters = {k: v for d in filters for k, v in d.to_dict().items()}
        elif filters != None:
            filters = filters.to_dict()
        response = await self.send(filters, new_row, method="post", extra_headers=self.application_headers | prefer)
        return response.text

    async def async_update(self, new_row: dict[str, Any], filters: Union[Filter, list[Filter]]) -> Optional[dict[str, Any]]:
        '''
        Update a row in the database.
        use filter to select the rows to update.
        new_row is a dictionary of new values.
        Returns the replaced values.
        '''
        if isinstance(filters, list):
            filters = {k: v for d in filters for k, v in d.to_dict().items()}
        else:
            filters = filters.to_dict()
        response = await self.send(filters, new_row, method="patch", extra_headers=self.application_headers | {"Prefer": "return=representation"})
        return response

    async def async_delete(self, filters: Union[Filter, list[Filter]]) -> None:
        '''
        Delete a row in the database.
        use filter to select the rows to delete.
        '''
        if isinstance(filters, list):
            filters = {k: v for d in filters for k, v in d.to_dict().items()}
        else:
            filters = filters.to_dict()
        response = await self.send(filters, method="delete")
        return response

    async def async_send(self, params: dict[str, Any], data: dict[str, Any] = {}, extra_headers: dict[str, Any] = {}, method="get") -> dict[str, Any]:
        '''
        Should not be called directly, rather, invoked by other methods.
        '''

        assert self.table != None, "Table name is required"
        response: requests.models.Response = requests.request(
            method, self.base + self.table, headers=self.headers | extra_headers, params=params, data=json.dumps(data))
        if not response.ok:
            raise Exception(f"Error: {response.status_code} - {response.text}")
        return response
