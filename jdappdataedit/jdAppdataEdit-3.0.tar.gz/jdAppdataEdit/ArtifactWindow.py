from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QLineEdit
from .Functions import is_url_valid, calculate_checksum_from_url
from PyQt6.QtCore import QCoreApplication, Qt
from typing import Optional
from lxml import etree
from PyQt6 import uic
import requests
import sys
import os


class ArtifactWindow(QDialog):
    def __init__(self, env, releases_window):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "ArtifactWindow.ui"), self)

        self._releases_window = releases_window

        self._checksum_list = []
        for key, value in vars(self).items():
            if key.startswith("checksum_edit_"):
                self._checksum_list.append(key[14:])

        self.platform_box.addItem(QCoreApplication.translate("ArtifactWindow", "Unknown"), "unknown")
        self.platform_box.addItems(env.platform_list)

        self.type_rad_source.toggled.connect(self._update_platform_enabled)
        self.calculate_checksums_button.clicked.connect(self._calculate_checksums_button_clicked)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _check_url(self) -> bool:
        url = self.url_edit.text()
        if len(url) == 0:
            QMessageBox.critical(self, QCoreApplication.translate("ArtifactWindow", "No URL"), QCoreApplication.translate("ArtifactWindow", "Please enter a URL"))
            return False
        if not is_url_valid(self.url_edit.text()):
            QMessageBox.critical(self, QCoreApplication.translate("ArtifactWindow", "Invalid URL"), QCoreApplication.translate("ArtifactWindow", "Please enter a valid URL"))
            return False
        return True

    def _check_checksums_exists(self) -> bool:
        for i in self._checksum_list:
            if getattr(self, "checksum_edit_" + i).text() != "":
                return True
        QMessageBox.critical(self, QCoreApplication.translate("ArtifactWindow", "No checksums"), QCoreApplication.translate("ArtifactWindow", "You need at least one checksum"))
        return False

    def _update_platform_enabled(self):
        enabled = self.type_rad_binary.isChecked()
        self.platform_label.setEnabled(enabled)
        self.platform_box.setEnabled(enabled)

    def _calculate_checksums_button_clicked(self):
        if not self._check_url():
            return

        url = self.url_edit.text()

        for i in self._checksum_list:
            try:
                checksum = calculate_checksum_from_url(url, i)
                if checksum is None:
                     QMessageBox.critical(self, QCoreApplication.translate("ArtifactWindow", "Invalid URL"), QCoreApplication.translate("ArtifactWindow", "Can't get the File from the URL"))
                     return
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, QCoreApplication.translate("ArtifactWindow", "Invalid URL"), QCoreApplication.translate("ArtifactWindow", "Can't get the File from the URL"))
                return
            except Exception:
                QMessageBox.critical(self, QCoreApplication.translate("ArtifactWindow", "Error"), QCoreApplication.translate("ArtifactWindow", "A Error happened while calculatig the checksum"))
                return
            getattr(self, "checksum_edit_" + i).setText(checksum)

    def _ok_button_clicked(self):
        if not self._check_url():
            return

        if not self._check_checksums_exists():
            return

        atrtifact_tag =  etree.Element("artifact")

        if self.type_rad_source.isChecked():
            atrtifact_tag.set("type", "source")
        else:
            atrtifact_tag.set("type", "binary")
            if self.platform_box.currentData() != "unknown":
                atrtifact_tag.set("platform", self.platform_box.currentText())

        location_tag = etree.SubElement(atrtifact_tag, "location")
        location_tag.text = self.url_edit.text()

        if self._position is None:
            row = self._releases_window.artifacts_table.rowCount()
            self._releases_window.add_artifacts_row(row)
        else:
            row = self._position

        for i in self._checksum_list:
            checksum = getattr(self, "checksum_edit_" + i).text()
            if checksum != "":
                checksum_tag = etree.SubElement(atrtifact_tag, "checksum")
                checksum_tag.set("type", i)
                checksum_tag.text = checksum

        for i in ["download", "installed"]:
            size = getattr(self, "size_edit_" + i).text()
            if size != "":
                size_tag = etree.SubElement(atrtifact_tag, "size")
                size_tag.set("type", i)
                size_tag.text = size

        if self.filename_edit.text() != "":
            filename_tag = etree.SubElement(atrtifact_tag, "filename")
            filename_tag.text = self.filename_edit.text()

        location_item = QTableWidgetItem(self.url_edit.text())
        location_item.setFlags(location_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
        location_item.setData(42, atrtifact_tag)
        self._releases_window.artifacts_table.setItem(row, 0, location_item)

        self.close()

    def _reset_data(self):
        for key, value in vars(self).items():
            if isinstance(value, QLineEdit):
                value.setText("")
        self.type_rad_source.setChecked(True)
        self.platform_box.setCurrentIndex(0)

    def _load_data(self, atrtifact_tag: etree.Element):
        if atrtifact_tag.get("type") == "source":
            self.type_rad_source.setChecked(True)
        else:
            self.type_rad_binary.setChecked(True)
            index = self.platform_box.findText(atrtifact_tag.get("platform"))
            if index != -1:
                self.platform_box.setCurrentIndex(index)

        location_tag = atrtifact_tag.find("location")
        if location_tag is not None:
            self.url_edit.setText(location_tag.text)

        for i in atrtifact_tag.findall("checksum"):
            try:
                getattr(self, "checksum_edit_" + i.get("type")).setText(i.text)
            except AttributeError:
                print(i.get("type") + " is a invalid type for a checksum", file=sys.stderr)

        for i in atrtifact_tag.findall("size"):
            try:
                getattr(self, "size_edit_" + i.get("type")).setText(i.text)
            except AttributeError:
                print(i.get("type") + " is a invalid type for a size", file=sys.stderr)

        filename_tag = atrtifact_tag.find("filename")
        if filename_tag is not None:
            self.filename_edit.setText(filename_tag.text)

    def open_window(self, position: Optional[int]):
        self._position = position

        self._reset_data()

        if position is not None:
            self.setWindowTitle(QCoreApplication.translate("ArtifactWindow", "Edit Artifact"))
            data = self._releases_window.artifacts_table.item(position, 0).data(42)
            self._load_data(data)
        else:
            self.setWindowTitle(QCoreApplication.translate("ArtifactWindow", "Add Artifact"))

        self._update_platform_enabled()

        self.exec()
