from operator import truediv
from PyQt6.QtWidgets import QTableWidget, QHeaderView, QListWidget, QComboBox
from typing import Optional, List, Any
from lxml import etree
import urllib.parse
import requests
import hashlib


def clear_table_widget(table: QTableWidget):
    """Removes all Rows from a QTableWidget"""
    while table.rowCount() > 0:
        table.removeRow(0)


def stretch_table_widget_colums_size(table: QTableWidget):
    """Stretch all Colums of a QTableWidget"""
    for i in range(table.columnCount()):
        table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)


def list_widget_contains_item(list_widget: QListWidget, text: str) -> bool:
    """Checks if a QListWidget contains a item with the given text"""
    for i in range(list_widget.count()):
        if list_widget.item(i).text() == text:
            return True
    return False


def is_url_valid(url: str) -> bool:
    """Checks if the given URL with http/https protocol is valid"""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "http" and parsed.scheme != "https":
        return False
    if parsed.netloc == "":
        return False
    return True


def is_url_reachable(url: str) -> bool:
    """Checks if a URL exists"""
    try:
        r = requests.head(url, stream=True)
        return r.status_code == 200
    except Exception:
        return False


def select_combo_box_data(box: QComboBox, data: Any, default_index: int = 0):
    """Set the index to the item with the given data"""
    index = box.findData(data)
    if index == -1:
        box.setCurrentIndex(default_index)
    else:
        box.setCurrentIndex(index)


def get_logical_table_row_list(table: QTableWidget) -> List[int]:
    """Returns a List of the row indexes in the order they appear in the table"""
    index_list = []
    header = table.verticalHeader()
    for i in range(table.rowCount()):
        index_list.append(header.logicalIndex(i))
    return index_list


def calculate_checksum_from_url(url: str, hashtype: str) -> Optional[str]:
    """Returns the checksum of the given hashtype of the given URL. returns None, if the status code is not 200."""
    BUF_SIZE = 65536
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        return None
    hash = sha1 = getattr(hashlib, hashtype)()
    for chunk in r.iter_content(chunk_size=65536):
        hash.update(chunk)
    return hash.hexdigest()


def create_artifact_source_tag(url: str) -> etree.Element:
    """Creates a artifact tag for the given source URL"""
    atrtifact_tag =  etree.Element("artifact")
    atrtifact_tag.set("type", "source")
    location_tag = etree.SubElement(atrtifact_tag, "location")
    location_tag.text = url
    for i in ("sha1", "sha256", "blake2b", "blake2s"):
        checksum_tag = etree.SubElement(atrtifact_tag, "checksum")
        checksum_tag.set("type", i)
        checksum_tag.text = calculate_checksum_from_url(url, i)
    return atrtifact_tag


def is_string_number(text: str) -> bool:
    """Checks if the given string is a number"""
    try:
        int(text)
        return True
    except ValueError:
        return False
