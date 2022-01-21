# Created by matveyev at 01.12.2020

# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------


"""Dalsa camera proxy
"""

import numpy as np
import PyTango
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import os.path as ospath

from PIL import Image

from petra_camera.devices.base_camera import BaseCamera
from petra_camera.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)

# ----------------------------------------------------------------------
class DalsaProxy(BaseCamera):

    _settings_map = {
                     'max_level_limit': (None, )
                     }

    visible_layouts = ('folder', 'source')

    # ----------------------------------------------------------------------
    def __init__(self, settings):
        super(DalsaProxy, self).__init__(settings)

        if settings.hasAttribute('folders'):
            self._possible_folders = [item.strip() for item in settings.getAttribute("folders").split(';')]
        else:
            self._possible_folders = ['/gpfs/current/raw/', '/gpfs/commissioning/raw/']

        if settings.hasAttribute('sources'):
            self._possible_sources = [item.strip() for item in settings.getAttribute("folders").split(';')]
        else:
            self._possible_sources = ['Event', 'Files']

        self._my_event_handler = PatternMatchingEventHandler(["*.tif"], "", False, True)
        self._my_event_handler.on_created = self._on_created

        self._my_observer = None

        self._source = self._possible_sources[0]

        self.path = self._possible_folders[0]

        self._last_frame = np.zeros((1, 1))

        self.error_flag = False
        self.error_msg = ''

        self._running = False

    # ----------------------------------------------------------------------
    def start_acquisition(self):

        if self._source == 'Event':

            logger.debug(f'{self._my_name}: starting acquisition: event mode')

            if self._device_proxy is None:
                raise RuntimeError('No device proxy')

            self._device_proxy.write_attribute("PixelFormat", "Mono16")
            self._device_proxy.write_attribute("ViewingMode", 2)
            self._eid = self._device_proxy.subscribe_event("Image16", PyTango.EventType.DATA_READY_EVENT,
                                                           self._on_event, [], True)
            self._running = True
            return True

        elif self._source == 'Files':
            if self.path != '':

                logger.debug(f'{self._my_name}: starting acquisition: file mode')

                self._my_observer = Observer()
                self._my_observer.schedule(self._my_event_handler, self.path, recursive=True)
                self._my_observer.start()
                self._running = True
                return True
            else:
                raise RuntimeError('Path is not exist')
        else:
            raise RuntimeError('Unknown mode')

    # ----------------------------------------------------------------------
    def stop_acquisition(self):

        if self._source == 'Event':
            logger.debug(f'{self._my_name}: stopping acquisition: event mode')
            self._device_proxy.unsubscribe_event(self._eid)

        elif self._source == 'Files':

            logger.debug(f'{self._my_name}: stopping acquisition: file mode')
            self._my_observer.stop()
            self._my_observer.join()

        else:
            raise RuntimeError('Unknown mode')

        self._running = False

    # ----------------------------------------------------------------------
    def _on_event(self, event):

        if not event.err:

            logger.debug(f'{self._my_name}: new tango event')

            data = event.device.read_attribute(event.attr_name.split('/')[6])
            self._last_frame = np.array(data.value)[self._picture_size[0]:self._picture_size[2],
                                                    self._picture_size[1]:self._picture_size[3]]

            self._new_frame_flag = True
        else:
            pass

    # ----------------------------------------------------------------------
    def _on_created(self, event):

        logger.debug(f'{self._my_name}: new file system event')

        self.id = ' file: {}'.format(ospath.splitext(ospath.basename(event.src_path))[0])

        self._last_frame = np.array(Image.open(event.src_path))[self._picture_size[0]:self._picture_size[2],
                                                                self._picture_size[1]:self._picture_size[3]]
        self._new_frame_flag = True

    # ----------------------------------------------------------------------
    def _set_new_path(self, path):

        logger.debug(f'{self._my_name}: new file path: {path}')

        need_to_restart = self._running
        if self._running:
            self.stop_acquisition()
            self._last_frame = np.zeros((1, 1))
            self._new_frame_flag = True

        self.path = path

        if need_to_restart:
            self.start_acquisition()

    # ----------------------------------------------------------------------
    def get_settings(self, option, cast):

        if option in ['Path', 'Source', 'possible_sources', 'possible_folders']:

            logger.debug(f'{self._my_name}: setting {cast.__name__}({option}) requested')

            if option == 'Path':
                path = super(DalsaProxy, self).get_settings(option, cast)
                if path != '':
                    self._set_new_path(path)
                return self.path

            elif option == 'Source':
                source = super(DalsaProxy, self).get_settings(option, cast)
                if source != '':
                    self._change_source(source)
                return self._source

            elif option == 'possible_sources':

                return self._possible_sources

            elif option == 'possible_folders':
                return self._possible_folders

        else:
            return super(DalsaProxy, self).get_settings(option, cast)

    # ----------------------------------------------------------------------
    def save_settings(self, option, value):

        if option in ['Path', 'Source']:
            logger.debug(f'{self._my_name}: setting {option}: new value {value}')

            if option == 'Path':
                self._set_new_path(value)

            elif option == 'Source':
                self._change_source(value)

        super(DalsaProxy, self).save_settings(option, value)

    # ----------------------------------------------------------------------
    def _change_source(self, source):
        need_to_restart = self._running
        if self._running:
            self.stop_acquisition()
            self._last_frame = np.zeros((1, 1))
            self._new_frame_flag = True

        self._source = source

        if need_to_restart:
            self.start_acquisition()