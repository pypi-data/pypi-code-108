from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, \
    QFileDialog, QCheckBox, QPushButton, QProgressDialog, \
    QSizePolicy, QTabWidget, QComboBox, QLabel, QMessageBox, \
    QDoubleSpinBox
from PyQt5.QtCore import QCoreApplication, QThread, QLocale, Qt

import SLIX._cmd.VisualizeParameter
from .ImageWidget import ImageWidget, convert_numpy_to_qimage
from .ThreadWorkers.Visualization import FOMWorker, VectorWorker
import numpy
import matplotlib
import os
from matplotlib import pyplot as plt

__all__ = ['VisualizationWidget']


class VisualizationWidget(QWidget):
    """
    This class is the main widget for the visualization of the SLIX data.
    """

    def __init__(self):
        super().__init__()
        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.layout = None
        self.sidebar = None
        self.sidebar_tabbar = None
        self.image_widget = None
        self.filename = None
        self.dirname = None

        self.parameter_map = None
        self.parameter_map_color_map = None
        self.parameter_map_tab_button_save = None

        self.directions = None
        self.inclinations = None

        self.fom = None
        self.fom_checkbox_weight_saturation = None
        self.fom_checkbox_weight_value = None
        self.fom_tab_button_generate = None
        self.fom_tab_save_button = None
        self.fom_color_map = None
        self.saturation_weighting = None
        self.value_weighting = None

        self.vector_field = None
        self.vector_checkbox_weight_value = None
        self.vector_tab_alpha_parameter = None
        self.vector_tab_thinout_parameter = None
        self.vector_tab_scale_parameter = None
        self.vector_tab_vector_width_parameter = None
        self.vector_tab_dpi_parameter = None
        self.vector_tab_button_generate = None
        self.vector_tab_save_button = None
        self.vector_checkbox_activate_distribution = None
        self.vector_tab_threshold_parameter = None
        self.vector_background = None
        self.vector_weighting = None
        self.vector_color_map = None

        self.worker = None
        self.worker_thread = None
        self.progress_dialog = None

        self.setup_ui()

    def __del__(self):
        if self.worker_thread is not None:
            self.worker_thread.terminate()
            self.worker_thread.deleteLater()

    def setup_ui_image_widget(self) -> None:
        """
        This method sets up the image widget.

        Returns:
            None
        """
        self.image_widget = ImageWidget()
        self.image_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setup_ui(self) -> None:
        """
        This method sets up the main widget.

        Returns:
            None
        """
        self.layout = QHBoxLayout()
        self.sidebar = QVBoxLayout()
        self.sidebar_tabbar = QTabWidget()
        self.sidebar_tabbar.addTab(self.setup_fom_tab(), 'FOM')
        self.sidebar_tabbar.addTab(self.setup_vector_tab(), 'Vector')
        self.sidebar_tabbar.addTab(self.setup_parameter_map_tab(), 'Parameter Map')
        self.sidebar.addWidget(self.sidebar_tabbar)

        self.setup_ui_image_widget()

        self.layout.addWidget(self.image_widget, stretch=7)
        self.layout.addLayout(self.sidebar, stretch=2)
        self.setLayout(self.layout)

    def setup_fom_tab(self) -> QWidget:
        """
        This method sets up the FOM tab.

        Returns:
            QWidget: The FOM tab.
        """
        fom_tab = QWidget()
        fom_tab.layout = QVBoxLayout()

        fom_tab_button_open_measurement = QPushButton("Open Directions")
        fom_tab_button_open_measurement.clicked.connect(self.open_direction)
        fom_tab.layout.addWidget(fom_tab_button_open_measurement)

        fom_tab_button_open_inclination = QPushButton("Open Inclination")
        fom_tab_button_open_inclination.clicked.connect(self.open_inclination)
        fom_tab.layout.addWidget(fom_tab_button_open_inclination)

        fom_tab.layout.addStretch(3)

        fom_tab.layout.addWidget(QLabel("Color map:"))
        self.fom_color_map = QComboBox()
        for cmap in SLIX._cmd.VisualizeParameter.available_colormaps.keys():
            self.fom_color_map.addItem(cmap)
        fom_tab.layout.addWidget(self.fom_color_map)

        fom_tab.layout.addStretch(1)

        self.fom_checkbox_weight_saturation = QCheckBox("Weight FOM by Saturation")
        self.fom_checkbox_weight_saturation.setChecked(False)
        fom_tab_button_open_saturation = QPushButton("Open Saturation weighting")
        fom_tab_button_open_saturation.setEnabled(False)
        fom_tab_button_open_saturation.clicked.connect(self.open_saturation_weighting)
        self.fom_checkbox_weight_saturation.stateChanged.connect(fom_tab_button_open_saturation.setEnabled)
        fom_tab.layout.addWidget(self.fom_checkbox_weight_saturation)
        fom_tab.layout.addWidget(fom_tab_button_open_saturation)

        fom_tab.layout.addStretch(1)

        self.fom_checkbox_weight_value = QCheckBox("Weight FOM by Value")
        self.fom_checkbox_weight_value.setChecked(False)
        fom_tab_button_open_value = QPushButton("Open Value weighting")
        fom_tab_button_open_value.setEnabled(False)
        fom_tab_button_open_value.clicked.connect(self.open_value_weighting)
        fom_tab.layout.addWidget(self.fom_checkbox_weight_value)
        fom_tab.layout.addWidget(fom_tab_button_open_value)
        self.fom_checkbox_weight_value.stateChanged.connect(fom_tab_button_open_value.setEnabled)

        fom_tab.layout.addStretch(3)

        self.fom_tab_button_generate = QPushButton("Generate")
        self.fom_tab_button_generate.clicked.connect(self.generate_fom)
        self.fom_tab_button_generate.setEnabled(False)
        fom_tab.layout.addWidget(self.fom_tab_button_generate)

        self.fom_tab_save_button = QPushButton("Save")
        self.fom_tab_save_button.clicked.connect(self.save_fom)
        self.fom_tab_save_button.setEnabled(False)
        fom_tab.layout.addWidget(self.fom_tab_save_button)

        fom_tab.setLayout(fom_tab.layout)
        return fom_tab

    def setup_vector_tab(self) -> QWidget:
        """
        This method sets up the vector tab.

        Returns:
            QWidget: The vector tab.
        """
        vector_tab = QWidget()
        vector_tab.layout = QVBoxLayout()

        vector_tab_button_open_measurement = QPushButton("Open Directions")
        vector_tab_button_open_measurement.clicked.connect(self.open_direction)
        vector_tab.layout.addWidget(vector_tab_button_open_measurement)

        vector_tab_button_open_background = QPushButton("Open Background Image")
        vector_tab_button_open_background.clicked.connect(self.open_vector_background)
        vector_tab.layout.addWidget(vector_tab_button_open_background)

        vector_tab.layout.addStretch(3)

        vector_tab.layout.addWidget(QLabel("<b>Options:</b>"))
        vector_tab.layout.addWidget(QLabel("Color map:"))
        self.vector_color_map = QComboBox()
        for cmap in SLIX._cmd.VisualizeParameter.available_colormaps.keys():
            self.vector_color_map.addItem(cmap)
        vector_tab.layout.addWidget(self.vector_color_map)

        self.vector_checkbox_weight_value = QCheckBox("Weight Vector Length")
        self.vector_checkbox_weight_value.setChecked(False)
        vector_tab_button_open_value = QPushButton("Open Weighting")
        vector_tab_button_open_value.setEnabled(False)
        vector_tab_button_open_value.clicked.connect(self.open_vector_weighting)
        vector_tab.layout.addWidget(self.vector_checkbox_weight_value)
        vector_tab.layout.addWidget(vector_tab_button_open_value)
        self.vector_checkbox_weight_value.stateChanged.connect(vector_tab_button_open_value.setEnabled)

        vector_tab.layout.addWidget(QLabel("Alpha:"))
        self.vector_tab_alpha_parameter = QDoubleSpinBox()
        self.vector_tab_alpha_parameter.setRange(0, 1)
        self.vector_tab_alpha_parameter.setSingleStep(0.001)
        self.vector_tab_alpha_parameter.setValue(1)
        self.vector_tab_alpha_parameter.setDecimals(3)
        vector_tab.layout.addWidget(self.vector_tab_alpha_parameter)

        vector_tab.layout.addWidget(QLabel("Thinout:"))
        self.vector_tab_thinout_parameter = QDoubleSpinBox()
        self.vector_tab_thinout_parameter.setRange(0, 100)
        self.vector_tab_thinout_parameter.setSingleStep(1)
        self.vector_tab_thinout_parameter.setValue(1)
        self.vector_tab_thinout_parameter.setDecimals(0)
        vector_tab.layout.addWidget(self.vector_tab_thinout_parameter)

        vector_tab.layout.addWidget(QLabel("Scale:"))
        self.vector_tab_scale_parameter = QDoubleSpinBox()
        self.vector_tab_scale_parameter.setRange(0, 100)
        self.vector_tab_scale_parameter.setSingleStep(1)
        self.vector_tab_scale_parameter.setValue(1)
        self.vector_tab_scale_parameter.setDecimals(0)
        vector_tab.layout.addWidget(self.vector_tab_scale_parameter)

        vector_tab.layout.addWidget(QLabel("Vector width:"))
        self.vector_tab_vector_width_parameter = QDoubleSpinBox()
        self.vector_tab_vector_width_parameter.setRange(0, 100)
        self.vector_tab_vector_width_parameter.setSingleStep(0.1)
        self.vector_tab_vector_width_parameter.setValue(1)
        self.vector_tab_vector_width_parameter.setDecimals(1)
        vector_tab.layout.addWidget(self.vector_tab_vector_width_parameter)

        vector_tab.layout.addWidget(QLabel("DPI:"))
        self.vector_tab_dpi_parameter = QDoubleSpinBox()
        self.vector_tab_dpi_parameter.setRange(100, 2000)
        self.vector_tab_dpi_parameter.setSingleStep(100)
        self.vector_tab_dpi_parameter.setValue(100)
        self.vector_tab_dpi_parameter.setDecimals(0)
        vector_tab.layout.addWidget(self.vector_tab_dpi_parameter)

        self.vector_checkbox_activate_distribution = QCheckBox("Activate Distribution")
        self.vector_checkbox_activate_distribution.setChecked(True)
        vector_tab.layout.addWidget(self.vector_checkbox_activate_distribution)

        vector_tab.layout.addWidget(QLabel("Threshold:"))
        self.vector_tab_threshold_parameter = QDoubleSpinBox()
        self.vector_tab_threshold_parameter.setRange(0, 1)
        self.vector_tab_threshold_parameter.setSingleStep(0.01)
        self.vector_tab_threshold_parameter.setValue(0)
        self.vector_tab_threshold_parameter.setDecimals(2)
        self.vector_tab_threshold_parameter.setEnabled(False)
        self.vector_checkbox_activate_distribution.stateChanged.connect(self.vector_tab_threshold_parameter.setDisabled)
        vector_tab.layout.addWidget(self.vector_tab_threshold_parameter)

        vector_tab.layout.addStretch(3)

        self.vector_tab_button_generate = QPushButton("Generate")
        self.vector_tab_button_generate.clicked.connect(self.generate_vector)
        self.vector_tab_button_generate.setEnabled(False)
        vector_tab.layout.addWidget(self.vector_tab_button_generate)

        self.vector_tab_save_button = QPushButton("Save")
        self.vector_tab_save_button.clicked.connect(self.save_vector)
        self.vector_tab_save_button.setEnabled(False)
        vector_tab.layout.addWidget(self.vector_tab_save_button)

        vector_tab.setLayout(vector_tab.layout)
        return vector_tab

    def setup_parameter_map_tab(self) -> QWidget:
        """
        Set up the parameter map tab.

        Returns:
            QWidget: The parameter map tab.
        """
        parameter_map_tab = QWidget()
        parameter_map_tab.layout = QVBoxLayout()

        parameter_map_button_open = QPushButton("Open parameter map")
        parameter_map_button_open.clicked.connect(self.open_parameter_map)
        parameter_map_tab.layout.addWidget(parameter_map_button_open)

        parameter_map_tab.layout.addWidget(QLabel("Color map:"))
        self.parameter_map_color_map = QComboBox()
        for cmap in matplotlib.cm.cmap_d.keys():
            self.parameter_map_color_map.addItem(cmap)
        parameter_map_tab.layout.addWidget(self.parameter_map_color_map)
        self.parameter_map_color_map.setEnabled(False)
        self.parameter_map_color_map.currentIndexChanged.connect(self.generate_parameter_map)

        self.parameter_map_tab_button_save = QPushButton("Save preview")
        self.parameter_map_tab_button_save.clicked.connect(self.save_parameter_map)
        self.parameter_map_tab_button_save.setEnabled(False)
        parameter_map_tab.layout.addWidget(self.parameter_map_tab_button_save)

        parameter_map_tab.layout.addStretch()

        parameter_map_tab.setLayout(parameter_map_tab.layout)
        return parameter_map_tab

    def show_error_message(self, message: str) -> None:
        """
        Shows an error message.

        Returns:
            None
        """
        QMessageBox.warning(self, "Error", message)

    def open_direction(self) -> None:
        """
        Open one or more direction files.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileNames(self, 'Open Directions', dirname,
                                                '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename[0])

        try:
            direction_image = None
            filename.sort()
            for file in filename:
                # Arrange the direction images in a NumPy stack
                single_direction_image = SLIX.io.imread(file)
                if direction_image is None:
                    direction_image = single_direction_image
                else:
                    if len(direction_image.shape) == 2:
                        direction_image = numpy.stack((direction_image,
                                                       single_direction_image),
                                                      axis=-1)
                    else:
                        direction_image = numpy.concatenate((direction_image,
                                                             single_direction_image
                                                             [:, :, numpy.newaxis]),
                                                            axis=-1)
            self.directions = direction_image
            self.inclinations = None
            self.fom_tab_button_generate.setEnabled(True)
            self.vector_tab_button_generate.setEnabled(True)
        except ValueError as e:
            QMessageBox.critical(self, 'Error',
                                 f'Could not load directions. Check your input files. Error message:\n{e}')

    def open_inclination(self) -> None:
        """
        Open one or more direction files.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileNames(self, 'Open Inclinations', dirname,
                                                '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename[0])

        try:
            inclination_image = None
            filename.sort()
            for file in filename:
                # Arrange the direction images in a NumPy stack
                single_inclination_image = SLIX.io.imread(file)
                if inclination_image is None:
                    inclination_image = single_inclination_image
                else:
                    if len(inclination_image.shape) == 2:
                        inclination_image = numpy.stack((inclination_image,
                                                         single_inclination_image),
                                                        axis=-1)
                    else:
                        inclination_image = numpy.concatenate((inclination_image,
                                                               single_inclination_image
                                                               [:, :, numpy.newaxis]),
                                                              axis=-1)
            self.inclinations = inclination_image
        except ValueError as e:
            QMessageBox.critical(self, 'Error',
                                 f'Could not load directions. Check your input files. Error message:\n{e}')

    def open_parameter_map(self) -> None:
        """
        Open a parameter map.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileName(self, 'Open Parameter Map', dirname,
                                               '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename)

        self.parameter_map = SLIX.io.imread(filename)
        self.parameter_map_tab_button_save.setEnabled(True)
        self.parameter_map_color_map.setEnabled(True)
        self.generate_parameter_map()

    def open_saturation_weighting(self) -> None:
        """
        Open a saturation weighting map.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileName(self, 'Open Saturation weight', dirname,
                                               '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename)
        self.saturation_weighting = SLIX.io.imread(filename)

    def open_value_weighting(self) -> None:
        """
        Open a value weighting map.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileName(self, 'Open Value weight', dirname,
                                               '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename)
        self.value_weighting = SLIX.io.imread(filename)

    def open_vector_background(self) -> None:
        """
        Open a vector background map.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileName(self, 'Open Background Image', dirname,
                                               '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename)
        self.vector_background = SLIX.io.imread(filename)
        while len(self.vector_background.shape) > 2:
            self.vector_background = numpy.mean(self.vector_background, axis=-1)

    def open_vector_weighting(self) -> None:
        """
        Open a vector weighting map.

        Returns:
            None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename = QFileDialog.getOpenFileName(self, 'Open Weight for vector', dirname,
                                               '*.tif;; *.tiff;; *.h5;; *.nii')[0]
        if len(filename) == 0:
            return
        self.dirname = os.path.dirname(filename)
        # Open and normalize the weighting image
        self.vector_weighting = SLIX.io.imread(filename)
        self.vector_weighting = (self.vector_weighting - self.vector_weighting.min()) / (
                numpy.percentile(self.vector_weighting, 99) - self.vector_weighting.min())

    def generate_fom(self) -> None:
        """
        Generate fiber orientation map based on the current settings.
        The generated FOM is saved in the self.fom attribute and will be
        shown to the user in the image viewer.

        Returns:
             None
        """
        self.fom_tab_button_generate.setEnabled(False)

        # If the FOM should be weighted by the saturation weighting,
        # set the parameter saturation_weighting to the loaded image
        if self.fom_checkbox_weight_saturation.isChecked():
            saturation_weighting = self.saturation_weighting
        # If not, set it to None disabling any weighting.
        else:
            saturation_weighting = None
        # Repeat for value channel
        if self.fom_checkbox_weight_value.isChecked():
            value_weighting = self.value_weighting
        else:
            value_weighting = None
        # Get the color map which will be used in the FOM generation method.
        color_map = SLIX._cmd.VisualizeParameter.available_colormaps[self.fom_color_map.currentText()]

        # Show a progress bar while the parameter maps are generated
        if self.progress_dialog:
            del self.progress_dialog
        self.progress_dialog = QProgressDialog("Generating...", "Cancel", 0, 0, self)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowFlag(Qt.CustomizeWindowHint, True)
        self.progress_dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)
        # Move the main workload to another thread to prevent freezing the GUI
        if self.worker_thread:
            del self.worker_thread
            self.worker_thread = None
        self.worker_thread = QThread()
        self.worker_thread.setTerminationEnabled(True)
        if self.worker:
            del self.worker
        self.worker = FOMWorker(saturation_weighting, value_weighting, color_map, self.directions, self.inclinations)
        # Update the progress bar whenever a step is finished
        self.worker.currentStep.connect(self.progress_dialog.setLabelText)
        self.worker.finishedWork.connect(self.worker_thread.quit)
        self.worker.finishedWork.connect(self.set_fom)
        self.worker.errorMessage.connect(self.show_error_message)
        self.worker.moveToThread(self.worker_thread)
        # Show the progress bar
        self.progress_dialog.show()

        self.worker_thread.started.connect(self.worker.process)
        self.worker_thread.finished.connect(self.progress_dialog.close)
        self.progress_dialog.canceled.connect(self.worker_thread.requestInterruption)
        self.worker_thread.start()

    def set_fom(self, fom: numpy.ndarray) -> None:
        """
        Set the generated FOM to the self.fom attribute and show it in the image viewer.

        Args:
            fom: The generated FOM.

        Returns:
            None
        """
        if self.worker_thread:
            del self.worker_thread
            self.worker_thread = None

        self.fom = fom
        if self.fom is not None:
            self.image_widget.set_image(convert_numpy_to_qimage(self.fom))
            self.fom_tab_save_button.setEnabled(True)
        self.fom_tab_button_generate.setEnabled(True)

    def generate_vector(self) -> None:
        """
        Generate vector map based on the current settings.

        Returns:
            None
        """
        # This method only works when a direction is loaded. If not, do nothing.
        if self.directions is None:
            return

        # Get parameters from interface
        color_map = self.vector_color_map.currentText()
        alpha = self.vector_tab_alpha_parameter.value()
        thinout = int(self.vector_tab_thinout_parameter.value())
        scale = self.vector_tab_scale_parameter.value()
        vector_width = self.vector_tab_vector_width_parameter.value()
        threshold = self.vector_tab_threshold_parameter.value()

        if self.vector_checkbox_weight_value.isChecked():
            value_weighting = self.vector_weighting
        else:
            value_weighting = None

        # Generate either the distrubution of vectors or the vector field
        # depending on the selected option. This method might fail if the
        # parameters are not valid or a measurement is missing.
        # If it fails, show an error message.
        fig, ax = plt.subplots(dpi=self.vector_tab_dpi_parameter.value())

        # Show a progress bar while the parameter maps are generated
        if self.progress_dialog:
            del self.progress_dialog
        self.progress_dialog = QProgressDialog("Generating...", "Cancel", 0, 0, self)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setWindowFlag(Qt.CustomizeWindowHint, True)
        self.progress_dialog.setWindowFlag(Qt.WindowCloseButtonHint, False)

        # Move the main workload to another thread to prevent freezing the GUI
        if self.worker_thread:
            del self.worker_thread
            self.worker_thread = None
        self.worker_thread = QThread()
        self.worker_thread.setTerminationEnabled(True)
        if self.worker:
            del self.worker
        self.worker = VectorWorker(fig, ax, self.directions, alpha, thinout, scale, vector_width,
                                   self.vector_checkbox_activate_distribution.isChecked(), threshold,
                                   color_map, self.vector_background, value_weighting)
        # Update the progress bar whenever a step is finished
        self.worker.currentStep.connect(self.progress_dialog.setLabelText)
        self.worker.finishedWork.connect(self.worker_thread.quit)
        self.worker.finishedWork.connect(self.set_vector)
        self.worker.errorMessage.connect(self.show_error_message)
        self.worker.moveToThread(self.worker_thread)
        # Show the progress bar
        self.progress_dialog.show()

        self.worker_thread.started.connect(self.worker.process)
        self.worker_thread.finished.connect(self.progress_dialog.close)
        self.worker_thread.start()

    def set_vector(self, image: numpy.ndarray) -> None:
        """
        Set the vector map to the image widget.

        Args:
            image: The vector map.

        Returns:
            None
        """
        if image is not None:
            self.vector_field = image
            self.image_widget.set_image(convert_numpy_to_qimage(self.vector_field))
            self.vector_tab_save_button.setEnabled(True)
        self.vector_tab_button_generate.setEnabled(True)

    def generate_parameter_map(self) -> None:
        """
        Generate parameter map based on the current settings.
        Show the result in the image widget.

        Returns:
            None
        """
        # Get color map from matplotlib
        colormap = matplotlib.cm.get_cmap(self.parameter_map_color_map.currentText())
        # Normalize the image to the range [0, 1]
        shown_image = self.parameter_map.copy()
        shown_image = shown_image.astype(numpy.float32)
        shown_image = (shown_image - shown_image.min()) / (shown_image.max() - shown_image.min())
        # Apply colormap on normalized image
        shown_image = colormap(shown_image)
        # Convert NumPy RGBA array to RGB array
        shown_image = shown_image[:, :, :3]
        self.image_widget.set_image(convert_numpy_to_qimage(shown_image))

    def save_fom(self) -> None:
        """
        Save the current FOM image to a file.

        Returns:
             None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename, datatype = QFileDialog.getSaveFileName(self, 'Save FOM', dirname, '*.tiff;; *.h5')
        self.dirname = os.path.dirname(filename)
        if len(filename) > 0:
            datatype = datatype[1:]
            if not filename.endswith(datatype):
                filename += datatype
            SLIX.io.imwrite_rgb(filename, self.fom)

    def save_vector(self) -> None:
        """
        Save the current vector field image to a file.

        Returns:
             None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename, datatype = QFileDialog.getSaveFileName(self, 'Save Vector Image', dirname, '*.tiff;; *.h5')
        self.dirname = os.path.dirname(filename)
        if len(filename) > 0:
            datatype = datatype[1:]
            if not filename.endswith(datatype):
                filename += datatype
            SLIX.io.imwrite_rgb(filename, self.vector_field)

    def save_parameter_map(self) -> None:
        """
        Save the current parameter map image to a file.

        Returns:
             None
        """
        if self.dirname:
            dirname = self.dirname
        else:
            dirname = os.path.expanduser('~')
        filename, datatype = QFileDialog.getSaveFileName(self, 'Save Parameter Map', dirname, '*.tiff;; *.h5')
        if len(filename) > 0:
            self.dirname = os.path.dirname(filename)
            datatype = datatype[1:]
            if not filename.endswith(datatype):
                filename += datatype

            colormap = matplotlib.cm.get_cmap(self.parameter_map_color_map.currentText())
            shown_image = self.parameter_map.copy()
            shown_image = shown_image.astype(numpy.float32)
            shown_image = (shown_image - shown_image.min()) / (shown_image.max() - shown_image.min())
            shown_image = colormap(shown_image)
            # Convert NumPy RGBA array to RGB array
            shown_image = (255 * shown_image[:, :, :3]).astype(numpy.uint8)
            SLIX.io.imwrite_rgb(filename, shown_image)
