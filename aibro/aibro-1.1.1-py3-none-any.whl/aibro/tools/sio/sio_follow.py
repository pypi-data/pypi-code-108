from time import sleep

import socketio

sio_follow = socketio.Client()


@sio_follow.event
def connect():
    pass


def add_job_to_socket(job_id: str):
    sio_follow.emit("add_job_to_socket", {"job_id": job_id})


def del_job_to_socket(job_id: str):
    sio_follow.emit("del_job_to_socket", {"job_id": job_id})


@sio_follow.on("to_client_follow")
def to_client_follow(data):
    print(data)


@sio_follow.on("to_client_follow_no_newline")
def to_client_follow_no_newline(data):
    print(data, end="")


@sio_follow.event
def disconnect():
    pass
    # print("disconnected from server")
    # TODO make an API call to tell that the server has disconnected


def sio_disconnect():
    if sio_follow.connected:
        sio_follow.disconnect()


def connect_to_server_socket(public_ip: str, port: str = "12346"):
    sio_disconnect()

    sleep(1)
    retries = 20
    while retries > 0:
        try:
            if sio_follow.connected:
                break
            sio_follow.connect(f"http://{public_ip}:{port}/", wait=True)
            break
        except Exception as e:
            print(f"{str(e)}")
            print("Connecting server unsuccessful, retry in 30s")
            sleep(5)
            retries -= 1

    if not retries:
        raise Exception(f"Failed to connect to server socket {public_ip}")
