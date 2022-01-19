import dataclasses
from typing import Optional

from qua.info import QuaMachineInfo


@dataclasses.dataclass
class ServerCapabilities:
    has_job_streaming_state: bool
    supports_multiple_inputs_for_element: bool
    supports_analog_delay: bool
    supports_shared_oscillators: bool
    supports_channel_weights: bool

    @staticmethod
    def build(qop_version: str, qua_implementation: Optional[QuaMachineInfo]):
        caps = (
            qua_implementation.capabilities
            if qua_implementation is not None
            else list()
        )
        return ServerCapabilities(
            has_job_streaming_state=_has_job_streaming_state(
                qop_version, qua_implementation
            ),
            supports_multiple_inputs_for_element="qm.multiple_inputs_for_element"
            in caps,
            supports_analog_delay="qm.analog_delay" in caps,
            supports_shared_oscillators="qm.shared_oscillators" in caps,
            supports_channel_weights="qm.channel_weights" in caps,
        )


def _has_job_streaming_state(
    qop_version: str, qua_implementation: Optional[QuaMachineInfo]
):
    if qop_version is not None:
        if qop_version.startswith("2.10"):
            return True
    if qua_implementation is not None:
        return "qm.job_streaming_state" in qua_implementation.capabilities
    return False
