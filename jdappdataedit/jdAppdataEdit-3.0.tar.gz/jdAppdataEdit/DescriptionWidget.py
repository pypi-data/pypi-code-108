from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QPlainTextEdit, QPushButton, QListWidget, QListWidgetItem, QHeaderView, QInputDialog, QAbstractItemView, QHBoxLayout, QVBoxLayout
from .Functions import clear_table_widget, get_logical_table_row_list
from PyQt6.QtCore import Qt, QCoreApplication
from typing import Dict, Optional
from lxml import etree
from PyQt6 import uic
import copy
import sys
import os


class ParagraphWidget(QWidget):
    def __init__(self, env, description_widget, text: Optional[str] = None, translations: Optional[Dict[str, str]] = None):
        super().__init__()

        self._env = env
        if translations is None:
            self._translations = {}
        else:
            self._translations = copy.copy(translations)
        self._description_widget = description_widget

        self._edit_widget = QPlainTextEdit()
        translate_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Translate"))

        if text is not None:
            self._edit_widget.setPlainText(text)

        self._edit_widget.textChanged.connect(description_widget.update_preview)
        translate_button.clicked.connect(self._translate_button_clicked)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._edit_widget)
        main_layout.addWidget(translate_button)

        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

    def _translate_button_clicked(self):
        self._env.translate_window.open_window(self._translations)
        self._description_widget.update_preview()

    def get_tag(self, parent_tag:  etree._Element, preview: bool = False):
        tag = etree.SubElement(parent_tag, "p")
        tag.text = self._edit_widget.toPlainText()
        if preview:
            return
        for key, value in self._translations.items():
            trans_tag = etree.SubElement(parent_tag, "p")
            trans_tag.set("{http://www.w3.org/XML/1998/namespace}lang", key)
            trans_tag.text = value


class ListWidget(QListWidget):
    def __init__(self, env, description_widget, list_type: str, parent_tag: Optional[etree._Element] = None):
        super().__init__()

        self._description_widget = description_widget
        self._list_type = list_type
        self._env = env

        self._list_widget = QListWidget()
        add_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Add"))
        edit_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Edit"))
        remove_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Remove"))
        translate_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Translate"))

        self._list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

        self._list_widget.model().rowsMoved.connect(description_widget.update_preview)
        self._list_widget.itemDoubleClicked.connect(self._edit_item)
        add_button.clicked.connect(self._add_button_clicked)
        edit_button.clicked.connect(self._edit_item)
        remove_button.clicked.connect(self._remove_item)
        translate_button.clicked.connect(self._translate_button_clicked)

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(translate_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self._list_widget)
        main_layout.addLayout(button_layout)

        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

        if parent_tag is not None:
            self._load_tag(parent_tag)

    def _load_tag(self, tag: etree._Element):
        translation_mode = False
        current_translations = {}
        current_text = None
        for i in tag.findall("li"):
            if translation_mode:
                if i.get("{http://www.w3.org/XML/1998/namespace}lang") is not None:
                    current_translations[i.get("{http://www.w3.org/XML/1998/namespace}lang")] = i.text
                    continue
                else:
                    item = QListWidgetItem(current_text)
                    item.setData(42, copy.copy(current_translations))
                    self._list_widget.addItem(item)
                    current_translations.clear()
                    translation_mode = False
                    current_text = None
            current_text = i.text
            translation_mode = True

        if current_text is not None:
            item = QListWidgetItem(current_text)
            item.setData(42, current_translations)
            self._list_widget.addItem(item)

    def _add_button_clicked(self):
        text, ok = QInputDialog.getText(self, QCoreApplication.translate("DescriptionWidget", "Add Item"), QCoreApplication.translate("DescriptionWidget", "Please enter a new list item"))
        if not ok:
            return
        item = QListWidgetItem(text)
        item.setData(42, {})
        self._list_widget.addItem(item)
        self._description_widget.update_preview()

    def _edit_item(self):
        item = self._list_widget.currentItem()
        if item is None:
            return
        old_text = item.text()
        new_text, ok = QInputDialog.getText(self, QCoreApplication.translate("DescriptionWidget", "Edit Item"), QCoreApplication.translate("DescriptionWidget", "Please enter a new value for the Item"), text=old_text)
        if not ok:
            return
        item.setText(new_text)
        self._description_widget.update_preview()

    def _remove_item(self):
        index = self._list_widget.currentRow()
        if index == -1:
            return
        self._list_widget.takeItem(index)
        self._description_widget.update_preview()

    def _translate_button_clicked(self):
        item = self._list_widget.currentItem()
        if item is None:
            return
        data = item.data(42)
        self._env.translate_window.open_window(data)
        item.setData(42, data)
        self._description_widget.update_preview()

    def get_tag(self, parent_tag:  etree._Element, preview: bool = False):
        list_tag = etree.SubElement(parent_tag, self._list_type)
        for i in range(self._list_widget.count()):
            entry_tag = etree.SubElement(list_tag, "li")
            item = self._list_widget.item(i)
            entry_tag.text = item.text()
            if preview:
                continue
            for key, value in item.data(42).items():
                trans_tag = etree.SubElement(list_tag, "li")
                trans_tag.set("{http://www.w3.org/XML/1998/namespace}lang", key)
                trans_tag.text = value



