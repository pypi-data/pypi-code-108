#!/usr/bin/python3
import sys

import pytest

sys.path.extend([f"{sys.path[0]}/..", f"{sys.path[0]}/../.."])
from niceshell import extra


class TestExtra:
    def test_force_sudo_password_promt(self):
        assert extra.force_sudo_password_promt() == None

    def test_has_root_privileges(self):
        assert type(extra.has_root_privileges()) == bool


if __name__ == "__main__":
    pytest.main()
