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

from datarobot.mlops.common import config
from datarobot.mlops.common.enums import SpoolerType
from datarobot.mlops.common.exception import DRUnsupportedType, DRConfigKeyNotFound
from datarobot.mlops.common.singleton import singleton
from datarobot.mlops.spooler.async_memory_spooler import AsyncMemoryRecordSpooler
from datarobot.mlops.spooler.filesystem_spooler import FSRecordSpooler
from datarobot.mlops.spooler.memory_spooler import MemoryRecordSpooler
from datarobot.mlops.spooler.rabbitmq_spooler import RabbitMQRecordSpooler
from datarobot.mlops.spooler.sqs_spool import SQSRecordSpooler
from datarobot.mlops.spooler.stdout_spooler import StdoutRecordSpooler


@singleton
class RecordSpoolerFactory(object):
    def create(self, spooler_type):

        if spooler_type == SpoolerType.STDOUT:
            return StdoutRecordSpooler()

        elif spooler_type == SpoolerType.FILESYSTEM:
            return FSRecordSpooler()

        elif spooler_type == SpoolerType.SQS:
            return SQSRecordSpooler()

        elif spooler_type == SpoolerType.RABBITMQ:
            return RabbitMQRecordSpooler()

        elif spooler_type == SpoolerType.PUBSUB:
            # install package as needed; conflict with DR packages; AGENT-1375
            try:
                from datarobot.mlops.spooler.pubsub_spooler import PubSubRecordSpooler
            except ImportError:
                message = ("PubSubSpoolChannel failed; missing package; "
                           "need to pip install google-cloud-pubsub==1.7.0")
                raise RuntimeError(message)
            return PubSubRecordSpooler()

        elif spooler_type == SpoolerType.MEMORY:
            return MemoryRecordSpooler()

        elif spooler_type == SpoolerType.ASYNC_MEMORY:
            return AsyncMemoryRecordSpooler()
        elif spooler_type == SpoolerType.NONE:
            return None

        elif spooler_type == SpoolerType.KAFKA:
            # Install package as needed, which includes pre-built binary of the librdkafka.
            # To enable TLS / Kerberos support, the librdkafka should be re-compiled with
            # libssl-dev and libsasl2-dev. See https://github.com/edenhill/librdkafka#requirements.
            try:
                from datarobot.mlops.spooler.kafka_spooler import KafkaRecordSpooler
            except ImportError:
                message = ("KafkaSpoolChannel failed; missing package; "
                           "need to pip install confluent-kafka>=1.6.0,<2")
                raise RuntimeError(message)
            return KafkaRecordSpooler()

        else:
            raise DRUnsupportedType("Unsupported spooler type: {}".format(spooler_type))

    def get_current_configured_spooler(self):
        # Try to read the spooler configuration from environment variables
        try:
            spooler_type = SpoolerType.from_name(
                config.get_config(config.ConfigConstants.SPOOLER_TYPE)
            )
        except DRConfigKeyNotFound:
            return None

        spooler = self.create(spooler_type)
        if spooler is not None:
            spooler.set_config()

        return spooler