class DescriptionWidget(QWidget):
    def __init__(self, env, main_window = None):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "DescriptionWidget.ui"), self)

        self._env = env
        self._main_window = main_window

        self.description_table.verticalHeader().setSectionsMovable(True)
        self.description_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.description_table.verticalHeader().sectionMoved.connect(self.update_preview)
        self.paragraph_add_button.clicked.connect(lambda: self._add_paragraph())
        self.ordered_list_add_button.clicked.connect(lambda: self._add_list("ol"))
        self.unordered_list_add_button.clicked.connect(lambda: self._add_list("ul"))

    def _add_paragraph(self, text: Optional[str] = None, translations: Optional[Dict[str, str]] = None):
        row = self.description_table.rowCount()
        self.description_table.insertRow(row)

        item = QTableWidgetItem(QCoreApplication.translate("DescriptionWidget", "Paragraph"))
        item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
        self.description_table.setItem(row, 0, item)

        self.description_table.setCellWidget(row, 1, ParagraphWidget(self._env, self, text=text, translations=translations))

        remove_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Remove"))
        remove_button.clicked.connect(self._remove_button_clicked)
        self.description_table.setCellWidget(row, 2, remove_button)

        self.description_table.resizeRowsToContents()

        self.update_preview()

    def _add_list(self, list_type: str, parent_tag: Optional[etree._Element] = None):
        row = self.description_table.rowCount()
        self.description_table.insertRow(row)

        item = QTableWidgetItem()
        if list_type == "ol":
            item.setText(QCoreApplication.translate("DescriptionWidget", "Ordered List"))
        elif list_type == "ul":
            item.setText(QCoreApplication.translate("DescriptionWidget", "Unordered List"))
        item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
        self.description_table.setItem(row, 0, item)

        self.description_table.setCellWidget(row, 1, ListWidget(self._env, self, list_type, parent_tag))

        remove_button = QPushButton(QCoreApplication.translate("DescriptionWidget", "Remove"))
        remove_button.clicked.connect(self._remove_button_clicked)
        self.description_table.setCellWidget(row, 2, remove_button)

        self.description_table.resizeRowsToContents()

        self.update_preview()

    def _remove_button_clicked(self):
        for i in range(self.description_table.rowCount()):
            if self.description_table.cellWidget(i, 2) == self.sender():
                self.description_table.removeRow(i)
                self.update_preview()
                return

    def reset_data(self):
        clear_table_widget(self.description_table)
        self.update_preview()

    def load_tags(self, parent_tag: etree._Element):
        paragraph_lang_mode = False
        current_paragraph = None
        current_paragraph_translations = {}
        for i in parent_tag.getchildren():
            if paragraph_lang_mode:
                if i.tag == "p" and i.get("{http://www.w3.org/XML/1998/namespace}lang") is not None:
                    current_paragraph_translations[i.get("{http://www.w3.org/XML/1998/namespace}lang")] = i.text
                    continue
                else:
                    self._add_paragraph(text=current_paragraph, translations=current_paragraph_translations)
                    current_paragraph_translations.clear()
                    current_paragraph = None
                    paragraph_lang_mode = False

            if i.tag == "p":
                current_paragraph = i.text
                paragraph_lang_mode = True
            elif i.tag == "ol":
                self._add_list("ol", i)
            elif i.tag == "ul":
                self._add_list("ul", i)
            else:
                print("Unknwon tag " + i.tag, file=sys.stderr)

        if current_paragraph is not None:
            self._add_paragraph(text=current_paragraph, translations=current_paragraph_translations)

        self.update_preview()

    def get_tags(self, parent_tag: etree._Element, preview: bool = False):
        for i in get_logical_table_row_list(self.description_table):
            self.description_table.cellWidget(i, 1).get_tag(parent_tag, preview=preview)

    def update_preview(self):
        body = etree.Element("body")
        self.get_tags(body, preview=True)
        self.description_preview.setHtml(etree.tostring(body).decode("utf-8"))
        if self._main_window:
            self._main_window.set_file_edited()