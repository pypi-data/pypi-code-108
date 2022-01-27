from abc import ABC
from abc import abstractmethod

from tecton_proto.args import virtual_data_source_pb2


class BaseBatchDataSource(ABC):
    @abstractmethod
    def _merge_batch_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        pass


class BaseStreamDataSource(ABC):
    @abstractmethod
    def _merge_stream_args(self, data_source_args: virtual_data_source_pb2.VirtualDataSourceArgs):
        pass
