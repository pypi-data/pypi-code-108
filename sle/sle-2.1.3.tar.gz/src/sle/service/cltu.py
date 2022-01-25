import time
import struct

from sle import logger
from sle.datatypes.cltu_pdu import CltuUserToProviderPdu,\
    CltuProviderToUserPdu
from sle.datatypes.cltu_structure import CltuParameterName
from .base import SleUser, CCSDS_EPOCH, State


class CltuServiceUser(SleUser):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            provider_to_user_pdu=CltuProviderToUserPdu,
            user_to_provider_pdu=CltuUserToProviderPdu,
            **kwargs)
        self._service_type = 'fwdCltu'
        self._handlers = {
            'CltuBindReturn': self._bind_return_handler,
            'CltuUnbindReturn': self._unbind_return_handler,
            'CltuStartReturn': self._start_return_handler,
            'CltuStopReturn': self._stop_return_handler,
            'CltuGetParameterReturn': self._get_parameter_return_handler,
            'CltuScheduleStatusReportReturn': self._schedule_status_report_return_handler,
            'CltuStatusReportInvocation': self._status_report_invocation_handler,
            'CltuTransferDataReturn': self._transfer_data_return_handler,
            'CltuThrowEventReturn': self._throw_event_return_handler,
        }

        self._cltu_id = 0
        self._event_invocation_id = 0
        self.production_status = None
        self.buffer_available = 0
        self.last_ok_cltu_id = 0

    def bind(self):
        pdu = CltuUserToProviderPdu()['cltuBindInvocation']
        super().bind(pdu)

    def unbind(self, reason='other'):
        pdu = CltuUserToProviderPdu()['cltuUnbindInvocation']
        pdu['unbindReason'] = reason
        super().unbind(pdu)

    def start(self):
        pdu = CltuUserToProviderPdu()['cltuStartInvocation']
        pdu['firstCltuIdentification'] = self._get_new_cltu_id()
        super().start(pdu)

    def stop(self):
        pdu = CltuUserToProviderPdu()['cltuStopInvocation']
        super().stop(pdu)

    def schedule_status_report(self, report_type='immediately', cycle=None):
        pdu = CltuUserToProviderPdu()['cltuScheduleStatusReportInvocation']
        super().schedule_status_report(pdu, report_type, cycle)

    def get_parameter(self, parameter):
        if parameter not in [n for n in CltuParameterName().namedValues]:
            raise ValueError('Unknown parameter: {}'.format(parameter))
        pdu = CltuUserToProviderPdu()['cltuGetParameterInvocation']
        pdu['cltuParameter'] = CltuParameterName().namedValues[parameter]
        super().get_parameter(pdu)

    def peer_abort(self, reason='otherReason'):
        pdu = CltuUserToProviderPdu()
        pdu['cltuPeerAbortInvocation'] = reason
        super().peer_abort(pdu)

    def transfer_data(
            self, data,
            earliest_time=None, latest_time=None, delay=0, notify=False):
        if self.state != State.ACTIVE:
            logger.error("Request not valid for current state")
            return

        if notify:
            # wait up to 10 seconds for notification that last command was ok
            spin_counter = 0
            while self.last_ok_cltu_id != self._cltu_id\
                    and spin_counter < 1000:
                time.sleep(0.01)
                spin_counter += 1
                if (spin_counter % 2 == 0):
                    logger.debug("Spinning, waiting for cltu confirmation")
            if spin_counter == 1000:
                logger.warning(
                    "Last cltu id " + str(self._cltu_id) +
                    " not verified within 10 sec, sending next TC anyway")
        pdu = CltuUserToProviderPdu()['cltuTransferDataInvocation']
        pdu['invokeId'] = self.invoke_id
        pdu['cltuIdentification'] = self.cltu_id

        if earliest_time:
            t = struct.pack(
                '!HIH', (earliest_time - CCSDS_EPOCH).days, 0, 0)
            pdu['earliestTransmissionTime']['known']['ccsdsFormat'] = t
        else:
            pdu['earliestTransmissionTime']['undefined'] = None

        if latest_time:
            t = struct.pack(
                '!HIH', (latest_time - CCSDS_EPOCH).days, 0, 0)
            pdu['latestTransmissionTime']['known']['ccsdsFormat'] = t
        else:
            pdu['latestTransmissionTime']['undefined'] = None

        pdu['delayTime'] = delay
        pdu['cltuData'] = data

        if notify:
            pdu['slduRadiationNotification'] = 0
        else:
            pdu['slduRadiationNotification'] = 1

        logger.info(
            "Sending CLTU id : " + str(self._cltu_id) +
            ". Last confirmed cltu id is : " + str(self.last_ok_cltu_id))
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)

    def _transfer_data_return_handler(self, pdu):

        if self.state not in [State.ACTIVE, State. STOP_PEND]:
            logger.error("Request not valid for current state")
            return

        key = pdu.getName()
        result = pdu[key]['result'].getName()
        cltu_id = pdu[key]['cltuIdentification']
        buffer_avail = pdu[key]['cltuBufferAvailable']
        self.buffer_available = buffer_avail

        if result == 'positiveResult':
            logger.info("CLTU #{} trans. passed. Buffer avail.: {}".format(
                cltu_id, buffer_avail))
            self.last_ok_cltu_id = cltu_id
        else:
            self._cltu_id -= 1  # CLTU was rejected, rollback cltu_id counter
            result = pdu[key]['result']['negativeResult']
            if result.getName() == 'common':
                opts = ['Duplicate Invoke Id', 'Other Reason']
                diag = opts[result['common']]
            else:
                opts = [
                    'Unable to Process', 'Unable to Store', 'Out of Sequence',
                    'Inconsistent Time Range', 'Invalid Time', 'Late Sldu',
                    'Invalid Delay Time', 'CLTU Error']
                diag = opts[result['specific']]
            logger.info(
                'CLTU #{} trans. failed. Diag: {}. Buffer avail: {}'.format(
                    cltu_id, diag, buffer_avail))

    def throw_event(self, event_id, event_qualifier):

        if self.state == State.UNBOUND:
            logger.error("Request not valid for current state")
            return

        pdu = CltuUserToProviderPdu()['cltuThrowEventInvocation']
        pdu['invokeId'] = self.invoke_id
        pdu['eventInvocationIdentification'] = self._event_invocation_id
        pdu['eventIdentifier'] = event_id
        pdu['eventQualifier'] = event_qualifier
        logger.info("Sending throw event invocation...")
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)

    def _throw_event_return_handler(self, pdu):

        if self.state == State.UNBOUND:
            logger.error("Request not valid for current state")
            return

        key = pdu.getName()
        result = pdu[key]['result'].getName()
        eid = pdu[key]['eventInvocationIdentification']
        if result == 'positiveResult':
            msg = "Throw event invocation successful"
            self._event_invocation_id = eid
        else:
            diag = pdu[key]['result'].getComponent()
            diag = diag[diag.getName()]
            msg = "Throw event invocation #{} Failed. Reason: {}".format(
                eid, diag)
        logger.info(msg)

    def _get_new_cltu_id(self):
        self._cltu_id += 1
        return self._cltu_id

    # def _async_notify_invocation_handler(self, pdu):
    #
    #     if self.state == State.UNBOUND:
    #         logger.error("Request not valid for current state")
    #         return
    #
    #     pdu = pdu['cltuAsyncNotifyInvocation']
    #
    #     report = '\n'
    #     if 'cltuNotification' in pdu:
    #         report += 'CLTU Notification: {}\n'.format(
    #             pdu['cltuNotification'].getName())
    #
    #     if 'cltuLastProcessed' in pdu:
    #         if pdu['cltuLastProcessed'].getName() == 'noCltuProcessed':
    #             report += 'Last Processed: None\n'
    #         else:
    #             last_processed = pdu['cltuLastProcessed'].getComponent()
    #             time = 'unknown'
    #             if 'known' in last_processed['radiationStartTime']:
    #                 time = last_processed[
    #                     'radiationStartTime'].getComponent(
    #                         ).getComponent().asOctets().hex()
    #                 # TODO: convert hex to datetime
    #             report += 'Last Processed: id: {} | '.format(
    #                 last_processed['cltuIdentification'])
    #             report += 'rad start: {} | status: {}\n '.format(
    #                 time, last_processed['cltuStatus'])
    #
    #     if 'cltuLastOk' in pdu:
    #         if pdu['cltuLastOk'].getName() == 'noCltuOk':
    #             report += 'Last Ok: No CLTU Ok\n'
    #         else:
    #             last_ok = pdu['cltuLastOk'].getComponent()
    #             time = 'unknown'
    #             if 'known' in last_ok['radiationStopTime']:
    #                 time = last_ok[
    #                     'radiationStopTime'].getComponent(
    #                         ).getComponent().asOctets().hex()
    #             report += 'Last Ok: id: {} | end: {}\n'.format(
    #                 last_ok['cltuIdentification'], time)
    #
    #     if 'productionStatus' in pdu:
    #         self.production_status = str(pdu['productionStatus'])
    #         report += 'Production Status: {}\n'.format(
    #             pdu['productionStatus'])
    #
    #     if 'uplinkStatus' in pdu:
    #         report += 'Uplink Status: {}\n'.format(
    #             pdu['uplinkStatus'])
    #
    #     logger.info(report)
