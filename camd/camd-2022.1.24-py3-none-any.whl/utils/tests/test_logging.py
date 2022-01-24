import unittest
import uuid
import logging
import json
from datetime import datetime, timedelta
import time

import boto3
from watchtower import CloudWatchLogHandler
from camd.utils.logging import KinesisStreamHandler


# TODO: These tests are only for development purposes
#       and are not being run in CI

class KinesisLoggerTest(unittest.TestCase):
    @unittest.skip
    def test_kinesis_logging(self):
        logger = logging.getLogger("test")
        kinesis_handler = KinesisStreamHandler("camd-events", "test/python-unit-test")
        logger.addHandler(kinesis_handler)
        logger.setLevel("INFO")
        event = {"iteration": 1,
                 "id": str(uuid.uuid4()),
                 "event": "agentGotHypotheses",
                 "metadata": {"chemsys": "Ag-Be"}
                 }
        logger.info(json.dumps(event))

    @unittest.skip
    def test_cloudwatch_logging(self):
        logger = logging.getLogger("test")
        uid = str(uuid.uuid4())
        kinesis_handler = CloudWatchLogHandler(
            log_group="/camd/test/",
            stream_name="python-unittest")
        logger.addHandler(kinesis_handler)
        logger.setLevel("INFO")
        event = {"iteration": 1,
                 "id": uid,
                 "event": "agentGotHypotheses",
                 "metadata": {"chemsys": "Ag-Be"},
                 "timestamp": datetime.now().timestamp()
                 }
        logger.info(json.dumps(event))
        time.sleep(10)

        # Query logs
        client = boto3.client("logs")
        start_query_response = client.get_log_events(
            logGroupName="/camd/test/",
            logStreamName="python-unittest",
            startTime=int((datetime.now() - timedelta(seconds=20)).timestamp())*1000,
            endTime=int(datetime.now().timestamp())*1000,
            # queryString="fields @timestamp, @message | filter streamName python-unittest"
        )


if __name__ == '__main__':
    unittest.main()