"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express 
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""
from typing import Union

from kaskada.client import Client
import kaskada
import kaskada.api.v1alpha.view_pb2 as view_pb

import grpc

def get_view_name(view: Union[view_pb.View, view_pb.CreateViewResponse, view_pb.GetViewResponse, str]) -> str:
    view_name = None
    if isinstance(view, view_pb.View):
        view_name = view.view_name
    elif isinstance(view, view_pb.CreateViewResponse) or isinstance(view, view_pb.GetViewResponse):
        view_name = view.view.view_name
    elif isinstance(view, str):
        view_name = view
    
    if view_name == None:
        raise Exception("invalid view parameter provided. the view parameter must be the view object, view response from the SDK, or the view name")

    return view_name

def list_views(search: str = None, client: Client = None) -> view_pb.ListViewsResponse:
    """
    Lists all the views the user has access to

    Args:
        search (str, optional): The search parameter to filter list by. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        view_pb.ListViewsResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = view_pb.ListViewsRequest(
            search = search,
        )
        return client.viewStub.ListViews(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)


def get_view(view: Union[view_pb.View, view_pb.CreateViewResponse, view_pb.GetViewResponse, str], client: Client = None) -> view_pb.GetViewResponse:
    """
    Gets a view by name 

    Args:
        view (Union[view_pb.View, view_pb.CreateViewResponse, view_pb.GetViewResponse, str]): The target view object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        view_pb.GetViewResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        view_name = get_view_name(view)
        kaskada.validate_client(client)
        req = view_pb.GetViewRequest(view_name = view_name)
        return client.viewStub.GetView(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def create_view(view_name: str, expression: str, client: Client = None) -> view_pb.CreateViewResponse:
    """
    Creates a view with a name and expression

    Args:
        view_name (str): The view name
        expression (str): The view fenl expression
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        view_pb.CreateViewResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = view_pb.CreateViewRequest(view = view_pb.View(
            view_name = view_name,
            expression = expression
        ))
        return client.viewStub.CreateView(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def delete_view(view: Union[view_pb.View, view_pb.CreateViewResponse, view_pb.GetViewResponse, str], client: Client = None) -> view_pb.DeleteViewResponse:
    """
    Deletes a view

    Args:
        view (Union[view_pb.View, view_pb.CreateViewResponse, view_pb.GetViewResponse, str]): The target view object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        view_pb.DeleteViewResponse: Response from the API
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        view_name = get_view_name(view)
        kaskada.validate_client(client)
        req = view_pb.DeleteViewRequest(view_name = view_name)
        return client.viewStub.DeleteView(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)
