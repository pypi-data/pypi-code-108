import os.path

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, \
    QFileDialog, QCheckBox, QPushButton, QProgressDialog, \
    QSizePolicy, QComboBox, QDoubleSpinBox, QLabel, QMessageBox
from PyQt5.QtCore import QThread, QLocale

from .ImageWidget import ImageWidget, convert_numpy_to_qimage
from .ThreadWorkers.ParameterGenerator import ParameterGeneratorWorker

import SLIX


__all__ = ['ParameterGeneratorWidget']


class ParameterGeneratorWidget(QWidget):
    """
    Widget for generating parameters.
    """

    def __init__(self):
        super().__init__()

        self.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))

        self.layout = None
        self.sidebar = None
        self.sidebar_button_open_measurement = None
        self.sidebar_button_open_folder = None
        self.sidebar_checkbox_filtering = None
        self.sidebar_filtering_algorithm = None
        self.sidebar_filtering_parameter_1 = None
        self.sidebar_filtering_parameter_2 = None
        self.sidebar_checkbox_average = None
        self.sidebar_checkbox_minimum = None
        self.sidebar_checkbox_maximum = None
        self.sidebar_checkbox_crossing_direction = None
        self.sidebar_checkbox_non_crossing_direction = None
        self.sidebar_checkbox_peak_distance = None
        self.sidebar_checkbox_peak_width = None
        self.sidebar_checkbox_peak_prominence = None
        self.sidebar_checkbox_peaks = None
        self.sidebar_checkbox_detailed = None
        self.sidebar_checkbox_use_gpu = None
        self.sidebar_dir_correction_parameter = None
        self.sidebar_button_generate = None
        self.image_widget = None

        self.filename = None
        self.image = None
        self.worker_thread = None
        self.worker = None
        self.progress_dialog = None

        self.setup_ui()

    def __del__(self):
        if self.worker_thread is not None:
            self.worker_thread.terminate()
            self.worker_thread.deleteLater()

    def setup_ui(self) -> None:
        """
        Set up the user interface.

        Returns:
            None
        """
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setup_ui_sidebar()
        self.setup_ui_image_widget()

        self.layout.addWidget(self.image_widget, stretch=7)
        self.layout.addLayout(self.sidebar, stretch=2)

    def setup_ui_sidebar(self) -> None:
        """
        Set up the sidebar.

        Returns:
            None
        """
        self.sidebar = QVBoxLayout()

        # Open part
        self.sidebar.addWidget(QLabel("<b>Open:</b>"))
        self.sidebar_button_open_measurement = QPushButton(" Measurement")
        self.sidebar_button_open_measurement.clicked.connect(self.open_measurement)
        self.sidebar.addWidget(self.sidebar_button_open_measurement)

        self.sidebar_button_open_folder = QPushButton("Folder")
        self.sidebar_button_open_folder.clicked.connect(self.open_folder)
        self.sidebar.addWidget(self.sidebar_button_open_folder)

        self.sidebar.addStretch(5)

        # Filtering part
        self.sidebar.addWidget(QLabel("<b>Filtering:</b>"))
        # Set filtering algorithm
        self.sidebar_checkbox_filtering = QCheckBox("Enable")
        self.sidebar_checkbox_filtering.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_filtering)
        self.sidebar_filtering_algorithm = QComboBox()
        self.sidebar_filtering_algorithm.setEnabled(False)
        self.sidebar_filtering_algorithm.addItems(["Fourier", "Savitzky-Golay"])
        self.sidebar_filtering_algorithm.setCurrentIndex(0)
        self.sidebar.addWidget(self.sidebar_filtering_algorithm)
        self.sidebar_checkbox_filtering.stateChanged.connect(self.sidebar_filtering_algorithm.setEnabled)
        # Set filtering window size
        self.sidebar_filtering_parameter_1 = QDoubleSpinBox()
        self.sidebar_filtering_parameter_1.setEnabled(False)
        self.sidebar_filtering_parameter_1.setRange(0, 1)
        self.sidebar_filtering_parameter_1.setSingleStep(0.001)
        self.sidebar_filtering_parameter_1.setValue(0)
        self.sidebar_filtering_parameter_1.setDecimals(3)
        self.sidebar.addWidget(self.sidebar_filtering_parameter_1)
        self.sidebar_checkbox_filtering.stateChanged.connect(self.sidebar_filtering_parameter_1.setEnabled)
        # Set filtering order / magnitude
        self.sidebar_filtering_parameter_2 = QDoubleSpinBox()
        self.sidebar_filtering_parameter_2.setEnabled(False)
        self.sidebar_filtering_parameter_2.setRange(0, 1)
        self.sidebar_filtering_parameter_2.setSingleStep(0.001)
        self.sidebar_filtering_parameter_2.setValue(0)
        self.sidebar_filtering_parameter_2.setDecimals(3)
        self.sidebar.addWidget(self.sidebar_filtering_parameter_2)
        self.sidebar_checkbox_filtering.stateChanged.connect(self.sidebar_filtering_parameter_2.setEnabled)

        self.sidebar.addStretch(1)
        # Parameter map part
        self.sidebar.addWidget(QLabel("<b>Parameter Maps:</b>"))

        self.sidebar_checkbox_average = QCheckBox("Average")
        self.sidebar_checkbox_average.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_average)

        self.sidebar_checkbox_minimum = QCheckBox("Minimum")
        self.sidebar_checkbox_minimum.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_minimum)

        self.sidebar_checkbox_maximum = QCheckBox("Maximum")
        self.sidebar_checkbox_maximum.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_maximum)

        self.sidebar_checkbox_crossing_direction = QCheckBox("Crossing Direction")
        self.sidebar_checkbox_crossing_direction.setChecked(True)
        self.sidebar.addWidget(self.sidebar_checkbox_crossing_direction)

        self.sidebar_checkbox_non_crossing_direction = QCheckBox("Non Crossing Direction")
        self.sidebar_checkbox_non_crossing_direction.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_non_crossing_direction)

        self.sidebar_checkbox_peak_distance = QCheckBox("Peak Distance")
        self.sidebar_checkbox_peak_distance.setChecked(True)
        self.sidebar.addWidget(self.sidebar_checkbox_peak_distance)

        self.sidebar_checkbox_peak_width = QCheckBox("Peak Width")
        self.sidebar_checkbox_peak_width.setChecked(True)
        self.sidebar.addWidget(self.sidebar_checkbox_peak_width)

        self.sidebar_checkbox_peak_prominence = QCheckBox("Peak Prominence")
        self.sidebar_checkbox_peak_prominence.setChecked(True)
        self.sidebar.addWidget(self.sidebar_checkbox_peak_prominence)

        self.sidebar_checkbox_peaks = QCheckBox("Peaks")
        self.sidebar_checkbox_peaks.setChecked(True)
        self.sidebar.addWidget(self.sidebar_checkbox_peaks)

        self.sidebar.addStretch(1)

        # Additional option part
        self.sidebar.addWidget(QLabel("<b>Other options:</b>"))

        self.sidebar.addWidget(QLabel("Correction direction (°):"))
        self.sidebar_dir_correction_parameter = QDoubleSpinBox()
        self.sidebar_dir_correction_parameter.setRange(0, 180)
        self.sidebar_dir_correction_parameter.setSingleStep(0.1)
        self.sidebar_dir_correction_parameter.setValue(0)
        self.sidebar_dir_correction_parameter.setDecimals(2)
        self.sidebar.addWidget(self.sidebar_dir_correction_parameter)

        self.sidebar_checkbox_detailed = QCheckBox("Detailed")
        self.sidebar_checkbox_detailed.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_detailed)

        self.sidebar_checkbox_use_gpu = QCheckBox("Use GPU")
        # Disable the gpu checkbox if no compatible GPU was found by SLIX
        self.sidebar_checkbox_use_gpu.setEnabled(SLIX.toolbox.gpu_available)
        self.sidebar_checkbox_use_gpu.setChecked(SLIX.toolbox.gpu_available)
        self.sidebar.addWidget(self.sidebar_checkbox_use_gpu)

        self.sidebar.addStretch(5)

        self.sidebar_button_generate = QPushButton("Generate")
        self.sidebar_button_generate.clicked.connect(self.generate)
        self.sidebar_button_generate.setEnabled(False)
        self.sidebar.addWidget(self.sidebar_button_generate)

    def setup_ui_image_widget(self) -> None:
        """
        Set up the image widget.

        Returns:
            None
        """
        self.image_widget = ImageWidget()
        self.image_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def open_measurement(self) -> None:
        """
        Called when pressing a button. Opens a file dialog to select a measurement file.
        The measurement will then be loaded and the image widget will be updated.

        Returns:
             None
        """
        if self.filename is None:
            open_folder = os.path.expanduser('~')
        else:
            open_folder = os.path.dirname(self.filename)
        file = QFileDialog.getOpenFileName(self, "Open Measurement", open_folder,
                                           "*.tiff ;; *.tif ;; *.h5 ;; *.nii ;; *.nii.gz")[0]
        if not file:
            return
        self.filename = file
        self.image = SLIX.io.imread(file)
        self.sidebar_button_generate.setEnabled(True)

        if self.image_widget:
            self.image_widget.set_image(convert_numpy_to_qimage(self.image))

    def open_folder(self) -> None:
        """
        Called when pressing a button. Opens a file dialog to select a measurement folder.
        The measurement will then be loaded and the image widget will be updated.

        Returns:
            None
        """
        if self.filename is None:
            open_folder = os.path.expanduser('~')
        else:
            open_folder = self.filename

        folder = QFileDialog.getExistingDirectory(self, "Open Folder", open_folder)

        if not folder:
            return

        self.filename = folder
        self.image = SLIX.io.imread(folder)
        # Couldn't read any image from the folder
        if self.image is None:
            QMessageBox.warning(self, "Error", "Couldn't read any image from the folder.")
            return
        self.sidebar_button_generate.setEnabled(True)

        if self.image_widget:
            self.image_widget.set_image(convert_numpy_to_qimage(self.image))

    def show_error_message(self, message: str) -> None:
        """
        Shows an error message.

        Returns:
            None
        """
        QMessageBox.warning(self, "Error", message)

    def generate(self) -> None:
        """
        Called when pressing a button. Generates the parameter maps and saves them to disk.

        Returns:
            None
        """
        if self.filename != "":
            open_folder = os.path.expanduser('~')
        else:
            open_folder = os.path.dirname(self.filename)

        # Prevent the button from being pressed multiple times
        output_folder = QFileDialog.getExistingDirectory(self, "Save files in folder", open_folder)

        if not output_folder:
            return

        # Show a progress bar while the parameter maps are generated
        if self.progress_dialog:
            del self.progress_dialog
        self.progress_dialog = QProgressDialog("Generating...", "Cancel", 0, 0, self)

        if self.sidebar_checkbox_filtering.isChecked():
            filtering_algorithm = self.sidebar_filtering_algorithm.currentText()
        else:
            filtering_algorithm = "None"

        # Move the main workload to another thread to prevent freezing the GUI
        self.worker_thread = QThread()
        self.worker = ParameterGeneratorWorker(self.filename, self.image, output_folder,
                                               filtering_algorithm,
                                               self.sidebar_filtering_parameter_1.value(),
                                               self.sidebar_filtering_parameter_2.value(),
                                               self.sidebar_checkbox_use_gpu.isChecked(),
                                               self.sidebar_checkbox_detailed.isChecked(),
                                               self.sidebar_checkbox_minimum.isChecked(),
                                               self.sidebar_checkbox_maximum.isChecked(),
                                               self.sidebar_checkbox_average.isChecked(),
                                               self.sidebar_checkbox_crossing_direction.isChecked(),
                                               self.sidebar_checkbox_non_crossing_direction.isChecked(),
                                               self.sidebar_checkbox_peaks.isChecked(),
                                               self.sidebar_checkbox_peak_width.isChecked(),
                                               self.sidebar_checkbox_peak_distance.isChecked(),
                                               self.sidebar_checkbox_peak_prominence.isChecked(),
                                               self.sidebar_dir_correction_parameter.value())
        # Update the progress bar whenever a step is finished
        self.worker.currentStep.connect(self.progress_dialog.setLabelText)
        self.worker.finishedWork.connect(self.worker_thread.quit)
        self.worker.errorMessage.connect(self.show_error_message)
        self.worker.moveToThread(self.worker_thread)
        # Show the progress bar
        self.progress_dialog.show()

        self.worker_thread.started.connect(self.worker.process)
        self.worker_thread.finished.connect(self.progress_dialog.close)
        self.progress_dialog.canceled.connect(self.worker_thread.requestInterruption)
        self.worker_thread.start()
