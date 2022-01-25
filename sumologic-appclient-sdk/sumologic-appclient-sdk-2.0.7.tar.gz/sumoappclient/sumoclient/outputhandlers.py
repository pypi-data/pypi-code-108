# -*- coding: future_fstrings -*-
import json
import sys
import math
import zlib
import time

from sumoappclient.common.ctocstatus import SourceHealthStatus
from sumoappclient.common.errors import ErrorType
from sumoappclient.sumoclient.base import BaseOutputHandler
from sumoappclient.sumoclient.httputils import ClientMixin
from sumoappclient.sumoclient.utils import get_body


class HTTPHandler(BaseOutputHandler):

    MaxBundleSize = (1024 * 1024 * 1)

    def setUp(self, config, *args, **kwargs):
        self.sumo_config = config["SumoLogic"]
        self.collection_config = config['Collection']
        self.deploy_config = config['DeployMetaData']
        self.sumosession = ClientMixin.get_new_session(self.collection_config['MAX_RETRY'], self.collection_config['BACKOFF_FACTOR'])

    def send(self, data, extra_headers=None, jsondump=True, endpoint_key='SUMO_ENDPOINT', **kwargs):
        if not data:
            return True
        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "X-Sumo-Client": self.deploy_config['PACKAGENAME']
        }

        if extra_headers:
            headers.update(extra_headers)

        for idx, batch in enumerate(self.bytesize_chunking(data, self.collection_config.get("MAX_PAYLOAD_BYTESIZE", self.MaxBundleSize), jsondump), start=1):
            body = get_body(batch, jsondump).encode('utf-8')
            self.log.debug(f'''Sending batch {idx} len: {len(body)}''')
            if self.collection_config.get("COMPRESSED", True):
                body = zlib.compress(body)
                headers.update({"Content-Encoding": "deflate"})

            fetch_success, respjson, status_code = ClientMixin.make_request_with_status(self.sumo_config[endpoint_key], method="post",
                                                               session=self.sumosession, data=body, TIMEOUT=self.collection_config['TIMEOUT'],
                                                               headers=headers, logger=self.log)
            if not fetch_success:
                self.log.error(f'''Error in Sending to Sumo {respjson} status_code: {status_code}''')
                return False
            del body
        del data
        return True

    def close(self):
        self.sumosession.close()

    def bytesize_chunking(self, iterable, max_byte_size, jsondump=False, extra_padding=0):
        if not isinstance(iterable, (list, set, tuple)):
            iterable = [iterable]
        num_batches = 0
        total_byte_size = 0
        payload = []
        cur_size = 0
        for item in iterable:
            item_size = self.utf8len(get_body(item, jsondump))
            if cur_size + item_size + extra_padding > max_byte_size:
                num_batches += 1
                yield payload
                payload = [item]
                cur_size = item_size
            else:
                payload.append(item)
                cur_size += item_size
            total_byte_size += item_size
        if payload:
            num_batches += 1
            yield payload
        self.log.debug(f'''Chunking data total_size: {total_byte_size} num_batches: {num_batches}''')

    @classmethod
    def batchsize_chunking(cls, iterable, size=1):
        l = len(iterable)
        for idx in range(0, l, size):
            data = iterable[idx:min(idx + size, l)]
            yield data


    @classmethod
    def get_chunk_size(cls, data, MAX_SIZE=500*1000):
        body = get_body(data)
        total_bytes = cls.utf8len(body)
        batch_count = math.ceil(total_bytes/(MAX_SIZE*1.0))
        chunk_size = math.floor(len(data)/(batch_count*1.0))
        chunk_size = 1 if chunk_size == 0 else chunk_size
        return int(batch_count), int(chunk_size)


class STDOUTHandler(BaseOutputHandler):

    def setUp(self, config, *args, **kwargs):
        pass

    def send(self, data, *args, **kwargs):
        if not data:
            return True
        body = get_body(data)
        self.log.debug(f'Posting data: len {len(body)}')
        # print(body)
        del body
        del data
        return True

    def close(self):
        sys.stdout.flush()


class FileHandler(BaseOutputHandler):

    def setUp(self, config, path=None, *args, **kwargs):
        self.filepath = path or "alerts.log"
        self.fp = open(self.filepath, "ab")

    def send(self, data, *args, **kwargs):
        if not data:
            return True
        body = get_body(data)
        self.log.debug(f'Posting data: len {len(body)}')
        self.fp.write(body)

        del body
        del data
        return True

    def close(self):
        self.fp.close()



