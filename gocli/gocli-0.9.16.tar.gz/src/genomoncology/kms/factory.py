import asyncio
from cytoolz.curried import curry, partition_all, concat, map

from gosdk import logger
from genomoncology.parse.ensures import ensure_collection
from genomoncology.kms.annotations import AnnBundleVersionAssertionError


def create_async_processor(
    state: "State", async_func, futures_batch_size=25, **kw
):
    sdk = state.create_sdk(async_enabled=True)

    return [
        map(async_func(sdk=sdk, **kw)),
        # roll up the futures in batches, await, flatten
        partition_all(futures_batch_size),
        map(do_await(state)),
        concat,
    ]


def create_sync_processor(state: "State", sync_func, **kw):
    sdk = state.create_sdk(async_enabled=False)
    return map(sync_func(sdk=sdk, **kw))


@curry
def do_await(state, pending):
    """
    pending must be a batch of futures from the async processor
    """
    exceptions_to_always_raise = (AnnBundleVersionAssertionError,)

    pending = ensure_collection(pending)
    logger.get_logger().debug("num pending per do_await: " + str(len(pending)))

    results = state.loop.run_until_complete(
        asyncio.gather(*pending, loop=state.loop, return_exceptions=True)
    )

    for result in results:

        if isinstance(result, exceptions_to_always_raise):
            raise result

        if isinstance(result, Exception):
            state.add_failure(result)
            logger.get_logger().error("do_await failed", error=result)
            if state.hard_failure:
                raise result

        else:
            yield result
