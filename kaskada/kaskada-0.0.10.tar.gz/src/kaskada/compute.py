"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from kaskada.client import Client
from typing import List
import kaskada
import kaskada.api.v1alpha.compute_pb2 as pb

import grpc

def query(query: str, with_tables: List[pb.WithTable] = [], with_views: List[pb.WithView] = [], result_behavior: str = 'all-results', response_as: str = 'parquet', data_token_id: str = None, resume_token: str = None, limits: pb.QueryRequest.Limits = None, client: Client = None) -> pb.QueryResponse:
    """
    Performs a query

    Args:
        query (str): The query to perform
        with_tables (List[pb.WithTable], optional): A list of tables to use in the query, in addition to the tables stored in the system.
        with_views (List[pb.WithView], optional): A list of views to use in the query, in addition to the views stored in the system.
        result_behavior (str, optional): Determines which results are returned. Either "all-results" (default), or "final-results" which returns only the final values for each entity.
        responsed_as (str, optional): Determines how the response is returned.  Either "parquet" (default) or "redis-bulk".  Note: if "redis-bulk", result_behavior is assumed to be "final-results".
        data_token_id (str, optional): Enables repeatable queries.  Queries performed against the same dataToken are always run on the same input data.
        resume_token (str, optional): Enables resumeable queries. Queries performed against a resumeToken and a dataToken produce the changed feature values from new data.
        limits (pb.QueryRequest.Limits, optional): Configure limits on the output set.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        compute_pb.QueryResponse: Response from the API
    """

    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)

        request_args = {
            "data_token_id": data_token_id,
            "resume_token": resume_token,
            "limits": limits,
            "query" : query,
            "result_behavior": 'RESULT_BEHAVIOR_FINAL_RESULTS' if result_behavior == 'final-results' else 'RESULT_BEHAVIOR_ALL_RESULTS',
            "with_tables" : with_tables,
            "with_views" : with_views,
        }

        if response_as == 'redis-bulk':
            request_args['redis_bulk'] = {}
        else:
            request_args['parquet'] = {}

        req = pb.QueryRequest(**request_args)

        return client.computeStub.Query(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)
