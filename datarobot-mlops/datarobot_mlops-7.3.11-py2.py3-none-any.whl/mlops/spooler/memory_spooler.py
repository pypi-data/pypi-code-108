#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

import logging
from queue import Queue, Empty, Full
import sys

from datarobot.mlops.channel.record import Record
from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.enums import SpoolerType
from datarobot.mlops.common.exception import DRSpoolerException
from datarobot.mlops.spooler.record_spooler import RecordSpooler


class MemoryRecordSpooler(RecordSpooler):
    __instance = None

    class __InnerMemoryRecordSpooler():
        DEFAULT_MAX_QUEUE_SIZE = 10 * 1024 * 1024
        MAX_RECORDS_TO_DEQUEUE = 10

        def __init__(self):
            self._logger = logging.getLogger(MemoryRecordSpooler.__name__)
            self.queue = None
            self._max_queue_size = self.DEFAULT_MAX_QUEUE_SIZE
            self.current_queue_size = 0
            self.initialized = False
            self._spool_data_format = None

        def set_config(self):
            data_format_str = config.get_config_default(ConfigConstants.SPOOLER_DATA_FORMAT, "")
            if data_format_str != "":
                raise DRSpoolerException("Data Format: '{}' is not supported by the Memory Spooler"
                                         .format(data_format_str))
            self._max_queue_size = config.get_config_default(ConfigConstants.MEMORY_MAX_QUEUE_SIZE,
                                                             self.DEFAULT_MAX_QUEUE_SIZE)

        def open(self):
            if not self.initialized:
                self.set_config()
                self.queue = Queue(self._max_queue_size)
                self.initialized = True

        def close(self):
            # This is a singleton. Others may be using the queue
            pass

        def delete(self):
            self.queue = None
            self.initialized = False

        def get_message_byte_size_limit(self):
            return self._max_queue_size

        def enqueue_single_message(self, message_json):
            if not self.initialized:
                raise DRSpoolerException("Spooler must be opened before using.")

            # Check size limit
            message_size = sys.getsizeof(message_json)
            if message_size > self.get_message_byte_size_limit():
                self._logger.warning("Cannot enqueue record size: {}".format(message_size))
                return False

            if message_size + self.current_queue_size > self._max_queue_size:
                self._logger.warning("Cannot enqueue: memory queue is full: {}"
                                     .format(self.current_queue_size))
                return False

            try:
                self.queue.put(message_json)
                self.current_queue_size += message_size
                self._logger.debug("Enqueued message of size {}".format(message_size))
                return True
            except Full:
                self._logger.error("Failed to publish a message; queue is full.")
                return False

        def enqueue(self, record_list):
            self._logger.debug("About to publish {} messages".format(len(record_list)))
            status_list = []

            for record in record_list:
                record_json = record.to_json()
                status = self.enqueue_single_message(record_json)
                status_list.append(status)
            self._logger.debug("Published {} messages, status {}".format(
                len(status_list), status_list
            ))
            return status_list

        def dequeue_single_message(self):
            if not self.initialized:
                raise DRSpoolerException("Spooler must be opened before using.")

            try:
                message_json = self.queue.get(block=False)
                message_size = sys.getsizeof(message_json)
                self.current_queue_size -= message_size
                self._logger.debug("Dequeued message of size {}".format(message_size))
                return message_json
            except Empty:
                return None

        def dequeue(self):
            record_list = []
            for _ in range(self.MAX_RECORDS_TO_DEQUEUE):
                message_json = self.dequeue_single_message()
                if message_json is None:
                    return record_list
                message = Record.from_json(message_json)
                record_list.append(message)

            return record_list

        def get_queue_size(self):
            return self._max_queue_size

    def __init__(self):
        super(MemoryRecordSpooler, self).__init__()
        if MemoryRecordSpooler.__instance is None:
            MemoryRecordSpooler.__instance = MemoryRecordSpooler.__InnerMemoryRecordSpooler()

    @staticmethod
    def get_type():
        return SpoolerType.MEMORY

    def get_required_config(self):
        return []

    def get_optional_config(self):
        return []

    def set_config(self):
        missing = super(MemoryRecordSpooler, self).get_missing_config()
        if len(missing) > 0:
            raise DRSpoolerException("Configuration values missing: {}".format(missing))
        return self.__instance.set_config()

    def open(self):
        self.__instance.open()

    def close(self):
        self.__instance.close()

    def delete(self):
        self.__instance.delete()

    def reset(self):
        self.__instance.delete()
        self.__instance.open()

    def get_message_byte_size_limit(self):
        return self.__instance.get_message_byte_size_limit()

    def enqueue_single_message(self, message_json):
        return self.__instance.enqueue_single_message(message_json)

    def enqueue(self, record_list):
        return self.__instance.enqueue(record_list)

    def dequeue_single_message(self):
        return self.__instance.dequeue_single_message()

    def dequeue(self):
        return self.__instance.dequeue()

    def __dict__(self):
        return {
            ConfigConstants.SPOOLER_TYPE.name: SpoolerType.MEMORY.name,
            ConfigConstants.MEMORY_MAX_QUEUE_SIZE.name: self.__instance.get_queue_size(),
        }
