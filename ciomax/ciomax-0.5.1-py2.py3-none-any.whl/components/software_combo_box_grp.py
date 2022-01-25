from PySide2 import QtWidgets, QtCore

from ciomax.components import widgets


class SoftwareComboBoxGrp(QtWidgets.QWidget):
    """Combo box triple for host software, renderers, and versions.

    The model is a tree of depth 3, and therefore the second combo box is
    maintained to always contain the children of the model item selected in the
    first combo box and the 3rd combo box is maintained to always contain the
    children of the model item selected in the second combo box.
    """

    def __init__(self, show_host=False):
        """Create the widgets"""
        super(SoftwareComboBoxGrp, self).__init__()
        self.scale_factor = self.logicalDpiX() / 96.0
        self.model = None

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        top_layout = QtWidgets.QHBoxLayout()
        bottom_layout = QtWidgets.QHBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        label = widgets.FormLabel("3ds Max version")
        top_layout.addWidget(label)
        self.combobox_host = QtWidgets.QComboBox()
        top_layout.addWidget(self.combobox_host)
        top_layout.addSpacing(85 * self.scale_factor)
        if not show_host:
            label.hide()
            self.combobox_host.hide()


        bottom_layout.addWidget(widgets.FormLabel("Renderer version"))
        self.combobox_renderer_name = QtWidgets.QComboBox()
        self.combobox_renderer_version = QtWidgets.QComboBox()
        bottom_layout.addWidget(self.combobox_renderer_name)
        bottom_layout.addWidget(self.combobox_renderer_version)
        bottom_layout.addSpacing(85 * self.scale_factor)

        self.combobox_host.currentIndexChanged.connect(self._host_changed)
        self.combobox_renderer_name.currentIndexChanged.connect(self._renderer_changed)

    def set_model(self, model):
        """Attach the model and set the widgets to the appropriate model depth."""
        self.model = model
        self.combobox_host.setModel(self.model)
        self.combobox_renderer_name.setModel(self.model)
        self.combobox_renderer_version.setModel(self.model)

        renderer_model_index = self.model.index(0, 0, QtCore.QModelIndex())
        self.combobox_renderer_name.setRootModelIndex(renderer_model_index)

        version_model_index = self.model.index(0, 0, renderer_model_index)
        self.combobox_renderer_version.setRootModelIndex(version_model_index)

    def set_host_by_text(self, text):
        """Set the host combo box to given 3dsmax version if it is available."""
        if not self.model:
            return
        host_row_count = self.model.rowCount()
        for row in range(host_row_count):
            if self.model.item(row).text() == text:
                self.combobox_host.setCurrentIndex(row)
                return
        # If desired version not found, choose the most recent version.
        self.combobox_host.setCurrentIndex(host_row_count-1)

    def set_renderer_by_text(self, text):
        """Set the renderer/veresion combo boxes to given renderer if it is available."""
        if not self.model:
            return
        found_renderer = False
        renderer_text, version_text = text.split(" ")

        host_item = self.model.item(self.combobox_host.currentIndex())
        renderer_row = 0
        for renderer_row in range(host_item.rowCount()):
            if host_item.child(renderer_row, 0).text() == renderer_text:

                found_renderer = True
                self.combobox_renderer_name.setCurrentIndex(renderer_row)
                break
        if not found_renderer:
            self.combobox_renderer_name.setCurrentIndex(0)  # triggers version model change
            self.combobox_renderer_version.setCurrentIndex(0)
            return

        renderer_item = host_item.child(renderer_row, 0)
        version_row_count = renderer_item.rowCount()
        for version_row in range(version_row_count):
            if renderer_item.child(version_row, 0).text() == version_text:
                self.combobox_renderer_version.setCurrentIndex(version_row)
                return
        # If desired version not found, choose the most recent version.
        self.combobox_renderer_version.setCurrentIndex(version_row_count-1)

    def get_renderer(self):
        return "{} {}".format(
            self.combobox_renderer_name.currentText(),
            self.combobox_renderer_version.currentText(),
            
        )
        
    ############ PRIVATE ############
    def _host_changed(self, host_row):
        # When host changes, update the selection of renderers 
        if not self.model:
            return

        # remember the text for currently selected renderer
        renderer_text = self.combobox_renderer_name.currentText()

        renderer_model_index = self.model.index(host_row, 0)
        self.combobox_renderer_name.setRootModelIndex(renderer_model_index)

        renderer_row = self._find_renderer_row(host_row, renderer_text)
        # When we set the renderer combo box, _renderer_changed() is called.
        self.combobox_renderer_name.setCurrentIndex(renderer_row)

    def _renderer_changed(self, renderer_row):
        # When renderer changes, update the selection of versions 
        if not self.model:
            return
        host_row = self.combobox_host.currentIndex()

        # remember the text for currently selected version
        version_text = self.combobox_renderer_version.currentText()

        renderer_model_index = self.model.index(host_row, 0)
        version_model_index = self.model.index(
            renderer_row, 0, renderer_model_index)
        self.combobox_renderer_version.setRootModelIndex(version_model_index)

        version_row = self._find_version_row(
            host_row, renderer_row, version_text)
        self.combobox_renderer_version.setCurrentIndex(version_row)

    def _find_renderer_row(self, host_row,  renderer_text):
        # renderer row from text
        host_item = self.model.item(host_row)
        for renderer_row in range(host_item.rowCount()):
            if host_item.child(renderer_row, 0).text() == renderer_text:
                return renderer_row
        return 0

    def _find_version_row(self, host_row, renderer_row, version_text):
        # version row from text
        renderer_item = self.model.item(host_row).child(renderer_row, 0)
        for version_row in range(renderer_item.rowCount()):
            if renderer_item.child(version_row, 0).text() == version_text:
                return version_row
        return 0
