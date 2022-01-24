import asyncio

from nehushtan.logger.NehushtanFileLogger import NehushtanFileLogger

logger = NehushtanFileLogger()


async def mirai(future_instance, p):
    logger.info(f"mirai[{p}] start")
    await asyncio.sleep(1)
    logger.info(f"mirai[{p}] slept for 1s")
    future_instance.set_exception(Exception("!"))
    # future_instance.set_result(p + " done")


def show_future_result(future_instance):
    if future_instance.cancelled():
        logger.warning("show_future_result::cancelled")
        return

    if not future_instance.done():
        logger.error("show_future_result::done not")
        return

    try:
        if future_instance.result():
            logger.notice("show_future_result::result", future_instance.result())
    except Exception as e:
        if future_instance.exception():
            logger.notice("show_future_result::exception", future_instance.exception().get_message())


async def main():
    loop = asyncio.get_running_loop()
    f = loop.create_future()

    f.add_done_callback(show_future_result)
    loop.create_task(mirai(f, "param"))

    logger.info("main start wait")
    logger.info(await f)

    if f.exception():
        logger.exception("exception", f.exception())


if __name__ == '__main__':
    asyncio.run(main())
