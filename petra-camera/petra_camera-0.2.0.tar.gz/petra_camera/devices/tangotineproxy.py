# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------


"""TangotoTine camera proxy
"""

import numpy as np
import time
import logging
from threading import Thread
try:
    import PyTango
except ImportError:
    pass

from petra_camera.devices.base_camera import BaseCamera
from petra_camera.main_window import APP_NAME

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class TangoTineProxy(BaseCamera):
    """Proxy to a physical TANGO device.
    """
    # SERVER_SETTINGS = {"PixelFormat": "Mono8",  # possibly more...
    #                    "ViewingMode": 1}

    _settings_map = {
                     "exposure": ("device_proxy", "ExposureTime"),
                     "gain": ("device_proxy", "Gain"),
                     'max_level_limit': (None, ),
                     "counter_x": ('roi_server', 'roi_x'),
                     "counter_y": ('roi_server', 'roi_y'),
                     "counter_w": ('roi_server', 'roi_w'),
                     "counter_h": ('roi_server', 'roi_h'),
                     "background": ("device_proxy", "SubtractBackground"),
                     "background_sigmas": ("device_proxy", "BackgroundSigmas"),
                     }

    visible_layouts = ('FPS', 'exposure', 'background')

    # ----------------------------------------------------------------------
    def __init__(self, settings):
        super(TangoTineProxy, self).__init__(settings)

        self._last_frame = np.zeros((1, 1))

        self.error_flag = False
        self.error_msg = ''

        self.period = 1/self.get_settings('FPS', int)

        self._camera_read_thread = None
        self._camera_read_thread_running = False

    # ----------------------------------------------------------------------
    def start_acquisition(self):
        """
        start acquisition tread
        :return: bool
        """

        logger.debug(f"{self._my_name} starting thread")

        try:
            self._camera_read_thread = Thread(target=self._readout_frame)
            self._camera_read_thread_running = True
            self._camera_read_thread.start()

            return True

        except Exception as err:

            logger.exception(err)

        return False

    # ----------------------------------------------------------------------
    def stop_acquisition(self):
        """
        stops acquisition tread
        :return:
        """

        if self._camera_read_thread_running:
            self._camera_read_thread_running = False
            self._camera_read_thread.join()

        logger.debug(f"{self._my_name} thread stopped")

    # ----------------------------------------------------------------------
    def is_running(self):
        """

        :return: bool
        """
        return self._camera_read_thread_running

    # ----------------------------------------------------------------------
    def _readout_frame(self):
        """Called each time new frame is available.
        """

        while self._camera_read_thread_running:
            try:
                self._last_frame = self._device_proxy.Frame[self._picture_size[0]:self._picture_size[2],
                                                            self._picture_size[1]:self._picture_size[3]]
                self._new_frame_flag = True
                logger.debug(f"{self._my_name} new frame")

                time.sleep(self.period)

            except Exception as err:

                logger.exception(f"{self._my_name} exception during new frame: {err}")
                self._camera_read_thread_running = False

    # ----------------------------------------------------------------------
    def get_settings(self, option, cast):
        """
        here we catch some settings before read them from general settings
        :param option:
        :param cast:
        :return:
        """

        if option in ['max_width', 'max_height', 'FPSmax']:

            logger.debug(f'{self._my_name}: setting {cast.__name__}({option}) requested')

            if option in ['max_width', 'max_height']:

                w, h = self._device_proxy.Frame.shape
                if option == 'max_width':
                    return w
                else:
                    return h

            elif option == 'FPSmax':
                return 1000/self.period

        elif option == 'FPS':
            return max(1, super(TangoTineProxy, self).get_settings(option, cast))

        else:
            return super(TangoTineProxy, self).get_settings(option, cast)