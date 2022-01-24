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
from trafaret import DataError

from datarobot.models.custom_task_version_dependency_build import CustomTaskVersionDependencyBuild
from tests.model.utils import assert_custom_task_version_dependency_build


@pytest.mark.parametrize(
    "missing_field", ["customTaskId", "customTaskVersionId", "buildStart", "buildStatus"],
)
def test_from_server_data__fail_with_missing_field(
    missing_field, custom_task_version_dependency_build_server_data
):
    custom_task_version_dependency_build_server_data.pop(missing_field)
    with pytest.raises(DataError):
        CustomTaskVersionDependencyBuild.from_server_data(
            custom_task_version_dependency_build_server_data
        )


@pytest.mark.parametrize(
    "field_null_not_allowed", ["customTaskId", "customTaskVersionId", "buildStart", "buildStatus"],
)
def test_from_server_data__fail__field_with_blank_values(
    field_null_not_allowed, custom_task_version_dependency_build_server_data,
):
    custom_task_version_dependency_build_server_data.update({field_null_not_allowed: None})
    with pytest.raises(DataError):
        CustomTaskVersionDependencyBuild.from_server_data(
            custom_task_version_dependency_build_server_data
        )


@pytest.mark.parametrize(
    "field_null_allowed", ["buildEnd", "buildLogLocation"],
)
def test_from_server_data__succeed__field_with_blank_values(
    field_null_allowed, custom_task_version_dependency_build_server_data,
):
    custom_task_version_dependency_build_server_data.update({field_null_allowed: None})
    dependency_build = CustomTaskVersionDependencyBuild.from_server_data(
        custom_task_version_dependency_build_server_data
    )
    assert_custom_task_version_dependency_build(
        dependency_build, custom_task_version_dependency_build_server_data
    )


def test_from_server_data__succeed_with_field_naming_conversion(
    custom_task_version_dependency_build_server_data,
):
    dependency_build = CustomTaskVersionDependencyBuild.from_server_data(
        custom_task_version_dependency_build_server_data
    )
    assert_custom_task_version_dependency_build(
        dependency_build, custom_task_version_dependency_build_server_data
    )


def test_from_server_data__succeed_ignoring_extra_fields(
    custom_task_version_dependency_build_server_data,
):
    custom_task_version_dependency_build_server_data["extra_fields"] = "aaa"
    dependency_build = CustomTaskVersionDependencyBuild.from_server_data(
        custom_task_version_dependency_build_server_data
    )
    assert_custom_task_version_dependency_build(
        dependency_build, custom_task_version_dependency_build_server_data
    )
