#  Copyright (c) 2021 Toyota Research Institute.  All rights reserved.
"""
Module that defines logging utilities, e.g. for stdout
and AWS Kinesis
"""
import boto3
import logging


class KinesisStreamHandler(logging.StreamHandler):
    def __init__(self, stream_name, partition_key):
        # By default, logging.StreamHandler uses sys.stderr
        # if stream parameter is not specified
        logging.StreamHandler.__init__(self)
        self.__kinesis = None
        self.__stream_buffer = []
        try:
            self.__kinesis = boto3.client('kinesis')
        except Exception:
            print('Kinesis client initialization failed.')
        self.__stream_name = stream_name
        self.__partition_key = partition_key

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.__kinesis:
                self.__stream_buffer.append(
                    msg.encode(encoding="UTF-8", errors="strict")
                )
            else:
                stream = self.stream
                stream.write(msg)
                stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

    def flush(self):
        self.acquire()
        try:
            if self.__kinesis and self.__stream_buffer:
                import pdb; pdb.set_trace()
                for record in self.__stream_buffer:
                    self.__kinesis.put_record(
                        StreamName=self.__stream_name,
                        PartitionKey=self.__partition_key,
                        Data=record
                    )
                self.__stream_buffer.clear()
        except Exception as e:
            print("An error occurred during flush operation.")
            print(f"Exception: {e}")
            print(f"Stream buffer: {self.__stream_buffer}")
        finally:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
            self.release()


class CloudWatchHandler(logging.StreamHandler):
    def __init__(self, stream_name, partition_key):
        # By default, logging.StreamHandler uses sys.stderr
        # if stream parameter is not specified
        logging.StreamHandler.__init__(self)
        self.__kinesis = None
        self.__stream_buffer = []
        try:
            self.__kinesis = boto3.client('kinesis')
        except Exception:
            print('Kinesis client initialization failed.')
        self.__stream_name = stream_name
        self.__partition_key = partition_key

    def emit(self, record):
        try:
            msg = self.format(record)
            if self.__kinesis:
                self.__stream_buffer.append(
                    msg.encode(encoding="UTF-8", errors="strict")
                )
            else:
                stream = self.stream
                stream.write(msg)
                stream.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

    def flush(self):
        self.acquire()
        try:
            if self.__kinesis and self.__stream_buffer:
                import pdb; pdb.set_trace()
                for record in self.__stream_buffer:
                    self.__kinesis.put_record(
                        StreamName=self.__stream_name,
                        PartitionKey=self.__partition_key,
                        Data=record
                    )
                self.__stream_buffer.clear()
        except Exception as e:
            print("An error occurred during flush operation.")
            print(f"Exception: {e}")
            print(f"Stream buffer: {self.__stream_buffer}")
        finally:
            if self.stream and hasattr(self.stream, "flush"):
                self.stream.flush()
            self.release()
