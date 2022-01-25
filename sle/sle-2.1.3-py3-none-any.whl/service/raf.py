import struct

from sle.datatypes.raf_pdu import RafUserToProviderPdu,\
    RafProviderToUserPdu
from sle.datatypes.raf_structure import RafParameterName
from .base import SleUser, CCSDS_EPOCH


class RafServiceUser(SleUser):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            provider_to_user_pdu=RafProviderToUserPdu,
            user_to_provider_pdu=RafUserToProviderPdu,
            **kwargs)
        self._service_type = 'rtnAllFrames'
        self._handlers = {
            'RafBindReturn': self._bind_return_handler,
            'RafUnbindReturn': self._unbind_return_handler,
            'RafStartReturn': self._start_return_handler,
            'RafStopReturn': self._stop_return_handler,
            'RafGetParameterReturn': self._get_parameter_return_handler,
            'RafScheduleStatusReportReturn': self._schedule_status_report_return_handler,
            'RafStatusReportInvocation': self._status_report_invocation_handler,
            'RafTransferBuffer': self._transfer_buffer_handler,
            'AnnotatedFrame': self._annotated_frame_handler,
        }

    def bind(self):
        pdu = RafUserToProviderPdu()['rafBindInvocation']
        super().bind(pdu)

    def unbind(self, reason='other'):
        pdu = RafUserToProviderPdu()['rafUnbindInvocation']
        pdu['unbindReason'] = reason
        super().unbind(pdu)

    def start(self, start_time=None, end_time=None, frame_quality='allFrames'):
        pdu = RafUserToProviderPdu()['rafStartInvocation']
        pdu['requestedFrameQuality'] = frame_quality

        # TODO: check start/stop times according to CCSDS 911.1-B-4, pg 3-27ff
        if start_time is None:
            pdu['startTime']['undefined'] = None
        else:
            start_time = struct.pack(
                '!HIH', (start_time - CCSDS_EPOCH).days, 0, 0)
            pdu['startTime']['known']['ccsdsFormat'] = start_time

        if end_time is None:
            pdu['stopTime']['undefined'] = None
        else:
            stop_time = struct.pack(
                '!HIH', (end_time - CCSDS_EPOCH).days, 0, 0)
            pdu['stopTime']['known']['ccsdsFormat'] = stop_time
        super().start(pdu)

    def stop(self):
        pdu = RafUserToProviderPdu()['rafStopInvocation']
        super().stop(pdu)

    def schedule_status_report(self, report_type='immediately', cycle=None):
        pdu = RafUserToProviderPdu()['rafScheduleStatusReportInvocation']
        super().schedule_status_report(pdu, report_type, cycle)

    def get_parameter(self, parameter):
        if parameter not in [n for n in RafParameterName().namedValues]:
            raise ValueError('Unknown parameter: {}'.format(parameter))
        pdu = RafUserToProviderPdu()['rafGetParameterInvocation']
        pdu['rafParameter'] = RafParameterName().namedValues[parameter]
        super().get_parameter(pdu)

    def peer_abort(self, reason='otherReason'):
        pdu = RafUserToProviderPdu()
        pdu['rafPeerAbortInvocation'] = reason
        super().peer_abort(pdu)
