"""Transport Service to safely send http requests through urllib library without intercepting itself.
Any agent services can fill transport_queue to send http data

"""

from __future__ import unicode_literals
import json
import threading
from urllib.request import Request, urlopen
import ssl

from appdynamics import config
from appdynamics.agent.core.logs import setup_logger
from appdynamics.lang import queue
from appdynamics.agent.interceptor.base import DO_NOT_INTERCEPT


class HttpTransportService(threading.Thread):
    """This class sends HTTP POST request to a given url using urllib library. Http calls made using this thread won't be
    intercepted so any service can safely send http requests using it without self interception.
    Usage:
        To send data put the request in transport queue.
        Transport queue accepts data in form (url, data_iterator, headers)
    """
    def __init__(self):
        super(HttpTransportService, self).__init__()
        self.name = 'HttpTransportService'
        self.logger = setup_logger('appdynamics.agent')
        self.transport_queue = queue.Queue()
        self.daemon = True
        self.running = False

    def _is_running(self):
        return self.running

    def run(self):
        self.running = True
        # Transport service sends data through an http call made with urllib library.
        # In order to avoid interception of this http call we set DO_NOT_INTERCEPT variable for this thread.
        DO_NOT_INTERCEPT.do_not_intercept = True
        while self._is_running():
            try:
                url, data_iterator, headers = self.transport_queue.get()
                self.logger.debug('Http transport service is sending request..')
                self.send_data(url, data_iterator, headers)
            except:
                self.logger.exception('Exception in http transport service thread')

    def send_data(self, url, data_iterator, headers):
        """This function makes post request and assumes content-type for body as json currently.
        We can extend for it to accept other types as well if required.

        Parameters
        ----------
        url : string
        data_iterator : iterator object traversed to make payload
        headers : dict
        """
        try:
            ssl_context = ssl.create_default_context(cafile=config.ANALYTICS_CAFILE)
            data = json.dumps(list(data_iterator)).encode('utf-8')
            headers['Content-Length'] = len(data)
            req = Request(url, data, headers)
            self.logger.debug('Json sent by http transport service is {}'.format(data))
            urlopen(req, context=ssl_context)
        except:
            self.logger.exception('Http Transport Service failed to send data')
