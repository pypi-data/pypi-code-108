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
import warnings

import mock
import pytest
import responses

from datarobot import Project
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.utils import to_api
from tests.utils import request_body_to_json


class SpecialProject(Project):
    """
    Class used by TestProjectExtensibility.

    Note that this is very similar to AdminProject for MBTests.
    """

    _fields = Project._fields

    @classmethod
    def create(cls, sourcedata, project_name="New Project", max_wait=DEFAULT_MAX_WAIT, **kwargs):
        form_data = cls._construct_create_form_data(project_name=project_name)

        if kwargs:
            form_data.update(kwargs)
        return cls._create_project_with_form_data(sourcedata, form_data, max_wait=max_wait)

    def _construct_aim_payload(self, *args, **kwargs):
        """
        Constructs the AIM payload that is POSTed to the server to set the target.
        Adds extras to the AIM request for special things.

        Returns
        -------
        dict
        """
        payload = super(SpecialProject, self)._construct_aim_payload(*args, **kwargs)
        payload.update(self._aim_extras)
        return payload

    def set_target(self, *args, **kwargs):
        """
        Sets the target.
        Adds extras to the AIM request.
        See Project.set_target for parameters and return value.
        """
        # gets the method arguments, excluding self (1st arg)
        import inspect

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            args_list = inspect.getargspec(Project.set_target).args[1:]
        # subset the dict on only the keys that the method accepts
        set_target_args = {k: v for k, v in kwargs.items() if k in args_list}
        # extract the extra kwargs to inject into the AIM payload
        self._aim_extras = {k: v for k, v in kwargs.items() if k not in args_list}
        return super(SpecialProject, self).set_target(*args, **set_target_args)


@pytest.fixture
def extras():
    return {"special": 100, "experimental_magic": True}


@responses.activate
@pytest.mark.usefixtures("project_creation_responses")
def test_create_with_extras(extras, async_url):
    """
    Creating a SpecialProject with extra kwargs should be appended to the POSTed create payload.
    """
    max_wait = 600

    with mock.patch.object(
        SpecialProject, "from_async", wraps=SpecialProject.from_async
    ) as mock_from_async:
        special_project = SpecialProject.create(
            "https://example.com/data.csv", "A Project Name", max_wait, **extras
        )

    mock_from_async.assert_called_once_with(async_url, max_wait)
    assert special_project.project_name == "A Project Name"
    assert isinstance(special_project, SpecialProject)

    posted_data = request_body_to_json(responses.calls[0].request)
    for extra in to_api(extras).items():
        # note that to_api will convert snake_case to CamelCase on dict keys
        assert extra in posted_data.items()


@responses.activate
def test_create_with_extras_should_fail_on_normal_project(extras):
    """
    By default, a normal Project should prevent any extra kwargs to create method.
    """
    with pytest.raises(TypeError):
        Project.create("https://example.com/data.csv", "Project Name", 600, **extras)


@responses.activate
def test_set_target_with_extras_should_fail_on_normal_project(project_without_target):
    """
    By default, a normal Project should prevent any extra kwargs to set_target.
    """
    extras = {"special": 100, "experimental_magic": True}

    with pytest.raises(TypeError):
        project_without_target.set_target("Bullseye", **extras)


@responses.activate
@pytest.mark.usefixtures("project_aim_responses")
def test_set_target_with_extras(extras, project_without_target_data):
    """
    With a SpecialProject that subclasses Project, it should be possible to pass additional
    kwargs to set_target as part of the POSTed payload to the server.
    """
    special_project = SpecialProject.from_data(project_without_target_data)
    special_project.set_target("Bullseye", **extras)
    posted_data = request_body_to_json(responses.calls[0].request)
    for extra in to_api(extras).items():
        # note that to_api will convert snake_case to CamelCase on dict keys
        assert extra in posted_data.items()
