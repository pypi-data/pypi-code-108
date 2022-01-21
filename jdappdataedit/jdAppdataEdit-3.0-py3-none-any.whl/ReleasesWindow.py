from .Functions import get_logical_table_row_list, clear_table_widget, stretch_table_widget_colums_size, select_combo_box_data
from PyQt6.QtWidgets import QDialog, QPushButton, QTableWidgetItem
from .DescriptionWidget import DescriptionWidget
from PyQt6.QtCore import QCoreApplication, Qt
from .ArtifactWindow import ArtifactWindow
from lxml import etree
from PyQt6 import uic
import sys
import os


class ReleasesWindow(QDialog):
    def __init__(self, env, main_window):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "ReleasesWindow.ui"), self)

        self._main_window = main_window

        self._description_widget = DescriptionWidget(env)
        self.description_layout.addWidget(self._description_widget)

        self._artifacts_window = ArtifactWindow(env, self)

        self.urgency_box.addItem(QCoreApplication.translate("ReleasesWindow", "Not specified"), "none")
        self.urgency_box.addItem(QCoreApplication.translate("ReleasesWindow", "Low"), "low")
        self.urgency_box.addItem(QCoreApplication.translate("ReleasesWindow", "Medium"), "medium")
        self.urgency_box.addItem(QCoreApplication.translate("ReleasesWindow", "High"), "high")
        self.urgency_box.addItem(QCoreApplication.translate("ReleasesWindow", "Critical"), "critical")

        stretch_table_widget_colums_size(self.artifacts_table)
        self.artifacts_table.verticalHeader().setSectionsMovable(True)

        self.add_artifact_button.clicked.connect(lambda: self._artifacts_window.open_window(None))
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _edit_artifact_clicked(self):
        for i in range(self.artifacts_table.rowCount()):
            if self.artifacts_table.cellWidget(i, 1) == self.sender():
                self._artifacts_window.open_window(i)

    def _remove_artifact_clicked(self):
        for i in range(self.artifacts_table.rowCount()):
            if self.artifacts_table.cellWidget(i, 2) == self.sender():
                self.artifacts_table.removeRow(i)

    def _ok_button_clicked(self):
        new_dict = {}

        if self.url_edit.text() != "":
            new_dict["url"] = self.url_edit.text()

        if self.urgency_box.currentData() != "none":
            new_dict["urgency"] = self.urgency_box.currentData()

        description_tag = etree.Element("description")
        self._description_widget.get_tags(description_tag)
        if len(description_tag.getchildren()) > 0:
            new_dict["description"] = description_tag

        if self.artifacts_table.rowCount() > 0:
            artifacts_tag = etree.Element("artifacts")
            for i in get_logical_table_row_list(self.artifacts_table):
                artifacts_tag.append(self.artifacts_table.item(i, 0).data(42))
            new_dict["artifacts"] = artifacts_tag

        self._main_window.releases_table.item(self._position, 0).setData(42, new_dict)

        self._main_window.set_file_edited()

        self.close()

    def add_artifacts_row(self, row: int):
        self.artifacts_table.insertRow(row)

        edit_button = QPushButton(QCoreApplication.translate("ReleasesWindow", "Edit"))
        edit_button.clicked.connect(self._edit_artifact_clicked)
        self.artifacts_table.setCellWidget(row, 1, edit_button)

        remove_button = QPushButton(QCoreApplication.translate("ReleasesWindow", "Remove"))
        remove_button.clicked.connect(self._remove_artifact_clicked)
        self.artifacts_table.setCellWidget(row, 2, remove_button)

    def open_window(self, position: int):
        self._position = position

        data = self._main_window.releases_table.item(self._position, 0).data(42)

        if "url" in data:
            self.url_edit.setText(data["url"])
        else:
            self.url_edit.setText("")

        if "urgency"in data:
            select_combo_box_data(self.urgency_box, data["urgency"])
        else:
            self.urgency_box.setCurrentIndex(0)

        self._description_widget.reset_data()
        if "description" in data:
            self._description_widget.load_tags(data["description"])

        clear_table_widget(self.artifacts_table)
        if "artifacts" in data:
            for i in data["artifacts"].findall("artifact"):
                location_tag = i.find("location")
                if location_tag is None:
                    print("artifact has no location tag", file=sys.stderr)
                    continue

                row = self.artifacts_table.rowCount()
                self.add_artifacts_row(row)

                location_item = QTableWidgetItem(location_tag.text)
                location_item.setFlags(location_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                location_item.setData(42, i)
                self.artifacts_table.setItem(row, 0, location_item)

        self.main_tab_widget.setCurrentIndex(0)

        self.exec()
