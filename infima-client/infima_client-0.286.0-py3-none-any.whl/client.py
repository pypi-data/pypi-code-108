"""The InfimaClient is used to interact with the infima platform."""
import os
import re
import ssl
import warnings
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
import pandas as pd
import semver
from attr import define, field

import infima_client.extras
from infima_client.api import ServiceAPI
from infima_client.demo import demo
from infima_client.extras.utils import DateT
from infima_client.version import __version__

TOKEN = os.environ.get("INFIMA_TOKEN", None)


class InfimaError(Exception):
    pass


class InfimaWarning(Warning):
    pass


@define(auto_attribs=True, slots=False)
class InfimaClient:
    """A class for keeping track of data related to the API"""

    base_url: str = field(default="https://api.infima.io", kw_only=True)
    token: Optional[str] = field(default=TOKEN, kw_only=True)
    check: bool = field(default=True, kw_only=True)
    timeout: httpx.Timeout = field(default=httpx.Timeout(60, connect=5), kw_only=True)
    cookies: Dict[str, str] = field(factory=dict, kw_only=True)
    headers: Dict[str, str] = field(factory=dict, kw_only=True)
    verify_ssl: Union[str, bool, ssl.SSLContext] = field(default=True, kw_only=True)

    api: ServiceAPI = field(init=False)

    def __attrs_post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")

        if self.token is None:
            raise InfimaError("No token provided or found in env var INFIMA_TOKEN")

        self.headers["INFIMA-TOKEN"] = self.token

        self.api = ServiceAPI(self)

        if self.check:
            self.check_auth()
            self.check_version()

    def get_headers(self) -> Dict[str, str]:
        """Get headers to be used in all endpoints"""
        return {**self.headers}

    def get_cookies(self) -> Dict[str, str]:
        return {**self.cookies}

    def get_timeout(self) -> httpx.Timeout:
        return self.timeout

    def get_available_version(self) -> Optional[str]:
        """Get available backend semantic version."""
        version = None
        try:
            with httpx.Client() as client:
                version = client.get(urljoin(self.base_url, "info")).json()["version"]
        except Exception:
            pass
        return version

    def check_version(self) -> None:
        """Check for possible version upgrade."""
        ver_match = re.search(r"(\d+\.\d+\.\d+)", __version__)
        if ver_match is None:
            warnings.warn(
                f"unable to verify versions: failed parsing library version {__version__}"
            )
            return
        else:
            ver_parsed = ver_match.group()

        ver_avail = self.get_available_version()
        if ver_avail is None:
            warnings.warn("unable to verify versions: failed getting API version")
            return

        lib_minor = semver.VersionInfo.parse(ver_parsed).replace(patch=0)
        avail_minor = semver.VersionInfo.parse(ver_avail).replace(patch=0)
        if avail_minor > lib_minor:
            msg = f"Your client: ~{lib_minor}.  Available: ~{avail_minor}"
            warnings.warn(msg, InfimaWarning)

    def check_auth(self) -> None:
        """Check for successful authentication."""
        with httpx.Client(headers=self.headers) as client:
            r = client.get(urljoin(self.base_url, "api/v1/welcome"))
            if r.status_code != 200:
                raise InfimaError("Unable to authenticate. Please check your token.")

    def demo(self) -> None:
        demo(self)

    def get_predictions(
        self,
        symbols: List[str],
        as_of: Optional[DateT] = None,
        col: Optional[str] = "cpr",
        wide: bool = True,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_as_of_predictions(
            client=self,
            symbols=symbols,
            as_of=as_of,
            col=col,
            wide=wide,
            progress=progress,
            chunk_size=chunk_size,
        )

    def get_n_months_ahead_predictions(
        self,
        symbols: List[str],
        num_months: int,
        start: Optional[DateT] = None,
        end: Optional[DateT] = None,
        col: Optional[str] = "cpr",
        wide: bool = True,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_n_months_ahead_predictions(
            client=self,
            symbols=symbols,
            num_months=num_months,
            start=start,
            end=end,
            col=col,
            wide=wide,
            progress=progress,
            chunk_size=chunk_size,
        )

    def get_preds(self, symbols: List[str], **kwargs: Any) -> Optional[pd.DataFrame]:
        as_of = kwargs.pop("as_of", None)
        num_months = kwargs.pop("num_months", None)
        if as_of is None and num_months is None:
            raise ValueError("must specify one of as_of or num_months")
        if as_of is not None and num_months is not None:
            raise ValueError("must specify only one of as_of or num_months")

        if as_of is not None:
            return self.get_predictions(symbols=symbols, as_of=as_of, **kwargs)
        else:
            return self.get_n_months_ahead_predictions(
                symbols=symbols, num_months=num_months, **kwargs
            )

    def get_pool_actuals(
        self,
        cusips: List[str],
        start: Optional[DateT] = None,
        end: Optional[DateT] = None,
        col: Optional[str] = "cpr",
        wide: bool = True,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_pool_actuals(
            client=self,
            cusips=cusips,
            start=start,
            end=end,
            col=col,
            wide=wide,
            progress=progress,
            chunk_size=chunk_size,
        )

    def get_cohort_actuals(
        self,
        cohorts: List[str],
        start: Optional[DateT] = None,
        end: Optional[DateT] = None,
        col: Optional[str] = "cpr",
        wide: bool = True,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_cohort_actuals(
            client=self,
            cohorts=cohorts,
            start=start,
            end=end,
            col=col,
            wide=wide,
            progress=progress,
            chunk_size=chunk_size,
        )

    def get_actuals(
        self,
        symbols: List[str],
        start: Optional[DateT] = None,
        end: Optional[DateT] = None,
        col: Optional[str] = "cpr",
        wide: bool = True,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_actuals(
            client=self,
            symbols=symbols,
            start=start,
            end=end,
            col=col,
            wide=wide,
            progress=progress,
            chunk_size=chunk_size,
        )

    def check_cohort_coverage(
        self,
        cohorts: List[str],
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.check_cohort_coverage(
            client=self, cohorts=cohorts, progress=progress, chunk_size=chunk_size
        )

    def check_coverage(
        self,
        cusips: List[str],
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.check_coverage(
            client=self, cusips=cusips, progress=progress, chunk_size=chunk_size
        )

    def get_cohort_summary(
        self,
        cohorts: List[str],
        factor_date: Optional[DateT] = None,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_cohort_summary(
            client=self,
            cohorts=cohorts,
            factor_date=factor_date,
            progress=progress,
            chunk_size=chunk_size,
        )

    def get_pool_attributes(
        self,
        cusips: List[str],
        factor_date: Optional[DateT] = None,
        progress: bool = True,
        chunk_size: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        return infima_client.extras.get_pool_attributes(
            client=self,
            cusips=cusips,
            factor_date=factor_date,
            progress=progress,
            chunk_size=chunk_size,
        )

    def get_member_lists(
        self, cohorts: List[str], factor_date: Optional[DateT] = None
    ) -> Optional[Dict[str, List[str]]]:
        return infima_client.extras.get_member_lists(
            client=self, cohorts=cohorts, factor_date=factor_date
        )
