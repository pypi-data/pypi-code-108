# -*- coding: utf-8 -*-

"""
Tools for handling sound/voice/audio data.
"""

from typing import Text
import wave
import threading
from queue import Queue


class Wave():
    """
    To save wav file in sub-threading

    This is a wrapper of wave module,
    it is implemented non-block way to save wav file
    by threading module
    Args:
        file_path: the full file path of the saving file
        mode: "wb", "rb" for wave module
    Returns:
        None
    Refer:
        https://docs.python.org/3/library/wave.html
    Usage:
        write file example:
            with Wave(file_path, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(16000)
                wav.writeframes(data)
        read file example:
            with Wave(file_path, 'rb') as wav:
                wav.readframes(5)
    """

    def __init__(
        self,
        file_path: Text,
        mode: Text
    ) -> None:
        """Init Wave object"""
        self.file_path = file_path
        self.mode = mode
        self._queue = Queue(maxsize=100)
        self._wav_obj = wave.open(self.file_path, self.mode)
        self._is_running = False
        self._thread = None
        self.lock = threading.Lock()
        self._thread = threading.Thread(
            target=self._write
        )
        self._thread.daemon = True
        self._thread.start()
        self.is_closed = False

    def __enter__(self) -> "Wave":
        """To return object for with statement."""
        return self

    def __exit__(self, type, value, traceback) -> None:
        """To clean up when go out of the block of with statement."""
        self.close()

    def setnchannels(self, nchannels: int) -> None:
        """To set wave.nchannels in write mode."""
        self._wav_obj.setnchannels(nchannels)

    def getnchannels(self) -> int:
        """To get wave.nchannels."""
        return self._wav_obj.getnchannels()

    def setsampwidth(self, sampwidth: int) -> None:
        """To set wave.sampwidth in write mode."""
        self._wav_obj.setsampwidth(sampwidth)

    def getsampwidth(self) -> int:
        """To get wave.sampwidth."""
        return self._wav_obj.getsampwidth()

    def setframerate(self, framerate: int) -> None:
        """To set wave.framerate in write mode."""
        self._wav_obj.setframerate(framerate)

    def getframerate(self) -> int:
        """To get wave.framerate."""
        return self._wav_obj.getframerate()

    def getnframes(self) -> int:
        """To get wave.framerate."""
        return self._wav_obj.getnframes()

    def writeframes(self, data: bytes) -> None:
        """To write bytes into wave object asynchronously"""
        if self.mode.startswith('w'):
            self._queue.put(data)
        else:
            raise RuntimeError(
                f"writeframes is unsupported in mode: {self.mode}"
            )

    def readframes(self, n: int) -> bytes:
        """To read bytes from private function"""
        if self.mode.startswith('r'):
            return self._read(n)
        else:
            raise RuntimeError(
                f"readframes is unsupported in mode: {self.mode}"
            )

    def _write(self) -> None:
        """To get bytes from private queue then write into wave object"""
        self._is_running = True
        while self._is_running:
            data = self._queue.get()
            # lock this program block to avoid unexpected file-closing process
            self.lock.acquire()
            self._wav_obj.writeframes(data)
            self.lock.release()

    def _read(self, n: int) -> bytes:
        """To read bytes from wave object"""
        return self._wav_obj.readframes(n)

    def close(self) -> bool:
        """To clean up everything of Wave object"""
        while self._is_running:
            # closing should wait for released lock and empty queue
            if self._queue.qsize() == 0 and self.lock.locked() is False:
                self._is_running = False
                self._wav_obj.close()
                break
        self.is_closed = True
        return self.is_closed
