import asyncio
from multiprocessing import Process, Queue

from cytoolz.curried import curry
from cytoolz.curried import dissoc

from genomoncology.parse import DocType
from genomoncology.parse import ensures
from genomoncology.pipeline.transformers.functions import filter_private_keys
from . import Sink

EOL = "EOL"


async def make_call(sdk, sdk_func, in_queue):
    unit = in_queue.get()

    while unit != EOL:
        await sdk.call_with_retry(sdk_func, data=unit)
        unit = in_queue.get()


def background_runner(state, data_type, queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sdk = state.create_sdk(async_enabled=True, loop=loop)
    sdk_module = getattr(sdk, f"warehouse_{data_type}")
    sdk_func = getattr(sdk_module, f"create_warehouse_{data_type}")
    loop.run_until_complete(asyncio.gather(make_call(sdk, sdk_func, queue)))


class LoadWarehouseSink(Sink):

    DATA_TYPE = None

    def __init__(self, _, state, num_workers=10):
        assert self.DATA_TYPE, "Do not instantiate LoadWarehouseSink directly."

        self.queue = Queue(maxsize=1000)
        self.workers = []

        self.num_workers = num_workers
        self.build = state.build

        for _ in range(num_workers):
            worker = Process(
                target=background_runner,
                args=(state, self.DATA_TYPE, self.queue),
            )
            worker.start()
            self.workers.append(worker)

    def close(self):
        for _ in range(self.num_workers):
            self.queue.put(EOL)

        for worker in self.workers:
            worker.join()

    def write(self, data):
        data = ensures.ensure_collection(data)
        data = filter(DocType.HEADER.is_not, data)
        data = map(filter_private_keys, data)
        data = [dissoc(d, "annotations") for d in data]
        data = [{**d, "build": self.build} for d in data]

        self.queue.put(data)

        return data


@curry
class LoadWarehouseVariantsSink(LoadWarehouseSink):

    DATA_TYPE = "variants"


@curry
class LoadWarehouseFeaturesSink(LoadWarehouseSink):

    DATA_TYPE = "features"
