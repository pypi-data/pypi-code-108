
import os
import filetype
import pandas as pd
import numpy as np
import tempfile
import queue
import logging
import typing
import copy
from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QModelIndex, QThread, QObject, pyqtSlot, QItemSelectionModel
from PyQt5.QtGui import QPixmap
from bcanalyzer.image_processing.image_processor import process_image
from bcanalyzer.common.io import im_save


def build_target_path(origin_path, target_dir, suffix):
    basename = os.path.basename(origin_path)
    name, ext = os.path.splitext(basename)
    target_path = f"{name}_{suffix}{ext}"
    target_path = os.path.join(target_dir, target_path)
    return target_path


class Worker(QObject):
    progress = QtCore.pyqtSignal(int)
    finished = QtCore.pyqtSignal()

    def __init__(self, target_path: str, target_file: str, global_params: dict, data: pd.DataFrame):
        super().__init__()
        self.threads_num = 4
        self.base_path = target_path
        self.report_path = target_file
        self.data = data
        self._is_not_canceled = True
        self._global_params = global_params

    def run(self):
        if self.base_path is not None:
            os.makedirs(self.base_path, exist_ok=True)

        column_names = ['file_name',
                        'abs_threshold',
                        'Non-selected area, px',
                        'Selected area, px',
                        'Non-selected area, %',
                        'Selected area, %',
                        ]
        self._report = pd.DataFrame(columns=column_names)

        for i, row in self.data.iterrows():
            params = {}
            params = copy.deepcopy(self._global_params)
            # params['thre'] = self._global_params['thre']
            # params['win_size'] = self._global_params['win_size']
            # params['channel_r'] = self._global_params['channel_r']
            # params['channel_g'] = self._global_params['channel_g']
            # params['channel_b'] = self._global_params['channel_b']
            # params['is_single_object'] = self._global_params['is_single_object']
            # params['thre_abs'] = self._global_params['thre_abs']
            # params['use_abs_threshhold'] = self._global_params['use_abs_threshhold']
            # params['do_bg_removing'] = self._global_params['do_bg_removing']
            # params['do_otsu_thresholding'] = self._global_params['do_otsu_thresholding']

            if row.alg_params is not None:
                params['thre'] = row.alg_params['thre']
                params['win_size'] = row.alg_params['win_size']

            img_np, mask, res_meta = process_image(row.url, params)
            basename = os.path.basename(row.url)
            if self.base_path is not None:
                img_path = build_target_path(row.url, self.base_path, "RENDER")
                im_save(img_path, img_np)
                img_path = build_target_path(row.url, self.base_path, "MASK")
                mask4save = mask.copy()
                if mask4save.max() == 1:
                    mask4save *= 255
                im_save(img_path, mask4save)

            above_threshold_px = np.count_nonzero(mask)
            below_threshold_px = mask.size - above_threshold_px
            data_row = {
                'file_name': basename,
                'abs_threshold': res_meta['thre_abs'] / 255.0,
                'Non-selected area, px': below_threshold_px,
                'Selected area, px': above_threshold_px,
                'Non-selected area, %': below_threshold_px / mask.size,
                'Selected area, %': above_threshold_px / mask.size,
            }
            self._report = self._report.append(data_row, ignore_index=True)
            if self._is_not_canceled:
                self.progress.emit(i+1)
            else:
                break
        if self.report_path is not None:
            self._report.to_csv(self.report_path)
        self.finished.emit()

    def __process(self, info):
        index, row = info

        img_np, result = process_image(row.url)

        #cv2.imwrite(os.path.join(self.base_path, row.label), img_np)
        logging.debug(f"Exp was completed {row.label}")
        self.queue.task_done()
        self.result.emit(index, result)
        self.progress.emit(index)
        self.sem.release()

    @pyqtSlot()
    def cancel_processing(self):
        logging.debug("Cancel processing by User")
        self._is_not_canceled = False


