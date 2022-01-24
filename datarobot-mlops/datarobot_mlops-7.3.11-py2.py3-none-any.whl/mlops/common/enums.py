#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
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

from enum import IntEnum


class EnumOrdinal(IntEnum):
    def ordinal(self):
        return self.value

    @classmethod
    def from_ordinal(cls, ordinal):
        return cls(ordinal)

    @classmethod
    def from_name(cls, name):
        name = name.upper()
        for n, member in cls.__members__.items():
            if name == n:
                return member
        raise ValueError(
            "'{}' name not found, allowed values: {}".format(name, str(cls.__members__.items()))
        )


class SpoolerType(EnumOrdinal):
    """
    Configures target location for output from MLOps library.
    """

    STDOUT = 0       # metrics go to stdout and are not forwarded to agent
    FILESYSTEM = 1   # output is buffered in files for agent forwarding
    NONE = 2         # no output. Disables MLOps library reporting
    INVALID = 3      # for internal use only
    SQS = 4          # output goes to AWS SQS
    RABBITMQ = 5     # output goes to RabbitMQ
    PUBSUB = 6       # output goes to PubSub
    MEMORY = 7       # in-memory spooler, can only be used when agent/lib are in the same process
    ASYNC_MEMORY = 8  # in-memory spooler, that works for multiple process
    KAFKA = 9        # output goes to Kafka


class DataFormat(EnumOrdinal):
    BYTE_ARRAY = 0
    JSON = 1
    INVALID = 2


class DataType(EnumOrdinal):
    INVALID = 0      # Note: in order to keep the same numeric value each time we add new type
    FEATURE_DRIFT = 1
    TARGET_DRIFT = 2
    DEPLOYMENT_STATS = 3
    FEATURE_DATA = 4
    PREDICTIONS_STATS_SC_CLASSIFICATION = 5
    PREDICTIONS_STATS_SC_REGRESSION = 6
    PREDICTIONS_DATA = 7
    EXTERNAL_EVENT = 8


class PredictionType(EnumOrdinal):
    REGRESSION = 0,
    CLASSIFICATION = 1


class SQSQueueType(EnumOrdinal):
    STANDARD = 0
    FIFO = 1


class MLOpsSpoolAction(EnumOrdinal):
    ENQUEUE = 0
    DEQUEUE = 1
