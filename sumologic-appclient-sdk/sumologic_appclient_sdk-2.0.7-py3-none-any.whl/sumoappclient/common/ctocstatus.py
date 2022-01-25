import json
import logging
import traceback
import urllib


class SourceHealthStatus(object):
    StatusError          = "Error"
    StatusNone           = "None"
    StatusStarting       = "Started"
    StatusInitialized    = "Initialized"
    StatusAuthenticated  = "Authenticated"
    StatusCollecting     = "Collecting"


class HealthStatusHandler(logging.Handler):
    """
        A handler class which posts source status to ctoc framework
    """

    def __init__(self, c2c_base_url, *args,  **kwargs):
        # for overcoming cyclic imports
        from sumoappclient.sumoclient.httputils import ClientMixin
        super(HealthStatusHandler, self).__init__(*args, **kwargs)
        self.c2c_base_url = c2c_base_url
        self.last_status = None
        self.session = ClientMixin.get_new_session()
        self.valid_health_statuses = {value for attr, value in SourceHealthStatus.__dict__.items() if attr.startswith(
            "Status") and value != SourceHealthStatus.StatusNone}

    def emit(self, record):
        try:

            has_status = hasattr(record, 'status')
            if has_status:
                self._set_status(record)

            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def _set_status(self, record):
        '''

        :param record: {status: ,errorType:}
        :return:
        '''
        current_status = record.status
        if self.last_status != current_status and current_status in self.valid_health_statuses:
            status_payload = {"state": current_status}
            if current_status == SourceHealthStatus.StatusError:
                error_code = record.errorCode if hasattr(record, "errorCode") else 500
                status_payload.update({"errorCode": error_code})
                if hasattr(record, "errorType"):
                    status_payload.update({"errorType": record.errorType})
                if record.exc_info:
                    msg = f'''{self.format(record)} Traceback: {traceback.format_exc()}'''
                    # Error msg should be between 0 to 300
                    status_payload.update({"errorInfo": msg[:300]})
            status, err = self._send_source_status(status_payload)
            if not status:
                # in case of health api error it is failed silently
                print("Unable to post health status: %s" % err)
                self.handleError(record)
            else:
                # setting it here after it is successfully set in framework
                self.last_status = current_status


    def _send_source_status(self, status_payload):
        '''

        :param status_payload: {state: ,errorType: ,errorInfo: }
        :return:
        '''
        # for overcoming cyclic imports
        from sumoappclient.sumoclient.httputils import ClientMixin


        ctoc_health_endpoint = self.c2c_base_url + "/health"
        status, err = ClientMixin.make_request(ctoc_health_endpoint, "post", session=self.session,data=json.dumps(status_payload),
                                                headers={"Content-Type": "application/json"})

        return status, err
