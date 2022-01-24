import os
import time
from time import sleep

import socketio

from aibro.tools.utils import printProgressBar

# logger=True, engineio_logger=True
sio_spot = socketio.Client()


@sio_spot.event
def connect():
    pass


def add_job_to_socket(job_id: str):
    sio_spot.emit("add_job_to_socket", {"job_id": job_id})


def del_job_to_socket(job_id: str):
    sio_spot.emit("del_job_to_socket", {"job_id": job_id})


@sio_spot.on("to_client_spot")
def to_client(data):
    print(data)


@sio_spot.event
def disconnect():
    pass
    # print("disconnected from server")
    # TODO make an API call to tell that the server has disconnected


@sio_spot.on("receive_model_return")
def receive_model_return(data):
    chunk = data["chunk"]
    json_mb = round(data["json_mb"], 2)
    job_id = data["job_id"]
    last_send = data["last_send"]
    progress = round(data["progress"], 2) if not last_send else json_mb
    time_start = data["time_start"]
    rate = round(progress / (time.time() - time_start), 2)
    unit = "MiB"
    filepath = f"model_and_data_unfinished_{job_id}.json"
    with open(filepath, "a") as f:
        f.write(chunk)
        printProgressBar(
            progress,
            json_mb,
            prefix="[RECEIVING]:",
            suffix=f"{progress}{unit}/{json_mb}{unit} [avg: {rate}{unit}/s]",
            length=10,
        )
    if last_send:
        os.rename(filepath, f"model_and_data_{job_id}.json")


def sio_disconnect():
    if sio_spot.connected:
        sio_spot.disconnect()


def connect_to_server_socket(public_ip: str, port: str = "12345"):
    sio_disconnect()

    sleep(1)
    retries = 20
    while retries > 0:
        try:
            if sio_spot.connected:
                break
            sio_spot.connect(f"http://{public_ip}:{port}/", wait=True)
            break
        except Exception as e:
            print(f"{str(e)}")
            print("Connecting server unsuccessful, retry in 30s")
            sleep(5)
            retries -= 1

    if not retries:
        raise Exception(f"Failed to connect to server socket {public_ip}")
