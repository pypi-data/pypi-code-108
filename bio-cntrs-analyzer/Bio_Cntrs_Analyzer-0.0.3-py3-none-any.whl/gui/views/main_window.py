import os

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QMainWindow
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QFileDialog, QProgressDialog, QSplitter
from PyQt5.QtWidgets import QSizePolicy, QProgressDialog
from PyQt5.QtGui import QIcon

from bcanalyzer.common.settings import AppSettings
from bcanalyzer.gui.widgets.about_widget import AboutWidget

from bcanalyzer.gui.widgets.processing_preview_widget import ProcessingPreviewWidget
from bcanalyzer.gui.widgets.processing_list_widget import ProcessinListWidget
from bcanalyzer.common.const import APP_NAME


class Main_GUI(QMainWindow):
    onClose = pyqtSignal()

    export_all = pyqtSignal(str, str)
    export_renders = pyqtSignal(str)
    export_stat = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._title = APP_NAME
        self.setupUi()
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setAcceptDrops(True)
        self._pd = None

    def setupUi(self):
        """constructs the GUI  """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setWindowTitle(self._title)

        ### creating the menu ###
        self._menu_bar = self.menuBar()

        self._menu_file = self._menu_bar.addMenu("File")

        self._submenu_export = self._menu_file.addMenu("Export")

        self.submenu_export_all = self._submenu_export.addAction(
            "All")
        self.submenu_export_all.triggered.connect(
            self.submenu_export_all_clicked)

        self.submenu_export_renders = self._submenu_export.addAction(
            "Renders")
        self.submenu_export_renders.triggered.connect(
            self.submenu_export_renders_clicked)

        self.submenu_export_stat = self._submenu_export.addAction(
            "Statistic")
        self.submenu_export_stat.triggered.connect(
            self.submenu_export_stat_clicked)

        self._menu_file.addSeparator()

        action = self._menu_file.addAction("Exit")
        action.triggered.connect(self.exit_clicked)

        self._menu_help = self._menu_bar.addMenu("Help")
        self._menu_help.addSeparator()
        action = self._menu_help.addAction("About")
        action.triggered.connect(self.about_clicked)

        ### create status bar ###

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

        ### Widgets ###
        self._main_widget = QSplitter(self)
        self._main_widget.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Main Layout
        self.processing_list_widget = ProcessinListWidget(self)

        self._main_widget.addWidget(self.processing_list_widget)

        self.processing_widget = ProcessingPreviewWidget()
        self._main_widget.addWidget(self.processing_widget)

        self.setCentralWidget(self._main_widget)
        # Icon
        res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "resources")
        QApplication.instance().setWindowIcon(
            QIcon(os.path.join(res_path, "logo.ico")))

    def set_processing_list_model(self, processing_list_model):
        self.processing_list_widget.set_processing_list_model(
            processing_list_model)

    def show_progress_dialog(self, labelText, minimum, maximum, cancelButtonText="Cancel"):
        self._pd = QProgressDialog(labelText,
                                   cancelButtonText,
                                   minimum,
                                   maximum,
                                   self)
        self._pd.setValue(0)
        self._pd.setWindowModality(Qt.WindowModal)

        return self._pd

    def select_folder_dialog_launch(self, question="Select folder"):
        chosen_dir = QFileDialog.getExistingDirectory(None, "Select folder",
                                                      (AppSettings().getParam('last_open_export_dir', "./")))
        if os.path.exists(chosen_dir):
            AppSettings().setParam('last_open_export_dir', chosen_dir)
            return chosen_dir
        return None

    def select_target_file_dialog_launch(self, question="Save report"):
        file_path = QFileDialog.getSaveFileName(None, question,
                                                AppSettings().getParam('last_open_export_dir', "./"),
                                                "CSV-file (*.csv)")[0]
        if os.path.exists(os.path.dirname(file_path)):
            AppSettings().setParam('last_open_export_dir', os.path.dirname(file_path))
        return file_path

    @pyqtSlot()
    def exit_clicked(self):
        self.onClose.emit()
        self.deleteLater()
        self.destroy(True, True)
        QApplication.closeAllWindows()
        QCoreApplication.instance().quit()

    @pyqtSlot()
    def about_clicked(self):
        self.aboutWidget = AboutWidget()
        self.aboutWidget.show()

    @pyqtSlot()
    def submenu_export_all_clicked(self):
        chosen_dir = self.select_folder_dialog_launch()
        chosen_file = self.select_target_file_dialog_launch()
        if chosen_dir is not None and chosen_file:
            self.export_all.emit(chosen_dir, chosen_file)

    @pyqtSlot()
    def submenu_export_renders_clicked(self):
        chosen_dir = self.select_folder_dialog_launch()
        if chosen_dir is not None:
            self.export_renders.emit(chosen_dir)

    @pyqtSlot()
    def submenu_export_stat_clicked(self):
        chosen_file = self.select_target_file_dialog_launch()
        if chosen_file:
            self.export_stat.emit(chosen_file)
