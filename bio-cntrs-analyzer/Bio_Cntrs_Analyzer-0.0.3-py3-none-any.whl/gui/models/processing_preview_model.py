import numpy as np

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QModelIndex, QObject
from PyQt5.QtGui import QImage

from bcanalyzer.image_processing.image_processor import process_image


class PreviewModel(QObject):
    preview = pyqtSignal(QImage)
    update_values = pyqtSignal(dict)

    save_local_params = pyqtSignal(QModelIndex, dict)
    save_global_params = pyqtSignal(dict)
    remove_local_params = pyqtSignal(QModelIndex)

    def __init__(self):
        super().__init__()
        self._im_url = None
        self._params = None
        self._current_model_index = None

    def update_processing(self, is_user=False):
        if self._current_model_index is None:
            return
        global_params, info = self._current_model_index.data(Qt.UserRole)
        im_url = info.url

        # self.update_values.emit(self._params)
        img_np, res, res_meta = process_image(
            im_url, self._params, force_q_th=is_user)

        self._params['thre_abs'] = res_meta["thre_abs"]
        self._params['thre'] = res_meta["thre"]
        self.update_values.emit(self._params)

        img_np = np.require(img_np, np.uint8, 'C')
        height, width, channel = img_np.shape
        bytesPerLine = 3 * width
        convertToQtFormat = QImage(
            img_np.data, width, height, bytesPerLine, QImage.Format_BGR888)
        convertToQtFormat.ndarray = img_np
        self.preview.emit(convertToQtFormat)

    def _update_params(self, item: QModelIndex):
        global_params, info = item.data(Qt.UserRole)
        params = {}
        params.update(global_params)
        if info.alg_params is not None:
            params['thre'] = info.alg_params['thre']
            params['win_size'] = info.alg_params['win_size']
            params['thre_abs'] = info.alg_params['thre_abs']
        self._params = params

    @ pyqtSlot(QModelIndex)
    def change_to(self, item: QModelIndex):
        self._current_model_index = item
        self._update_params(self._current_model_index)
        self.update_processing()

    @ pyqtSlot(dict)
    def upd_global_params(self, value: dict) -> bool:
        if self._params is None:
            return False
        self._params.update(value)
        self.update_processing(is_user=True)
        self.save_global_params.emit(self._params)

    @ pyqtSlot(int)
    def set_thresh_value(self, value: int):
        if self._params is None:
            return False
        self._params['thre'] = value
        self.update_processing(is_user=True)

    @ pyqtSlot(int)
    def set_win_size_value(self, value: int):
        if self._params is None:
            return False
        self._params['win_size'] = value
        self.update_processing(is_user=True)

    def upd_local_param(self, params):
        if self._current_model_index is None:
            return False
        self.save_local_params.emit(self._current_model_index, params)

    @ pyqtSlot()
    def remove_local_param(self):
        if self._current_model_index is None:
            return False
        self.remove_local_params.emit(self._current_model_index)
        self._update_params(self._current_model_index)
        self.update_processing()
