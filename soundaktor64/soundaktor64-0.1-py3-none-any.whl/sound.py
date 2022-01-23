import logging

from AppKit import NSSound
from Foundation import NSURL


class Sound:
    def __init__(self, sound_file_path):
        sound_url_path = f'file://{sound_file_path}'
        self.sound_url = NSURL.URLWithString_(sound_url_path)
        self.ns_sound = NSSound.alloc().initWithContentsOfURL_byReference_(self.sound_url, True)
        if self.ns_sound:
            logging.info(f'Sound {sound_file_path} loaded')
        else:
            logging.error(f'Failed to load sound {sound_file_path}')

    def set_volume(self, volume):
        logging.debug(f'Volume set to {volume}')
        self.ns_sound.setVolume_(volume)

    def set_loop(self, to_loop):
        self.ns_sound.setLoops_(to_loop)

    def set_time(self, current_time):
        self.ns_sound.setCurrentTime_(current_time)

    @property
    def current_time(self):
        return self.ns_sound._.currentTime

    def play(self):
        self.ns_sound.play()

    def pause(self):
        self.ns_sound.pause()

    def resume(self):
        self.ns_sound.resume()

    def stop(self):
        self.ns_sound.stop()
