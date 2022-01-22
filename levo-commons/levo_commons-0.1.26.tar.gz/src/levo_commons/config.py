from logging import Handler
from typing import Dict, Optional, Tuple

import attr

from .models import Module
from .providers import Provider

CONFIG_VERSION = (1, 0)


@attr.s(slots=True)
class AuthConfig:
    auth_type: str = attr.ib(kw_only=True, default="None")
    username: Optional[str] = attr.ib(kw_only=True, default=None)
    password: Optional[str] = attr.ib(kw_only=True, default=None)
    api_key: Optional[str] = attr.ib(kw_only=True, default=None)
    token: Optional[str] = attr.ib(kw_only=True, default=None)


@attr.s(slots=True, kw_only=True)
class PlanConfig:
    """Test plan configuration."""

    target_url: str = attr.ib(kw_only=True)
    spec_path: Optional[str] = attr.ib(kw_only=True, default=None)
    test_plan_path: Optional[str] = attr.ib(kw_only=True, default=None)
    # This is deprecated and should be removed in next version.
    auth: Optional[Tuple[str, str]] = attr.ib(kw_only=True, default=None)
    auth_type: Optional[str] = attr.ib(kw_only=True, default=None)
    report_to_saas: bool = attr.ib(kw_only=True, default=True)
    auth_config: AuthConfig = attr.ib(kw_only=True)
    headers: Dict[str, str] = attr.ib(kw_only=True, factory=dict)
    env_file_path: Optional[str] = attr.ib(kw_only=True, default=None)
    module_providers: Dict[Module, Provider] = attr.ib(kw_only=True, factory=dict)
    # Current config version
    version = CONFIG_VERSION

    test_case_log_handler: Optional[Handler] = attr.ib(kw_only=True, default=None)
    runner_log_handler: Optional[Handler] = attr.ib(kw_only=True, default=None)

    # Shortcut to convert PlanConfig to dictionary
    asdict = attr.asdict
