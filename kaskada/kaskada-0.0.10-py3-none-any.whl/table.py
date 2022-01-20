"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express 
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""
from typing import Union

from kaskada.client import Client
import kaskada
import kaskada.staging as ks
import kaskada.api.v1alpha.table_pb2 as table_pb
import kaskada.api.v1alpha.staged_file_pb2 as staged_pb

import grpc
import os
import pandas as pd

def get_table_name(table: Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]) -> str:
    """
    Gets the table name from either the table protobuf, create table response, get table response, or a string

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]): The target table object

    Returns:
        str: The table name (None if unable to match)
    """
    table_name = None
    if isinstance(table, table_pb.Table):
        table_name = table.table_name
    elif isinstance(table, table_pb.CreateTableResponse) or isinstance(table, table_pb.GetTableResponse):
        table_name = table.table.table_name
    elif isinstance(table, str):
        table_name = table
    
    if table_name == None:
        raise Exception("invalid table parameter provided. the table parameter must be the table object, table response from the SDK, or the table name")

    return table_name

def list_tables(search: str = None, client: Client = None) -> table_pb.ListTablesResponse:
    """
    Lists all tables the user has access to

    Args:
        search (str, optional): The search parameter to filter list by. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.ListTablesResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = table_pb.ListTablesRequest(
            search = search,
        )
        return client.tableStub.ListTables(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def get_table(table: Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str], client: Client = None) -> table_pb.GetTableResponse:
    """
    Gets a table by name

    Args:
        table (Union[Table, CreateTableResponse, GetTableResponse, str]): The target table object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.GetTableResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)
        req = table_pb.GetTableRequest(table_name = table_name)
        return client.tableStub.GetTable(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def create_table(table_name: str, time_column_name: str, entity_key_column_name: str, subsort_column_name: str, grouping_id: str = None, client: Client = None) -> table_pb.CreateTableResponse:
    """
    Creates a table

    Args:
        table_name (str): The name of the table
        time_column_name (str): The time column
        entity_key_column_name (str): The entity key column
        subsort_column_name (str): The subsort column
        grouping_id (str, optional): The grouping id. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.CreateTableResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = table_pb.CreateTableRequest(table = table_pb.Table(
            table_name = table_name,
            time_column_name = time_column_name,
            entity_key_column_name = entity_key_column_name,
            subsort_column_name = subsort_column_name,
            grouping_id = grouping_id
        ))
        return client.tableStub.CreateTable(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def delete_table(table: Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str], client: Client = None) -> table_pb.DeleteTableResponse:
    """
    Deletes a table referenced by name

    Args:
        table (Union[Table, CreateTableResponse, GetTableResponse, str]): The target table object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        table_pb.DeleteTableResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)
        req = table_pb.DeleteTableRequest(table_name = table_name)
        return client.tableStub.DeleteTable(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def load_data(
    table: Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str], 
    staged_file: Union[staged_pb.StagedFile, staged_pb.CreateStagedFileResponse, staged_pb.GetStagedFileResponse, str],
    client: Client = None) -> table_pb.LoadDataResponse:
    """
    Loads data to a table from a staged file

    Args:
        table (Union[Table, CreateTableResponse, GetTableResponse, str]): The target table object
        staged_file (Union[StagedFile, CreateStagedFileResponse, GetStagedFileResponse, Str]): The staged file object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Raises:
        Exception: No valid table parameter provided
        Exception: No valid staged file ID parameter provided

    Returns:
        table_pb.LoadDataResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    staged_file_id = None
    if isinstance(staged_file, staged_pb.StagedFile):
        staged_file_id = staged_file.file_id
    elif isinstance(staged_file, staged_pb.CreateStagedFileResponse) or isinstance(staged_file, staged_pb.GetStagedFileResponse):
        staged_file_id = staged_file.file.file_id
    elif isinstance(staged_file, str):
        staged_file_id = staged_file
    
    if staged_file_id == None:
        raise Exception("invalid staged file parameter provided. the second parameter must be the staged file object, staged file response from the SDK, or the staged file ID")

    try:
        table_name = get_table_name(table)
        kaskada.validate_client(client)
        req = table_pb.LoadDataRequest(
            table_name = table_name,
            file_id = staged_file_id,
        )
        return client.tableStub.LoadData(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def upload_file(table: Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str], file_path: str, client: Client = None):
    """
    Uploads a file directly to a table. Reads the file and uses the staging area to load the data.

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]): The target table object
        file_path (str): The source local file path
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        LoadDataResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT
    staged_file = ks.create_staged_file(file_path, client = client)
    return load_data(table, staged_file)

def upload_dataframe(table: Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str], df: pd.DataFrame, client: Client = None):
    """
    Uploads a dataframe directly to a table. Writes the dataframe to a local file and loads the data to the table

    Args:
        table (Union[table_pb.Table, table_pb.CreateTableResponse, table_pb.GetTableResponse, str]): The target table object
        df (pd.DataFrame): The source Pandas dataframe
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        LoadDataResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT
    staged_file = ks.create_staged_file(df, client = client)
    return load_data(table, staged_file)
