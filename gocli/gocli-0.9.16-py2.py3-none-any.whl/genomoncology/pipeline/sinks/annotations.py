import asyncio
import uuid
from multiprocessing import Process, Queue

from cytoolz.curried import assoc, curry
from glom import glom, Coalesce

from genomoncology import kms
from genomoncology.parse import DocType
from genomoncology.pipeline.transformers import filter_private_keys
from . import Sink

EOL = "EOL"


async def make_call(sdk, data_set, data_set_version, build, in_queue):
    unit = in_queue.get()

    while unit != EOL:
        data, response = await kms.annotations.async_load_annotations(
            unit,
            sdk=sdk,
            data_set=data_set,
            data_set_version=data_set_version,
            build=build,
        )
        exceptions = response.get("failed_to_load", [])
        if len(exceptions) > 0:
            [
                print(f"FAILED TO LOAD ANNOTATION: {exception}")
                for exception in exceptions
            ]
        other_exceptions = response.get("loaded_but_with_errors", [])
        if len(other_exceptions) > 0:
            [
                print(f"ANNOTATION THAT LOADED BUT WITH AN ERROR: {exception}")
                for exception in other_exceptions
            ]
        unit = in_queue.get()


def background_runner(state, data_set, data_set_version, queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    sdk = state.create_sdk(
        async_enabled=True, loop=loop, timeout=state.timeout
    )
    loop.run_until_complete(
        asyncio.gather(
            make_call(sdk, data_set, data_set_version, state.build, queue)
        )
    )


@curry
class LoadAnnotationSink(Sink):
    def __init__(self, _, state, data_set, data_set_version, num_workers=10):
        self.data_set = data_set
        self.data_set_version = data_set_version
        self.queue = Queue(maxsize=1000)
        self.workers = []

        self.num_workers = num_workers

        for _ in range(num_workers):
            worker = Process(
                target=background_runner,
                args=(state, data_set, data_set_version, self.queue),
            )
            worker.start()
            self.workers.append(worker)

    def close(self):
        for _ in range(self.num_workers):
            self.queue.put(EOL)

        for worker in self.workers:
            worker.join()

    def write(self, data):
        data = filter(lambda x: not DocType.HEADER.is_a(x), data)
        data = list(map(filter_private_keys, data))

        self.queue.put(data)
        return data


UUID = "uuid"


@curry
def set_uuid(data_set, data_set_version, record):
    if UUID not in record:
        uuid_value = glom(record, Coalesce("hgvs_g", "hgvs_c", default=None))

        if uuid_value:
            uuid_value = f"{data_set}|{data_set_version}|{uuid_value}"
            uuid_value = str(uuid.uuid3(uuid.NAMESPACE_DNS, uuid_value))
        else:
            uuid_value = str(uuid.uuid4())

        record = assoc(record, UUID, uuid_value)

    return record
