import struct

from sle.datatypes.rcf_pdu import RcfUserToProviderPdu,\
    RcfProviderToUserPdu
from sle.datatypes.rcf_structure import RcfParameterName
from .base import SleUser, CCSDS_EPOCH


class RcfServiceUser(SleUser):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            provider_to_user_pdu=RcfProviderToUserPdu,
            user_to_provider_pdu=RcfUserToProviderPdu,
            **kwargs)
        self._service_type = 'rtnChFrames'
        self._handlers = {
            'RcfBindReturn': self._bind_return_handler,
            'RcfUnbindReturn': self._unbind_return_handler,
            'RcfStartReturn': self._start_return_handler,
            'RcfStopReturn': self._stop_return_handler,
            'RcfGetParameterReturn': self._get_parameter_return_handler,
            'RcfScheduleStatusReportReturn': self._schedule_status_report_return_handler,
            'RcfTransferBuffer': self._transfer_buffer_handler,
            'AnnotatedFrame': self._annotated_frame_handler,
        }

    def bind(self):
        pdu = RcfUserToProviderPdu()['RcfBindInvocation']
        super().bind(pdu)

    def unbind(self, reason='other'):
        pdu = RcfUserToProviderPdu()['RcfUnbindInvocation']
        pdu['unbindReason'] = reason
        super().unbind(pdu)

    def start(self, gvcid, start_time=None, end_time=None):
        # gvcid is a tuple of type (spacecraft_id, version, virtual_channel)
        pdu = RcfUserToProviderPdu()['RcfStartInvocation']
        pdu['requestedGvcId']['spacecraftId'] = gvcid[0]
        pdu['requestedGvcId']['versionNumber'] = gvcid[1]
        pdu['requestedGvcId']['vcId']['virtualChannel'] = gvcid[2]

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
        pdu = RcfUserToProviderPdu()['RcfStopInvocation']
        super().stop(pdu)

    def schedule_status_report(self, report_type='immediately', cycle=None):
        pdu = RcfUserToProviderPdu()['RcfScheduleStatusReportInvocation']
        super().schedule_status_report(pdu, report_type, cycle)

    def get_parameter(self, parameter):
        if parameter not in [n for n in RcfParameterName().namedValues]:
            raise ValueError('Unknown parameter: {}'.format(parameter))
        pdu = RcfUserToProviderPdu()['RcfGetParameterInvocation']
        pdu['RcfParameter'] = RcfParameterName().namedValues[parameter]
        super().get_parameter(pdu)

    def peer_abort(self, reason='otherReason'):
        pdu = RcfUserToProviderPdu()
        pdu['RcfPeerAbortInvocation'] = reason
        super().peer_abort(pdu)
