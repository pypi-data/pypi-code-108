import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot

from bcanalyzer.gui.controllers.basic_controller import AbstractController
from bcanalyzer.gui.views.main_window import Main_GUI

from bcanalyzer.gui.models.processing_list_model import ProcessModel
from bcanalyzer.gui.models.processing_preview_model import PreviewModel
from bcanalyzer.common.io import im_load


class MainController(AbstractController):
    def __init__(self):
        super().__init__()
        self.proj_ext = ".json"
        self._app = QtWidgets.QApplication(sys.argv)
        self._view = Main_GUI()
        self.__init_models()
        self.__init_signals()

    def run(self):
        self._view.show()
        return self._app.exec()

    def __init_models(self):
        self._processing_model = ProcessModel()
        self._view.set_processing_list_model(
            self._processing_model.process_list_model)

        self._preview_model = PreviewModel()

    def __init_signals(self):
        self._view.dragEnterEvent = self.imageLabelDragEnterEvent
        self._view.dropEvent = self.imageLabelDropEvent

        # Menu
        self._view.export_all.connect(self.export_all)
        self._view.export_renders.connect(self.export_renders)
        self._view.export_stat.connect(self.export_stat)

        # ProcessList
        self._view.processing_list_widget.processing_list.clicked.connect(
            self._preview_model.change_to)

        self._view.processing_list_widget.delete_item.connect(
            self._processing_model.process_list_model.removeItem)

        # processing_widget
        self._preview_model.preview.connect(
            self._view.processing_widget.updateImage)
        self._preview_model.update_values.connect(
            self._view.processing_widget.setValues)
        self._view.processing_widget.sensitivity_slider.valueChanged.connect(
            self._preview_model.set_thresh_value)
        self._view.processing_widget.window_size_slider.valueChanged.connect(
            self._preview_model.set_win_size_value)

        self._view.processing_widget.global_params_updated.connect(
            self._preview_model.upd_global_params)

        self._preview_model.save_global_params.connect(
            self._processing_model.process_list_model.updGlobalData)

        self._view.processing_widget.save_local_params.connect(
            self._preview_model.upd_local_param)
        self._preview_model.save_local_params.connect(
            self._processing_model.process_list_model.updLocalData)
        self._view.processing_widget.remove_local_params.connect(
            self._preview_model.remove_local_param)
        self._preview_model.remove_local_params.connect(
            self._processing_model.process_list_model.removeLocalData)

    def __load_screen(self, next_screen: int):
        raise Exception(f"Can't find screen with num={next_screen}")

    def imageLabelDragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def imageLabelDropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        corrupted_files = []
        for f in files:
            if im_load(f) is not None:
                self._processing_model.process_list_model.add_item(f)
            else:
                corrupted_files.append(f)
        if len(corrupted_files) > 0:

            message_list_text = ""
            for f in corrupted_files:
                message_list_text += f
                message_list_text += "\n"
            QtWidgets.QMessageBox.warning(
                self._view, "Warning", f"The next images is corrupted: \n {message_list_text}")

    @pyqtSlot(str, str)
    def export_all(self, target_folder: str, target_file: str):
        row_count, process_sig, terminator_slot = self._processing_model.process_data(
            target_folder, target_file)
        if row_count == 0:
            return
        pd = self._view.show_progress_dialog(
            "Exporting all data", 0, row_count)

        process_sig.connect(pd.setValue)
        pd.canceled.connect(terminator_slot, Qt.DirectConnection)
        pd.show()

    @pyqtSlot(str)
    def export_renders(self, target_folder: str):
        row_count, process_sig, terminator_slot = self._processing_model.process_data(
            target_folder, None)
        if row_count == 0:
            return
        pd = self._view.show_progress_dialog(
            "Rendering", 0, row_count)

        process_sig.connect(pd.setValue)
        pd.canceled.connect(terminator_slot, Qt.DirectConnection)
        pd.show()

    @pyqtSlot(str)
    def export_stat(self, target_file: str):
        row_count, process_sig, terminator_slot = self._processing_model.process_data(
            None, target_file)
        if row_count == 0:
            return
        pd = self._view.show_progress_dialog(
            "Preparing statistics", 0, row_count)

        process_sig.connect(pd.setValue)
        pd.canceled.connect(terminator_slot, Qt.DirectConnection)
        pd.show()
