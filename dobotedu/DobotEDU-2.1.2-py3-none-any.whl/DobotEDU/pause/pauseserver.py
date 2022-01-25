import asyncio
import time
import os
import platform
from DobotRPC import RPCServer, loggers

is_run = True
IP = "127.0.0.1"
PORT = 9007
MODULE_NAME = "DOBOTEDU"
loop = None
stop_flag = None
server = None


def pause_run():
    global is_run

    while True:
        if is_run:
            break
        time.sleep(0.5)


async def pause():
    global is_run
    is_run = False


async def run():
    global is_run
    is_run = True


async def quit():
    global stop_flag
    loop.stop()


# async def hight_light_async(single_line):
#     global server
#     if server is None:
#         time.sleep(0.5)
#     await server.notify("highline", single_line)


# def hight_light(single_line):
#     loop = asyncio.get_event_loop()
#     if loop:
#         loop = asyncio.new_event_loop()
#     loop.run_until_complete(hight_light_async(single_line))


def asyn_main(new_loop):
    global loop, stop_flag, server
    loop = new_loop
    server = RPCServer(loop, IP, PORT, max_size=5)

    server.register("pause", pause)
    server.register("run", run)
    server.register("quit", quit)

    log_dir = os.getcwd()
    log_name = "Pause"
    log_name = f"{log_dir}\\{log_name}" if platform.system(
    ) == "Windows" else f"{log_dir}/{log_name}"
    loggers.set_use_console(False)
    loggers.set_use_file(False)
    loggers.set_filename(log_name)
    try:
        loggers.get(MODULE_NAME).info("running...")
        loop.run_forever()
    except Exception as e:
        loggers.get(MODULE_NAME).exception(e)
        loop.close()
    finally:
        loggers.get(MODULE_NAME).info("quited.")