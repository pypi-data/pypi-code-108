from typing import Any, Dict, Optional

import attr

from .params import ParamType


@attr.s(slots=True, repr=False)
class Evidence:
    """Evidence of an assertion failure."""

    # Short description of what happened
    title: str = attr.ib()
    param_type: ParamType = attr.ib()
    param_path: str = attr.ib()
    # A longer description of what happened
    message: Optional[str] = attr.ib(factory=str)
    metadata: Optional[Dict[str, Any]] = attr.ib(default=None)


@attr.s(slots=True, repr=False)
class SerializedEvidence:
    """Serialized evidence of an assertion failure."""

    # Short description of what happened
    title: str = attr.ib()
    # A longer one
    param_type: str = attr.ib()
    param_path: str = attr.ib()
    message: Optional[str] = attr.ib(factory=str)
    metadata: Optional[Dict[str, Any]] = attr.ib(default=None)

    @classmethod
    def from_evidence(cls, evidence: Evidence) -> "SerializedEvidence":
        return cls(
            title=evidence.title,
            param_type=str(evidence.param_type),
            param_path=evidence.param_path,
            message=evidence.message,
            metadata=evidence.metadata,
        )
