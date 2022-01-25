# -*- coding: UTF-8 -*-
#! python3  # noqa E265

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Batch export to XML ISO19139
# Purpose:      Exports each of 10 last updated metadata into an XML ISO19139
# Author:       Isogeo
#
# Python:       3.5+
# Created:      14/11/2016
# Updated:      15/04/2019
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from pathlib import Path
from timeit import default_timer

# Isogeo
from isogeo_pysdk import Isogeo, Metadata

# #############################################################################
# ########## Globals ###############
# ##################################

# required subfolders
out_dir = Path("_output/")
out_dir.mkdir(exist_ok=True)

# ############################################################################
# ######### Main program ###########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    chrono_start = default_timer()  # chrono

    # ------------ Specific imports ----------------
    from os import environ
    from dotenv import load_dotenv

    # ------------ Load .env file variables ----------------
    load_dotenv(".env", override=True)

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_DEV_ID")
    client_secret = environ.get("ISOGEO_API_DEV_SECRET")

    # instanciating the class
    isogeo = Isogeo(
        auth_mode="group",
        client_id=client_id,
        client_secret=client_secret,
        auto_refresh_url="{}/oauth/token".format(environ.get("ISOGEO_ID_URL")),
        platform=environ.get("ISOGEO_PLATFORM", "qa"),
        lang="fr",
    )
    isogeo.connect()

    # Process #########
    latest_data_modified = isogeo.search(
        page_size=10, order_by="modified", whole_results=0
    )
    isogeo.close()

    for md in latest_data_modified.results:
        metadata = Metadata.clean_attributes(md)
        title = metadata.title
        xml_stream = isogeo.metadata.download_xml(metadata)

        with open(out_dir / "{}.xml".format(title), "wb") as fd:
            for block in xml_stream.iter_content(1024):
                fd.write(block)

    # chrono
    chrono_end = default_timer()
    print("Done in: {:5.2f}s".format(chrono_end - chrono_start))
