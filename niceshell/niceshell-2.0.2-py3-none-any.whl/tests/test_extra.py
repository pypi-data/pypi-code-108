#!/usr/bin/python3
import sys

import pytest

sys.path.extend([f"{sys.path[0]}/..", f"{sys.path[0]}/../.."])
from niceshell import extra


class TestExtra:
    def test_has_root_privileges(self):
        assert type(extra.has_root_privileges()) == bool

    def test_list_dirs(self):
        list_dirs = extra.list_dirs

        # Errors
        # path must be str.
        with pytest.raises(TypeError):
            list_dirs(1)
        with pytest.raises(TypeError):
            list_dirs(["path1", "path2"])

        # Invalid path.
        with pytest.raises(ValueError):
            list_dirs(R"\/")

        # Asserts
        dirs = list_dirs('/')
        assert type(dirs) == list
        assert len(dirs) != 0

    def test_list_files(self):
        list_files = extra.list_files

        # Errors
        # path must be str.
        with pytest.raises(TypeError):
            list_files(1)
        with pytest.raises(TypeError):
            list_files(["path1", "path2"])

        # Invalid path.
        with pytest.raises(ValueError):
            list_files(R"\/")

        # Asserts
        files = list_files("/bin/")
        assert type(files) == list
        assert len(files) != 0


if __name__ == "__main__":
    pytest.main()
