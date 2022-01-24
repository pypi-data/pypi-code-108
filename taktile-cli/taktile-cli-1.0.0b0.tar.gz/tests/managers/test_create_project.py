import os
import shutil

import pytest

from tktl.commands.init import init_project
from tktl.commands.validate import validate_project_config
from tktl.core.managers.constants import TEMPLATE_PROJECT_DIRS, TEMPLATE_PROJECT_FILES
from tktl.core.managers.project import ProjectManager
from tktl.core.t import TemplateT


def test_create_in_existing_directory(monkeypatch, tmpdir):
    monkeypatch.setattr("builtins.input", lambda: "Y")
    ProjectManager.init_project(
        tmpdir.dirpath(), "test_project_dir", TemplateT.REPAYMENT
    )
    for d in TEMPLATE_PROJECT_DIRS:
        assert os.path.isdir(os.path.join(tmpdir.dirpath(), "test_project_dir", d))
    for file in TEMPLATE_PROJECT_FILES[TemplateT.REPAYMENT]:
        assert os.path.exists(os.path.join(tmpdir.dirpath(), "test_project_dir", file))
    assert os.path.exists(
        os.path.join(tmpdir.dirpath(), "test_project_dir", "tktl.yaml")
    )


def test_create_project():
    ProjectManager.init_project(None, "sample_project", TemplateT.REPAYMENT)
    for file in TEMPLATE_PROJECT_FILES[TemplateT.REPAYMENT]:
        assert os.path.exists(os.path.join("sample_project", file))
    assert os.path.exists(os.path.join("sample_project", "tktl.yaml"))

    for d in TEMPLATE_PROJECT_DIRS:
        assert os.path.isdir(os.path.join("sample_project", d))
    shutil.rmtree("sample_project")


def test_safe_init(monkeypatch, caplog):
    monkeypatch.setattr("builtins.input", lambda: "n")

    with pytest.raises(SystemExit):
        ProjectManager.safe_init(None, "sample_project", TemplateT.REPAYMENT)
        assert "Path specified already exists" in caplog.text


def test_overwrite(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda: "Y")
    ProjectManager.init_project(None, "sample_project", TemplateT.REPAYMENT)
    init_project(None, "sample_project", TemplateT.REPAYMENT)
    out, err = capsys.readouterr()
    assert "Project scaffolding created successfully" in out
    shutil.rmtree("sample_project")


def test_validate(capsys):
    ProjectManager.init_project(None, "sample_project", TemplateT.REPAYMENT)
    validate_project_config("sample_project")
    out, err = capsys.readouterr()
    assert "Project scaffolding is valid!\n" in out
    shutil.rmtree("sample_project")

    ProjectManager.init_project(None, "sample_project", TemplateT.REPAYMENT)
    shutil.rmtree("sample_project/src")
    validate_project_config("sample_project")
    out, err = capsys.readouterr()
    assert err is not None
    assert "Project scaffolding is invalid: Missing Files or Directory ❌\n" in out
    assert "Missing directories in repository: src" in err
    shutil.rmtree("sample_project")

    ProjectManager.init_project(None, "sample_project", TemplateT.REPAYMENT)
    with open("sample_project/tktl.yaml", "w") as inf:
        inf.write(
            """
default_branch_name: master
service:
  replicas: 3
  compute_type: CPUqqqqqqqq
  endpoint_type: RESTuuuuuu
"""
        )
    validate_project_config("sample_project")
    out, err = capsys.readouterr()
    assert "Project scaffolding is invalid: Invalid Config File ❌\n" in out
    shutil.rmtree("sample_project")