class CToCHandler(HTTPHandler):

    # same as used by jask team

    CNCLogPaddingSize = 10  # padding for cost of { "data" : ....}
    # 2MB is greater than 1MB limit for HTTP source since there is less processing on collection end in case of CNC
    # the below two settings governs when the record buffer will be flushed
    MaxBundleSize = (1024 * 1024 * 2)
    MaxWaitingTime = 15

    def setUp(self, config, extra_headers=None, *args, **kwargs):
        super(CToCHandler, self).setUp(config, *args, **kwargs)
        self.record_buffer = []
        self.current_buffer_size = 0
        self.last_send_time = time.time()
        self.extra_headers = extra_headers

    def add_records(self, records, *args, **kwargs):

        data = [record.get_log() for record in records]
        del records
        body = get_body(data, jsondump=True)
        current_data_size = self.utf8len(body)
        del body
        current_time = time.time()
        has_buffer_size_exceeded = self.current_buffer_size + current_data_size + self.CNCLogPaddingSize >= self.MaxBundleSize
        has_waiting_time_exceeded = current_time - self.last_send_time >= self.MaxWaitingTime
        is_send = send_status = False
        if has_buffer_size_exceeded or has_waiting_time_exceeded:
            self.log.info(f"Flushing records has_buffer_size_exceeded: {has_buffer_size_exceeded} buffer_size: {self.current_buffer_size} has_waiting_time_exceeded: {has_waiting_time_exceeded} total_wait_time: {current_time - self.last_send_time}")
            self.last_send_time = current_time
            self.record_buffer.extend(data)
            send_status = self.send(self.record_buffer, self.extra_headers)
            del self.record_buffer
            # Setting record buffer to empty so that state is saved till the whole data is sent
            # integrations should save state only when is_send flag is True
            self.record_buffer = []
            self.current_buffer_size = current_data_size
            is_send = True
        else:
            self.record_buffer.extend(data)
            self.current_buffer_size += current_data_size
            self.log.debug(f"Adding to buffer size: {self.current_buffer_size} current_wait_time: {current_time - self.last_send_time} last_send_time: {self.last_send_time} ")

        del data
        return is_send, send_status

    def flush_records(self, records=None, *args, **kwargs):
        if records and len(records) > 0:
            self.add_records(records)
        send_status = self.send(self.record_buffer, self.extra_headers, **kwargs)
        del self.record_buffer
        self.record_buffer = []
        self.current_buffer_size = 0
        self.last_send_time = time.time()
        del kwargs
        del records
        return send_status

    def send(self, data, extra_headers=None, jsondump=True, **kwargs):
        '''

        :param data:
            forCncLog {
                timestamp:
                message:
            }
        :param extra_headers:
        :param jsondump:
        :param endpoint_key:
        :return fetch_success:
        '''
        if not data:
            return True

        headers = {
            "content-type": "application/json",
            "accept": "application/json",
            "X-Sumo-Client": self.deploy_config['PACKAGENAME']
        }

        if extra_headers:
            headers.update(extra_headers)

        max_chunk_size = self.collection_config.get("MAX_PAYLOAD_BYTESIZE", self.MaxBundleSize)
        for idx, batch in enumerate(self.bytesize_chunking(data, max_chunk_size, jsondump, extra_padding=self.CNCLogPaddingSize), start=1):
            body = json.dumps({"data": batch}, ensure_ascii=False).encode('utf-8')
            self.log.debug(f'''Sending batch {idx} len: {len(body)}''')

            ctoc_data_endpoint = self.sumo_config['CTOC_BASE_URL'] + "/data"
            fetch_success, respjson, status_code = ClientMixin.make_request_with_status(ctoc_data_endpoint, method="post", session=self.sumosession, data=body, TIMEOUT=self.collection_config['TIMEOUT'], headers=headers, logger=self.log)
            del body
            del batch
            if not fetch_success:
                self.log.error(f'''DataAPIError: {respjson}''',
                               extra={"status": SourceHealthStatus.StatusError,
                                      "errorType": ErrorType.ERROR_FRAMEWORK,
                                      "errorCode": status_code
                                      })
                return False

        del data
        return True
