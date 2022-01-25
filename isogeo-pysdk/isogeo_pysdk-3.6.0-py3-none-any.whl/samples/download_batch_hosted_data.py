# -*- coding: UTF-8 -*-
#! python3  # noqa E265

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Batch export to XML ISO19139
# Purpose:      Exports hosted data of 10 last updated metadata into an XML ISO19139
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6.x
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from pathlib import Path

# Isogeo
from isogeo_pysdk import Isogeo

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

    # ------------ REAL START ------------------------------------------------
    latest_data_modified = isogeo.search(
        page_size=10,
        order_by="modified",
        whole_results=0,
        query="action:download",
        include=("links",),
    )
    isogeo.close()
    # parse and download
    for md in latest_data_modified.results:
        for link in filter(lambda x: x.get("type") == "hosted", md.get("links")):
            dl_stream = isogeo.metadata.links.download_hosted(link=link)
            with open(out_dir / dl_stream[1], "wb") as fd:
                for block in dl_stream[0].iter_content(1024):
                    fd.write(block)
