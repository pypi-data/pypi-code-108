import inspect
import os
from sys import path
from typing import Any, Dict, List

from anyscale import version


anyscale_dir = os.path.dirname(os.path.abspath(__file__))
path.append(os.path.join(anyscale_dir, "client"))
path.append(os.path.join(anyscale_dir, "sdk"))
ANYSCALE_RAY_DIR = os.path.join(anyscale_dir, "anyscale_ray")

from anyscale.cluster import get_job_submission_client_cluster_info  # noqa: E402
from anyscale.connect import ClientBuilder  # noqa: E402
from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK  # noqa: E402


# Note: indentation here matches that of connect.py::ClientBuilder.
BUILDER_HELP_FOOTER = """
        See ``anyscale.ClientBuilder`` for full documentation of
        this experimental feature."""

# Auto-add all Anyscale connect builder functions to the top-level.
for attr, _ in inspect.getmembers(ClientBuilder, inspect.isfunction):
    if attr.startswith("_"):
        continue

    def _new_builder(attr: str) -> Any:
        target = getattr(ClientBuilder, attr)

        def new_session_builder(*a: List[Any], **kw: Dict[str, Any]) -> Any:
            builder = ClientBuilder()
            return target(builder, *a, **kw)

        new_session_builder.__name__ = attr
        new_session_builder.__doc__ = target.__doc__ + BUILDER_HELP_FOOTER
        setattr(new_session_builder, "__signature__", inspect.signature(target))

        return new_session_builder

    globals()[attr] = _new_builder(attr)

__version__ = version.__version__

ANYSCALE_ENV = os.environ.copy()
ANYSCALE_ENV["PYTHONPATH"] = ANYSCALE_RAY_DIR + ":" + ANYSCALE_ENV.get("PYTHONPATH", "")
