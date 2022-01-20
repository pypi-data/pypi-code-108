"""
Tests for the build utils
"""
from pathlib import Path

import pytest
from airflow.exceptions import AirflowException

from dkist_processing_core.build_utils import export
from dkist_processing_core.build_utils import validate_workflows
from dkist_processing_core.tests import invalid_workflow_package
from dkist_processing_core.tests import valid_workflow_package
from dkist_processing_core.tests import zero_node_workflow_package


def test_validate_workflow_valid():
    """
    Given: A workflow package with a valid workflow
    When: validating the workflow
    Then: No errors raised
    """
    validate_workflows(valid_workflow_package)


def test_validate_workflow_invalid():
    """
    Given: A workflow package with an invalid workflow
    When: validating the workflow
    Then: Errors raised
    """
    exceptions = (SyntaxError, AirflowException)
    with pytest.raises(exceptions):
        validate_workflows(invalid_workflow_package)


def test_validate_workflow_zero_nodes():
    """
    Given: A workflow package with an invalid workflow of zero nodes
    When: validating the workflow
    Then: Errors raised
    """
    exceptions = (ValueError, AirflowException)
    with pytest.raises(exceptions):
        validate_workflows(zero_node_workflow_package)


def test_export(export_path):
    """
    Given: A path to export to and a package containing a valid workflow
    When: Workflows in the package are exported
    Then: Expected export file exists
    """
    export(valid_workflow_package, export_path)
    path = export_path / Path("valid_workflow_dev.py")
    assert path.exists()
