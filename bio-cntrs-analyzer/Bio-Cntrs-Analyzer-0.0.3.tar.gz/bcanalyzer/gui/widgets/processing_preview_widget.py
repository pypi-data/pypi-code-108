from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QPushButton, QWidget, QSizePolicy
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtWidgets import QLabel, QCheckBox
from PyQt5.QtGui import QPixmap, QImage, QResizeEvent

from bcanalyzer.gui.widgets.extended_slider_widget import ExtendedSliderWidget
import logging

logger = logging.Logger(__file__)


class ProcessingPreviewWidget(QWidget):
    global_params_updated = pyqtSignal(dict)
    save_local_params = pyqtSignal(dict)
    remove_local_params = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # self._processing_model = processing_model
        self._curent_image = None
        self.initUI()

    def initUI(self):
        self._root_layout = QVBoxLayout()
        # 1. Common settings
        self.common_settings_group = QGroupBox(
            "Common settings")
        self.common_settings_group_layout = QVBoxLayout()
        self.common_settings_group.setLayout(self.common_settings_group_layout)
        self._root_layout.addWidget(self.common_settings_group)

        # 1.1 Channel Selection
        self.channel_group = QGroupBox("Select color channels for processing")
        self.channel_group_layout = QHBoxLayout()

        self.red_channel_check_box = QCheckBox()
        self.red_channel_check_box.setText("RED")
        self.red_channel_check_box.setChecked(True)
        self.channel_group_layout.addWidget(self.red_channel_check_box)
        self.red_channel_check_box.released.connect(
            self.global_param_wigdet_released)

        self.green_channel_check_box = QCheckBox()
        self.green_channel_check_box.setText("GREEN")
        self.green_channel_check_box.setChecked(True)
        self.channel_group_layout.addWidget(self.green_channel_check_box)
        self.green_channel_check_box.released.connect(
            self.global_param_wigdet_released)

        self.blue_channel_check_box = QCheckBox()
        self.blue_channel_check_box.setText("BLUE")
        self.blue_channel_check_box.setChecked(True)
        self.channel_group_layout.addWidget(self.blue_channel_check_box)
        self.blue_channel_check_box.released.connect(
            self.global_param_wigdet_released)

        self.channel_group.setLayout(self.channel_group_layout)

        self.common_settings_group_layout.addWidget(self.channel_group)

        # 1.2 Global processing settings
        self._top_gl_settings_layout = QHBoxLayout()
        self.common_settings_group_layout.addLayout(
            self._top_gl_settings_layout)

        # 1.2.1 Use BG removing
        self.do_bg_removing = QCheckBox(self)
        self.do_bg_removing.setObjectName("do_bg_removing")
        self.do_bg_removing.setText("Apply BG removal")
        self._top_gl_settings_layout.addWidget(self.do_bg_removing)
        self.do_bg_removing.released.connect(
            self.global_param_wigdet_released)

        # 1.2.2 Automatic thresholding
        self.do_otsu_thresholding = QCheckBox(self)
        self.do_otsu_thresholding.setObjectName("do_otsu_thresholding")
        self.do_otsu_thresholding.setText("Automatic threshold")
        self._top_gl_settings_layout.addWidget(self.do_otsu_thresholding)
        self.do_otsu_thresholding.stateChanged.connect(
            self.do_otsu_thresholding_state_changed)
        self.do_otsu_thresholding.released.connect(
            self.global_param_wigdet_released)

        # 1.2.3 Use abs threshold

        self.use_abs_threshold = QCheckBox(self)
        self.use_abs_threshold.setObjectName("use_abs_threshhold")
        self.use_abs_threshold.setText("Freeze threshold")
        self._top_gl_settings_layout.addWidget(self.use_abs_threshold)
        self.use_abs_threshold.stateChanged.connect(
            self.use_abs_threshold_state_changed)
        self.use_abs_threshold.released.connect(
            self.global_param_wigdet_released)

        # 1.2.4 Single object

        self.one_contour_only = QCheckBox(self)
        self.one_contour_only.setObjectName("one_contour_only")
        self.one_contour_only.setText("Single oblect segmentation")
        self._top_gl_settings_layout.addWidget(self.one_contour_only)
        self.one_contour_only.released.connect(
            self.global_param_wigdet_released)

        # 2. Preview

        self._image_label = QLabel(self)
        self._image_label.setText("")
        self._image_label.setAlignment(Qt.AlignHCenter)
        self._image_label.setObjectName("image_label")
        self._image_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._root_layout.addWidget(self._image_label)

        # 3. Local settings

        self.local_settings_group_layout = QVBoxLayout()
        self.local_settings_group = QGroupBox()
        self.local_settings_group.setTitle("Algorithm parameters")
        self.local_settings_group.setLayout(self.local_settings_group_layout)
        self._root_layout.addWidget(self.local_settings_group)

        self.sensitivity_slider = ExtendedSliderWidget("Sensitivity")
        self.sensitivity_slider.set_range(0, 100)
        self.window_size_slider = ExtendedSliderWidget("Resolution")
        self.window_size_slider.set_range(10, 100)

        self.local_settings_group_layout.addWidget(self.sensitivity_slider)
        self.local_settings_group_layout.addWidget(self.window_size_slider)

        self.button_layout = QHBoxLayout()
        self.local_settings_group_layout.addLayout(self.button_layout)
        self.accept4all_button = QPushButton("Apply to all")
        self.accept4all_button.clicked.connect(self.accept4all_button_clicked)
        self.accept4current_button = QPushButton("Apply to current")
        self.accept4current_button.clicked.connect(
            self.accept4current_button_clicked)
        self.cancel_individual_button = QPushButton("Remove individual")
        self.cancel_individual_button.clicked.connect(
            self.cancel_individual_button_clicked)
        self.button_layout.addWidget(self.accept4all_button)
        self.button_layout.addWidget(self.accept4current_button)
        self.button_layout.addWidget(self.cancel_individual_button)

        # self._root_layout.addStretch()
        self.setLayout(self._root_layout)

    def updateImage(self, image: QImage):
        self._curent_image = image.scaled(
            1920, 1080, Qt.KeepAspectRatio)
        self.__update_image()

    def __update_image(self):
        if self._curent_image is None:
            return
        try:
            image = self._curent_image.scaled(
                self._image_label.width()*0.95,
                self._image_label.height()*0.95,
                Qt.KeepAspectRatio
            )
            self._image_label.setPixmap(QPixmap(image))
        except Exception as e:
            print(str(e))

    def resizeEvent(self,  e: QResizeEvent):
        super().resizeEvent(e)
        self.__update_image()

    @pyqtSlot(bool)
    def accept4all_button_clicked(self, checked: bool):
        glob_param_values = {}
        glob_param_values['thre'] = self.sensitivity_slider.value()
        glob_param_values['win_size'] = self.window_size_slider.value()
        self.global_params_updated.emit(glob_param_values)

    @pyqtSlot(bool)
    def accept4current_button_clicked(self, checked: bool):
        param_values = {}
        param_values['thre'] = self.sensitivity_slider.value()
        param_values['win_size'] = self.window_size_slider.value()
        self.save_local_params.emit(param_values)

    @pyqtSlot(bool)
    def cancel_individual_button_clicked(self, checked: bool):
        self.remove_local_params.emit()

    @pyqtSlot(int)
    def use_abs_threshold_state_changed(self, state: int):
        if state == Qt.CheckState.Checked:
            self.do_otsu_thresholding.setChecked(False)

    @pyqtSlot(int)
    def do_otsu_thresholding_state_changed(self, state: int):
        if state == Qt.CheckState.Checked:
            self.use_abs_threshold.setChecked(False)

    @pyqtSlot()
    def global_param_wigdet_released(self):
        glob_param_values = {}
        glob_param_values['channel_r'] = self.red_channel_check_box.isChecked()
        glob_param_values['channel_g'] = self.green_channel_check_box.isChecked()
        glob_param_values['channel_b'] = self.blue_channel_check_box.isChecked()
        glob_param_values['is_single_object'] = self.one_contour_only.isChecked()
        glob_param_values['do_bg_removing'] = self.do_bg_removing.isChecked()

        glob_param_values['use_abs_threshhold'] = self.use_abs_threshold.isChecked()
        glob_param_values['do_otsu_thresholding'] = (
            self.do_otsu_thresholding.isChecked())

        self.global_params_updated.emit(glob_param_values)

    @ pyqtSlot(dict)
    def setValues(self, values):

        sensitivity = values.get('thre', 50)
        self.sensitivity_slider.set_value(sensitivity)

        window_size = values.get('win_size', 20)
        self.window_size_slider.set_value(window_size)

        channel_r = values.get('channel_r', True)
        self.red_channel_check_box.setChecked(channel_r)

        channel_g = values.get('channel_g', True)
        self.green_channel_check_box.setChecked(channel_g)

        channel_b = values.get('channel_b', True)
        self.blue_channel_check_box.setChecked(channel_b)

        is_single_object = values.get('is_single_object', False)
        self.one_contour_only.setChecked(is_single_object)

        thre_abs = values.get("thre_abs", '')
        self.use_abs_threshold.setText(
            f"Freeze threshold ({thre_abs/(255):.4f})")

        do_bg_removing = values.get('do_bg_removing', False)
        self.do_bg_removing.setChecked(do_bg_removing)

        do_otsu_thresholding = values.get('do_otsu_thresholding', False)
        self.do_otsu_thresholding.setChecked(do_otsu_thresholding)
