import pytest

from molgenis.bbmri_eric import utils
from molgenis.bbmri_eric.model import TableMeta


@pytest.fixture
def rows():
    return [
        {
            "_href": "/api/v2/test_collection/collA",
            "id": "collA",
            "parent_collection": {
                "_href": "/api/v2/test_collection/collB",
                "id": "collB",
            },
            "sub_collections": [],
        },
        {
            "_href": "/api/v2/test_collection/collB",
            "id": "collB",
            "sub_collections": [
                {"_href": "/api/v2/test_collection/collA", "id": "collA"}
            ],
        },
    ]


@pytest.fixture
def meta():
    return TableMeta(
        {  # output from metadata API, heavily pruned for brevity
            "data": {
                "id": "test_collection",
                "attributes": {
                    "items": [
                        {
                            "data": {
                                "name": "id",
                                "type": "string",
                                "idAttribute": True,
                            },
                        },
                        {
                            "data": {
                                "name": "parent_collection",
                                "type": "xref",
                                "idAttribute": False,
                            },
                        },
                        {
                            "data": {
                                "name": "sub_collections",
                                "type": "onetomany",
                                "idAttribute": False,
                            },
                        },
                    ],
                },
            },
        }
    )


def test_to_upload_format(rows):
    assert utils.to_upload_format(rows) == [
        {
            "id": "collA",
            "parent_collection": "collB",
            "sub_collections": [],
        },
        {"id": "collB", "sub_collections": ["collA"]},
    ]


def test_remove_one_to_manys(meta):
    rows = [
        {
            "id": "collA",
            "parent_collection": "collB",
            "sub_collections": [],
        },
        {"id": "collB", "sub_collections": ["collA"]},
    ]
    assert utils.remove_one_to_manys(rows, meta) == [
        {
            "id": "collA",
            "parent_collection": "collB",
        },
        {"id": "collB"},
    ]
