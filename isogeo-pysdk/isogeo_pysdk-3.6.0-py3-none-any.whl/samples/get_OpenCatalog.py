# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo sample - Check if OpenCatalog exists in shares, then build a matching table between metadata and opencatalog URL

    To use it from the repository root:

        `python ./isogeo_pysdk/samples/get_OpenCatalog.py`
"""

# ##############################################################################
# ########## Libraries #############
# ##################################

# standard
import logging

# Isogeo
from isogeo_pysdk import Isogeo, Share

# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    # standard
    from os import environ

    # 3rd party
    from dotenv import load_dotenv
    import urllib3

    logger = logging.getLogger()
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(logging.DEBUG)
    logger.addHandler(log_console_handler)

    # get user ID as environment variables
    load_dotenv("prod.env")

    # ignore warnings related to the QA self-signed cert
    if environ.get("ISOGEO_PLATFORM").lower() == "qa":
        urllib3.disable_warnings()

    # for oAuth2 Backend (Client Credentials Grant) Flow
    isogeo = Isogeo(
        auth_mode="group",
        client_id=environ.get("ISOGEO_API_GROUP_CLIENT_ID"),
        client_secret=environ.get("ISOGEO_API_GROUP_CLIENT_SECRET"),
        auto_refresh_url="{}/oauth/token".format(environ.get("ISOGEO_ID_URL")),
        platform=environ.get("ISOGEO_PLATFORM", "qa"),
    )

    # getting a token
    isogeo.connect()

    # Check OpenCatalog URLS
    print(
        "This application is authenticated as {} and supplied by {} shares.".format(
            isogeo.app_properties.name, len(isogeo._shares)
        )
    )

    for s in isogeo._shares:
        share = Share(**s)
        print(
            "\nShare {} owned by {}".format(
                share.name, share._creator.get("contact").get("name")
            )
        )

        # OpenCatalog status
        opencatalog_url = share.opencatalog_url(isogeo.oc_url)
        if isogeo.head(opencatalog_url):
            print("OpenCatalog available at: {}".format(opencatalog_url))
        else:
            print(
                "OpenCatalog not enabled yet. Go to the administration to add it: {}".format(
                    share.admin_url(isogeo.app_url)
                )
            )

        # get metadata present into the share
        share_mds = isogeo.search(whole_results=1, share=share._id)
        print("{} metadata are available through this share.".format(share_mds.total))

    # closing the connection
    isogeo.close()
