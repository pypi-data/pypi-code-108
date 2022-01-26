

import os
import glob
import atexit
import shutil
import tempfile

from threading import Thread
from pdf2image import convert_from_path
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from .gallery import ImageGallery


def generate_pdf_images(source, target, callback):

    if not os.path.exists(source):
        raise FileNotFoundError(source)

    if os.path.exists(target):
        if callback:
            callback()
        return

    os.makedirs(target, exist_ok=True)

    def _namegen():
        while True:
            yield 'page'

    convert_from_path(source, fmt='png', dpi=100,
                      output_folder=target,
                      output_file=_namegen())

    if callback:
        callback()


class PDFPlayer(FloatLayout):
    source = StringProperty()
    loop = BooleanProperty(True)
    interval = NumericProperty(10)

    def __init__(self, source, loop=True, temp_dir=None,
                 exit_retrace=False, **kwargs):
        super(PDFPlayer, self).__init__(**kwargs)

        self._gallery = ImageGallery(parent_layout=self,
                                     animation_vector=(-1, 0),
                                     exit_retrace=exit_retrace)
        self._gallery.transition = 'in_out_expo'

        self._current_page = -1
        self._task = None
        self._cancelled = False
        self._pages = []

        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
            atexit.register(shutil.rmtree, temp_dir)
        self._temp_dir = temp_dir

        self.bind(source=self._load_source)
        self.bind(interval=self.start)

        self.loop = loop
        self.source = source

    @property
    def num_pages(self):
        return len(self._pages)

    @property
    def pages_dir(self):
        name = os.path.splitext(os.path.basename(self.source))[0]
        return os.path.join(self._temp_dir, name)

    def _generate_images(self, callback):
        generate_pdf_images(self.source, self.pages_dir, callback)

    def _load_source(self, *_):
        if not self.source:
            return

        if not os.path.exists(self.source):
            raise FileNotFoundError(self.source)

        if not os.path.exists(self.pages_dir):
            Thread(target=self._generate_images,
                   args=[self._start_display]).start()
        else:
            self._start_display()

    def _start_display(self):
        if self._cancelled:
            return

        def _sort_key(filepath):
            fname = os.path.splitext(os.path.basename(filepath))[0]
            return int(fname.split('-')[1])

        self._pages = sorted(glob.glob(os.path.join(self.pages_dir, '*.png')),
                             key=_sort_key)
        self.start()

    def stop(self):
        self._cancelled = True
        if self._task:
            self._task.cancel()

    def _next_page(self):
        if self._current_page < len(self._pages) - 1:
            return self._current_page + 1
        else:
            return 0

    def step(self, *_):
        last_page = self._current_page
        self._current_page = self._next_page()
        if last_page == self._current_page:
            return
        self._gallery.current = self._pages[self._current_page]

    def start(self):
        self.stop()
        if not self._pages:
            return
        self._task = Clock.schedule_interval(self.step, self.interval)
        self.step()
