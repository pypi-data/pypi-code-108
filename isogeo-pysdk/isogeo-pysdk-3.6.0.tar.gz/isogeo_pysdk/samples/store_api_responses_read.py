# -*- coding: UTF-8 -*-
#! python3  # noqa E265

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Store API responses into JSON
# Purpose:      useful to generate tests fixtures or documentation
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from os import environ
from pathlib import Path
from random import sample
from timeit import default_timer

# 3rd party
from dotenv import load_dotenv

# Isogeo
from isogeo_pysdk import Isogeo

# #############################################################################
# ######## Globals #################
# ##################################

# output dir
outdir = Path(Path(__file__).parent, "_output/")
outdir.mkdir(exist_ok=True)

# environment vars
load_dotenv(".env", override=True)


# ############################################################################
# ######## Export functions ###########
# ###########################################################################
def _meta_get_resource_sync(func_outname_params: dict):
    """Meta function."""
    route_method = func_outname_params.get("route")
    out_filename = Path(outdir, func_outname_params.get("output_json_name") + ".json")

    try:
        request = route_method(**func_outname_params.get("params"))
        # use request
        if not isinstance(request, (dict, list)):
            request = request.to_dict()
        else:
            pass
        # store response into a json file
        with out_filename.open("w") as out_json:
            json.dump(request, out_json, sort_keys=True, indent=4, default=list)
    except Exception as e:
        logging.error(
            "Export failed to '{output_json_name}.json' "
            "using route '{route}' "
            "with these params '{params}'".format(**func_outname_params)
        )
        logging.error(e)


# ASYNC
async def get_data_asynchronous():
    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="IsogeoApi") as executor:
        # Set any session parameters here before calling `fetch`
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                _meta_get_resource_sync,
                # Allows us to pass in multiple arguments to `fetch`
                *(api_route,),
            )
            for api_route in li_api_routes
        ]

        # store responses
        out_list = []
        for response in await asyncio.gather(*tasks):
            out_list.append(response)

        return out_list


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    # chronometer
    START_TIME = default_timer()

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_DEV_ID")
    client_secret = environ.get("ISOGEO_API_DEV_SECRET")

    # -- Authentication and connection ---------------------------------
    isogeo = Isogeo(
        auth_mode="group",
        client_id=client_id,
        client_secret=client_secret,
        auto_refresh_url="{}/oauth/token".format(environ.get("ISOGEO_ID_URL")),
        platform=environ.get("ISOGEO_PLATFORM", "qa"),
        lang="fr",
    )
    isogeo.connect()

    # -- Async exports --------------------------------------------------
    # get some object identifiers required for certain routes
    resource_id = sample(isogeo.search(whole_results=0, page_size=50).results, 1)[
        0
    ].get("_id")
    share_id = isogeo.share.listing()[0].get("_id")

    # list of methods to execute
    li_api_routes = [
        {
            "route": isogeo.search,
            "output_json_name": "api_search_empty",
            "params": {"page_size": 0, "whole_results": 0, "augment": 1},
        },
        {
            "route": isogeo.search,
            "output_json_name": "api_search_complete",
            "params": {"whole_results": 1, "include": "all", "augment": 1},
        },
        {
            "route": isogeo.metadata.get,
            "output_json_name": "api_metadata_complete",
            "params": {"metadata_id": resource_id, "include": "all"},
        },
        # shares
        {"route": isogeo.share.listing, "output_json_name": "api_shares", "params": {}},
        {
            "route": isogeo.share.get,
            "output_json_name": "api_share_augmented",
            "params": {"share_id": share_id},
        },
        # static stuff
        {
            "route": isogeo.thesaurus.thesauri,
            "output_json_name": "api_thesauri",
            "params": {},
        },
        {
            "route": isogeo.thesaurus.thesaurus,
            "output_json_name": "api_thesaurus",
            "params": {},
        },
        {
            "route": isogeo.metadata.links.kinds_actions,
            "output_json_name": "api_link_kinds",
            "params": {},
        },
        {
            "route": isogeo.directive.listing,
            "output_json_name": "api_directives",
            "params": {},
        },
    ]

    # async loop
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)

    # display elapsed time
    elapsed = default_timer() - START_TIME
    time_completed_at = "{:5.2f}s".format(elapsed)
    print(
        "Export finished. {} routes executed in {}".format(
            len(li_api_routes), time_completed_at
        )
    )

    isogeo.close()
