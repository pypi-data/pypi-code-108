# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------

"""Vimba camera proxy
"""

import time
import numpy as np
import logging

try:
    import PyTango
except ImportError:
    pass

from threading import Thread
from distutils.util import strtobool

from petra_camera.devices.base_camera import BaseCamera
from petra_camera.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class VimbaProxy(BaseCamera):
    """Proxy to a physical TANGO device.
    """
    SERVER_SETTINGS = {'bw':    {'low': [1, 'Image8'],
                                 'high': [2, 'Image16']},
                       'color': {'low': [5, 'ImageRGB'],
                                 'high': [5, 'ImageRGB']}
                       }

    PIXEL_FORMATS = {'color': {'high': [],
                               'low': ['RGB8Packed']},
                     'bw':    {'high': ["Mono12", "BayerGR12", "BayerRG12", "BayerGB12"],
                               'low': ['Mono8']}
                     }

    START_DELAY = 1
    STOP_DELAY = 0.5

    _settings_map = {"exposure": ("device_proxy", "ExposureTimeAbs"),
                     "gain": ["device_proxy", "Gain"],
                     'FPSmax': ("device_proxy", "AcquisitionFrameRateLimit"),
                     'FPS': ("device_proxy", "AcquisitionFrameRateAbs"),
                     'view_x': ("device_proxy", "OffsetX"),
                     'view_y': ("device_proxy", "OffsetY"),
                     'view_h': ("device_proxy", "Height"),
                     'view_w': ("device_proxy", "Width"),
                     'max_width': ("device_proxy", "WidthMax"),
                     'max_height': ("device_proxy", "HeightMax")
                     }

    visible_layouts = ('FPS', 'exposure')

    # ----------------------------------------------------------------------
    def __init__(self, settings):
        super(VimbaProxy, self).__init__(settings)

        self._settings_map["gain"][1] = str(self._device_proxy.get_property('GainFeatureName')['GainFeatureName'][0])
        if settings.hasAttribute('high_depth'):
            high_depth = strtobool(settings.getAttribute("high_depth"))
        else:
            high_depth = False

        if settings.hasAttribute('color'):
            color = strtobool(settings.getAttribute("color"))
        else:
            color = False

        accepted_format = None

        if self._device_proxy.state() != PyTango.DevState.MOVING:
            valid_formats = self._device_proxy.read_attribute('PixelFormat_Values').value
        else:
            valid_formats = self._device_proxy.pixelformat
        if color:
            if high_depth:
                for pixel_format in self.PIXEL_FORMATS['color']['high']:
                    if pixel_format in valid_formats:
                        accepted_format = pixel_format
                        self._high_depth = True
                        self._color = True
            if accepted_format is None:
                for pixel_format in self.PIXEL_FORMATS['color']['low']:
                    if pixel_format in valid_formats:
                        accepted_format = pixel_format
                        self._high_depth = False
                        self._color = True

        if accepted_format is None:
            if high_depth:
                for pixel_format in self.PIXEL_FORMATS['bw']['high']:
                    if pixel_format in valid_formats:
                        accepted_format = pixel_format
                        self._high_depth = True
                        self._color = False
            if accepted_format is None:
                for pixel_format in self.PIXEL_FORMATS['bw']['low']:
                    if pixel_format in valid_formats:
                        accepted_format = pixel_format
                        self._high_depth = False
                        self._color = False

        if accepted_format is None:
            raise RuntimeError('Cannot find acceptable pixel format!')

        if self._device_proxy.state() != PyTango.DevState.MOVING:
            self._device_proxy.pixelformat = accepted_format
            self._device_proxy.viewingmode = \
            self.SERVER_SETTINGS['color' if self._color else 'bw']['high' if self._high_depth else 'low'][0]

        self._image_source = \
            self.SERVER_SETTINGS['color' if self._color else 'bw']['high' if self._high_depth else 'low'][1]

        self.error_msg = ''
        self.error_flag = False
        self._last_frame = np.zeros((1, 1))
        self._last_time = time.time()

        self._mode = 'event'
        self._eid = None
        self._frame_thread = None
        self._frame_thread_running = False
        self._stop_frame_thread = False

    # ----------------------------------------------------------------------
    def get_settings(self, option, cast):

        if option == 'max_level_limit':

            logger.debug(f'{self._my_name}: setting {cast.__name__}({option}) requested')

            if self._high_depth:
                return 2 ** 12
            else:
                return 2 ** 8

        elif option == 'exposure':
            return super(VimbaProxy, self).get_settings(option, cast) / 1000

        else:
            return super(VimbaProxy, self).get_settings(option, cast)

    # ----------------------------------------------------------------------
    def save_settings(self, option, value):

        if option == 'exposure':
            super(VimbaProxy, self).save_settings(option, value*1000)
        else:
            super(VimbaProxy, self).save_settings(option, value)

    # ----------------------------------------------------------------------
    def start_acquisition(self):
        """
        """

        if self._device_proxy.state() == PyTango.DevState.ON:

            logger.debug(f'{self._my_name}: starting acquisition: event mode')

            self._mode = 'event'
            self._eid = self._device_proxy.subscribe_event(self._image_source,
                                                           PyTango.EventType.DATA_READY_EVENT,
                                                           self._readout_frame, [], True)

            self._device_proxy.command_inout("StartAcquisition")
            time.sleep(self.START_DELAY)  # ? TODO

            return True
        elif self._device_proxy.state() == PyTango.DevState.MOVING:

            logger.debug(f'{self._my_name}: starting acquisition: thread mode')

            self._stop_frame_thread = False
            self._mode = 'attribute'
            self._frame_thread = Thread(target=self._read_frame)
            self._frame_thread_running = True
            self._frame_thread.start()
            return True

        else:
            logger.warning("Camera should be in ON state (is it running already?)")
            return False

    # ----------------------------------------------------------------------
    def stop_acquisition(self):
        """
        """
        if self._mode == 'event':
            if self._eid is not None:
                self._device_proxy.unsubscribe_event(self._eid)
                self._eid = None
            if self._device_proxy.state() == PyTango.DevState.MOVING:
                self._device_proxy.command_inout("StopAcquisition")
        else:
            if self._frame_thread_running:
                self._stop_frame_thread = True
                while self._frame_thread_running:
                    time.sleep(0.1)

            time.sleep(self.STOP_DELAY)  # ? TODO

    # ----------------------------------------------------------------------
    def is_running(self):
        if self._mode == 'event':
            return self._device_proxy.state() == PyTango.DevState.MOVING
        else:
            if self._device_proxy.state() != PyTango.DevState.MOVING:
                return False
            else:
                return self._frame_thread_running

    # ----------------------------------------------------------------------
    def _read_frame(self):
        sleep_time = self.get_settings('FPS', int)
        while not self._stop_frame_thread:
            if self._device_proxy.state() != PyTango.DevState.MOVING:
                self._frame_thread_running = False
                raise RuntimeError('Camera was stopped!')
            try:
                self._last_frame = self._process_frame(getattr(self._device_proxy, self._image_source))
                self._new_frame_flag = True
            except Exception as err:
                logger.error('Vimba error: {}'.format(err))
                self.error_flag = True
                self.error_msg = str(err)
            time.sleep(1/sleep_time)
        self._frame_thread_running = False

    # ----------------------------------------------------------------------
    def _readout_frame(self, event):
        """Called each time new frame is available.
        """
        if not event.err:
            try:
                data = event.device.read_attribute(event.attr_name.split('/')[6])
                self._last_frame = self._process_frame(data.value)
                self._new_frame_flag = True

            except Exception as err:
                logger.error('Vimba error: {}'.format(err))
                self.error_flag = True
                self.error_msg = str(err)
        else:
            logger.error('Vimba error: {}'.format(self.error_msg))
            self.error_flag = True
            self.error_msg = event.errors

    # ----------------------------------------------------------------------
    def _process_frame(self, data):
        data = np.transpose(data)
        if self._color:
            c_data = np.zeros(data.shape + (3,), dtype=np.ubyte)
            c_data[..., 0] = data & 255
            c_data[..., 1] = (data >> 8) & 255
            c_data[..., 2] = (data >> 16) & 255

            return c_data
        else:
            return data

    # ----------------------------------------------------------------------
    def close_camera(self):
        super(VimbaProxy, self).close_camera()

        if self._eid is not None:
            self._device_proxy.unsubscribe_event(self._eid)

        if self._frame_thread_running:
            self._stop_frame_thread = True
            while self._frame_thread_running:
                time.sleep(0.1)

