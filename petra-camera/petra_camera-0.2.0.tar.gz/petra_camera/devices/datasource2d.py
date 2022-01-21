# ----------------------------------------------------------------------
# Author:        yury.matveev@desy.de
# ----------------------------------------------------------------------

"""
This class provides data from camera, keeps, loads, saves camera settings etc
"""

import importlib
import logging
import threading
import time
import json
import math
import PyTango

import scipy.ndimage.measurements as scipymeasure
import numpy as np

from skimage.feature import peak_local_max

from petra_camera.utils.errors import report_error
from petra_camera.utils.functions import FWHM
from petra_camera.main_window import APP_NAME

from PyQt5 import QtCore

logger = logging.getLogger(APP_NAME)


# ----------------------------------------------------------------------
class DataSource2D(QtCore.QObject):
    """
    """
    new_frame = QtCore.pyqtSignal()

    update_roi_statistics = QtCore.pyqtSignal()

    update_peak_search = QtCore.pyqtSignal()

    got_error = QtCore.pyqtSignal(str)

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        """
        """
        super(DataSource2D, self).__init__(parent)

        self._parent = parent
        self.settings = parent.settings

        self.device_id = ''
        self._base_id = ''

        self.auto_screen = False

        self._device_proxy = None
        self._worker = None  # thread, which reads from camera

        self._frame_mutex = QtCore.QMutex()  # sync access to frame
        self._last_frame = np.zeros((1, 1))  # keeps last read frame

        self.got_first_frame = False

        self._state = "idle"
        self.fps_limit = 1

        self.set_new_image = False

        # picture levels settings
        self.levels = []
        self.level_mode = 'lin'

        # ROIs parameters and data
        self.rois = []
        self.rois_data = []
        self._counter_roi = 0

        # ROIs parameters and data
        self.markers = []

        # peak search parameters and data
        self.peak_search = {}
        self.peak_coordinates = []

        self._dark_image = None
        self.subtract_dark_image = False

    # ----------------------------------------------------------------------
    def new_device_proxy(self, name, auto_screen):
        """

        :param name: str, camera name to be loaded from config
        :param auto_screen: bool, is generally moving screens is allowed
        :return: bool, success or not
        """

        for device in self.settings.get_nodes('camera_viewer', 'camera'):
            if device.getAttribute('name') == name:

                self._base_id = name

                try:
                    proxyClass = device.getAttribute("proxy")
                    logger.info("Loading device proxy {}...".format(proxyClass))

                    module = importlib.import_module("petra_camera.devices.{}".format(proxyClass.lower()))
                    self._device_proxy = getattr(module, proxyClass)(device)

                    self.device_id = self._base_id + self._device_proxy.file_name

                    # reset flags and variables
                    self.got_first_frame = False
                    self._last_frame = np.zeros((1, 1))

                    # load LUT and levels settings
                    lut = self.get_settings('lut', str)
                    if lut != '':
                        self.levels = json.loads(lut)
                    else:
                        self.levels = {'gradient': {'mode': 'rgb',
                                                    'ticks': [(0.0, (0, 0, 0, 255)), (1.0, (255, 255, 255, 255))],
                                                    'ticksVisible': True},
                                       'levels': (0, 255.0),
                                       'mode': 'mono',
                                       'auto_levels': True}

                    self.level_mode = self.get_settings('level_mode', str)
                    if self.level_mode == '':
                        self.level_mode = 'lin'

                    self.auto_screen = self.get_settings('auto_screen', bool)

                    # load ROI params
                    self.rois = []
                    self.rois_data = []

                    # TODO find a better solution for Sardana counter....
                    self._counter_roi = self.get_settings('counter_roi', int)
                    self._counter_param = self.get_settings('counter_roi', int)

                    for ind in range(self.get_settings('num_rois', int)):
                        self.rois.append({'x': self.get_settings('roi_{}_x'.format(ind), int),
                                          'y': self.get_settings('roi_{}_y'.format(ind), int),
                                          'w': self.get_settings('roi_{}_w'.format(ind), int),
                                          'h': self.get_settings('roi_{}_h'.format(ind), int),
                                          'bg': self.get_settings('roi_{}_bg'.format(ind), int),
                                          'visible': self.get_settings('roi_{}_visible'.format(ind), bool),
                                          'mark': self.get_settings('roi_{}_mark'.format(ind), str),
                                          'color': self.get_settings('roi_{}_color'.format(ind), str)})

                        if ind == self._counter_roi:
                            for setting in ['x', 'y', 'w', 'h']:
                                self.save_settings('counter_{}'.format(setting), self.rois[ind][setting])

                        self.rois_data.append(dict.fromkeys(['max_x', 'max_y', 'max_v',
                                                             'min_x', 'min_y', 'min_v',
                                                             'com_x', 'com_y', 'com_v',
                                                             'fwhm_x', 'fwhm_y', 'sum']))

                    # load markers params
                    self.markers = []
                    for ind in range(self.get_settings('num_markers', int)):
                        self.markers.append({'x': self.get_settings('marker_{}_x'.format(ind), int),
                                             'y': self.get_settings('marker_{}_y'.format(ind), int),
                                             'visible': self.get_settings('marker_{}_visible'.format(ind), bool),
                                             'color': self.get_settings('marker_{}_color'.format(ind), str)})

                    # load peak search params
                    self.peak_search = {'search': False, #TODO: need solution for wrong settings!
                                        'search_mode': self.get_settings('peak_search_mode', bool),
                                        'rel_threshold': self.get_settings('peak_rel_threshold', int),
                                        'abs_threshold': self.get_settings('peak_abs_threshold', int)}

                    if self.peak_search['rel_threshold'] == 0:
                        self.peak_search['rel_threshold'] = 80

                    if self.peak_search['abs_threshold'] == 0:
                        self.peak_search['abs_threshold'] = 16000

                    # if Tango server for camera already acquiring - start data thread
                    if self._device_proxy.is_running():
                        self.start(auto_screen)

                    return True, ''

                except PyTango.DevFailed as ex:
                    logger.error(ex.args[0].desc)
                    return False, ex.args[0].desc

                except Exception as ex:
                    logger.error(ex)
                    return False, ex.__repr__()

        return False, 'Cannot find camera in config'

    # ----------------------------------------------------------------------
    def close_camera(self):
        """
        safe close for camera (e.g. to kill all threads)
        :return: None
        """

        if self._device_proxy is not None:
            self._device_proxy.close_camera()

    # ----------------------------------------------------------------------
    def start(self, auto_screen):
        """

        :param auto_screen: is generally moving screens is allowed
        :return:
        """
        self._reset_worker()
        self._worker.start()

        if self.auto_screen and auto_screen:
            self._device_proxy.move_motor(True)

        logger.debug('CameraDevice started')

    # ----------------------------------------------------------------------
    def stop(self, auto_screen):
        """

        :param auto_screen: is generally moving screens is allowed
        :return:
        """
        if self._state != 'idle':
            self._state = "abort"

        while self._state != 'idle':
            time.sleep(1e-3)

        if self.auto_screen and auto_screen:
            self._device_proxy.move_motor(False)

        logger.debug('CameraDevice stopped')

    # ----------------------------------------------------------------------
    # --------------------- Data acquiring thread---------------------------
    # ----------------------------------------------------------------------
    def _reset_worker(self):
        """
        """
        if self._worker:
            self._state = 'abort'
            self._worker.join()

        self._worker = threading.Thread(target=self.run)

    # ----------------------------------------------------------------------
    def run(self):
        """
        main thread cycle
        :return:
        """
        if self._start_acquisition():

            while self._state == "running":

                frame = self._device_proxy.maybe_read_frame()

                if frame is not None:
                    self.got_first_frame = True
                    self._last_frame = frame
                    self.new_frame.emit()

                    self.calculate_roi_statistics()
                    self.find_peaks()

                if self._device_proxy.error_flag:
                    self.got_error.emit(str(self._device_proxy.error_msg))
                    self._state = "abort"

                time.sleep(1 / self.fps_limit)  # to decrease processor load

            logger.info("Closing {}...".format(self.device_id))

            if self._device_proxy:
                self._device_proxy.stop_acquisition()

        self._state = "idle"

    # ----------------------------------------------------------------------
    def _start_acquisition(self):
        """
        tries to start camera
        :return: bool, success or not
        """

        if self._device_proxy:

            try:
                if self._device_proxy.start_acquisition():
                    self._state = "running"
                    return True
                else:
                    return False

            except Exception as err:
                report_error(err, self._parent)
                return False

    # ----------------------------------------------------------------------
    # ---------------------- Frame functionality ---------------------------
    # ----------------------------------------------------------------------
    def get_frame(self):
        """
        returns last frame after applying dark image and level mode
        :return: 2d np.array
        """
        if self.subtract_dark_image and self._dark_image is not None:
            try:
                invalid_idx = self._last_frame < self._dark_image
                frame = self._last_frame - self._dark_image
                frame[invalid_idx] = 0
            except:
                self.subtract_dark_image = False
                self._dark_image = None
                frame = self._last_frame
        else:
            frame = self._last_frame

        if self.level_mode == 'sqrt':
            frame = np.sqrt(np.abs(frame))
        elif self.level_mode == 'log':
            frame = np.log(np.maximum(1, frame))

        if np.max(frame) == 0:
            return np.ones_like(frame)
        else:
            return frame

    # ----------------------------------------------------------------------
    # ------------------- Levels functionality ----------------------------
    # ----------------------------------------------------------------------
    def level_setting_change(self, lut_state):
        """

        :param lut_state: dict, levels settings
        :return: None
        """
        lut_state['levels'] = (int(lut_state['levels'][0]), int(lut_state['levels'][1]))
        self.levels = lut_state
        self.save_settings('lut', json.dumps(lut_state))
        if self.got_first_frame:
            self.new_frame.emit()

    # ----------------------------------------------------------------------
    def set_new_level_mode(self, mode):
        """

        :param mode: srt, mode: "lin", "sqrt", "log"
        :return:
        """
        if self.level_mode != mode:
            self.level_mode = mode
            self.save_settings('level_mode', mode)
            if self.got_first_frame:
                self.new_frame.emit()

    # ----------------------------------------------------------------------
    # ------------------- Markers functionality ----------------------------
    # ----------------------------------------------------------------------
    def _save_marker_settings(self):
        """

        :return: drops markers to settings
        """
        num_markers = len(self.markers)
        self.save_settings('num_markers', num_markers)
        for ind, marker in enumerate(self.markers):
            for param in ['x', 'y', 'visible', 'color']:
                self.save_settings('marker_{}_{}'.format(ind, param), marker[param])

    # ----------------------------------------------------------------------
    def set_marker_value(self, marker_id, setting, value):
        """

        :param marker_id: int
        :param setting: str, setting name
        :param value: new value
        :return:
        """
        self.markers[marker_id][setting] = value
        self.save_settings('marker_{}_{}'.format(marker_id, setting), value)

    # ----------------------------------------------------------------------
    def append_marker(self):
        """

        :return: None
        """
        self.markers.append({'x': 0, 'y': 0, 'visible': True, 'color': self.settings.option('colors', 'marker')})
        self._save_marker_settings()

    # ----------------------------------------------------------------------
    def delete_marker(self, index):
        """

        :param index: int, maker to be deleted
        :return:
        """

        del self.markers[index]
        self._save_marker_settings()

    # ----------------------------------------------------------------------
    # ----------------------- ROI functionality ----------------------------
    # ----------------------------------------------------------------------
    def _save_roi_settings(self):
        """
        drops ROIs to settings
        :return:
        """
        num_rois = len(self.rois)
        self.save_settings('num_rois', num_rois)
        for ind, roi in enumerate(self.rois):
            for param in ['x', 'y', 'w', 'h', 'bg', 'visible', 'mark']:
                self.save_settings('roi_{}_{}'.format(ind, param), roi[param])

    # ----------------------------------------------------------------------
    def set_roi_value(self, roi_id, setting, value):
        """

        :param roi_id: int
        :param setting: str, setting name
        :param value:new value
        :return:
        """
        self.rois[roi_id][setting] = value
        self.save_settings('roi_{}_{}'.format(roi_id, setting), value)

        if roi_id == self._counter_roi:
            if setting in ['x', 'y', 'w', 'h']:
                self.save_settings('counter_{}'.format(setting), value)

    # ----------------------------------------------------------------------
    def num_roi(self):
        """
        return how many ROIs are there
        :return: int
        """
        return len(self.rois)

    # ----------------------------------------------------------------------
    def get_counter_roi(self):
        """

        :return: int, which ROIs selected as counter for Sardana
        """
        return self._counter_roi

    # ----------------------------------------------------------------------
    def set_counter_roi(self, value):
        """
        set new ROIs as counter for Sardana
        :param value: int
        :return:
        """
        self._counter_roi = value
        self.save_settings('counter_roi', value)
        for setting in ['x', 'y', 'w', 'h']:
            if len(self.rois):
                self.save_settings('counter_{}'.format(setting), self.rois[value][setting])

    # ----------------------------------------------------------------------
    def get_active_roi_value(self, value):
        """

        :param value: str, name of parameter
        :return:
        """
        return self.rois_data[self._counter_roi][value]

    # ----------------------------------------------------------------------
    def add_roi(self):
        """

        :return: None
        """
        self.rois.append({'x': 0, 'y': 0, 'w': 50, 'h': 50, 'bg': 0, 'visible': True, 'mark': '',
                          'color': self.settings.option('colors', 'roi')})
        self.rois_data.append(dict.fromkeys(['max_x', 'max_y', 'max_v',
                                             'min_x', 'min_y', 'min_v',
                                             'com_x', 'com_y', 'com_v',
                                             'fwhm_x', 'fwhm_y', 'sum']))

        self._save_roi_settings()

    # ----------------------------------------------------------------------
    def delete_roi(self, index):
        """

        :param index: roi to be deleted
        :return: None
        """

        del self.rois[index]
        del self.rois_data[index]
        self._save_roi_settings()

    # ----------------------------------------------------------------------
    def calculate_roi_statistics(self):
        """
        calculates ROIs statistics after new frame comes of ROIs parameter changed

        :return: None
        """
        if self._last_frame is None:
            return

        for info, data in zip(self.rois, self.rois_data):
            if info['visible']:

                image_size = self.get_picture_clip()
                _image_x_pos, _image_y_pos = image_size[0], image_size[1]
                x, y, w, h = int(info['x'] - _image_x_pos), int(info['y'] - _image_y_pos), int(info['w']), int(info['h'])

                array = self._last_frame[x:x + w, y:y + h]
                if array != []:
                    array[array < info['bg']] = 0  # All low values set to 0

                    roi_sum = np.sum(array)

                    try:
                        roiExtrema = scipymeasure.extrema(array)  # all in one!
                    except:
                        roiExtrema = (0, 0, (0, 0), (0, 0))

                    roi_max = (int(roiExtrema[3][0] + x + _image_x_pos), int(roiExtrema[3][1] + y + _image_y_pos))
                    roi_min = (int(roiExtrema[2][0] + x + _image_x_pos), int(roiExtrema[2][1] + y + _image_y_pos))

                    try:
                        roi_com = scipymeasure.center_of_mass(array)
                    except:
                        roi_com = (0, 0)

                    if math.isnan(roi_com[0]) or math.isnan(roi_com[1]):
                        roi_com = (0, 0)

                    roi_com = (int(roi_com[0] + x + _image_x_pos), int(roi_com[1] + y + _image_y_pos))

                    try:
                        intensity_at_com = self._last_frame[int(round(roi_com[0])), int(round(roi_com[1]))]
                    except:
                        intensity_at_com = [0, 0]

                    roi_FWHM = (FWHM(np.sum(array, axis=1)), FWHM(np.sum(array, axis=0)))

                    data['max_x'], data['max_y'] = roi_max
                    data['max_v'] = np.round(roiExtrema[1], 3)

                    data['min_x'], data['min_y'] = roi_min
                    data['min_v'] = np.round(roiExtrema[0], 3)

                    data['com_x'], data['com_y'] = roi_com
                    data['com_v'] = np.round(intensity_at_com, 3)

                    data['fwhm_x'], data['fwhm_y'] = roi_FWHM
                    data['sum'] = np.round(roi_sum, 3)

        self.update_roi_statistics.emit()

    # ----------------------------------------------------------------------
    # ------------- Peak search functionality ------------------------------
    # ----------------------------------------------------------------------
    def set_peak_search_value(self, setting, value):
        """

        :param setting: str, parameter name
        :param value: new value
        :return:
        """
        self.peak_search[setting] = value
        self.save_settings('peak_{}'.format(setting), value)
        self.find_peaks()

    # ----------------------------------------------------------------------
    def find_peaks(self):
        """
        finds peaks after new frame comes of parameter changed
        :return: None
        """
        if self.peak_search['search']:
            try:
                if self.peak_search['search_mode']:
                    coordinates = peak_local_max(self._last_frame,
                                                 threshold_rel=self.peak_search['rel_threshold'] / 100)
                else:
                    coordinates = peak_local_max(self._last_frame,
                                                 threshold_abs=self.peak_search['abs_threshold'])

                if len(coordinates) > 100:
                    report_error(
                        'Too many ({}) peaks found. Show first 100. Adjust the threshold'.format(len(coordinates)),
                        self, True)
                    self.peak_coordinates = coordinates[:100]
            except:
                self.peak_coordinates = ()
        else:
            self.peak_coordinates = ()

        self.update_peak_search.emit()

    # ----------------------------------------------------------------------
    # ---------------Communication with camera worker-----------------------
    # ----------------------------------------------------------------------
    def get_settings(self, setting, cast):
        """

        :param setting: str, settings name
        :param cast: expected type
        :return: cast(value), if there is no device proxy - None
        """

        if self._device_proxy:
            if setting == 'FPS':
                self.fps_limit = max(1, self._device_proxy.get_settings('FPS', int))
                return self.fps_limit
            else:
                return self._device_proxy.get_settings(setting, cast)
        else:
            return None

    # ----------------------------------------------------------------------
    def save_settings(self, setting, value):
        """

        :param setting: str, settings name
        :param value: value to save
        :return:
        """
        if self._device_proxy:
            if setting == 'FPS':
                self.fps_limit = value

            self._device_proxy.save_settings(setting, value)

    # ----------------------------------------------------------------------
    def is_running(self):
        """

        :return: bool, if there is no device proxy - None
        """
        if self._device_proxy is None:
            return None
        else:
            return self._device_proxy.is_running()

    # ----------------------------------------------------------------------
    def has_motor(self):
        """

        :return: bool
        """
        return self._device_proxy.has_motor()

    # ----------------------------------------------------------------------
    def move_motor(self, new_state=None):
        """

        :param new_state: True - move screen in, False - out
        :return:
        """

        self._device_proxy.move_motor(new_state)

    # ----------------------------------------------------------------------
    def motor_position(self):
        """

        :return: bool, True - move in, False - out; if there is no device proxy - None
        """
        if self._device_proxy is not None:
            return self._device_proxy.motor_position()

        return None

    # ----------------------------------------------------------------------
    def has_counter(self):
        """

        :return: bool, there is a corresponding Tango server or not
        """
        if self._device_proxy is not None:
            return self._device_proxy.has_counter()

        return False

    # ----------------------------------------------------------------------
    def get_counter(self):
        """

        :return: name of currently selected parameter in server
        """
        if self._device_proxy is not None:
            return self._device_proxy.get_counter()

        return ""

    # ----------------------------------------------------------------------
    def set_counter(self, value):
        """
        set new paramater in server
        :param value: str, parameter name
        :return:
        """
        self._device_proxy.set_counter(value)

    # ----------------------------------------------------------------------
    def visible_layouts(self):

        return self._device_proxy.visible_layouts

    # ----------------------------------------------------------------------
    def set_picture_clip(self, size):

        self.set_new_image = True
        self.save_settings('view_x', size[0])
        self.save_settings('view_y', size[1])
        self.save_settings('view_w', size[2])
        self.save_settings('view_h', size[3])
        self._device_proxy.set_picture_clip(size)

    # ----------------------------------------------------------------------
    def get_picture_clip(self):
        """

        :return: (x, y, w, h), where x, y - top left corner coordinates
        """
        return self._device_proxy.get_picture_clip()

    # ----------------------------------------------------------------------
    def get_max_picture_size(self):
        """

        :return: int, int, max frame width and heigth
        """
        return self._device_proxy.get_settings('max_width', int), self._device_proxy.get_settings('max_height', int)

    # ----------------------------------------------------------------------
    def get_reduction(self):
        """

        :return: int, reduction of camera resolution rate
        """
        return self._device_proxy.get_reduction()

    # ----------------------------------------------------------------------
    def set_reduction(self, value):

        self._device_proxy.set_reduction(value)
        self.set_new_image = True
        if self.got_first_frame:
            self.new_frame.emit()

    # ----------------------------------------------------------------------
    def set_auto_screen(self, state):
        """
         switch on or off screen motor
        :param state: bool
        :return:
        """
        self.auto_screen = state
        self.save_settings('auto_screen', state)

    # ----------------------------------------------------------------------
    # -------------------- Dark image functionality ------------------------
    # ----------------------------------------------------------------------
    def set_dark_image(self):
        """
        saves current image as dark image
        :return:
        """
        self._dark_image = self._last_frame

    # ----------------------------------------------------------------------
    def load_dark_image(self, file_name):
        """
        load dark image from file
        :param file_name:
        :return:
        """
        self._dark_image = np.load(file_name)

    # ----------------------------------------------------------------------
    def save_dark_image(self, file_name):
        """
        saves current image to the file
        :param file_name:
        :return:
        """
        np.save(file_name, self._dark_image)

    # ----------------------------------------------------------------------
    def has_dark_image(self):
        """

        :return: bool
        """
        return self._dark_image is not None

    # ----------------------------------------------------------------------
    def toggle_dark_image(self, state):
        """

        :param state: bool
        :return:
        """
        if self._dark_image is not None:
            self.subtract_dark_image = state

        if self.got_first_frame:
            self.new_frame.emit()