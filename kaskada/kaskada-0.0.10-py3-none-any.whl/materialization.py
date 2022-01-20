"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express 
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""
from typing import List, Union

import grpc
from kaskada.api.v1alpha.compute_pb2 import WithView
from kaskada.client import Client
import kaskada
import kaskada.api.v1alpha.materialization_pb2 as material_pb

class RedisAIDestination(object):
    db: int = 0
    host: str = None
    port: int = 0

    def __init__(self, db: int, host: str, port: int):
        """
        Kaskada Redis AI Destination object

        Args:
            db (int): The RedisAI database number to write to. Between 0 and 15 inclusive.
            host (str): The RedisAI instance hostname
            port (int): The RedisAI instance port
        """
        self.db = db
        self.host = host
        self.port = port

class MaterializationView(object):
    name: str = None
    expression: str = None

    def __init__(self, name: str, expression: str):
        """
        Kaskada Materialization View

        Args:
            name (str): The name of the view
            expression (str): The fenl expression to compute
        """
        self.name = name
        self.expression = expression

def create_materialization(name: str, query: str, destination: RedisAIDestination, views: List[MaterializationView] = [], client: Client = None) -> material_pb.CreateMaterializationResponse:
    """
    Creates a materialization

    Args:
        name (str): The Materialization's Name.
        query (str): A Fenl expression to compute.
        destination (RedisAIDestination): RedisAI instance
        views (list, optional): List of MaterializationView. Defaults to [].

    Returns:
        material_pb.CreateMaterializationResponse: [description]
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        req = material_pb.CreateMaterializationRequest(
            materialization = material_pb.Materialization(
                materialization_name = name,
                query = query,
                with_views = to_with_views(views),
                redis_a_i = material_pb.Materialization.RedisAI(
                    db = destination.db,
                    host = destination.host,
                    port = destination.port
                )
            )
        )
        return client.materializationStub.CreateMaterialization(req, metadata = client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def delete_materialization(materialization: Union[material_pb.Materialization, material_pb.CreateMaterializationResponse, material_pb.GetMaterializationResponse, str], client: Client = None) -> material_pb.DeleteMaterializationResponse:
    """
    Deletes a materialization by name

    Args:
        materialization (Union[material_pb.Materialization, material_pb.CreateMaterializationResponse, material_pb.GetMaterializationResponse, str]): The target materialization object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        material_pb.DeleteMaterializationResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        materialization_name = get_materialization_name(materialization)
        kaskada.validate_client(client)
        req = material_pb.DeleteMaterializationRequest(materialization_name = materialization_name)
        return client.materializationStub.DeleteMaterialization(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def get_materialization(materialization: Union[material_pb.Materialization, material_pb.CreateMaterializationResponse, material_pb.GetMaterializationResponse, str], client: Client = None) -> material_pb.GetMaterializationResponse:
    """
    Gets a materialization by name

    Args:
        materialization (Union[material_pb.Materialization, material_pb.CreateMaterializationResponse, material_pb.GetMaterializationResponse, str]): The target materialization object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        material_pb.GetMaterializationResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        materialization_name = get_materialization_name(materialization)
        kaskada.validate_client(client)
        req = material_pb.GetMaterializationRequest(materialization_name = materialization_name)
        return client.materializationStub.GetMaterialization(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def list_materializations(search: str = None, client: Client = None) -> material_pb.ListMaterializationsResponse:
    """
    Lists all the materializations the user has access to

    Args:
        search (str, optional): The search parameter to filter list by. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        material_pb.ListMaterializationsResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = material_pb.ListMaterializationsRequest(
            search = search
        )
        return client.materializationStub.ListMaterializations(req, metadata = client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def get_materialization_name(materialization) -> str:
    name = None
    if isinstance(materialization, str):
        name = materialization
    elif isinstance(materialization, material_pb.CreateMaterializationResponse) or isinstance(materialization, material_pb.GetMaterializationResponse):
        name = materialization.materialization.materialization_name
    elif isinstance(materialization, material_pb.Materialization):
        name = materialization.materialization_name
    else:
        raise Exception("invalid materialization parameter provided. the materialization parameter must be the materialization object, response from SDK or the materialization name")
    return name

def to_with_views(views: List[MaterializationView]) -> List[WithView]:
    with_views = []
    for v in views:
        with_views.append(WithView(
            name = v.name,
            expression = v.expression
        ))
    return with_views