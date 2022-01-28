from typing import Any, Dict, List, Optional, Tuple

import attr
import click

CONFIG_VERSION = (1, 0)

PASSTHRU_ARGUMENT_PREFIX = "--passthru-"


def parse_passthru_arguments(args: List[str]) -> Dict[str, Any]:
    """Convert raw command line inputs into a dictionary."""
    output = {}
    for arg in args:
        if arg.startswith(PASSTHRU_ARGUMENT_PREFIX):
            key, value = (arg[len(PASSTHRU_ARGUMENT_PREFIX) :].split("=", 1) + [""])[:2]
            output[key] = value
        else:
            raise click.NoSuchOption(arg)
    return output


@attr.s(slots=True)
class TestConformanceCommandConfig:
    """Conformance test configuration."""

    __test__ = False  # to avoid pytest warning

    site_name: str = attr.ib(kw_only=True, default="default_site")
    service_name: str = attr.ib(kw_only=True, default="default_service")
    target_url: str = attr.ib(kw_only=True)
    schema: str = attr.ib(kw_only=True, default=None)
    auth: Optional[Tuple[str, str]] = attr.ib(kw_only=True)
    auth_type: str = attr.ib(kw_only=True, default="basic")
    report_to_saas: bool = attr.ib(kw_only=True, default=False)
    headers: Dict[str, str] = attr.ib(factory=dict)
    passthru: Dict[str, Any] = attr.ib(
        kw_only=True, factory=dict, converter=parse_passthru_arguments
    )
    show_errors_tracebacks: bool = attr.ib(kw_only=True, default=False)

    # Config version
    version = CONFIG_VERSION


@attr.s(slots=True)
class TestPlanCommandConfig:
    """Test Command configuration available in the current CLI version."""

    __test__ = False  # to avoid pytest warning

    testplan_ref: str = attr.ib(kw_only=True)  # a file path or LRN
    site_name: str = attr.ib(kw_only=True, default="default_site")
    service_name: str = attr.ib(kw_only=True, default="default_service")
    target_url: str = attr.ib(kw_only=True)
    auth: Optional[Tuple[str, str]] = attr.ib(kw_only=True)
    auth_type: str = attr.ib(kw_only=True, default="basic")
    report_to_saas: bool = attr.ib(kw_only=True, default=False)
    headers: Dict[str, str] = attr.ib(factory=dict)
    passthru: Dict[str, Any] = attr.ib(
        kw_only=True, factory=dict, converter=parse_passthru_arguments
    )
    env_file_path: Optional[str] = attr.ib(kw_only=True, default=None)
    show_errors_tracebacks: bool = attr.ib(kw_only=True, default=False)
    # Config version
    version = CONFIG_VERSION
