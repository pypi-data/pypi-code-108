from .Functions import select_combo_box_data, is_string_number, get_logical_table_row_list, clear_table_widget
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QIntValidator
from typing import Optional, List
from lxml import etree
from PyQt6 import uic
import sys
import os


class RelationsWidget(QWidget):
    def __init__(self, env, main_window):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "RelationsWidget.ui"), self)

        self._main_window = main_window

        for key, value in vars(self).items():
            if key.startswith("rad_screen_device_class_"):
                value.setChecked(True)
                value.toggled.connect(self._update_screen_widgets_enabled)
            elif key.startswith("box_screen_device_class_"):
                value.addItem(QCoreApplication.translate("RelationsWidget", "Not specified"), "none")
                value.addItem(QCoreApplication.translate("RelationsWidget", "Very small screens e.g. wearables"), "xsmall")
                value.addItem(QCoreApplication.translate("RelationsWidget", "Small screens e.g. phones"), "small")
                value.addItem(QCoreApplication.translate("RelationsWidget", "Screens in laptops, tablets"), "medium")
                value.addItem(QCoreApplication.translate("RelationsWidget", "Bigger computer monitors"), "large")
                value.addItem(QCoreApplication.translate("RelationsWidget", "Television screens, large projected images"), "xlarge")
            elif key.startswith("edit_screen_custom_"):
                value.setValidator(QIntValidator())

            if isinstance(value, QComboBox):
                value.currentIndexChanged.connect(main_window.set_file_edited)
            elif isinstance(value, QLineEdit):
                value.textEdited.connect(main_window.set_file_edited)

        self.edit_memory_requires.setValidator(QIntValidator())
        self.edit_memory_recommends.setValidator(QIntValidator())

        self.modalias_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.hardware_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.modalias_table.verticalHeader().setSectionsMovable(True)
        self.hardware_table.verticalHeader().setSectionsMovable(True)

        self.button_modalias_add.clicked.connect(self._add_modalias_row)
        self.button_hardware_add.clicked.connect(self._add_hardware_row)

        self._update_screen_widgets_enabled()

        self.main_tab_widget.setCurrentIndex(0)

    # Screen

    def _update_screen_widgets_enabled(self):
        for size in ("ge", "le"):
            for relation in ("requires", "recommends"):
                append_string = size + "_" + relation
                if getattr(self, "rad_screen_device_class_" + append_string).isChecked():
                    getattr(self, "box_screen_device_class_" + append_string).setEnabled(True)
                    getattr(self, "edit_screen_custom_" + append_string).setEnabled(False)
                else:
                    getattr(self, "box_screen_device_class_" + append_string).setEnabled(False)
                    getattr(self, "edit_screen_custom_" + append_string).setEnabled(True)

    def _load_screen_data(self, tag_list: List[etree.Element], relation: str):
        for i in tag_list:
            size = i.get("compare")
            if size is None:
                size = "ge"
            if size not in ("ge", "le"):
                print("Unsupported compare attribute " + size, file=sys.stderr)
                continue
            append_string = size + "_" + relation
            if is_string_number(i.text):
                getattr(self, "rad_screen_custom_" + append_string).setChecked(True)
                getattr(self, "edit_screen_custom_" + append_string).setText(i.text)
            else:
                select_combo_box_data(getattr(self, "box_screen_device_class_" + append_string), i.text)

    def _get_screen_save_data(self, parent_tag: etree.Element, relation: str):
        for size in ("ge", "le"):
            append_string = size + "_" + relation
            if getattr(self, "rad_screen_device_class_" + append_string).isChecked():
                box = getattr(self, "box_screen_device_class_" + append_string)
                if box.currentData() == "none":
                    continue
                display_tag = etree.SubElement(parent_tag, "display_length")
                display_tag.set("compare", size)
                display_tag.text = box.currentData()
            else:
                display_tag = etree.SubElement(parent_tag, "display_length")
                display_tag.set("compare", size)
                display_tag.text = getattr(self, "edit_screen_custom_" + append_string).text()

    # Modalias

    def _add_modalias_row(self, relation: Optional[str] = None, chid: Optional[str] = None):
        row = self.modalias_table.rowCount()
        self.modalias_table.insertRow(row)

        relation_box = QComboBox()
        relation_box.addItem(QCoreApplication.translate("RelationsWidget", "Supported"), "supports")
        relation_box.addItem(QCoreApplication.translate("RelationsWidget", "Recommend"), "recommends")
        relation_box.addItem(QCoreApplication.translate("RelationsWidget", "Required"), "requires")
        if relation is not None:
            select_combo_box_data(relation_box, relation)
        relation_box.currentIndexChanged.connect(self._main_window.set_file_edited)
        self.modalias_table.setCellWidget(row, 0, relation_box)

        item = QTableWidgetItem()
        if chid is not None:
            item.setText(chid)
        self.modalias_table.setItem(row, 1, item)

        remove_button = QPushButton(QCoreApplication.translate("RelationsWidget", "Remove"))
        remove_button.clicked.connect(self._remove_modalias_clicked)
        self.modalias_table.setCellWidget(row, 2, remove_button)

        self._main_window.set_file_edited()

    def _remove_modalias_clicked(self):
        for i in range(self.modalias_table.rowCount()):
            if self.modalias_table.cellWidget(i, 2) == self.sender():
                self.modalias_table.removeRow(i)
                self._main_window.set_file_edited()
                return

    # Hardware

    def _add_hardware_row(self, relation: Optional[str] = None, chid: Optional[str] = None):
        row = self.hardware_table.rowCount()
        self.hardware_table.insertRow(row)

        relation_box = QComboBox()
        relation_box.addItem(QCoreApplication.translate("RelationsWidget", "Supported"), "supports")
        relation_box.addItem(QCoreApplication.translate("RelationsWidget", "Recommend"), "recommends")
        relation_box.addItem(QCoreApplication.translate("RelationsWidget", "Required"), "requires")
        if relation is not None:
            select_combo_box_data(relation_box, relation)
        relation_box.currentIndexChanged.connect(self._main_window.set_file_edited)
        self.hardware_table.setCellWidget(row, 0, relation_box)

        item = QTableWidgetItem()
        if chid is not None:
            item.setText(chid)
        self.hardware_table.setItem(row, 1, item)

        remove_button = QPushButton(QCoreApplication.translate("RelationsWidget", "Remove"))
        remove_button.clicked.connect(self._remove_hardware_clicked)
        self.hardware_table.setCellWidget(row, 2, remove_button)

        self._main_window.set_file_edited()

    def _remove_hardware_clicked(self):
        for i in range(self.hardware_table.rowCount()):
            if self.hardware_table.cellWidget(i, 2) == self.sender():
                self.hardware_table.removeRow(i)
                self._main_window.set_file_edited()
                return

    def reset_data(self):
        for key, value in vars(self).items():
            if key.startswith("rad_screen_device_class_"):
                value.setChecked(True)
            elif isinstance(value, QComboBox):
                value.setCurrentIndex(0)
            elif isinstance(value, QLineEdit):
                value.setText("")
            elif isinstance(value, QTableWidget):
                clear_table_widget(value)

    def load_data(self, relation_tag: etree.Element):
        self._load_screen_data(relation_tag.findall("display_length"), relation_tag.tag)

        memory_tag = relation_tag.find("memory")
        if memory_tag is not None:
            if relation_tag.tag == "requires":
                self.edit_memory_requires.setText(memory_tag.text)
            elif relation_tag.tag == "recommends":
                self.edit_memory_recommends.setText(memory_tag.text)
            else:
                print("memory tag is only allowd in requires and recommends", file=sys.stderr)

        for i in relation_tag.findall("modalias"):
            self._add_modalias_row(relation=relation_tag.tag, chid=i.text)

        for i in relation_tag.findall("hardware"):
            self._add_hardware_row(relation=relation_tag.tag, chid=i.text)

    def get_save_data(self, parent_tag: etree.Element, relation: str):
        if relation == "requires" or relation == "recommends":
            self._get_screen_save_data(parent_tag, relation)

        if relation == "requires" and self.edit_memory_requires.text() != "":
            memory_tag = etree.SubElement(parent_tag, "memory")
            memory_tag.text = self.edit_memory_requires.text()
        elif relation == "recommends" and self.edit_memory_recommends.text() != "":
            memory_tag = etree.SubElement(parent_tag, "memory")
            memory_tag.text = self.edit_memory_recommends.text()

        for i in get_logical_table_row_list(self.modalias_table):
            if self.modalias_table.cellWidget(i, 0).currentData() == relation:
                modalias_tag = etree.SubElement(parent_tag, "modalias")
                modalias_tag.text =  self.modalias_table.item(i, 1).text()

        for i in get_logical_table_row_list(self.hardware_table):
            if self.hardware_table.cellWidget(i, 0).currentData() == relation:
                hardware_tag = etree.SubElement(parent_tag, "hardware")
                hardware_tag.text =  self.hardware_table.item(i, 1).text()
