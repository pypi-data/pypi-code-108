"""Utilities for the build pipeline"""
import importlib
from pathlib import Path
from shutil import rmtree
from types import ModuleType
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from airflow.models import DAG

from dkist_processing_core import Workflow


__all__ = ["validate_workflows", "export"]


def validate_workflows(workflow_package: ModuleType, export_path: Optional[Path] = None) -> None:
    """
    Validates that workflow engine (airflow) objects are acyclic and that
    exported workflows compile.
    """
    # configure export path.  Clean up after if export path not provided
    rm_export_path_after_test = not bool(export_path)
    if export_path is None:
        export_path = Path("export/")
    workflows = _extract_workflows_from_package(workflow_package)
    try:
        _validate_workflows(workflows, export_path)
    finally:
        if rm_export_path_after_test:
            rmtree(export_path)
    dags = [w.load() for w in workflows]
    _validate_dags(dags)


def export(workflow_package: ModuleType, export_path: Optional[Union[str, Path]] = None) -> None:
    """
    Export workflows for deployment
    """
    [w.export(export_path) for w in _extract_workflows_from_package(workflow_package)]


def _extract_workflows_from_package(workflow_package: ModuleType) -> List[Workflow]:
    return _extract_objects_from_package_by_type(workflow_package, Workflow)


def _extract_objects_from_package_by_type(package: ModuleType, object_type: type) -> List[Any]:
    modules = _parse_unprotected_modules_names_from_package(package)
    objects = []
    for module in modules:
        imported_module = importlib.import_module(f".{module}", package.__name__)
        objects += [var for var in vars(imported_module).values() if isinstance(var, object_type)]
    return objects


def _parse_unprotected_modules_names_from_package(package: ModuleType) -> List[str]:
    package_path = Path(package.__path__[0])
    return [m.stem for m in package_path.glob("[!_]*.py")]


def _validate_dags(dags: List[DAG]) -> None:
    """
    Validate dags by ensuring they can be traversed without cycles and are syntactically correct
    """
    for d in dags:
        try:
            d.topological_sort()
        except Exception as e:
            raise SyntaxError(f"DAG {d.dag_id} malformed.  Parsing resulted in error: {e=}") from e


def _validate_workflows(workflows: List[Workflow], export_path: Path) -> None:
    """
    Validate workflows by ensuring their exported version compiles as python and that there
    is at least one node
    """
    for w in workflows:
        try:
            workflow_py = w.export(export_path)
            with workflow_py.open(mode="r") as f:
                compile(f.read(), filename=f"{workflow_py.stem}.pyc", mode="exec")
        except Exception as e:
            raise SyntaxError(
                f"Workflow {w.workflow_name} malformed. "
                f"Parsing exported workflow resulted in error: {e=}"
            ) from e
        if len(w.nodes) == 0:
            raise ValueError(f"Workflow {w.workflow_name} has 0 nodes.")
