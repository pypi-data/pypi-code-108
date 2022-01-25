# -*- coding: UTF-8 -*-
#! python3  # noqa E265

# ------------------------------------------------------------------------------
# Name:         Isogeo sample - Attributes analisis
# Purpose:      Get feature attributes from Isogeo to perform some metrics.
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/04/2016
# Updated:      10/05/2017
# ------------------------------------------------------------------------------

# ##############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from collections import Counter

# Isogeo
from isogeo_pysdk import Isogeo, MetadataSearch

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

    # search
    search = isogeo.search(
        query="type:vector-dataset",  # filter only on vectors
        include=("feature-attributes",),  # ask for including feature attributes
        page_size=100,  # max metadata to download
        whole_results=0,  # download only the first results page
    )

    isogeo.close()

    if not isinstance(search, MetadataSearch):
        raise TypeError(search)
    else:
        pass

    # variables
    attributes = {}
    attributes_names = []
    attributes_types = []
    attributes_alias = []
    attributes_description = []
    vectors_without_attributes = []

    # parse
    for md in search.results:
        md_attributes = md.get("feature-attributes")
        if not md_attributes:
            vectors_without_attributes.append(
                "{} ({})".format(md.get("title"), md.get("_id"))
            )
            continue
        for field in md_attributes:
            attributes_names.append(field.get("name"))
            attributes_alias.append(field.get("alias", "NR"))
            attributes_types.append(field.get("dataType"))
            attributes_description.append(field.get("description", "NR"))
            attributes[field.get("name")] = (
                field.get("dataType"),
                field.get("alias", "NR"),
                field.get("description", "NR"),
            )

    # global metrics
    print(
        "{} attributes among "
        "{} metadatas retrieved of which "
        "{} do not have feature attributes.".format(
            len(attributes_names),
            len(search.results),
            len(vectors_without_attributes),
        )
    )

    # attributes names
    names_frequency = Counter(attributes_names)
    names_top10 = names_frequency.most_common(10)
    print("\nTop 10 attributes names: ", names_top10)

    # attributes types
    types_frequency = Counter(attributes_types)
    types_top10 = types_frequency.most_common(10)
    print("\nTop 10 attributes types: ", types_top10)

    # attributes aliases
    alias_frequency = Counter(attributes_alias)
    alias_top10 = alias_frequency.most_common(10)
    print("\nTop 10 attributes aliases: ", alias_top10)

    # attributes descriptions
    description_frequency = Counter(attributes_description)
    description_top10 = description_frequency.most_common(10)
    print("\nTop 10 attributes descriptions: ", description_top10)
