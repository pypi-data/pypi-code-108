from typing import Sequence, Any

import pytest

from ibm_watson_studio_pipelines import CpdPath
from ibm_watson_studio_pipelines.cpd_paths import CpdResource, CpdScope, \
    CpdScopeFile, CpdConnectionFile


def test_00_simple_paths_parse_well():
    paths = [
        "cpd://dev-dallas/projects/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "cpd:///projects/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "/projects/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "d12adac-c073-4038-ba19-9c57017a5b57",
    ]
    for path in paths:
        CpdPath.from_string(path)

def test_01_non_string_do_not_parse():
    non_paths: Sequence[Any] = [
        None,
        4038,
        12.073,
        [
            "projects",
            "6e351231-e734-4437-83e5-257fcfbb0a0a",
            "assets",
            "0d12adac-c073-4038-ba19-9c57017a5b57",
        ],
        {
            "scope_type": "project",
            "scope_id": "6e351231-e734-4437-83e5-257fcfbb0a0a",
            "resource_type": "asset",
            "resource_id": "0d12adac-c073-4038-ba19-9c57017a5b57",
        },
    ]
    for non_path in non_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(non_path)

def test_02a_wrong_scope():
    wrong_paths = [
        "cpd://dev/stockpiles/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "cpd:///stockpiles/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "/stockpiles/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
    ]
    for non_path in wrong_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(non_path)

def test_02b_wrong_format():
    wrong_paths = [
        "{'type': 'space'}",
        "[1, 2 ,3]",
    ]
    for non_path in wrong_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(non_path)

def test_02c_wrong_chars():
    wrong_paths = [
        "abc!def",
        "abc(def)",
    ]
    for non_path in wrong_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(non_path)

def test_03a_leading_slash_in_relative_path():
    wrong_paths = [
        "/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "/0d12adac-c073-4038-ba19-9c57017a5b57",
    ]
    for non_path in wrong_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(non_path)

def test_03b_no_leading_slash_in_absolute_path():
    wrong_paths = [
        "projects/6e351231-e734-4437-83e5-257fcfbb0a0a/assets/0d12adac-c073-4038-ba19-9c57017a5b57",
    ]
    for non_path in wrong_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(non_path)

def test_04a_scope_parses_fine():
    paths = [
        "cpd:///spaces/4b4946f4-242e-4ed0-9c80-24ae9b48db19",
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19",
    ]
    for path in paths:
        cpd_path = CpdPath.from_string(path)
        cpd_scope = CpdScope.from_string(path)
        assert cpd_path == cpd_scope

def test_04b_resource_parses_fine():
    paths = [
        "assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "d12adac-c073-4038-ba19-9c57017a5b57",
    ]
    for path in paths:
        cpd_path = CpdPath.from_string(path)
        cpd_resource = CpdResource.from_string(path)
        assert cpd_path == cpd_resource

def test_04c_scope_is_not_resource():
    wrong_paths = [
        "cpd:///spaces/4b4946f4-242e-4ed0-9c80-24ae9b48db19",
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19",
    ]
    for path in wrong_paths:
        cpd_path = CpdPath.from_string(path)
        assert not isinstance(cpd_path, CpdResource)
        with pytest.raises(TypeError):
            CpdResource.from_string(path)

def test_04d_resource_is_not_scope():
    wrong_paths = [
        "assets/0d12adac-c073-4038-ba19-9c57017a5b57",
        "d12adac-c073-4038-ba19-9c57017a5b57",
    ]
    for path in wrong_paths:
        cpd_path = CpdPath.from_string(path)
        assert not isinstance(cpd_path, CpdScope)
        with pytest.raises(TypeError):
            CpdScope.from_string(path)

def test_05a_scope_file_parses_fine():
    paths = [
        "cpd:///projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/files/abc/def",
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/files/abc/def",
    ]
    for path in paths:
        cpd_path = CpdPath.from_string(path)
        cpd_scope_file = CpdScopeFile.from_string(path)
        assert cpd_path == cpd_scope_file

def test_05b_connection_file_parses_fine():
    paths = [
        "cpd:///projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/connections/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/connections/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
    ]
    for path in paths:
        cpd_path = CpdPath.from_string(path)
        cpd_scope_file = CpdConnectionFile.from_string(path)
        assert cpd_path == cpd_scope_file

def test_05c_non_connection_file_not_parsing():
    wrong_paths = [
        "cpd:///projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/deployments/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/deployments/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
        "cpd:///projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/notebooks/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/notebooks/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
    ]
    for path in wrong_paths:
        with pytest.raises(TypeError):
            CpdPath.from_string(path)

def test_05d_scope_file_is_not_connection_file():
    wrong_paths = [
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/files/abc/def",
    ]
    for path in wrong_paths:
        cpd_path = CpdPath.from_string(path)
        assert not isinstance(cpd_path, CpdConnectionFile)
        with pytest.raises(TypeError):
            CpdConnectionFile.from_string(path)

def test_05e_connection_file_is_not_scope_file():
    wrong_paths = [
        "/projects/4b4946f4-242e-4ed0-9c80-24ae9b48db19/connections/90985f12-2ae6-49bc-9872-4b94e1b47ef5/files/~/abc/def",
    ]
    for path in wrong_paths:
        cpd_path = CpdPath.from_string(path)
        assert not isinstance(cpd_path, CpdScopeFile)
        with pytest.raises(TypeError):
            CpdScopeFile.from_string(path)
