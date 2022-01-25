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
WG_TEST_UUID = environ.get("ISOGEO_WORKGROUP_TEST_UUID")


# ############################################################################
# ######## Export functions ###########
# ###########################################################################
def _meta_get_resource_sync(func_outname_params: dict):
    """Meta function."""
    route_method = func_outname_params.get("route")
    out_filename = Path(outdir, func_outname_params.get("output_json_name") + ".json")

    try:
        # use request
        request = route_method(**func_outname_params.get("params"))
        # transform objects into dicts
        if not isinstance(request, (dict, list)):
            request = request.to_dict()
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

    # handle warnings
    if environ.get("ISOGEO_PLATFORM").lower() == "qa":
        import urllib3

        urllib3.disable_warnings()

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_USER_LEGACY_CLIENT_ID")
    client_secret = environ.get("ISOGEO_API_USER_LEGACY_CLIENT_SECRET")

    # -- Authentication and connection ---------------------------------
    # Isogeo client
    isogeo = Isogeo(
        auth_mode="user_legacy",
        client_id=client_id,
        client_secret=client_secret,
        auto_refresh_url="{}/oauth/token".format(environ.get("ISOGEO_ID_URL")),
        platform=environ.get("ISOGEO_PLATFORM", "qa"),
        lang="fr",
    )

    # getting a token
    isogeo.connect(
        username=environ.get("ISOGEO_USER_NAME"),
        password=environ.get("ISOGEO_USER_PASSWORD"),
    )

    # display elapsed time
    print("Authentication succeeded at {:5.2f}s".format(default_timer() - START_TIME))

    # get some object identifiers required for certain routes
    app_id = sample(isogeo.application.listing(include=()), 1)[0].get("_id")
    # resource_id = sample(isogeo.search(whole_results=0, page_size=50).results, 1)[
    #     0
    # ].get("_id")
    # share_id = isogeo.shares()[0].get("_id")

    # display elapsed time
    print(
        "Fixtures identifiers synchronously retrieved at {:5.2f}s".format(
            default_timer() - START_TIME
        )
    )

    # -- Async exports --------------------------------------------------
    # list of methods to execute
    li_api_routes = [
        # Account
        {"route": isogeo.account.get, "output_json_name": "api_account", "params": {}},
        # Applications
        {
            "route": isogeo.application.listing,
            "output_json_name": "api_applications",
            "params": {},
        },
        {
            "route": isogeo.application.get,
            "output_json_name": "api_application",
            "params": {"application_id": app_id},
        },
        # Keywords
        {
            "route": isogeo.keyword.thesaurus,
            "output_json_name": "api_keywords",
            "params": {"include": ("count",), "order_by": "count.isogeo"},
        },
        # Licenses
        {
            "route": isogeo.license.listing,
            "output_json_name": "api_licenses",
            "params": {"workgroup_id": WG_TEST_UUID},
        },
        # Specifications
        {
            "route": isogeo.specification.listing,
            "output_json_name": "api_specifications",
            "params": {"workgroup_id": WG_TEST_UUID},
        },
        # Workgroups
        {
            "route": isogeo.application.listing,
            "output_json_name": "api_workgroup_applications",
            "params": {"workgroup_id": WG_TEST_UUID, "caching": 0},
        },
        {
            "route": isogeo.catalog.listing,
            "output_json_name": "api_workgroup_catalogs",
            "params": {"workgroup_id": WG_TEST_UUID, "caching": 0},
        },
        {
            "route": isogeo.contact.listing,
            "output_json_name": "api_workgroup_contacts",
            "params": {"workgroup_id": WG_TEST_UUID, "caching": 0},
        },
        {
            "route": isogeo.license.listing,
            "output_json_name": "api_workgroup_licenses",
            "params": {"workgroup_id": WG_TEST_UUID, "caching": 0},
        },
        {
            "route": isogeo.specification.listing,
            "output_json_name": "api_workgroup_specifications",
            "params": {"workgroup_id": WG_TEST_UUID, "caching": 0},
        },
        {
            "route": isogeo.workgroup.statistics,
            "output_json_name": "api_workgroup_stats",
            "params": {"workgroup_id": WG_TEST_UUID},
        },
    ]

    # async loop
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)

    # display elapsed time
    time_completed_at = "{:5.2f}s".format(default_timer() - START_TIME)
    print(
        "Export finished. {} routes executed in {}".format(
            len(li_api_routes), time_completed_at
        )
    )

    isogeo.close()
