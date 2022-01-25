import datetime
import time

from sle import logger
from sle.datatypes.service_instance import OperationIdentifier_v1,\
    OperationIdentifier, ServiceInstanceIdentifier,\
    ServiceInstanceAttributeElement, ServiceInstanceAttribute
from sle.proxy import Proxy


CCSDS_EPOCH = datetime.datetime(1958, 1, 1)


class State:
    UNBOUND = 'unbound'
    BOUND = 'bound'
    ACTIVE = 'active'


class SleUser:

    def __init__(
            self,
            service_instance_identifier,
            responder_host,
            responder_port,
            auth_level,
            local_identifier,
            peer_identifier,
            responder_port_identifier=None,
            local_password=None,
            peer_password=None,
            heartbeat=25,
            deadfactor=5,
            buffer_size=256000,
            version_number=5,
            provider_to_user_pdu=None,
            user_to_provider_pdu=None):

        self._service_instance_identifier = service_instance_identifier
        self._responder_host = responder_host
        self._responder_port = responder_port
        self._responder_port_identifier = responder_port_identifier
        self._auth_level = auth_level
        self._initiator_identifier = local_identifier
        self._version_number = version_number

        self._bind_pending = False
        self._unbind_pending = False
        self._start_pending = False
        self._stop_pending = False

        self.state = State.UNBOUND
        self._handlers = {}
        self._invoke_id = 0

        if provider_to_user_pdu is None:
            raise ValueError("Value for 'provider_to_user_pdu' is missing")
        if user_to_provider_pdu is None:
            raise ValueError("Value for 'user_to_provider_pdu' is missing")

        self._provider_to_user_pdu = provider_to_user_pdu
        self._user_to_provider_pdu = user_to_provider_pdu

        self._proxy = Proxy(
            self,
            local_identifier, peer_identifier,
            local_password, peer_password,
            auth_level,
            self._provider_to_user_pdu,
            heartbeat, deadfactor, buffer_size)

    def bind(self, pdu):

        if self.state != State.UNBOUND:
            logger.error("Request not valid for current state")
            return

        logger.info('Sending TML connect request...')
        self._proxy.transport.connect_request(
            self._responder_host, self._responder_port)

        while not self._proxy.connected:
            if self._proxy.transport.socket_error:
                logger.error('TML connection error')
                self._proxy.transport._tcp_disconnect_request()
                return
            time.sleep(0.1)

        logger.info('TML connection successful')

        pdu['initiatorIdentifier'] = self._initiator_identifier
        pdu['responderPortIdentifier'] = self._responder_port_identifier
        pdu['serviceType'] = self._service_type
        pdu['versionNumber'] = self._version_number

        inst_ids = [
            st.split('=')
            for st in self._service_instance_identifier.split('.')
        ]

        if self._version_number == 1:
            OID = OperationIdentifier_v1
        else:
            OID = OperationIdentifier

        sii = ServiceInstanceIdentifier()
        for i, iden in enumerate(inst_ids):
            identifier = OID[iden[0].replace('-', '_')]
            siae = ServiceInstanceAttributeElement()
            siae['identifier'] = identifier
            siae['siAttributeValue'] = iden[1]
            sia = ServiceInstanceAttribute()
            sia[0] = siae
            sii[i] = sia
        pdu['serviceInstanceIdentifier'] = sii

        logger.info("Sending bind request...")

        if self._auth_level in ['bind', 'all']:
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)
        self._bind_pending = True

    def _bind_return_handler(self, pdu):

        if not self._bind_pending:
            logger.error("Request not valid for current state")
            return

        key = pdu.getName()
        result = pdu[key]['result'].getName()

        if result == 'positive':
            logger.info("Bind successful")
            self.state = State.BOUND
        else:
            logger.warning("Bind unsuccessful")
            self._proxy.transport.disconnect_request()
            self.state = State.UNBOUND
        self._bind_pending = False

    def unbind(self, pdu):

        if self.state != State.BOUND:
            logger.error("Request not valid for current state")
            return

        logger.info("Sending unbind request...")
        # TODO: clear local returns
        # ...
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)
        self._unbind_pending = True

    def _unbind_return_handler(self, pdu):

        if not self._unbind_pending:
            logger.error("Request not valid for current state")
            return

        # TODO: cleanup
        # ...
        self._proxy.transport.disconnect_request()
        logger.info("Unbind successful")
        self.state = State.UNBOUND
        self._unbind_pending = False

    def start(self, pdu):

        if self.state != State.BOUND:
            logger.error("Request not valid for current state")
            return

        pdu['invokeId'] = self._get_new_invoke_id()
        logger.info("Sending start invocation...")
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)
        self._start_pending = True

    def _start_return_handler(self, pdu):

        if not self._start_pending:
            logger.error("Request not valid for current state")
            return

        key = pdu.getName()
        result = pdu[key]['result'].getName()
        if result == 'positiveResult':
            logger.info('Start successful')
            self.state = State.ACTIVE
        else:
            logger.info("Start unsuccessful: {}".format(
                pdu[key]['result'][result].prettyPrint()))
            self.state = State.BOUND
        self._start_pending = False

    def stop(self, pdu):

        if self.state != State.ACTIVE:
            logger.error("Request not valid for current state")
            return

        pdu['invokeId'] = self._get_new_invoke_id()
        logger.info("Sending stop invocation...")
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)
        self._stop_pending = True

    def _stop_return_handler(self, pdu):

        if not self._stop_pending:
            logger.error("Request not valid for current state")
            return

        key = pdu.getName()
        result = pdu[key]['result'].getName()
        if result == 'positiveResult':
            logger.info("Stop successful")
            self.state = State.BOUND
        else:
            logger.info("Stop unsuccessful")
            self.state = State.ACTIVE
        self._stop_pending = False

    def schedule_status_report(self, pdu, report_type, cycle):

        if self.state not in [State.BOUND, State.ACTIVE]:
            logger.error("Request not valid for current state")
            return

        pdu['invokeId'] = self._get_new_invoke_id()

        if report_type == 'immediately':
            pdu['reportRequestType']['immediately'] = None
        elif report_type == 'periodically':
            pdu['reportRequestType']['periodically'] = cycle
        elif report_type == 'stop':
            pdu['reportRequestType']['stop'] = None
        else:
            raise ValueError('Unknown report type: {}'.format(report_type))

        logger.info("Schedule status report invocation...")
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)

    def _schedule_status_report_return_handler(self, pdu):

        if self.state == State.UNBOUND:
            logger.error("Request not valid for current state")
            return

        logger.info("Received schedule status report return")
        key = pdu.getName()
        result = pdu[key]['result'].getName()
        if result == 'positiveResult':
            logger.info("Schedule status report successful")
        else:
            diag = pdu[key]['result'].getComponent()
            if diag.getName() == 'common':
                diag_options = ['duplicateInvokeId', 'otherReason']
            else:
                diag_options = [
                    'notSupportedInThisDeliveryMode', 'alreadyStopped',
                    'invalidReportingCycle']
            reason = diag_options[int(diag.getComponent())]
            logger.warning(
                "Status report scheduling failed. "
                "Reason: {}".format(reason))

    def _status_report_invocation_handler(self, pdu):
        key = pdu.getName()
        self.status_report_indication(pdu[key])

    def get_parameter(self, pdu):

        if self.state not in [State.BOUND, State.ACTIVE]:
            logger.error("Request not valid for current state")
            return

        pdu['invokeId'] = self._get_new_invoke_id()
        logger.info("Sending get parameter invocation...")
        if self._auth_level == 'all':
            self._proxy.authentication.sle_pdu_request(pdu, True)
        else:
            self._proxy.authentication.sle_pdu_request(pdu, False)

    def _get_parameter_return_handler(self, pdu):

        if self.state == State.UNBOUND:
            logger.error("Request not valid for current state")
            return

        logger.info("Received get parameter return")
        key = pdu.getName()
        result = pdu[key]['result'].getName()
        if result == 'negativeResult':
            logger.warning("Get parameter invokation failed")
            return
        pdu = pdu[key]['result'].getComponent()
        self.parameter_indication(pdu)

    def peer_abort(self, pdu):

        if self.state == State.UNBOUND:
            logger.error("Request not valid for current state")
            return

        logger.info("Sending peer abort invocation...")
        self._proxy.authentication.sle_pdu_request(pdu, False)
        self.state = State.UNBOUND
        self._proxy.transport.disconnect_request()

    def _get_new_invoke_id(self):
        self._invoke_id += 1
        return self._invoke_id

    def sle_pdu_indication(self, pdu):
        key = pdu.getName()
        key = key[:1].upper() + key[1:]
        if key in self._handlers:
            pdu_handler = self._handlers[key]
            pdu_handler(pdu)
        else:
            err = (
                'PDU of type {} has no associated handlers. '
                'Unable to process further and skipping ...'
            )
            logger.error(err.format(key))

    def _transfer_buffer_handler(self, pdu):

        if self.state != State.ACTIVE:
            logger.error("Request not valid for current state")
            return

        key = pdu.getName()
        for frame_or_notify in pdu[key]:
            self.sle_pdu_indication(frame_or_notify)

    def _annotated_frame_handler(self, pdu):
        frame = pdu.getComponent()
        if not frame.isValue:
            err = (
                'TransferBuffer received but data cannot be located. '
                'Skipping further processing of this PDU ...'
            )
            logger.info(err)
            return
        self.frame_indication(frame)

    def parameter_indication(self, pdu):
        pass  # to be implemented by application

    def status_report_indication(self, pdu):
        pass  # to be implemented by application

    def frame_indication(self, pdu):
        pass  # to be implemented by application
