from .Functions import clear_table_widget, select_combo_box_data, get_logical_table_row_list, stretch_table_widget_colums_size
from PyQt6.QtWidgets import QDialog, QComboBox, QPushButton, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QCoreApplication, QLocale
from typing import Dict, Optional
from PyQt6 import uic
import os


class TranslateWindow(QDialog):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "TranslateWindow.ui"), self)

        self._env = env

        stretch_table_widget_colums_size(self.table_widget)

        self.table_widget.verticalHeader().setSectionsMovable(True)

        self.add_button.clicked.connect(self._add_row)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _add_row(self, language: Optional[str] = None, text: Optional[str] = None):
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)

        language_box = QComboBox()
        language_box.setPlaceholderText(QCoreApplication.translate("TranslateWindow", "Select Language"))
        for i in self._env.language_codes:
            language_box.addItem(QLocale.languageToString(QLocale(i).language()) + " (" + i + ")", i)
        if not language is None:
            select_combo_box_data(language_box, language, default_index=-1)
        else:
            language_box.setCurrentIndex(-1)
        self.table_widget.setCellWidget(row, 0, language_box)

        if text is None:
            self.table_widget.setItem(row, 1, QTableWidgetItem())
        else:
            self.table_widget.setItem(row, 1, QTableWidgetItem(text))

        remove_button = QPushButton(QCoreApplication.translate("TranslateWindow", "Remove"))
        remove_button.clicked.connect(self._remove_button_clicked)
        self.table_widget.setCellWidget(row, 2, remove_button)

    def _remove_button_clicked(self):
        for i in range(self.table_widget.rowCount()):
            if self.table_widget.cellWidget(i, 2) == self.sender():
                self.table_widget.removeRow(i)
                return

    def _check_valid(self) -> bool:
        known_languages = []
        for i in range(self.table_widget.rowCount()):
            if self.table_widget.cellWidget(i, 0).currentIndex() == -1:
                QMessageBox.critical(self, QCoreApplication.translate("TranslateWindow", "No Language selected"), QCoreApplication.translate("TranslateWindow", "You had no Language selected for at least one Item"))
                return False

            name = self.table_widget.cellWidget(i, 0).currentText()
            language = self.table_widget.cellWidget(i, 0).currentData()
            if language in known_languages:
                QMessageBox.critical(self, QCoreApplication.translate("TranslateWindow", "Language double"), QCoreApplication.translate("TranslateWindow", "{name} appears twice or more times in the table").format(name=name))
                return False
            known_languages.append(language)
            if self.table_widget.item(i, 1).text() == "":
                QMessageBox.critical(self, QCoreApplication.translate("TranslateWindow", "No Text"), QCoreApplication.translate("TranslateWindow", "The Translation for {name} has no Text").format(name=name))
                return False
        return True

    def _ok_button_clicked(self):
        if not self._check_valid():
            return

        self._current_dict.clear()
        for i in get_logical_table_row_list(self.table_widget):
            language = self.table_widget.cellWidget(i, 0).currentData()
            text = self.table_widget.item(i, 1).text()
            self._current_dict[language] = text

        if self._main_window:
            self._main_window.set_file_edited()

        self._saved = True

        self.close()

    def open_window(self, current_dict: Dict[str, str], main_window = None) -> bool:
        self._current_dict = current_dict
        self._saved = False

        if main_window:
            self._main_window = main_window
        else:
            self._main_window = None

        clear_table_widget(self.table_widget)

        for key, value in current_dict.items():
            self._add_row(language=key, text=value)

        self.exec()

        return self._saved
