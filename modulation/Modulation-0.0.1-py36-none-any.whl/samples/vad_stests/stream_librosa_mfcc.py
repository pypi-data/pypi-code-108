#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Christian Heider Nielsen"
__doc__ = r"""

           Created on 21-11-2020
           """

import time

import librosa
import numpy
import pyaudio


def a():
    sr = 44100
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sr, input=True)
    # with s as stream:
    # librosa.get_samplerate(stream)
    for y_block in librosa.stream(
        stream, block_length=256, frame_length=2048, hop_length=2048
    ):
        m_block = librosa.feature.melspectrogram(
            y_block, sr=sr, n_fft=2048, hop_length=2048, center=False
        )
        print(type(m_block))

    stream.close()


def b():
    class AudioHandler(object):
        def __init__(self):
            self.FORMAT = pyaudio.paFloat32
            self.CHANNELS = 1
            self.RATE = 44100
            self.CHUNK = 1024 * 2
            self.p = None
            self.stream = None

        def start(self):
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                output=False,
                stream_callback=self.callback,
                frames_per_buffer=self.CHUNK,
            )

        def stop(self):
            self.stream.close()
            self.p.terminate()

        def callback(self, in_data, frame_count, time_info, flag):
            numpy_array = numpy.frombuffer(in_data, dtype=numpy.float32)
            a = librosa.feature.mfcc(numpy_array)
            print(a)
            return None, pyaudio.paContinue

        def mainloop(self):
            while (
                self.stream.is_active()
            ):  # if using button you can set self.stream to 0 (self.stream = 0), otherwise you can use a stop condition
                time.sleep(2.0)

    audio = AudioHandler()
    audio.start()  # open the the stream
    audio.mainloop()  # main operations with librosa
    audio.stop()


b()
