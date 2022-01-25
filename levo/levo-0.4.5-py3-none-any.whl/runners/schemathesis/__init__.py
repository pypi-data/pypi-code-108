from typing import Any, Callable, Dict, List

import click
import schemathesis.checks
from schemathesis import runner
from schemathesis.cli import get_exit_code
from schemathesis.constants import DataGenerationMethod
from schemathesis.schemas import BaseSchema
from schemathesis.specs.openapi import loaders as oas_loaders
from schemathesis.utils import get_requests_auth

from ... import events
from ...config import TestConformanceCommandConfig
from ...handlers import EventHandler
from ...logger import get_logger
from ...login import get_config_or_exit
from ...utils import file_exists
from .adapter import convert_event
from .config import Config
from .context import ExecutionContext
from .reporters import SchemathesisConsoleOutputHandler, SchemathesisReportPortalHandler

Loader = Callable[..., BaseSchema]

log = get_logger(__name__)


def load_schema(config: Config) -> BaseSchema:
    """Load API schema from config."""
    loader = detect_loader(config.spec_path)
    kwargs = get_loader_kwargs(loader, config)
    return loader(config.spec_path, **kwargs)


def detect_loader(schema_location: str) -> Loader:
    """Detect the appropriate loader based on the schema location."""
    if file_exists(schema_location):
        # If there is an existing file with the given name,
        # then it is likely that the user wants to load API schema from there
        return oas_loaders.from_path
    # Default behavior
    return oas_loaders.from_uri


def get_loader_kwargs(loader: Loader, config: Config) -> Dict[str, Any]:
    """Build kwargs, depending on `config`."""
    kwargs = {"base_url": config.target_url, "validate_schema": config.validate_schema}
    if config.auth is not None:
        kwargs["auth"] = get_requests_auth(config.auth, config.auth_type)

    # Enable both positive and negative testing by default.
    kwargs["data_generation_methods"] = (
        DataGenerationMethod.positive,
        DataGenerationMethod.negative,
    )
    return kwargs


def get_from_schema_kwargs(config: Config) -> Dict[str, Any]:
    """Extract kwargs for the `from_schema` call."""
    return {}


class SchemathesisEventStream(events.EventStream):
    def stop(self) -> None:
        self.inner.stop()


def into_event_stream(config: Config) -> events.EventStream:
    """Schemathesis event stream.

    Could be used as a building block for different commands.
    """
    loaded_schema = load_schema(config)
    from_schema_kwargs = get_from_schema_kwargs(config)

    # Add User-Agent header to requests
    headers = config.headers if config.headers is not None else {}
    headers["User-Agent"] = "levocli"

    inner = runner.from_schema(
        loaded_schema,
        store_interactions=True,
        checks=schemathesis.checks.ALL_CHECKS,
        headers=headers,
        **from_schema_kwargs,
    ).execute()
    return SchemathesisEventStream(inner, convert_event)


def cli_entrypoint(input_config: TestConformanceCommandConfig):
    """CLI entrypoint for Schemathesis.

    Responsibilities:
      - Validate input config
      - Optionally update the config from the SaaS side
      - Construct a list of handlers, depending on the resulting config
      - Create a stream of Schemathesis events
      - Run handlers against the stream & exit
    """
    # NOTE. Config can be extended here - e.g. from SaaS
    handlers: List[EventHandler] = [SchemathesisConsoleOutputHandler()]
    # Report the test results to ReportPortal, if enabled.
    if input_config.report_to_saas:
        levo_config = get_config_or_exit()
        handlers.append(
            SchemathesisReportPortalHandler(
                levo_config.workspace_id,
                levo_config.auth.access_token,
                input_config.schema,
            )
        )
    handler_names = [h.get_name() for h in handlers]
    log.debug(f"Initialized the handlers: {handler_names}")

    final_config = Config.from_input_config(input_config)
    event_stream = into_event_stream(final_config)
    execution_context = ExecutionContext(
        show_errors_tracebacks=input_config.show_errors_tracebacks,
        validate_schema=False,
    )
    event = events.handle(handlers, event_stream, execution_context)
    exit_code = get_exit_code(event)
    raise click.exceptions.Exit(exit_code)
