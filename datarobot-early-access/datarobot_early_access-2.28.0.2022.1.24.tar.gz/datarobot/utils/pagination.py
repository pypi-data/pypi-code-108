#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.


def unpaginate(initial_url, initial_params, client):
    """ Iterate over a paginated endpoint and get all results

    Assumes the endpoint follows the "standard" pagination interface (data stored under "data",
    "next" used to link next page, "offset" and "limit" accepted as query parameters).

    Yields
    ------
    data : dict
        a series of objects from the endpoint's data, as raw server data
    """
    resp_data = client.get(initial_url, params=initial_params).json()
    for item in resp_data["data"]:
        yield item
    while resp_data["next"] is not None:
        next_url = resp_data["next"]
        resp_data = client.get(next_url).json()
        for item in resp_data["data"]:
            yield item
