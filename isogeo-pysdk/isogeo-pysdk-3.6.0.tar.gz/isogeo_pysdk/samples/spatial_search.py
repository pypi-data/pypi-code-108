# -*- coding: UTF-8 -*-
#! python3  # noqa E265

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Geographic search
# Purpose:      Filter results within an Isogeo share with spatial criteria, using
#               the Isogeo API Python minimalist SDK.
# Author:       Julien Moura (@geojulien)
#
# Python:       3.6+
# Created:      14/04/2016
# Updated:      18/05/2016
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Isogeo
from isogeo_pysdk import Isogeo


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

    # specific imports
    import geojson
    from geomet import wkt

    # ------------Authentication credentials ----------------
    client_id = environ.get("ISOGEO_API_DEV_ID")
    client_secret = environ.get("ISOGEO_API_DEV_SECRET")

    # ------------ Real start ----------------
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

    # ------------ REAL START ----------------------------

    geo_relation = "within"

    # opening a geojson file
    gson_input = r"samples_boundingbox.geojson"
    with open(gson_input) as data_file:
        data = data_file.read()
        data = geojson.loads(data)

    # search & compare
    basic_search = isogeo.search(page_size=0, whole_results=0)

    print("Comparing count of results returned: ")
    print("\t- without any filter = ", basic_search.total)

    for feature in data.get("features"):
        # just for VIPolygons
        if feature.get("geometry").get("type") != "Polygon":
            print("Geometry type must be a polygon")
            continue
        else:
            pass
        # get bounding box and convex hull
        bbox = ",".join(str(round(c, 3)) for c in feature.get("bbox"))
        poly = wkt.dumps(feature.get("geometry"), decimals=3)

        # search & display results - with bounding box
        filtered_search_bbox = isogeo.search(
            page_size=0, whole_results=0, bbox=bbox, georel=geo_relation
        )
        print(
            str("\t- {} (BOX) = {}\t{}").format(
                feature.get("properties").get("name"),
                filtered_search_bbox.total,
                bbox,
            )
        )
        # search & display results - with convex hull
        filtered_search_geo = isogeo.search(
            page_size=0, whole_results=0, poly=poly, georel=geo_relation
        )
        print(
            str("\t- {} (GEO) = {}\t{}").format(
                feature.get("properties").get("name"),
                filtered_search_geo.total,
                poly,
            )
        )

    isogeo.close()
