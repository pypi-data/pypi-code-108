from os import path
from flask import send_file
from eisenradio.api import ghettoApi


def audio_feed(name):

    while True:
        try:
            chunk = b''
            """grab from queue"""
            while not ghettoApi.ghetto_audio_stream_dict[name + ',audio'].empty():
                chunk = chunk + ghettoApi.ghetto_audio_stream_dict[name + ',audio'].get()
            yield chunk

        except KeyError:
            pass


def fill_sound_serve():
    # file_path = path.join(path.dirname(__file__), 'bp_util_static', 'sound', 'white_noise_192k.wav')
    # mimetype = "audio/x-wav"
    file_path = path.join(path.dirname(__file__), 'bp_util_static', 'sound', 'goa.mp3')
    mimetype = "audio/mpeg"

    return send_file(file_path, mimetype=mimetype)
