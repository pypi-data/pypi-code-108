import os
import queue
from concurrent import futures
from multiprocessing import Process, Value, Queue

import grpc
import pickle

from .protos import DataProducerServicer, \
	add_DataProducerServicer_to_server
from .protos import BatchData, BatchDataResponse
from .protos.data_consumer_pb2 import ProducerStopResponse, Hints

_MAX_SIZE_OF_MESSAGE = 4000000
default_hints = {"topic": "default", "units": 1}


class _DataProducerServicer(DataProducerServicer):
	# extra bytes for reserving
	# _EXTRA_SPACE = 1000

	def __init__(self, data_queue: Queue, stopped):
		self.data_queue = data_queue
		self.stopped = stopped
		self.previous_picked_data = None
		self.previous_hints = None

	def PullBatch(self, request_iterator, context):
		for _ in request_iterator:
			yield self._create_response()

	def Stop(self, request, context):
		self.stopped.value = True
		return ProducerStopResponse(status=True)

	def _create_response(self):
		if self.previous_picked_data is None:
			batch = self.data_queue.get()
			hints = getattr(batch, "hints", default_hints)
			self.previous_picked_data = pickle.dumps(
				batch
			)
			self.previous_hints = hints

		pickled_data = self.previous_picked_data
		is_final = True

		# with empty data it is equal to 17
		response = BatchDataResponse(
			is_final=is_final,
			data=BatchData(
				pickled_data=pickled_data
			),
			hints=Hints(
				units=self.previous_hints.get("units", 1),
				topic=self.previous_hints.get("topic", "default")
			)
		)
		if response.ByteSize() < _MAX_SIZE_OF_MESSAGE:
			self.previous_picked_data = None
			self.previous_hints = None
			return response
		excess = response.ByteSize() - _MAX_SIZE_OF_MESSAGE
		n_bytes = len(self.previous_picked_data)
		offset = n_bytes - excess
		pickled_data = self.previous_picked_data[:offset]
		self.previous_picked_data = self.previous_picked_data[offset:]
		is_final = False
		return BatchDataResponse(
			is_final=is_final,
			data=BatchData(
				pickled_data=pickled_data
			),
			hints=Hints(
				units=self.previous_hints.get("units", 1),
				topic=self.previous_hints.get("topic", "default")
			)
		)


def _serve(data_queue: Queue, stopped):
	port = int(os.environ['SERVER_PORT'])
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
	add_DataProducerServicer_to_server(
		servicer=_DataProducerServicer(data_queue, stopped),
		server=server
	)
	server.add_insecure_port(f'[::]:{port}')
	server.start()
	server.wait_for_termination()


class _TaasDataIterator:

	def __init__(self, data_loader, data_queue: Queue, stopped):
		self._inner_iter = iter(data_loader)
		self._data_queue = data_queue
		self.stopped = stopped

	def __iter__(self):
		return self

	def __next__(self):
		batch = next(self._inner_iter)
		while not self.stopped.value:
			try:
				self._data_queue.put(batch, timeout=5)
				return
			except queue.Full:
				pass
		raise StopIteration


def data_sender(data_loader):
	batch_queue = Queue(int(os.environ['MAX_QUEUE_LENGTH']))
	stopped = Value("i", False)

	Process(target=_serve, args=(batch_queue, stopped)).start()
	return _TaasDataIterator(
		data_loader=data_loader,
		data_queue=batch_queue,
		stopped=stopped
	)
