import sys
import numpy
import pyaudio
from quiet import Encoder, Decoder


def decode():
    if sys.version_info[0] < 3:
        import Queue as queue
    else:
        import queue

    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100
    CHUNK = 16384  # int(RATE / 100)

    p = pyaudio.PyAudio()
    q = queue.Queue()

    def callback(in_data, frame_count, time_info, status):
        q.put(in_data)
        return (None, pyaudio.paContinue)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    stream_callback=callback)

    count = 0
    with Decoder(profile_name='ultrasonic-experimental') as decoder:
        while True:
            try:
                audio = q.get()
                audio = numpy.fromstring(audio, dtype='float32')
                # audio = audio[::CHANNELS]
                code = decoder.decode(audio)
                if code is not None:
                    count += 1
                    print(code.tostring().decode('utf-8', 'ignore'))
            except KeyboardInterrupt:
                break


decode()