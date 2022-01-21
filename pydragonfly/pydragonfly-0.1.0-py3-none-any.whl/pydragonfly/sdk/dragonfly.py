import logging
import time
from typing import List, Union

from django_rest_client import APIClient
from django_rest_client.types import THeaders, Toid

from ..version import VERSION
from .resources import (
    Action,
    Analysis,
    Invitation,
    Organization,
    Profile,
    Report,
    Rule,
    Sample,
    Session,
    UserAccessInfo,
    UserPreferences,
)
from .resources.analysis import AnalysisResult


class Dragonfly(APIClient):
    # overwrite
    _server_url: str = "https://dragonfly.certego.net"

    @property
    def _headers(self) -> THeaders:
        return {
            **super()._headers,
            "User-Agent": f"PyDragonfly/{VERSION}",
        }

    def __init__(self, api_key: str, logger: logging.Logger = None):
        super().__init__(api_key, None, logger)

    # resources
    Action = Action
    Analysis = Analysis
    Invitation = Invitation
    Organization = Organization
    Profile = Profile
    Report = Report
    Rule = Rule
    Sample = Sample
    Session = Session
    UserAccessInfo = UserAccessInfo
    UserPreferences = UserPreferences

    # utilities

    def analyze_file(
        self,
        sample_name: str,
        sample_buffer: bytes,
        retrieve_analysis: bool = True,
        profiles: List[int] = None,
        private: bool = False,
        root: bool = False,
        operating_system: str = None,
        arguments: List[str] = None,
        dll_entrypoints: List[str] = None,
    ) -> Union[AnalysisResult, int]:
        """
        Utility function to create a new analysis and get analysis ID
        or optionally receive result directly.

        Args:
            ``sample_name`` (str):
             Name of the sample to analyze.\n
            ``sample_buffer`` (bytes):
             Sample buffer in bytes form.\n
            ``retrieve_analysis`` (bool, optional):
             If ``True``, fetch and return result otherwise return only analysis ID.
             Default ``True``.\n
            ``profiles`` (List[int], optional):
             List of IDs of profiles to emulate against.
             Default ``[1,2]``.\n
            ``private`` (bool, optional):
             Mark analysis as private limitting access to you
             and members in your organization only. Requires paid subscription.
             Default ``False``.\n
            ``root`` (bool, optional):
             Emulate with root permissions on OS level.
             Default ``False``.\n
            ``operating_system`` (str, optional):
             OS of the given sample. Default ``None`` i.e. detected by dragonfly.\n
            ``arguments`` (List[str], optional):
             List of extra CLI arguments to pass to the emulator.
             Only use if you know what you are doing.
             Default ``None``.\n
            ``dll_entrypoints`` (List[str], optional):
             DLL entrypoints.
             Default ``None``.

        .. versionadded:: 0.0.4
        """
        if profiles is None:
            profiles = [1, 2]
        data = self.Analysis.CreateAnalysisRequestBody(
            # We have 2 defaults profile, one for qiling, one for speakeasy.
            profiles=profiles,
            # right now we do not support private analysis anyway
            private=private,
            # emulation hooks on rule matching. Not released yet
            allow_actions=False,
            # your wish here, imho executing thing as users is more common
            root=root,
            # we can detected the OS on our backend.
            # It is required if you want to analyze shellcodes unfortunately
            os=operating_system,
            # the safer approach is that the sample did not require specific arguments
            arguments=arguments,
            # if not entrypoints are selected, and the sample is a dll
            # we will emulate a maximum of 100 entrypoints
            dll_entrypoints=dll_entrypoints,
        )
        resp = self.Analysis.create(
            data=data, sample_name=sample_name, sample_buffer=sample_buffer
        ).data
        analysis_id = resp["id"]
        if retrieve_analysis:
            return self.analysis_result(analysis_id)
        else:
            return analysis_id

    def analysis_result(
        self,
        analysis_id: Toid,
        waiting_time: int = 10,
        max_wait_cycle: int = 30,  # 30 x 10 = 5 mins
    ) -> AnalysisResult:
        """
        Utility function to retrieve an analysis' result.

        Total waiting time = ``waiting_time x max_wait_cycle``.

        Args:
           ``analysis_id`` (int|str):
            Analysis ID to fetch result of.\n
           ``waiting_time`` (int, optional):
            Wait time between subsequent HTTP requests. Default ``10``.\n
           ``max_wait_cycle`` (int, optional):
            Maximum number of HTTP requests. Default ``30``.

        .. versionadded:: 0.0.4
        """
        result = self.Analysis.Result(analysis_id)
        if max_wait_cycle:
            waiting_cycle: int = 0
            while not result.is_ready() and waiting_cycle < max_wait_cycle:
                time.sleep(waiting_time)
                result.refresh()
                waiting_cycle += 1
        return result
