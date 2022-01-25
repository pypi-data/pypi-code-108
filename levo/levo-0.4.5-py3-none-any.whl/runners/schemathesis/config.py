from typing import Any, Dict, Optional, Tuple

import attr
import click

from ...config import TestConformanceCommandConfig


@attr.s(slots=True)
class Config:
    """Schemathesis config."""

    spec_path: str = attr.ib()
    target_url: str = attr.ib()
    auth: Optional[Tuple[str, str]] = attr.ib()
    auth_type: Optional[str] = attr.ib()
    validate_schema: bool = attr.ib(default=False)
    headers: Dict[str, str] = attr.ib(factory=dict)

    @classmethod
    def from_input_config(cls, input_config: TestConformanceCommandConfig) -> "Config":
        """Create a new Schemathesis config from prepared CLI input.

        Passthru options are processed here.
        """
        kwargs: Dict[str, Any] = {
            "target_url": input_config.target_url,
            "spec_path": input_config.schema,
            "auth": input_config.auth,
            "auth_type": input_config.auth_type,
            "headers": input_config.headers,
        }
        for option, value in input_config.passthru.items():
            if option in CONFIG_FIELDS:
                if option in kwargs:
                    raise click.UsageError(
                        f"Passthru option name clashes with the regular one: {option}"
                    )
                kwargs[option] = cast_value(option, value)
            else:
                raise click.UsageError(f"Invalid Schemathesis option: {option}")
        return cls(**kwargs)


def cast_value(option: str, value: str) -> Any:
    """Convert a raw string argument value to its defined type."""
    type_ = CONFIG_FIELDS[option].type
    if type_ is bool:
        lower_value = value.lower()
        if lower_value in ["true", "1", "t", "y", "yes"]:
            return True
        if lower_value in ["false", "0", "f", "n", "no"]:
            return False
        raise click.UsageError(f"Invalid value for boolean type: {value}")
    return value


CONFIG_FIELDS = attr.fields_dict(Config)
