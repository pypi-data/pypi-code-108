# -*- coding: utf-8 -*-
from pathlib import Path

import pytest
from gitlab import GitlabCreateError, GitlabError
from requests import ConnectionError

from arkindex_worker.git import GitlabHelper

PROJECT_ID = 21259233
MERGE_REQUEST_ID = 7
SOURCE_BRANCH = "new_branch"
TARGET_BRANCH = "master"
MR_TITLE = "merge request title"
CREATE_MR_RESPONSE_JSON = {
    "id": 107,
    "iid": MERGE_REQUEST_ID,
    "project_id": PROJECT_ID,
    "title": MR_TITLE,
    "target_branch": TARGET_BRANCH,
    "source_branch": SOURCE_BRANCH,
    # several fields omitted
}


@pytest.fixture
def fake_responses(responses):
    responses.add(
        responses.GET,
        "https://gitlab.com/api/v4/projects/balsac_exporter%2Fbalsac-exported-xmls-testing",
        json={
            "id": PROJECT_ID,
            # several fields omitted
        },
    )
    return responses


def test_clone_done(fake_git_helper):
    assert not fake_git_helper.is_clone_finished
    fake_git_helper._clone_done(None, None, None)
    assert fake_git_helper.is_clone_finished


def test_clone(fake_git_helper):
    command = fake_git_helper.run_clone_in_background()
    cmd_str = " ".join(list(map(str, command.cmd)))

    assert "git" in cmd_str
    assert "clone" in cmd_str


def _get_fn_name_from_call(call):
    # call.add(2, 3) => "add"
    return str(call)[len("call.") :].split("(")[0]


def test_save_files(fake_git_helper, mocker):
    mocker.patch("sh.wc", return_value=2)
    fake_git_helper._git = mocker.MagicMock()
    fake_git_helper.is_clone_finished = True
    fake_git_helper.success = True

    fake_git_helper.save_files(Path("/tmp/test_1234/tmp/"))

    expected_calls = ["checkout", "add", "commit", "show", "push"]
    actual_calls = list(map(_get_fn_name_from_call, fake_git_helper._git.mock_calls))

    assert actual_calls == expected_calls
    assert fake_git_helper.gitlab_helper.merge.call_count == 1


def test_save_files__fail_with_failed_clone(fake_git_helper, mocker):
    mocker.patch("sh.wc", return_value=2)
    fake_git_helper._git = mocker.MagicMock()
    fake_git_helper.is_clone_finished = True

    with pytest.raises(Exception) as execinfo:
        fake_git_helper.save_files(Path("/tmp/test_1234/tmp/"))

    assert execinfo.value.args[0] == "Clone was not a success"


def test_merge(mocker):
    api = mocker.MagicMock()
    project = mocker.MagicMock()
    api.projects.get.return_value = project
    merqe_request = mocker.MagicMock()
    project.mergerequests.create.return_value = merqe_request
    mocker.patch("gitlab.Gitlab", return_value=api)

    gitlab_helper = GitlabHelper("project_id", "url", "token", "branch")

    gitlab_helper._wait_for_rebase_to_finish = mocker.MagicMock()
    gitlab_helper._wait_for_rebase_to_finish.return_value = True

    success = gitlab_helper.merge("source", "merge title")

    assert success
    assert project.mergerequests.create.call_count == 1
    assert merqe_request.merge.call_count == 1


def test_merge__rebase_failed(mocker):
    api = mocker.MagicMock()
    project = mocker.MagicMock()
    api.projects.get.return_value = project
    merqe_request = mocker.MagicMock()
    project.mergerequests.create.return_value = merqe_request
    mocker.patch("gitlab.Gitlab", return_value=api)

    gitlab_helper = GitlabHelper("project_id", "url", "token", "branch")

    gitlab_helper._wait_for_rebase_to_finish = mocker.MagicMock()
    gitlab_helper._wait_for_rebase_to_finish.return_value = False

    success = gitlab_helper.merge("source", "merge title")

    assert not success
    assert project.mergerequests.create.call_count == 1
    assert merqe_request.merge.call_count == 0


