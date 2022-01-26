import os

import pytest

from tktl.login import login, logout


@pytest.fixture
def user_key():
    return os.environ["TEST_USER"], os.environ["TEST_USER_API_KEY"]


@pytest.fixture
def test_user_deployed_repos():
    return (
        ("tktl-admin/other-project", "testbranch", "repayment"),
        ("tktl-admin/other-project", "master", "repayment"),
        ("tktl-admin/sample-project", "master", "repayment"),
        ("tktl-admin/integ-testing", "master", "repayment"),
        ("tktl-admin/grpc-test", "main", "repayment"),
    )


@pytest.fixture(scope="function")
def logged_in_context():
    yield login(os.environ["TEST_USER_API_KEY"])
    logout()


@pytest.fixture()
def sample_deployed_url():
    return "tktl-adm-grpc-test-main-1a485d0d54.stg-saas.taktile.com"
