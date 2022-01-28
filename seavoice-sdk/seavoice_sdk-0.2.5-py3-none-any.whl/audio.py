"""
SeaVoice speech SDK

Descriptions:
The input stream is defined in here.
It would use Queue to transfer the input audio and be packaged into AudioConfig.
speech.Recognizer can be configured by the AudioConfig to get the input stream object.

"""

from typing import (
    Optional,
    Text
)
import queue


class AudioStreamFormat():
    """audio configuration"""

    def __init__(
        self,
        samples_per_second: int = 16000,
        bits_per_sample: int = 16,
        channels: int = 1
    ):
        """Initialize audio stream format"""
        self.samples_per_second = samples_per_second
        self.bits_per_sample = bits_per_sample
        self.channels = channels
        self.content_type = (
            "audio/x-raw, layout=(string)interleaved, "
            f"rate=(int){self.samples_per_second}, "
            f"format=(string)S{self.bits_per_sample}LE, "
            f"channels=(int){self.channels}"
        )


class AudioInputStream():
    """Base class for Input Streams"""

    def __init__(
        self,
        stream_format: Optional[AudioStreamFormat] = None
    ) -> None:
        """Init stream_format and __buffer_space"""
        if stream_format is not None:
            self.stream_format = stream_format
        else:
            self.stream_format = AudioStreamFormat()
        self.__buffer_space = queue.Queue(maxsize=1000)
        self.is_closed = False

    def __del__(self):
        """Del"""
        self.__buffer_space = None

    def write(self, buffer: bytes):
        """Write buffer to __buffer_space"""
        if self.is_closed is False:
            self.__buffer_space.put(buffer)
        else:
            raise RuntimeError("Stream has been closed")

    def read(self):
        """Read bytes from __buffer_space, nowait"""
        if self.is_closed is False:
            if self.__buffer_space.empty() is False:
                return self.__buffer_space.get_nowait()
            else:
                return None
        else:
            raise RuntimeError("Stream has been closed")

    def read_wait(self):
        """Read bytes from __buffer_space, wait until get"""
        if self.is_closed is False:
            return self.__buffer_space.get()
        else:
            raise RuntimeError("Stream has been closed")

    def close(self):
        """Close stream"""
        self.is_closed = True
        self.__buffer_space.put(bytearray())
        self.__del__()


class AudioOutputStream():
    """
    Base class for Output Streams
    """

    def __init__(
        self,
        output_stream = None
    ) -> None:
        """Init stream_format and __buffer_space"""
        if output_stream is not None:
            self.__output_stream = output_stream
        else:
            self.__output_stream = queue.Queue(maxsize=1000000)
        self.is_closed = False

    def __del__(self):
        """Del"""
        self.__output_stream = None

    def write(self, buffer: bytes):
        """Write buffer to output_stream"""
        if self.is_closed is False:
            self.__output_stream.put(buffer)
        else:
            raise RuntimeError("Stream has been closed")

    def read(self):
        """Read bytes from __output_stream, nowait"""
        if self.is_closed is False:
            return self.__output_stream.get_nowait()
        else:
            raise RuntimeError("Stream has been closed")

    def read_wait(self):
        """Read bytes from __output_stream, wait until get"""
        if self.is_closed is False:
            return self.__output_stream.get()
        else:
            raise RuntimeError("Stream has been closed")

    def close(self):
        """Close stream"""
        self.is_closed = True
        self.__del__()


class PushAudioInputStream(AudioInputStream):
    """Audio input stream"""

    def __init__(
        self,
        stream_format: Optional[AudioStreamFormat] = None
    ):
        """Init audio input stream"""
        super().__init__(stream_format)


class AudioConfig():
    """audio configuration"""

    def __init__(
        self,
        use_default_microphone: bool = False,
        filename: Optional[Text] = None,
        stream: Optional[AudioInputStream] = None,
        device_name: Optional[Text] = None
    ):
        """Init audio configuration"""
        if use_default_microphone is True:
            if filename is None and stream is None and device_name is None:
                # TODO: Implement microphone input receiving.
                raise NotImplementedError
            else:
                raise ValueError('default microphone can not be combined with any other options')

        if sum(x is not None for x in (filename, stream, device_name)) > 1:
            raise ValueError('only one of filename, stream, and device_name can be given')

        self.filename = None
        self.stream = None
        self.device_name = None

        if filename is not None:
            self.filename = filename
            return
        if stream is not None:
            self.stream = stream
            return
        if device_name is not None:
            raise NotImplementedError

        raise ValueError('cannot construct AudioConfig with the given arguments')


class AudioOutputConfig():
    """
    Represents specific audio configuration, such as audio output device, file, or custom audio streams

    Generates an audio configuration for the speech synthesizer. Only one argument can be
    passed at a time.

    :param use_default_speaker: Specifies to use the system default speaker for audio
        output.
    :param filename: Specifies an audio output file. The parent directory must already exist.
    :param stream: Creates an AudioOutputConfig object representing the specified stream.
    """

    def __init__(
        self,
        use_default_speaker: bool = False,
        filename: Optional[Text] = None,
        stream: Optional[AudioInputStream] = None,
    ):
        """Init audio configuration"""
        if use_default_speaker is True:
            raise NotImplementedError

        if sum(x is not None for x in (filename, stream)) > 1:
            raise ValueError('either filename or stream must be given, but not both')

        self.filename = None
        self.stream = None

        if filename is not None:
            self.filename = filename
            return
        if stream is not None:
            self.stream = stream
            return

        raise ValueError('cannot construct AudioOutputConfig with the given arguments')
