#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import pytest
import responses

from datarobot.models import ComplianceDocTemplate


@pytest.fixture
def templates_list_response():
    return [
        {
            "id": "5bbdf361962d7435e2c447fc",
            "name": "template #1",
            "creatorId": "5a421957aadebb4f0df2f096",
            "creatorUsername": "admin@datarobot.com",
            "orgId": "5a421957aadebb4f0df2f091",
            "sections": [
                {
                    "contentId": u"HOW_TO_USE",
                    "sections": [],
                    "title": u"How To Use This Document",
                    "type": u"datarobot",
                },
                {"title": u"Table of Contents", "type": u"table_of_contents"},
                {
                    "title": u"Empty user section",
                    "type": u"user",
                    "regularText": u"",
                    "highlighted_text": u"",
                },
                {
                    "contentId": u"PREFACE",
                    "sections": [],
                    "title": u"DataRobot Model Development Documentation",
                    "type": u"datarobot",
                },
                {
                    "contentId": u"EXECUTIVE_SUMMARY_AND_MODEL_OVERVIEW",
                    "sections": [],
                    "title": u"Exec Summary And Model Overview",
                    "type": u"datarobot",
                },
            ],
        },
        {
            "id": "5bbdf361962d7435e2c447fd",
            "name": "template #2",
            "creatorId": "5a421957aadebb4f0df2f096",
            "creatorUsername": "admin@datarobot.com",
            "orgId": "5a421957aadebb4f0df2f091",
            "sections": [
                {
                    "contentId": u"HOW_TO_USE",
                    "sections": [],
                    "title": u"How To Use This Document",
                    "type": u"datarobot",
                },
                {"title": u"Table of Contents", "type": u"table_of_contents"},
                {
                    "contentId": u"PREFACE",
                    "sections": [],
                    "title": u"DataRobot Model Development Documentation",
                    "type": u"datarobot",
                },
                {
                    "contentId": u"EXECUTIVE_SUMMARY_AND_MODEL_OVERVIEW",
                    "sections": [],
                    "title": u"Exec Summary And Model Overview",
                    "type": u"datarobot",
                },
            ],
        },
    ]


@responses.activate
def test_list(templates_list_response):
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/",
        json={
            "data": templates_list_response,
            "next": None,
            "previous": None,
            "count": len(templates_list_response),
        },
    )

    templates = ComplianceDocTemplate.list()

    for template, server_data in zip(templates, templates_list_response):
        assert template.id == server_data["id"]
        assert template.name == server_data["name"]
        assert template.creator_id == server_data["creatorId"]
        assert template.creator_username == server_data["creatorUsername"]
        assert template.org_id == server_data["orgId"]
        assert template.sections is not None


@responses.activate
def test_get(templates_list_response):
    server_data = templates_list_response[0]
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/{}/".format(server_data["id"]),
        json=server_data,
    )
    template = ComplianceDocTemplate.get(server_data["id"])

    assert template.id == server_data["id"]
    assert template.name == server_data["name"]
    assert template.creator_id == server_data["creatorId"]
    assert template.creator_username == server_data["creatorUsername"]
    assert template.org_id == server_data["orgId"]
    assert template.sections is not None


@responses.activate
def test_get_no_org_id(templates_list_response):
    server_data = dict(templates_list_response[0], orgId=None)
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/{}/".format(server_data["id"]),
        json=server_data,
    )
    template = ComplianceDocTemplate.get(server_data["id"])

    assert template.id == server_data["id"]
    assert template.name == server_data["name"]
    assert template.creator_id == server_data["creatorId"]
    assert template.creator_username == server_data["creatorUsername"]
    assert template.org_id is None
    assert template.sections is not None


@responses.activate
def test_update_name(templates_list_response):
    server_data = templates_list_response[0]
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/{}/".format(server_data["id"]),
        json=server_data,
    )
    responses.add(
        responses.PATCH,
        "https://host_name.com/complianceDocTemplates/{}/".format(server_data["id"]),
        body="",
        status=204,
    )
    template = ComplianceDocTemplate.get(server_data["id"])
    template.update(name="updated name")

    assert template.name == "updated name"


@responses.activate
def test_update_section(templates_list_response):
    server_data = templates_list_response[0]
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/{}/".format(server_data["id"]),
        json=server_data,
    )
    responses.add(
        responses.PATCH,
        "https://host_name.com/complianceDocTemplates/{}/".format(server_data["id"]),
        body="",
        status=204,
    )
    new_sections = [
        {"contentId": "HOW_TO_USE", "title": "How To Use", "type": "datarobot"},
        {"title": "Table of Contents", "type": "table_of_contents"},
        {"contentId": "PREFACE", "title": "Preface", "type": "datarobot"},
        {
            "contentId": "EXECUTIVE_SUMMARY_AND_MODEL_OVERVIEW",
            "title": "Summary",
            "type": "datarobot",
        },
        {
            "highlightedText": "Foo",
            "regularText": "Bar",
            "title": "Custom Section Added by User",
            "type": "user",
        },
    ]
    template = ComplianceDocTemplate.get(server_data["id"])
    template.update(sections=new_sections)

    assert template.sections[0]["contentId"] == "HOW_TO_USE"


@responses.activate
def test_create(templates_list_response):
    data = templates_list_response[0]
    responses.add(
        responses.POST,
        "https://host_name.com/complianceDocTemplates/",
        body="",
        status=201,
        adding_headers={
            "Location": "https://host_name.com/complianceDocTemplates/{}/".format(data["id"])
        },
    )
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/{}/".format(data["id"]),
        json=data,
    )
    template = ComplianceDocTemplate.create(name=data["name"], sections=data["sections"])
    assert template.id == data["id"]
    assert template.name == data["name"]
    assert template.creator_id == data["creatorId"]
    assert template.creator_username == data["creatorUsername"]
    assert template.org_id == data["orgId"]
    assert template.sections is not None


@responses.activate
def test_get_default(templates_list_response):
    server_data = templates_list_response[0]
    responses.add(
        responses.GET, "https://host_name.com/complianceDocTemplates/default/", json=server_data
    )
    template = ComplianceDocTemplate.get_default()
    assert template.id is None
    assert template.creator_id is None
    assert template.creator_username is None
    assert template.org_id is None
    assert template.sections is not None
    assert template.name == "default"


@responses.activate
def test_sections_to_json_file(templates_list_response, tmpdir):
    server_data = templates_list_response[0]
    responses.add(
        responses.GET, "https://host_name.com/complianceDocTemplates/default/", json=server_data
    )
    responses.add(
        responses.POST,
        "https://host_name.com/complianceDocTemplates/",
        body="",
        status=201,
        headers={
            "Location": "https://host_name.com/complianceDocTemplates/{}/".format("new-template")
        },
    )
    responses.add(
        responses.GET,
        "https://host_name.com/complianceDocTemplates/new-template/",
        json=dict(server_data, name="new template"),
    )
    template = ComplianceDocTemplate.get_default()
    tmpfile = tmpdir.mkdir("sections").join("sections.json")
    template.sections_to_json_file(path=tmpfile.strpath)
    assert tmpfile.exists()

    new_template = ComplianceDocTemplate.create_from_json_file(
        name="new template", path=tmpfile.strpath
    )
    assert new_template.name == "new template"
    assert new_template.creator_id == server_data["creatorId"]
    assert new_template.creator_username == server_data["creatorUsername"]
    assert new_template.org_id == server_data["orgId"]
    assert new_template.sections is not None
