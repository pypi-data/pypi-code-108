"""Pygeoapi instance of NLDI get splitcatchment at point."""
import logging
import time
from distutils.util import strtobool
from typing import Any

from pygeoapi.process.base import BaseProcessor

from nldi_flowtools.splitcatchment import SplitCatchment

LOGGER = logging.getLogger(__name__)

PROCESS_METADATA = {
    "version": "0.1.0",
    "id": "nldi-splitcatchment",
    "title": "NLDI Split Catchment process",
    "description": "NLDI Split Catchment process",
    "keywords": ["NLDI Split Catchment"],
    "links": [
        {
            "type": "text/html",
            "rel": "canonical",
            "title": "information",
            "href": "https://example.org/process",
            "hreflang": "en-US",
        }
    ],
    "inputs": [
        {
            "id": "lat",
            "title": "lat",
            "abstract": "The latitude coordinate of the pour point in decimal degrees",
            "input": {
                "literalDataDomain": {
                    "dataType": "float",
                    "valueDefinition": {"anyValue": True},
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
        {
            "id": "lon",
            "title": "lon",
            "abstract": "The longitude coordinate of the pour point in decimal degrees",
            "input": {
                "literalDataDomain": {
                    "dataType": "float",
                    "valueDefinition": {"anyValue": True},
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
        {
            "id": "upstream",
            "title": "upstream",
            "abstract": "Determines whether to return the portion of the drainage basin "
            "that falls outside of the local catchment. If True, then the entire "
            "drainage basin is returned. If False, then only the portion within the local "
            "catchment is returned.",
            "input": {
                "literalDataDomain": {
                    "dataType": "boolean",
                    "valueDefinition": {"anyValue": True},
                }
            },
            "minOccurs": 1,
            "maxOccurs": 1,
        },
    ],
    "outputs": [
        {
            "id": "catchment",
            "title": "catchment",
            "description": "The local NHD catchment that the pour point falls within."
            " This is also the catchment that gets split.",
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
        {
            "id": "splitCatchment",
            "title": "splitCatchment",
            "description": "Either a portion or the entire drainage basin for the pour "
            "point, depending if the pour point falls on an NHD flowline or not. It "
            "gets returned if the drainage basin fits only within the local catchment, "
            "or if the upstream variable is set to False.",
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
        {
            "id": "mergedCatchment",
            "title": "mergedCatchment",
            "description": "The entire drainage basin which flows to the pour point. "
            "It will include area outside of the local catchment, and it will only be "
            "returned if the upstream variable is set to True.",
            "output": {"formats": [{"mimeType": "application/geo+json"}]},
        },
    ],
    "example": {
        "inputs": [
            {"id": "lat", "value": "43.29139", "type": "text/plain"},
            {"id": "lon", "value": "-73.82705", "type": "text/plain"},
            {"id": "upstream", "value": "False", "type": "text/plain"},
        ]
    },
}


class NLDISplitCatchmentProcessor(BaseProcessor):
    """NLDI Split Catchment Processor."""

    def __init__(self, provider_def: Any):
        """Initialize object.

        :param provider_def: provider definition
        :returns: pygeoapi.process.nldi_delineate.NLDIDelineateProcessor
        """
        BaseProcessor.__init__(self, provider_def, PROCESS_METADATA)

    def execute(self, data: Any) -> tuple[str, dict[Any, Any]]:
        """Execute Split Catchment Processor."""
        mimetype = "application/json"
        newdata = {d["id"]: d["value"] for d in data}
        print(newdata)
        lat = float(newdata.get("lat"))
        lon = float(newdata.get("lon"))
        upstream = bool(strtobool(newdata.get("upstream")))

        print(lat, lon, upstream)

        time_before = time.perf_counter()

        results = SplitCatchment(lon, lat, upstream)

        time_after = time.perf_counter()
        total_time = time_after - time_before
        print("Total Time:", total_time)

        # outputs = [{
        #     'results': results.serialize()
        # }]

        return mimetype, results.serialize()

    def __repr__(self):  # noqa D105
        return "<NLDISplitCatchmentProcessor> {}".format(
            self.nldi - splitcatchment - response  # noqa F821
        )
