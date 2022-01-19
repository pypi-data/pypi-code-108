"""Test integrity of workflows."""
from dkist_processing_core.build_utils import validate_workflows

from dkist_processing_visp import workflows


def test_workflow_integrity():
    """Validate workflow to ensure acyclic-ness and export compilation"""
    validate_workflows(workflows)
