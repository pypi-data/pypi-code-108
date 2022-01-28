#!/usr/bin/env python3
import logging
import platform
import queue
import threading
import time
import typing
from dataclasses import dataclass, field
from pathlib import Path


class PlaybackException(Exception):
    pass


@dataclass(order=True, eq=True)
class SoundRequest:
    priority: int
    timestamp: int
    sub_index: int
    request: Path = field(compare=False)
    block: bool = field(default=True, compare=False)


# Playsound is alright, but it could be better and it seems to be leaking resources in windows
class SoundServer:
    def __init__(self, shutdown_event: typing.Union[threading.Event, None] = None):
        self._sound_queue = queue.PriorityQueue()
        self._sound_thread = None
        # Not a perfect solution, playback thread will still get stuck on the queue get
        if shutdown_event is not None:
            self._shutdown = shutdown_event
        else:
            self._shutdown = threading.Event()

        system = platform.system()
        close_list = []

        if system == 'Windows':
            # OK SO MCI IS LIKE SOME WINDOWS 3.1 GARBAGE
            # But microsoft can't deprecate literally anything, so it still works.
            # DirectShow would be the real target, and modern MCI most likely uses DirectShow
            # https://github.com/sebdelsol/pyPlayer/blob/master/miniplayer.py
            # But that's a level of complicated that... no.
            # ALSO FIXME: This is a nightmare of glued together variables. subclass?
            import ctypes as ct

            def _mci_cmd(command: str) -> str:
                # It's 20XX, I'm sending a unicode string
                response = ct.create_unicode_buffer(255)
                error_code = int(ct.windll.winmm.mciSendStringW(command, response, 254, 0))
                if error_code:
                    errstr = ct.create_unicode_buffer(255)
                    ct.windll.winmm.mciGetErrorStringW(error_code, errstr, 254)
                    raise PlaybackException(f'MCI Error {error_code} during "{command}": {errstr.value}')
                return response.value

            # LMAO COOL MCI DEVICES ARE PER THREAD SO I CAN'T EVEN CLOSE THEM ELSEWHERE
            counter = 0

            def _play_func(path, block):
                nonlocal counter  # offload the work from random, sounds are silo'd per thread, a counter is fine
                alias = f'_sound_{str(counter)}'
                counter += 1
                _mci_cmd(f'open "{str(path)}" alias {alias}')
                if block:
                    # Waiting works even when it can't accurately say how long a sound is lol
                    _mci_cmd(f'play {alias} wait')
                    _mci_cmd(f'close {alias}')
                else:
                    # Tests suggest it only supports MS for mp3s, so it's already in MS
                    #  The number seems wildly off in some cases, seems to be bad MP3s?
                    #  Could also be variable bitrate encoding
                    # _mci_cmd(f'set {alias} time format milliseconds')
                    # Just, idk, add 30 seconds ot be safe
                    close_time = (int(_mci_cmd(f'status {alias} length')) / 1000) + 30 + time.time()
                    _mci_cmd(f'play {alias}')
                    close_list.append((close_time, f'close {alias}'))
                    # do NOT get me started on MCI_NOTIFY
                    # I'd like to use it to trigger cleanup automatically but WOW
                    # MCI_NOTIFY callbacks are NOT just functions. It's a window... function?
                    # I think you need to register with SetWindowsHookEx
                    # OMG WINE HAS A TEST FOR PLAYBACK CALLBACKS OH MAN
                    # Looks like I was on to something with SetWindowsHookEx
                    # https://github.com/wine-mirror/wine/blob/master/dlls/winmm/tests/mci.c#L1439
                    # We don't want a new window, so we can get ourself with GetActiveWindow??
                    # https://github.com/wine-mirror/wine/blob/master/dlls/winmm/tests/mci.c#L143
                    # But man it's just so much effort. And who knows how that will interrupt our process.

            def _close_func(cmd):
                _mci_cmd(cmd)

        elif system == 'Darwin':
            from AppKit import NSSound
            from Foundation import NSURL

            def _play_func(path, block):
                # Eat it NSURL I don't need you
                target = path.absolute().as_uri()
                # Hell, has to be an NSURL or NSString
                url = NSURL.URLWithString_(target)
                sound = NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
                # NSSound warns that the sound will be killed if this object gets GC'd
                # And we've got, like, LAYERS of GC here
                # No guarantee it won't get GC'd if we are under heavy load
                if not sound:
                    raise PlaybackException(f'Could not load {target}')
                sound.play()
                if block:
                    shutdown_event.wait(sound.duration())
                else:
                    close_time = time.time() + sound.duration() + 10
                    close_list.append((close_time, sound))

            def _close_func(sound):
                # I mean, I could call dealloc??
                # But I'd rather not interfere
                pass

        else:
            raise NotImplementedError('TODO: playsound for linux is iffy. Just run the windows build in wine')

        def _queue_listener():
            while not self._shutdown.is_set():
                try:
                    # UGH adding a timeout will get rid of the need for a shutdown sound
                    # But I hate the idea of this raising in too tight of a loop
                    # But too long of a timeout will cause it to hang
                    # TODO: Figure this out, it stays a daemon thread for now
                    sr = self._sound_queue.get(True)
                    logging.debug(f'Queue play {sr}')
                    if sr.request is None:
                        continue
                    _play_func(sr.request, sr.block)
                    if close_list and self._sound_queue.empty():
                        now = time.time()
                        while close_list and close_list[0][0] < now:
                            logging.debug(f'Closing {close_list[0][1]}')
                            _close_func(close_list.pop(0)[1])
                except queue.Empty:
                    pass
                except Exception as err:
                    logging.error(err)

            for entry in close_list:
                try:
                    _close_func(entry[1])
                except Exception as err:
                    logging.error(err)

        self._sound_thread = threading.Thread(target=_queue_listener, daemon=True, name='sounds')
        self._sound_thread.start()

    def enqueue(self, request: SoundRequest):
        self._sound_queue.put(request)

    def __del__(self):
        # I'd like to join it, but it could block no matter what I do.
        # This will at least ask it to shut off if, for some reason, we need this deleted and are still running.
        self._shutdown.set()
        self._sound_queue.put(SoundRequest(-9999, -9999, None))
