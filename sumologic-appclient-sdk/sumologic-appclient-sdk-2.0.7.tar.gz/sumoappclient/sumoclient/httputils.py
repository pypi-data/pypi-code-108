# -*- coding: future_fstrings -*-
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests.packages.urllib3.exceptions import MaxRetryError
from datetime import datetime
import threading
import traceback

from sumoappclient.common.logger import get_logger

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


class ClientMixin(object):

    RETRIED_STATUS_CODES = [502, 503, 504, 429]
    # including POST in default whitelist
    METHOD_TO_RETRY = ['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST']

    @classmethod
    def get_new_session(cls, MAX_RETRY=3, BACKOFF_FACTOR=0.1):
        sess = requests.Session()
        retries = Retry(total=MAX_RETRY, backoff_factor=BACKOFF_FACTOR, status_forcelist=cls.RETRIED_STATUS_CODES,
                        method_whitelist=cls.METHOD_TO_RETRY)
        sess.mount('https://', HTTPAdapter(max_retries=retries))
        sess.mount('http://', HTTPAdapter(max_retries=retries))
        return sess

    @classmethod
    def make_request(cls, url, method="get", session=None, TIMEOUT=5,  is_file=False, logger=None, MAX_RETRY=3, BACKOFF_FACTOR=0.1, **kwargs):
        is_success, err_msg, status_code = cls.make_request_with_status(url, method, session, TIMEOUT,  is_file, logger, MAX_RETRY, BACKOFF_FACTOR, **kwargs)
        return is_success, err_msg

    @classmethod
    def make_request_with_status(cls, url, method="get", session=None, TIMEOUT=5,  is_file=False, logger=None, MAX_RETRY=3, BACKOFF_FACTOR=0.1, **kwargs):
        # if BACKOFF_FACTOR = 1 second the successive sleeps will be 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256

        log = get_logger(__name__) if logger is None else logger
        start_time = datetime.now()
        sess = session if session else cls.get_new_session(MAX_RETRY, BACKOFF_FACTOR)
        err_msg = ""
        status_code = 500 # default 500 status code
        try:
            resp = getattr(sess, method)(url, timeout=TIMEOUT, **kwargs)
            if "headers" in kwargs:
                kwargs.pop("headers")
            status_code = resp.status_code
            if 400 <= resp.status_code < 600:
                resp.reason = resp.text if resp.text else resp.reason
            resp.raise_for_status()
            log.debug(f'''MethodType: {method} Request url: {url} status_code: {resp.status_code}''')
            if resp.status_code >= 200 or resp.status_code < 300:
                if is_file:
                    data = resp.content
                else:
                    data = resp.json() if len(resp.content) > 0 else {}

                del kwargs
                del resp
                return True, data, status_code
            else:
                err_msg = f'''Request Failed: {resp.content} url: {url} status_code: {resp.status_code} reason: {resp.reason}'''
                del resp

        except JSONDecodeError as err:
            err_msg = f'''Error in Decoding response {err} traceback: {traceback.format_exc()} {resp.content} {resp.status_code}'''
        except requests.exceptions.HTTPError as err:
            err_msg = f'''Http Error: {err}  traceback: {traceback.format_exc()}'''
        except requests.exceptions.ConnectionError as err:
            err_msg = f'''Connection Error:{err}  traceback: {traceback.format_exc()}'''
        except requests.exceptions.Timeout as err:
            time_elapsed = datetime.now() - start_time
            err_msg = f'''Timeout Error:{err}  {time_elapsed} traceback: {traceback.format_exc()}'''
        except requests.exceptions.RequestException as err:
            err_msg = f'''Error: {err}  traceback: {traceback.format_exc()}'''

        except MaxRetryError as err:
            err_msg = f'''Retry Limit Reached: {err} traceback: {traceback.format_exc()}'''
        finally:
            if not session:
                # if session was not input then deleting the current session
                sess.close()

        del kwargs
        return False, err_msg, status_code


class SessionPool(object):
    # by default request library will not timeout for any request
    # session is not thread safe hence each thread gets new session
    def __init__(self, max_retry, backoff, logger=None):
        self.sessions = {}
        self.max_retry = max_retry
        self.backoff = backoff
        self.log = get_logger(__name__) if logger is None else logger
        self.total_sessions_created = 0
        self.total_sessions_deleted = 0

    def get_thread_id(self):
        try:
            thread_id = threading.get_ident()
        except AttributeError:
            thread_id = threading._get_ident()
        return thread_id

    def get_request_session(self):
        thread_id = self.get_thread_id()
        if thread_id in self.sessions:
            return self.sessions[thread_id]
        else:
            self.log.debug(f'''Creating session for {thread_id}''')
            sess = ClientMixin.get_new_session(self.max_retry, self.backoff)
            self.sessions[thread_id] = sess
            self.total_sessions_created += 1
            return sess

    def closeall(self):
        self.log.debug("Closing all sessions")
        for _, v in self.sessions.items():
            self.total_sessions_deleted += 1
            v.close()
        self.log.info(f'''Total sessions present: {len(self.sessions.keys())} Total sessions created: {self.total_sessions_created} Total sessions deleted: {self.total_sessions_deleted}''')

    def close(self):
        thread_id = self.get_thread_id()
        self.log.debug(f'Deleting session for {thread_id}')
        if thread_id in self.sessions:
            self.sessions[thread_id].close()
            del self.sessions[thread_id]
            self.total_sessions_deleted += 1
