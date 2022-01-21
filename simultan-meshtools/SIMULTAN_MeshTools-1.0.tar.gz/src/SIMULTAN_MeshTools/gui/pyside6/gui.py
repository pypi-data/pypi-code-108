import sys
import os
import logging
import warnings
from tkinter import *
from tkinter.filedialog import askopenfile, asksaveasfile
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

from PySide6 import QtCore, QtGui, QtWidgets, QtConcurrent
from PySide6.QtWidgets import QApplication, QMainWindow

from PySimultan.data_model import GeometryModel

from ...project import ProjectLoader
from ...logger import logger, formatter

logger2 = logging.getLogger('PySimultan')

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 importlib_resources.
    import importlib_resources as pkg_resources

Tk().withdraw()


from ...resources.gui.ui_main_window import Ui_MainWindow


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.ERROR:   ("[%(levelname)-8s] %(message)s", QtGui.QColor("red")),
        logging.DEBUG:   ("[%(levelname)-8s] [%(filename)s:%(lineno)d] %(message)s", "green"),
        logging.INFO:    ("[%(levelname)-8s] %(message)s", "green"),
        logging.WARNING: ('%(asctime)s - %(name)s - %(levelname)s - %(message)s', QtGui.QColor(100, 100, 0))
    }

    def format( self, record ):
        last_fmt = self._style._fmt
        opt = CustomFormatter.FORMATS.get(record.levelno)
        if opt:
            fmt, color = opt
            self._style._fmt = "<font color=\"{}\">{}</font>".format(QtGui.QColor(color).name(),fmt)
        res = logging.Formatter.format( self, record )
        self._style._fmt = last_fmt
        return res


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.add_functions()

        # program content
        self._project_loader = None

        self.geo_models = {}
        self.tables = {}
        self.tables_list_model = None

        self.settings = QtCore.QSettings()

    @property
    def project_filename(self):
        return self.ui.project_lineEdit.text()

    @property
    def username(self):
        return self.ui.user_lineEdit.text()

    @property
    def password(self):
        return self.ui.password_lineEdit.text()

    @property
    def project_loader(self):
        if self._project_loader is None:

            if not self.project_filename:
                logger.error(f'No project selected. Please select a project!')
                return
            else:
                # check if file exists:
                if not os.path.isfile(self.project_filename):
                    logger.error(
                        f'Project {self.project_filename} not found. Please check the path and the name of the project!')
                    return

            if not self.username:
                logger.error(f'No user name defined. Please define a user name!')
                return
            if not self.password:
                logger.error(f'No password defined. Please define a password!')
                return

            try:
                self._project_loader = ProjectLoader(project_filename=self.project_filename,
                                                     user_name=self.username,
                                                     password=self.password,
                                                     app=self)
            except Exception as e:
                logger.error(f'Error creating project loader:\n{e}')

        return self._project_loader

    @project_loader.setter
    def project_loader(self, value):
        self._project_loader = value

    @property
    def last_path(self):
        last_path = self.settings.value("LAST_PATH", ".")
        return last_path

    @last_path.setter
    def last_path(self, value):
        self.settings.setValue("LAST_PATH", value)

    @property
    def mesh_format(self):
        return '.' + self.ui.mesh_format_comboBox.currentText()

    def add_functions(self):
        self.ui.cp_pushButton.clicked.connect(self.choose_project)
        self.ui.load_project_pushButton.clicked.connect(self.load_project)
        self.ui.password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        text_browser = self.ui.log_plainTextEdit
        text_browser.setReadOnly(True)
        scrollbar = text_browser.verticalScrollBar()

        class GuiLogger(logging.Handler):
            def emit(self, record):
                text_browser.appendHtml(self.format(record))
                scrollbar.setValue(scrollbar.maximum())

        h = GuiLogger()
        h.setFormatter(CustomFormatter())
        logger.addHandler(h)

        self.ui.close_project_pushButton.clicked.connect(self.close_project)

        # mesh stuff:
        self.ui.select_file_pushButton.clicked.connect(self.select_mesh_file)
        self.ui.save_mesh_pushButton.clicked.connect(self.save_mesh)
        self.ui.mesh_format_comboBox.currentTextChanged.connect(self.mesh_format_changed)

    def choose_project(self, *args, **kwargs):
        # filename, filter = QtWidgets.QFileDialog.getOpenFileName(parent=self, caption='Open file', dir=self.last_path,
        #                                                          filter='*.simultan')
        filename = askopenfile(title='Select a SIMULTAN Project...',
                               filetypes=[("SIMULTAN", ".simultan")])
        if filename is None:
            logger.warning(f'Did not choose any project')
            return
        else:
            filename = filename.name

        self.last_path = os.path.dirname(filename)

        if filename:
            self.ui.project_lineEdit.setText(filename)

    def select_mesh_file(self, *args, **kwargs):
        # filename, filter = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption='Save file', dir=self.last_path,
        #                                                          filter='*' + self.mesh_format)

        filename = asksaveasfile(title='Select output mesh file...',
                                 filetypes=[(self.mesh_format, self.mesh_format)],
                                 defaultextension=self.mesh_format)

        if filename is None:
            logger.warning(f'Did not choose any project')
            return
        else:
            filename = filename.name

        filename += self.mesh_format
        self.last_path = os.path.dirname(filename)

        if filename:
            self.ui.mesh_output_lineEdit.setText(filename)

    def load_project(self):
        if self.project_loader is None:
            logger2.error(f'No project loader')
            logger.error('Could not load project')
            return

        try:
            self.project_loader.load_project()
        except Exception as e:
            logger.error(f'Error loading project:\n{e}')

        logger.info(f'Project loaded successfully\n\n')

        self.update_mesh_options()

    def close_project(self):
        if self.project_loader is None:
            logger2.error(f'No project loader')
            return

        if self.project_loader.loaded:
            try:
                self.project_loader.close_project()
                self.project_loader = None
            except Exception as e:
                logger.error(f'Error closing project:\n{e}')
        else:
            logger.info('No project loaded')

    def save_project(self):
        if self.project_loader is None:
            logger2.error(f'No project loader')
            return

        if self.project_loader.loaded:
            try:
                self.project_loader.save()
                logger.info(f'Project saved successfully')
            except Exception as e:
                logger.error(f'Error saving project:\n{e}')
        else:
            logger.info('No project loaded')

    def update_mesh_options(self):

        self.geo_models = {}

        for key, model in self.project_loader.data_model.models_dict.items():
            if isinstance(model, GeometryModel):
                self.geo_models[os.path.basename(model.File.FullPath)] = model

        self.tables = {}
        for value_field in self.project_loader.data_model.ValueFields:
            self.tables[value_field.Name] = value_field

        self.tables_list_model = QtGui.QStandardItemModel()
        for string in self.tables.keys():
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            self.tables_list_model.appendRow(item)
        self.ui.tables_listView.setModel(self.tables_list_model)

        self.ui.geometry_comboBox.addItems(self.geo_models.keys())

        logger.info('Updated geometries and tables')

    def save_mesh(self):

        if not self.ui.mesh_output_lineEdit.text():
            logger.error(f'No mesh output file defined')
            return

        geometry_index = self.ui.geometry_comboBox.currentText()
        geo_model = self.geo_models[geometry_index]

        tables = []
        for i in range(self.tables_list_model.rowCount()):
            item = self.tables_list_model.item(i)
            if item.checkState() is QtCore.Qt.CheckState.Checked:
                tables.append(self.tables[item.text()])

        # get mesh format:
        try:
            self.project_loader.run(geo_model=geo_model,
                                    tables=tables,
                                    mesh_filename=self.ui.mesh_output_lineEdit.text(),
                                    mesh_format=self.mesh_format)
        except Exception as e:
            logger.error(f'Error saving mesh:\n{e}')

        logger.info(f'Mesh exported successfully')

    def mesh_format_changed(self, value):
        self.ui.mesh_output_lineEdit.setText('')


def main():
    app = QApplication(sys.argv)

    app.setOrganizationName("TU Wien")
    app.setOrganizationDomain("https://www.bph.tuwien.ac.at")
    app.setApplicationName("SIMULTAN Mesh tools")
    window = MainWindow()
    window.show()
    app.exec()
    sys.exit()
