"""Loop play audio"""

import argparse
import io
import sys
import collections
from collections.abc import Iterable
from typing import Optional

import sounddevice
import soundfile

# - Streaming audio

def loop_stream_audio(
    file: soundfile.SoundFile,
    frames: Optional[int] = 65536,
    dtype: Optional[str] = "int16",
    *,
    seekable: Optional[bool] = None,
):
    """Forever yields audio chunks from the file

    - frames => 65536
    - dtype => "int16"
    - seekable => file.seekable()

    Both arguments are passed to file.buffer_read to get the next chunk.

    To loop the audio, seekable files use seeking, and unseekable ones use an
    internal buffer instead.

    """
    if frames is None:
        frames = 65536
    if dtype is None:
        dtype = "int16"
    if seekable is None:
        seekable = file.seekable()

    if not seekable:
        # Samplesize is dtype * channels
        samplesize = _DTYPE_SIZE[dtype] * file.channels
        errors = []
        def _error_append(err: int, prefix: str = ""):
            if err != 0:
                errors.append((err, prefix))

        # Read blocks until EOF
        buffers = collections.deque()
        while True:
            block = bytearray(frames * samplesize)

            # libsndfile raises an SF_ERR_SYSTEM (2) error when EOF occurs
            # inside a block so we're appending errors to a list for later
            # processing.
            original_error_check = soundfile._error_check
            soundfile._error_check = _error_append
            try:
                frames_read = file.buffer_read_into(block, dtype=dtype)
            finally:
                soundfile._error_check = original_error_check

            # Process errors
            if errors:
                for err, prefix in errors:
                    if frames_read != frames and err == 2:
                        # We probably hit EOF. Ignore error
                        continue
                    soundfile._error_check(err, prefix)
                errors.clear()

            # Truncate unwritten bytes
            if frames_read != frames:
                del block[frames_read * samplesize : ]

            buffers.append(block)
            yield block

            # Break if it's the last block
            if frames_read != frames:
                break

        # Yield buffers forever
        while True:
            yield from buffers

    # Seekable files
    while True:
        while block := file.buffer_read(frames, dtype=dtype):
            yield block
        file.seek(0)

# - Chunking audio stream

def equal_chunk_stream(
    data_iterable: Iterable[bytes],
    buffer_len: int,
):
    """Normalizes a stream of buffers into ones of length buffer_len

    - data_iterable is the iterable of buffers.
    - buffer_len is the size to normalize buffers to

    Note that the yielded buffer is not guaranteed to be unchanged. Basically,
    create a copy if it needs to be used for longer than a single iteration.
    It may be reused inside this function to reduce object creation and
    collection.

    The last buffer yielded is always smaller than buffer_len. Other code can
    fill it with zeros, drop it, or execute clean up code

        >>> list(map(bytes, equal_chunk_stream([b"abcd", b"efghi"], 3)))
        [b'abc', b'def', b'ghi', b'']
        >>> list(map(bytes, equal_chunk_stream([b"abcd", b"efghijk"], 3)))
        [b'abc', b'def', b'ghi', b'jk']
        >>> list(map(bytes, equal_chunk_stream([b"a", b"b", b"c", b"d"], 3)))
        [b'abc', b'd']
        >>> list(map(bytes, equal_chunk_stream([], 3)))
        [b'']
        >>> list(map(bytes, equal_chunk_stream([b"", b""], 3)))
        [b'']
        >>> list(map(bytes, equal_chunk_stream([b"", b"", b"a", b""], 3)))
        [b'a']

    """
    if not buffer_len > 0:
        raise ValueError("buffer length is not positive")
    data_iterator = iter(data_iterable)

    # Initialize buffer / data variables
    buffer = memoryview(bytearray(buffer_len))
    buffer_ptr = 0
    data = b""
    data_ptr = 0
    data_len = len(data)

    while True:
        # Buffer is full. This must come before the data checking so that the
        # final chunk always passes an if len(chunk) != buffer_len.
        if buffer_ptr == buffer_len:
            yield buffer
            buffer_ptr = 0

        # Data is consumed
        if data_ptr == data_len:
            data = next(data_iterator, None)
            if data is None:
                # Yield everything that we have left (could be b"") so that
                # other code can simply check the length to know if the stream
                # is ending.
                yield buffer[:buffer_ptr]
                return
            data = memoryview(data)
            data_ptr = 0
            data_len = len(data)

        # Either fill up the buffer or consume the data (or both)
        take = min(buffer_len - buffer_ptr, data_len - data_ptr)
        buffer[buffer_ptr:buffer_ptr + take] = data[data_ptr:data_ptr + take]
        buffer_ptr += take
        data_ptr += take

# - Playing audio

# Only contains the types from soundfile
_DTYPE_SIZE = {
    "int16": 2,
    "int32": 4,
    "float32": 4,
    "float64": 8,
}

def loop_play_audio(
    file: soundfile.SoundFile,
    *,
    dtype: Optional[str] = "int16",
    seekable: Optional[bool] = None,
):
    """Seamlessly loop plays an audio file

    - file is the soundfile.SoundFile instance
    - dtype => "int16"
    - seekable => file.seekable()

    """
    if dtype is None:
        dtype = "int16"
    if seekable is None:
        seekable = file.seekable()

    # Blocksize is 20 ms * dtype * channels
    blocksize = (
        round(file.samplerate * 0.02)
        * _DTYPE_SIZE[dtype]
        * file.channels
    )

    stream = loop_stream_audio(file, dtype=dtype, seekable=seekable)

    # Matching the input's format so we don't need to do resampling / mixing
    with sounddevice.RawOutputStream(
        samplerate=file.samplerate,
        channels=file.channels,
        dtype=dtype,
        blocksize=blocksize,
    ) as output:

        # Using the specified blocksize is better for performance
        for chunk in equal_chunk_stream(stream, blocksize):
            output.write(chunk)

# - Command line

parser = argparse.ArgumentParser(
    description="Loop play audio",
)
parser.add_argument(
    "filename",
    help="file to play, use - for stdin",
)

def main(argv: Optional[list[str]] = None):
    """Command line entry point

    - argv => sys.argv[1:]

    """
    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)
    file = args.filename

    if file == "-":
        # Even though file descriptors are technically not supported on
        # Windows (see https://github.com/bastibe/python-soundfile/issues/63),
        # stdin being 0 is _probably_ something that we can rely on.
        file = 0

    with soundfile.SoundFile(file) as audio:
        try:
            loop_play_audio(audio)
        except KeyboardInterrupt:
            parser.exit()

if __name__ == "__main__":
    main()
