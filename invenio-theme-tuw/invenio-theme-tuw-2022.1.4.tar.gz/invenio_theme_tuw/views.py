# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

import requests
from flask import Blueprint, render_template
from invenio_cache import current_cache
from invenio_rdm_records.resources.serializers import UIJSONSerializer

from .search import FrontpageRecordsSearch


def fetch_schemaorg_jsonld(doi_url):
    """Fetch the Schema.org metadata for the DOI."""
    key = f"schemaorg_{doi_url}"
    metadata = current_cache.get(key)

    if metadata is None:
        try:
            response = requests.get(
                doi_url,
                headers={"Accept": "application/vnd.schemaorg.ld+json"},
                timeout=2,
            )
            if response.status_code == 200:
                metadata = response.text.strip()
                current_cache.set(key, metadata)

        except Exception:
            pass

    return metadata


def create_blueprint(app):
    """Create a blueprint with routes and resources."""

    blueprint = Blueprint(
        "invenio_theme_tuw",
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    @blueprint.app_template_filter("tuw_doi_identifier")
    def tuw_doi_identifier(identifiers):
        """Extract DOI from sequence of identifiers."""
        if identifiers is not None:
            for identifier in identifiers:
                if identifier.get("scheme") == "doi":
                    return identifier.get("identifier")

    @blueprint.app_template_global("tuw_create_schemaorg_metadata")
    def tuw_create_schemaorg_metadata(record):
        """Create schema.org metadata to include in a <script> tag."""
        metadata = None

        # get the DOI from the managed PIDs, or from the metadata as fallback
        rec_pids = record.get("pids", {})
        if "doi" in rec_pids:
            doi = rec_pids["doi"].get("identifier")
        else:
            rec_meta = record.get("metadata", {})
            doi = tuw_doi_identifier(rec_meta.get("identifiers"))

        if doi is not None:
            doi_url = (
                doi if doi.startswith("https://") else ("https://doi.org/%s" % doi)
            )
            metadata = fetch_schemaorg_jsonld(doi_url)

        return metadata

    @blueprint.route("/")
    def tuw_index():
        records = FrontpageRecordsSearch()[:5].sort("-created").execute()
        return render_template("invenio_theme_tuw/frontpage.html", records=_records_serializer(records))

    def _records_serializer(records=None):
        """Serialize list of records."""
        record_list = []
        for record in records:
            record_list.append(UIJSONSerializer().serialize_object_to_dict(record.to_dict()))
        return record_list

    @blueprint.route("/tuw/policies")
    def tuw_policies():
        return render_template("invenio_theme_tuw/policies.html")

    @blueprint.route("/tuw/contact")
    def tuw_contact():
        return render_template("invenio_theme_tuw/contact.html")

    return blueprint