def test_wait_for_rebase_to_finish(fake_responses, fake_gitlab_helper_factory):
    get_mr_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}?include_rebase_in_progress=True"

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        json={
            "rebase_in_progress": True,
            "merge_error": None,
        },
    )

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        json={
            "rebase_in_progress": True,
            "merge_error": None,
        },
    )

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        json={
            "rebase_in_progress": False,
            "merge_error": None,
        },
    )

    gitlab_helper = fake_gitlab_helper_factory()

    success = gitlab_helper._wait_for_rebase_to_finish(MERGE_REQUEST_ID)

    assert success
    assert len(fake_responses.calls) == 4
    assert gitlab_helper.is_rebase_finished


def test_wait_for_rebase_to_finish__fail_connection_error(
    fake_responses, fake_gitlab_helper_factory
):
    get_mr_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}?include_rebase_in_progress=True"

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        body=ConnectionError(),
    )

    gitlab_helper = fake_gitlab_helper_factory()

    with pytest.raises(ConnectionError):
        gitlab_helper._wait_for_rebase_to_finish(MERGE_REQUEST_ID)

    assert len(fake_responses.calls) == 2
    assert not gitlab_helper.is_rebase_finished


def test_wait_for_rebase_to_finish__fail_server_error(
    fake_responses, fake_gitlab_helper_factory
):
    get_mr_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}?include_rebase_in_progress=True"

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        body="Service Unavailable",
        status=503,
    )

    gitlab_helper = fake_gitlab_helper_factory()

    with pytest.raises(GitlabError):
        gitlab_helper._wait_for_rebase_to_finish(MERGE_REQUEST_ID)

    assert len(fake_responses.calls) == 2
    assert not gitlab_helper.is_rebase_finished


def test_merge_request(fake_responses, fake_gitlab_helper_factory, mocker):
    fake_responses.add(
        fake_responses.POST,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests",
        json=CREATE_MR_RESPONSE_JSON,
    )

    fake_responses.add(
        fake_responses.PUT,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/rebase",
        json={},
    )

    fake_responses.add(
        fake_responses.PUT,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/merge?should_remove_source_branch=True",
        json={
            "iid": MERGE_REQUEST_ID,
            "state": "merged",
            # several fields omitted
        },
    )

    # the fake_responses are defined in the same order as they are expected to be called
    expected_http_methods = [r.method for r in fake_responses.registered()]
    expected_urls = [r.url for r in fake_responses.registered()]

    gitlab_helper = fake_gitlab_helper_factory()
    gitlab_helper._wait_for_rebase_to_finish = mocker.MagicMock()
    gitlab_helper._wait_for_rebase_to_finish.return_value = True

    success = gitlab_helper.merge(SOURCE_BRANCH, MR_TITLE)

    assert success
    assert len(fake_responses.calls) == 4
    assert [c.request.method for c in fake_responses.calls] == expected_http_methods
    assert [c.request.url for c in fake_responses.calls] == expected_urls


def test_merge_request_fail(fake_responses, fake_gitlab_helper_factory, mocker):
    fake_responses.add(
        fake_responses.POST,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests",
        json=CREATE_MR_RESPONSE_JSON,
    )

    fake_responses.add(
        fake_responses.PUT,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/rebase",
        json={},
    )

    fake_responses.add(
        fake_responses.PUT,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/merge?should_remove_source_branch=True",
        json={"error": "Method not allowed"},
        status=405,
    )

    # the fake_responses are defined in the same order as they are expected to be called
    expected_http_methods = [r.method for r in fake_responses.registered()]
    expected_urls = [r.url for r in fake_responses.registered()]

    gitlab_helper = fake_gitlab_helper_factory()
    gitlab_helper._wait_for_rebase_to_finish = mocker.MagicMock()
    gitlab_helper._wait_for_rebase_to_finish.return_value = True

    success = gitlab_helper.merge(SOURCE_BRANCH, MR_TITLE)

    assert not success
    assert len(fake_responses.calls) == 4
    assert [c.request.method for c in fake_responses.calls] == expected_http_methods
    assert [c.request.url for c in fake_responses.calls] == expected_urls


