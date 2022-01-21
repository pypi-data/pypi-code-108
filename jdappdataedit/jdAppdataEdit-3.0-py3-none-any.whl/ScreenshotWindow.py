from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QIntValidator, QPixmap
from PyQt6.QtCore import QCoreApplication
from .Functions import is_url_valid
from typing import Union
from PyQt6 import uic
import requests
import copy
import os


class ScreenshotWindow(QDialog):
    def __init__(self, env, main_window):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "ScreenshotWindow.ui"), self)

        self._main_window = main_window

        self.height_edit.setValidator(QIntValidator())
        self.width_edit.setValidator(QIntValidator())

        self.translate_caption_button.clicked.connect(lambda: env.translate_window.open_window(self._caption_translations))
        self.preview_button.clicked.connect(self._preview_button_clicked)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _check_url(self) -> bool:
        url = self.url_edit.text()
        if len(url) == 0:
            QMessageBox.critical(self, QCoreApplication.translate("ScreenshotWindow", "No URL"), QCoreApplication.translate("ScreenshotWindow", "Please enter a URL"))
            return False
        if not is_url_valid(self.url_edit.text()):
            QMessageBox.critical(self, QCoreApplication.translate("ScreenshotWindow", "Invalid URL"), QCoreApplication.translate("ScreenshotWindow", "Please enter a valid URL"))
            return False
        return True

    def _preview_button_clicked(self):
        if not self._check_url():
            return

        try:
            r = requests.get(self.url_edit.text(), stream=True)
        except Exception:
            QMessageBox.critical(self, QCoreApplication.translate("ScreenshotWindow", "Can't get Image"), QCoreApplication.translate("ScreenshotWindow", "It looks like the given URL does not work"))
            return

        pixmap = QPixmap()
        if pixmap.loadFromData(r.raw.read()):
            self.image_label.setPixmap(pixmap.scaled(256, 256))
        else:
            QMessageBox.critical(self, QCoreApplication.translate("ScreenshotWindow", "Can't decode Image"), QCoreApplication.translate("ScreenshotWindow", "The given Image can't be decoded"))

    def _ok_button_clicked(self):
        if not self._check_url():
            return

        new_dict = {}
        new_dict["url"] = self.url_edit.text()
        if self.width_edit.text() != "":
            new_dict["width"] = int(self.width_edit.text())
        if self.height_edit.text() != "":
            new_dict["height"] = int(self.height_edit.text())
        if self.caption_edit.text() != "":
            new_dict["caption"] = self.caption_edit.text()
        new_dict["caption_translations"] = copy.copy(self._caption_translations)

        if len(self._main_window.screenshot_list) == 0:
            new_dict["default"] = True
        else:
            new_dict["default"] =  self._main_window.screenshot_list[self._position]["default"]

        if self._position is None:
            self._main_window.screenshot_list.append(new_dict)
        elif self._position is None:
            new_dict["default"] = False
        else:
            self._main_window.screenshot_list[self._position] = new_dict

        self._main_window.update_sceenshot_table()
        self._main_window.set_file_edited()
        self.close()

    def open_window(self, position: Union[int, None]):
        self._position = position

        if position is None:
            self.url_edit.setText("")
            self.width_edit.setText("")
            self.height_edit.setText("")
            self.caption_edit.setText("")
            self._caption_translations = {}
            self.setWindowTitle(QCoreApplication.translate("ScreenshotWindow", "Add Screenshot"))
        else:
            current_entry = self._main_window.screenshot_list[position]
            self.url_edit.setText(current_entry["url"])
            if "width" in current_entry:
                self.width_edit.setText(str(current_entry["width"]))
            else:
                self.width_edit.setText("")
            if "height" in current_entry:
                self.height_edit.setText(str(current_entry["height"]))
            else:
                 self.height_edit.setText("")
            if "caption" in current_entry:
                self.caption_edit.setText(current_entry["caption"])
            else:
                self.caption_edit.setText("")
            self._caption_translations = copy.copy(current_entry["caption_translations"])
            self.setWindowTitle(QCoreApplication.translate("ScreenshotWindow", "Edit Screenshot"))

        self.image_label.clear()
        self.image_label.setText(QCoreApplication.translate("ScreenshotWindow", "If you click Preview, your Screenshot will appear here scaled by 256x256"))

        self.exec()
