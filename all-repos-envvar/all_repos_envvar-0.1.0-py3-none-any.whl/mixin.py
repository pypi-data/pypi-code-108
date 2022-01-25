from __future__ import annotations

import os
from typing import Any


class GitHubEnvMixin:
    def __new__(cls, *args: Any, **kwargs: Any):  # type: ignore[no-untyped-def]
        kwargs.setdefault("api_key", os.getenv("GITHUB_API_KEY"))
        return super().__new__(cls, *args, **kwargs)