class ProcessListModel(QtCore.QAbstractListModel):
    def __init__(self,
                 parent: QObject = None) -> None:
        super().__init__(parent)
        self._cache_dir = tempfile.TemporaryDirectory()
        self._global_params = {}
        self._global_params['thre'] = 50
        self._global_params['thre_abs'] = None
        self._global_params['win_size'] = 32
        self._global_params['channel_r'] = True
        self._global_params['channel_g'] = True
        self._global_params['channel_b'] = True
        self._global_params['is_single_object'] = False
        self._global_params['use_abs_threshhold'] = False
        self._global_params['do_bg_removing'] = False
        self._global_params['do_otsu_thresholding'] = False

        column_names = ['url',
                        'label',
                        'is_processed',
                        'alg_params',
                        'result']
        self._data = pd.DataFrame(columns=column_names)

    def add_item(self, url):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        if url in self._data['url'].values:
            return
        if not filetype.is_image(url):
            return
        data_row = {
            'url': url,
            'label': os.path.basename(url),
            'is_processed': False,
            'alg_params': None,
            'result': None
        }
        self._data = self._data.append(data_row, ignore_index=True)
        self.endInsertRows()

    def data(self, index: QModelIndex, role: int = ...):
        row = index.row()
        value = self._data.iloc[row]
        if role == QtCore.Qt.DisplayRole:
            is_unique_params = "*" if value.alg_params is not None else ""
            return is_unique_params + value.label
        # elif role == QtCore.Qt.DecorationRole:
        #    pixmap = QtGui.QPixmap(26, 26)
        #    if not value.is_processed:
        #        pixmap.fill(QtGui.QColor('red'))
        #    else:
        #        pixmap.fill(QtGui.QColor('green'))
        #    return QtGui.QIcon(pixmap)
        elif role == QtCore.Qt.UserRole:
            row = index.row()
            return self._global_params, value

        return None

    def reverse_processed(self, index: int):
        self._data.iloc[index].is_processed = not self._data.iloc[index].is_processed

    def is_processed(self, index: int):
        return self._data.iloc[index].is_processed

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data.index)

    def get_raw_data(self):
        return self._data

    def get_image_path(self, index: int) -> typing.Union[str, None]:
        return self._data.iloc[index].url

    def on_result_listener(self, index: int, result):
        self._data.iloc[index].url = result

    @pyqtSlot(QModelIndex, dict)
    def updLocalData(self, index: QModelIndex, value: dict):
        row = index.row()
        # = {'thre': 0.7}  #
        self._data.at[row, "alg_params"] = value
        self.dataChanged.emit(index, index)

    @pyqtSlot(QModelIndex)
    def removeLocalData(self, index: QModelIndex):
        row = index.row()
        self._data.at[row, "alg_params"] = None
        self.dataChanged.emit(index, index)

    @pyqtSlot(dict)
    def updGlobalData(self, value: dict):
        self._global_params.update(value)

    @pyqtSlot(QModelIndex, QItemSelectionModel)
    def removeItem(self, index: QModelIndex, selection_model: QItemSelectionModel):
        if selection_model.hasSelection():
            self.beginRemoveRows(index,
                                 selection_model.selectedRows()[0].row(),
                                 selection_model.selectedRows()[-1].row())
            list_to_delete = []
            for row_ind in selection_model.selectedRows():
                list_to_delete.append(self._data.index[row_ind.row()])
            self._data.drop(list_to_delete, inplace=True)
        else:
            self.beginRemoveRows(index, index.row(), index.row())
            self._data.drop(self._data.index[index.row()], inplace=True)
            self.endRemoveRows()


class ProcessModel(QObject):
    def __init__(self):
        super().__init__()
        self.process_list_model: ProcessListModel = ProcessListModel()

    def get_processed_image(self, index: int) -> typing.Union[QPixmap, None]:
        """
        :param index:
        :type index:
        :param tab_index: Result of QTabWidget.currentIndex() . tab_index == 0 is first tab
        :type tab_index:
        :return:
        :rtype:
        """
        processed_path = self.process_list_model.get_image_path(
            self, index)
        if processed_path:
            qpm = QPixmap(processed_path)
            return qpm
        return None

    def process_data(self, target_folder=None, target_file=None):
        self._q = queue.Queue()
        self._thread = QThread()
        self._worker = Worker(
            target_folder,
            target_file,
            self.process_list_model._global_params,
            self.process_list_model.get_raw_data())
        self._worker.moveToThread(self._thread)

        # connect_signals_and_slots
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished
        self._thread.start()

        return self.process_list_model.rowCount(), self._worker.progress, self._worker.cancel_processing
