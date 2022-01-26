from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, \
    QLabel, QPushButton, QCheckBox, QSizePolicy, QHBoxLayout, QComboBox, QMessageBox

from .ImageWidget import ImageWidget, convert_numpy_to_qimage
import SLIX
from SLIX._cmd import Cluster

import matplotlib
import numpy
import os

__all__ = ['ClusterWidget']


class ClusterWidget(QWidget):
    """
    Widget for clustering images.
    """

    def __init__(self):
        super().__init__()

        self.folder = None

        self.layout = None
        self.sidebar = None
        self.image_widget = None

        self.sidebar_checkbox_all = None
        self.sidebar_checkbox_flat = None
        self.sidebar_checkbox_crossing = None
        self.sidebar_checkbox_inclined = None

        self.sidebar_button_preview = None
        self.sidebar_button_generate = None
        self.sidebar_button_open_folder = None

        self.sidebar_color_map = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """
        Set up the main layout.

        Returns:
             None
        """
        self.setup_ui_image_widget()
        self.setup_ui_sidebar()

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.image_widget, stretch=7)
        self.layout.addLayout(self.sidebar, stretch=2)
        self.setLayout(self.layout)

    def setup_ui_image_widget(self) -> None:
        """
        Set up the image widget.

        Returns:
             None
        """
        self.image_widget = ImageWidget()
        self.image_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setup_ui_sidebar(self) -> None:
        """
        Set up the sidebar.

        Returns:
             None
        """
        self.sidebar = QVBoxLayout()

        self.sidebar.addWidget(QLabel("<b>Open:</b>"))
        self.sidebar_button_open_folder = QPushButton("Folder")
        self.sidebar_button_open_folder.clicked.connect(self.open_folder)
        self.sidebar.addWidget(self.sidebar_button_open_folder)

        self.sidebar.addWidget(QLabel("Color map:"))
        self.sidebar_color_map = QComboBox()
        for cmap in matplotlib.cm.cmap_d.keys():
            self.sidebar_color_map.addItem(cmap)
        self.sidebar.addWidget(self.sidebar_color_map)
        self.sidebar_color_map.currentIndexChanged.connect(self.generate_preview)

        self.sidebar.addStretch(5)

        self.sidebar.addWidget(QLabel("<b>Parameter Maps:</b>"))

        self.sidebar_checkbox_all = QCheckBox("All")
        self.sidebar_checkbox_all.setChecked(True)
        self.sidebar.addWidget(self.sidebar_checkbox_all)

        self.sidebar_checkbox_inclined = QCheckBox("Inclined")
        self.sidebar_checkbox_inclined.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_inclined)

        self.sidebar_checkbox_flat = QCheckBox("Flat")
        self.sidebar_checkbox_flat.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_flat)

        self.sidebar_checkbox_crossing = QCheckBox("Crossing")
        self.sidebar_checkbox_crossing.setChecked(False)
        self.sidebar.addWidget(self.sidebar_checkbox_crossing)

        self.sidebar.addStretch(5)

        self.sidebar_button_preview = QPushButton("Preview all")
        self.sidebar_button_preview.clicked.connect(self.generate_preview)
        self.sidebar_button_preview.setEnabled(False)
        self.sidebar.addWidget(self.sidebar_button_preview)

        self.sidebar_button_generate = QPushButton("Save")
        self.sidebar_button_generate.clicked.connect(self.save)
        self.sidebar_button_generate.setEnabled(False)
        self.sidebar.addWidget(self.sidebar_button_generate)

    def open_folder(self):
        """
        Let the user select a folder save the selected folder for future actions.

        Returns:
            None
        """
        if self.folder is None:
            self.folder = os.path.expanduser('~')
        folder = QFileDialog.getExistingDirectory(self, "Open Folder", self.folder)

        if not folder:
            # The user cancelled the dialog
            return

        self.folder = folder
        self.sidebar_button_preview.setEnabled(True)
        self.sidebar_button_generate.setEnabled(True)

    def generate_preview(self) -> None:
        """
        Generate a preview of the all parameter map.

        Returns:
            None
        """
        if self.folder is None:
            # Do nothing if the user didn't open a folder
            return

        loaded_parameter_maps, _ = Cluster.load_parameter_maps(self.folder)
        try:
            result_mask = SLIX.classification.full_mask(loaded_parameter_maps['high_prominence_peaks'],
                                                        loaded_parameter_maps['low_prominence_peaks'],
                                                        loaded_parameter_maps['peakdistance'],
                                                        loaded_parameter_maps['max'])
        except KeyError:
            QMessageBox.warning(self, "Error", "Could not generate preview.\n"
                                               "Make sure you have selected a folder with all parameter maps.")
            return

        # Get the color map from matplotlib based on the selected item in the QWidget
        colormap = matplotlib.cm.get_cmap(self.sidebar_color_map.currentText())
        # Normalize the image to the range [0, 1] and apply the color map to it
        shown_image = result_mask.astype(numpy.float32)
        shown_image = (shown_image - shown_image.min()) / (shown_image.max() - shown_image.min())
        shown_image = colormap(shown_image)
        # Convert NumPy RGBA array to RGB array
        shown_image = shown_image[:, :, :3]
        self.image_widget.set_image(convert_numpy_to_qimage(shown_image))

    def save(self) -> None:
        """
        Saves the chosen parameter maps to a folder.

        Returns:
            None
        """
        if self.folder is None:
            self.folder = os.path.expanduser('~')
        folder = QFileDialog.getExistingDirectory(self, 'Save Cluster Images', self.folder)
        if len(folder) == 0:
            # The user canceled the selection
            return

        # Get the parameter maps and the basename from the images in the chosen folder
        loaded_parameter_maps, basename = Cluster.load_parameter_maps(self.folder)
        # Flat mask might get set before reaching the inclined region.
        # This ensures that the flat mask will not get generated twice saving
        # time.
        flat_mask = None
        # If the user has selected to generate the flat mask, generate it.
        # Save the result in the folder the user has chosen. The filename will be
        # determined by the input file name.
        if self.sidebar_checkbox_flat.isChecked():
            name = basename.replace('basename', 'flat_mask')
            try:
                flat_mask = SLIX.classification.flat_mask(loaded_parameter_maps['high_prominence_peaks'],
                                                          loaded_parameter_maps['low_prominence_peaks'],
                                                          loaded_parameter_maps['peakdistance'])
                filename = f'{folder}/{name}.tiff'
                SLIX.io.imwrite(filename, flat_mask)
            except KeyError:
                QMessageBox.warning(self, "Error", "Could not generate flat mask.\n"
                                                   "Make sure you have selected a folder with all parameter maps.")
                return
        # If the user has selected to generate the crossing mask, generate it.
        # Save the result in the folder the user has chosen. The filename will be
        # determined by the input file name.
        if self.sidebar_checkbox_crossing.isChecked():
            name = basename.replace('basename', 'crossing_mask')
            try:
                mask = SLIX.classification.crossing_mask(loaded_parameter_maps['high_prominence_peaks'],
                                                         loaded_parameter_maps['max'])
                filename = f'{folder}/{name}.tiff'
                SLIX.io.imwrite(filename, mask)
            except KeyError:
                QMessageBox.warning(self, "Error", "Could not generate crossing mask.\n"
                                                   "Make sure you have selected a folder with all parameter maps.")
                return
        # If the user has selected to generate the inclined mask, generate it.
        # Save the result in the folder the user has chosen. The filename will be
        # determined by the input file name.
        if self.sidebar_checkbox_inclined.isChecked():
            name = basename.replace('basename', 'inclined_mask')
            try:
                if flat_mask is None:
                    flat_mask = SLIX.classification.flat_mask(loaded_parameter_maps['high_prominence_peaks'],
                                                              loaded_parameter_maps['low_prominence_peaks'],
                                                              loaded_parameter_maps['peakdistance'])

                mask = SLIX.classification.inclinated_mask(loaded_parameter_maps['high_prominence_peaks'],
                                                           loaded_parameter_maps['peakdistance'],
                                                           loaded_parameter_maps['max'],
                                                           flat_mask)
                filename = f'{folder}/{name}.tiff'
                SLIX.io.imwrite(filename, mask)
            except KeyError:
                QMessageBox.warning(self, "Error", "Could not generate inclined mask.\n"
                                                   "Make sure you have selected a folder with all parameter maps.")
                return
        # If the user has selected to generate the mask containing all parameters, generate it.
        # Save the result in the folder the user has chosen. The filename will be
        # determined by the input file name.
        if self.sidebar_checkbox_all.isChecked():
            name = basename.replace('basename', 'full_mask')
            try:
                mask = SLIX.classification.full_mask(loaded_parameter_maps['high_prominence_peaks'],
                                                     loaded_parameter_maps['low_prominence_peaks'],
                                                     loaded_parameter_maps['peakdistance'],
                                                     loaded_parameter_maps['max'])
                filename = f'{folder}/{name}.tiff'
                SLIX.io.imwrite(filename, mask)
            except KeyError:
                QMessageBox.warning(self, "Error", "Could not generate mask.\n"
                                                   "Make sure you have selected a folder with all parameter maps.")
                return