def test_merge_request__success_after_errors(
    fake_responses, fake_gitlab_helper_factory
):
    fake_responses.add(
        fake_responses.POST,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests",
        json=CREATE_MR_RESPONSE_JSON,
    )

    rebase_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/rebase"

    fake_responses.add(
        fake_responses.PUT,
        rebase_url,
        json={"rebase_in_progress": True},
    )

    get_mr_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}?include_rebase_in_progress=True"

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        body="Service Unavailable",
        status=503,
    )

    fake_responses.add(
        fake_responses.PUT,
        rebase_url,
        json={"rebase_in_progress": True},
    )

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        body=ConnectionError(),
    )

    fake_responses.add(
        fake_responses.PUT,
        rebase_url,
        json={"rebase_in_progress": True},
    )

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        json={
            "rebase_in_progress": True,
            "merge_error": None,
        },
    )

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        json={
            "rebase_in_progress": False,
            "merge_error": None,
        },
    )

    fake_responses.add(
        fake_responses.PUT,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/merge?should_remove_source_branch=True",
        json={
            "iid": MERGE_REQUEST_ID,
            "state": "merged",
            # several fields omitted
        },
    )

    # the fake_responses are defined in the same order as they are expected to be called
    expected_http_methods = [r.method for r in fake_responses.registered()]
    expected_urls = [r.url for r in fake_responses.registered()]

    gitlab_helper = fake_gitlab_helper_factory()

    success = gitlab_helper.merge(SOURCE_BRANCH, MR_TITLE)

    assert success
    assert len(fake_responses.calls) == 10
    assert [c.request.method for c in fake_responses.calls] == expected_http_methods
    assert [c.request.url for c in fake_responses.calls] == expected_urls


def test_merge_request__fail_bad_request(fake_responses, fake_gitlab_helper_factory):
    fake_responses.add(
        fake_responses.POST,
        f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests",
        json=CREATE_MR_RESPONSE_JSON,
    )

    rebase_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}/rebase"

    fake_responses.add(
        fake_responses.PUT,
        rebase_url,
        json={"rebase_in_progress": True},
    )

    get_mr_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests/{MERGE_REQUEST_ID}?include_rebase_in_progress=True"

    fake_responses.add(
        fake_responses.GET,
        get_mr_url,
        body="Bad Request",
        status=400,
    )

    # the fake_responses are defined in the same order as they are expected to be called
    expected_http_methods = [r.method for r in fake_responses.registered()]
    expected_urls = [r.url for r in fake_responses.registered()]

    gitlab_helper = fake_gitlab_helper_factory()

    with pytest.raises(GitlabError):
        gitlab_helper.merge(SOURCE_BRANCH, MR_TITLE)

    assert len(fake_responses.calls) == 4
    assert [c.request.method for c in fake_responses.calls] == expected_http_methods
    assert [c.request.url for c in fake_responses.calls] == expected_urls


def test_create_merge_request__no_retry_5xx_error(
    fake_responses, fake_gitlab_helper_factory
):
    request_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests"

    fake_responses.add(
        fake_responses.POST,
        request_url,
        body="Service Unavailable",
        status=503,
    )

    # the fake_responses are defined in the same order as they are expected to be called
    expected_http_methods = [r.method for r in fake_responses.registered()]
    expected_urls = [r.url for r in fake_responses.registered()]

    gitlab_helper = fake_gitlab_helper_factory()

    with pytest.raises(GitlabCreateError):
        gitlab_helper.project.mergerequests.create(
            {
                "source_branch": "branch",
                "target_branch": gitlab_helper.branch,
                "title": "MR title",
            }
        )

    assert len(fake_responses.calls) == 2
    assert [c.request.method for c in fake_responses.calls] == expected_http_methods
    assert [c.request.url for c in fake_responses.calls] == expected_urls


def test_create_merge_request__retry_5xx_error(
    fake_responses, fake_gitlab_helper_factory
):
    request_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/merge_requests"

    fake_responses.add(
        fake_responses.POST,
        request_url,
        body="Service Unavailable",
        status=503,
    )

    fake_responses.add(
        fake_responses.POST,
        request_url,
        body="Service Unavailable",
        status=503,
    )

    fake_responses.add(
        fake_responses.POST,
        request_url,
        json=CREATE_MR_RESPONSE_JSON,
    )

    # the fake_responses are defined in the same order as they are expected to be called
    expected_http_methods = [r.method for r in fake_responses.registered()]
    expected_urls = [r.url for r in fake_responses.registered()]

    gitlab_helper = fake_gitlab_helper_factory()

    gitlab_helper.project.mergerequests.create(
        {
            "source_branch": "branch",
            "target_branch": gitlab_helper.branch,
            "title": "MR title",
        },
        retry_transient_errors=True,
    )

    assert len(fake_responses.calls) == 4
    assert [c.request.method for c in fake_responses.calls] == expected_http_methods
    assert [c.request.url for c in fake_responses.calls] == expected_urls
