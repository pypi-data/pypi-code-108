from PyQt6.QtWidgets import QApplication, QCheckBox, QComboBox, QLineEdit, QListWidget, QMainWindow, QMessageBox, QDateEdit, QInputDialog, QPlainTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QRadioButton, QFileDialog
from .Functions import clear_table_widget, stretch_table_widget_colums_size, list_widget_contains_item, is_url_reachable, get_logical_table_row_list, create_artifact_source_tag
from PyQt6.QtCore import Qt, QCoreApplication, QDate
from .DescriptionWidget import DescriptionWidget
from .ScreenshotWindow import ScreenshotWindow
from .RelationsWidget import RelationsWidget
from .ReleasesWindow import ReleasesWindow
from .SettingsWindow import SettingsWindow
from .ValidateWindow import ValidateWindow
from .AboutWindow import AboutWindow
from .OarsWidget import OarsWidget
from PyQt6.QtGui import QAction
from typing import Optional
from lxml import etree
from PyQt6 import uic
import urllib.parse
import webbrowser
import requests
import sys
import os


class MainWindow(QMainWindow):
    def __init__(self, env):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "MainWindow.ui"), self)

        self._env = env

        self._current_path = None

        self._settings_window = SettingsWindow(env, self)
        self._validate_window = ValidateWindow(env, self)
        self._screenshot_window = ScreenshotWindow(env, self)
        self._releases_window = ReleasesWindow(env, self)
        self._about_window = AboutWindow(env)

        self._description_widget = DescriptionWidget(env, self)
        self.description_layout.addWidget(self._description_widget)

        self._relations_widget = RelationsWidget(env, self)
        self.relations_layout.addWidget(self._relations_widget)

        self._oars_widget = OarsWidget(env, self)
        self.oras_layout.addWidget(self._oars_widget)

        self.screenshot_list = []

        self._url_list = []
        self._control_type_list = []
        for key, value in vars(self).items():
            if key.endswith("_url_edit"):
                self._url_list.append(key[:-9])
            elif key.startswith("control_box_"):
                self._control_type_list.append(key[12:])
                value.addItem(QCoreApplication.translate("MainWindow", "Not specified"), "none")
                value.addItem(QCoreApplication.translate("MainWindow", "Required"), "requires")
                value.addItem(QCoreApplication.translate("MainWindow", "Recommend"), "recommends")
                value.addItem(QCoreApplication.translate("MainWindow", "Supported"), "supports")

            if isinstance(value, QLineEdit):
                value.textEdited.connect(self.set_file_edited)
            elif isinstance(value, QComboBox):
                value.currentIndexChanged.connect(self.set_file_edited)
            elif isinstance(value, QPlainTextEdit):
                value.modificationChanged.connect(self.set_file_edited)
            elif isinstance(value, QTableWidget):
                value.verticalHeader().sectionMoved.connect(self.set_file_edited)
            elif isinstance(value, QListWidget):
                value.model().rowsMoved.connect(self.set_file_edited)

        self._update_recent_files_menu()

        for key, value in env.metadata_license_list.items():
            self.metadata_license_box.addItem(value, key)

        for i in env.project_license_list["licenses"]:
            self.project_license_box.addItem(i["name"], i["licenseId"])

        self.metadata_license_box.model().sort(0, Qt.SortOrder.AscendingOrder)
        self.project_license_box.model().sort(0, Qt.SortOrder.AscendingOrder)

        unknown_text = QCoreApplication.translate("MainWindow", "Unknown")
        self.metadata_license_box.insertItem(0, unknown_text, "unknown")
        self.project_license_box.insertItem(0, unknown_text, "unknown")

        self.metadata_license_box.setCurrentIndex(0)
        self.project_license_box.setCurrentIndex(0)

        stretch_table_widget_colums_size(self.screenshot_table)
        stretch_table_widget_colums_size(self.releases_table)
        stretch_table_widget_colums_size(self.provides_table)

        self.screenshot_table.verticalHeader().setSectionsMovable(True)
        self.releases_table.verticalHeader().setSectionsMovable(True)
        self.provides_table.verticalHeader().setSectionsMovable(True)

        self._update_categorie_remove_button_enabled()
        self._update_keyword_edit_remove_button()

        self._edited = False

        self._name_translations = {}
        self._summary_translations = {}

        self.translate_name_button.clicked.connect(lambda: env.translate_window.open_window(self._name_translations))
        self.translate_summary_button.clicked.connect(lambda: env.translate_window.open_window(self._summary_translations))

        self.screenshot_table.verticalHeader().sectionMoved.connect(self._screenshot_table_row_moved)
        self.screenshot_add_button.clicked.connect(lambda: self._screenshot_window.open_window(None))
        self.check_screenshot_url_button.clicked.connect(self._check_screenshot_urls)

        self.release_add_button.clicked.connect(self._release_add_button_clicked)
        self.release_import_github_button.clicked.connect(self._release_import_github)
        self.release_import_gitlab_button.clicked.connect(self._release_import_gitlab)

        self.check_links_url_button.clicked.connect(self._check_links_url_button_clicked)

        self.categorie_list.itemSelectionChanged.connect(self._update_categorie_remove_button_enabled)
        self.categorie_add_button.clicked.connect(self._add_categorie_button_clicked)

        self.categorie_remove_button.clicked.connect(self._remove_categorie_button_clicked)

        self.provides_add_button.clicked.connect(self._add_provides_row)

        self.keyword_list.itemDoubleClicked.connect(self._edit_keyword)
        self.keyword_list.itemSelectionChanged.connect(self._update_keyword_edit_remove_button)
        self.keyword_add_button.clicked.connect(self._add_keyword)
        self.keyword_edit_button.clicked.connect(self._edit_keyword)
        self.keyword_remove_button.clicked.connect(self._remove_keyword)

        self.new_action.triggered.connect(self._new_menu_action_clicked)
        self.open_action.triggered.connect(self._open_menu_action_clicked)
        self.save_action.triggered.connect(self._save_file_clicked)
        self.save_as_action.triggered.connect(self._save_as_clicked)
        self.exit_action.triggered.connect(self._exit_menu_action_clicked)

        self.settings_action.triggered.connect(self._settings_window.open_window)
        self.validate_action.triggered.connect(self._validate_window.open_window)

        self.documentation_action.triggered.connect(lambda: webbrowser.open("https://www.freedesktop.org/software/appstream/docs"))
        self.about_action.triggered.connect(self._about_window.exec)
        self.about_qt_action.triggered.connect(QApplication.instance().aboutQt)

        self.main_tab_widget.setCurrentIndex(0)
        self.update_window_title()

    def set_file_edited(self):
        self._edited = True
        self.update_window_title()

    def update_window_title(self):
        if self._current_path is None or self._env.settings.get("windowTitleType") == "none":
            self.setWindowTitle("jdAppdataEdit")
            return
        elif self._env.settings.get("windowTitleType") == "filename":
            if self._edited and self._env.settings.get("showEditedTitle"):
                self.setWindowTitle(os.path.basename(self._current_path) + "* - jdAppdataEdit")
            else:
                self.setWindowTitle(os.path.basename(self._current_path) + " - jdAppdataEdit")
        elif self._env.settings.get("windowTitleType") == "filename":
            if self._edited and self._env.settings.get("showEditedTitle"):
                self.setWindowTitle(self._current_path + "* - jdAppdataEdit")
            else:
                self.setWindowTitle(self._current_path + " - jdAppdataEdit")

    def _update_recent_files_menu(self):
        self.recent_files_menu.clear()

        if len(self._env.recent_files) == 0:
            empty_action = QAction(QCoreApplication.translate("MainWindow", "No recent files"), self)
            empty_action.setEnabled(False)
            self.recent_files_menu.addAction(empty_action)
            return

        for i in self._env.recent_files:
            file_action = QAction(i, self)
            file_action.setData(i)
            file_action.triggered.connect(self._open_recent_file)
            self.recent_files_menu.addAction(file_action)

        self.recent_files_menu.addSeparator()

        clear_action = QAction(QCoreApplication.translate("MainWindow", "Clear"), self)
        clear_action.triggered.connect(self._clear_recent_files)
        self.recent_files_menu.addAction(clear_action)

    def _add_to_recent_files(self, path: str):
        while path in self._env.recent_files:
            self._env.recent_files.remove(path)
        self._env.recent_files.insert(0, path)
        self._env.recent_files = self._env.recent_files[:self._env.settings.get("recentFilesLength")]
        self._update_recent_files_menu()
        self._env.save_recent_files()

    def _ask_for_save(self) -> bool:
        if not self._edited:
            return True
        if not self._env.settings.get("checkSaveBeforeClosing"):
            return
        answer = QMessageBox.warning(self, QCoreApplication.translate("MainWindow", "Unsaved changes"), QCoreApplication.translate("MainWindow", "You have unsaved changes. Do you want to save now?"), QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Save:
            self._save_file_clicked()
            return True
        elif answer == QMessageBox.StandardButton.Discard:
            return True
        elif answer == QMessageBox.StandardButton.Cancel:
            return False

    def _new_menu_action_clicked(self):
        if not self._ask_for_save():
            return
        self.reset_data()
        self._edited = False
        self._current_path = None
        self.update_window_title()

    def _open_menu_action_clicked(self):
        if not self._ask_for_save():
            return
        path = QFileDialog.getOpenFileName(self)
        if path[0] == "":
            return
        self.open_file(path[0])
        self._add_to_recent_files(path[0])
        self._current_path = path[0]
        self.update_window_title()

    def _open_recent_file(self):
        if not self._ask_for_save():
            return
        action = self.sender()
        if not action:
            return
        self.open_file(action.data())
        self._add_to_recent_files(action.data())
        self._current_path = action.data()
        self.update_window_title()

    def _save_file_clicked(self):
        if self._current_path is None:
            self._save_as_clicked()
            return
        self.save_file(self._current_path)
        self._add_to_recent_files(self._current_path)
        self._edited = False
        self.update_window_title()

    def _save_as_clicked(self):
        path = QFileDialog.getSaveFileName(self)
        if path[0] == "":
            return
        self.save_file(path[0])
        self._current_path = path[0]
        self._add_to_recent_files(path[0])
        self._edited = False
        self.update_window_title()

    def _exit_menu_action_clicked(self):
        if self._ask_for_save():
            sys.exit(0)

    def _clear_recent_files(self):
        self._env.recent_files.clear()
        self._update_recent_files_menu()
        self._env.save_recent_files()

    # Screenshots
    def update_sceenshot_table(self):
        clear_table_widget(self.screenshot_table)
        for row, i in enumerate(self.screenshot_list):
            self.screenshot_table.insertRow(row)

            url_item = QTableWidgetItem(i["url"])
            url_item.setFlags(url_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.screenshot_table.setItem(row, 0, url_item)

            default_button = QRadioButton()
            if i["default"]:
                default_button.setChecked(True)
            default_button.clicked.connect(self._default_button_clicked)
            self.screenshot_table.setCellWidget(row, 1, default_button)

            edit_button = QPushButton(QCoreApplication.translate("MainWindow", "Edit"))
            edit_button.clicked.connect(self._edit_screenshot_button_clicked)
            self.screenshot_table.setCellWidget(row, 2, edit_button)

            remove_button = QPushButton(QCoreApplication.translate("MainWindow", "Remove"))
            remove_button.clicked.connect(self._remove_screenshot_clicked)
            self.screenshot_table.setCellWidget(row, 3, remove_button)

    def _check_screenshot_urls(self):
        for i in self.screenshot_list:
            if not is_url_reachable(i["url"]):
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Invalid URL"), QCoreApplication.translate("MainWindow", "The URL {url} does not work").format(url=i["url"]))
                return
        QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Everything OK"), QCoreApplication.translate("MainWindow", "All URLs are working"))

    def _default_button_clicked(self):
        for count, i in enumerate(self.screenshot_list):
            if self.screenshot_table.cellWidget(count, 1).isChecked():
                i["default"] = True
            else:
                i["default"] = False
        self.set_file_edited()

    def _edit_screenshot_button_clicked(self):
        for i in range(self.screenshot_table.rowCount()):
            if self.screenshot_table.cellWidget(i, 2) == self.sender():
                self._screenshot_window.open_window(i)
                return

    def _remove_screenshot_clicked(self):
        for i in range(self.screenshot_table.rowCount()):
            if self.screenshot_table.cellWidget(i, 3) == self.sender():
                default = self.screenshot_list[i]["default"]
                del self.screenshot_list[i]
                if default and len(self.screenshot_list) != 0:
                    self.screenshot_list[0]["default"] = True
                self.update_sceenshot_table()
                self.set_file_edited()
                return

    def _screenshot_table_row_moved(self, logical_index: int, old_visual_index: int, new_visual_index: int):
        item = self.screenshot_list[old_visual_index]
        if new_visual_index == len(self.screenshot_list) - 1:
            self.screenshot_list.append(item)
        else:
            if new_visual_index > old_visual_index:
                self.screenshot_list.insert(new_visual_index + 1, item)
            else:
                self.screenshot_list.insert(new_visual_index, item)
        if new_visual_index > old_visual_index:
            del self.screenshot_list[old_visual_index]
        else:
            del self.screenshot_list[old_visual_index + 1]
        print(new_visual_index)
        self.update_sceenshot_table()

    # Releases

    def _set_release_row(self, row: int, version: Optional[str] = "", date: Optional[QDate] = None, development: bool = False, data: Optional[dict] = None):
        version_item = QTableWidgetItem(version)
        if data:
            version_item.setData(42, data)
        else:
            version_item.setData(42, {})
        self.releases_table.setItem(row, 0, version_item)

        if date is None:
            self.releases_table.setCellWidget(row, 1, QDateEdit())
        else:
            self.releases_table.setCellWidget(row, 1, QDateEdit(date))

        type_box = QComboBox()
        type_box.addItem(QCoreApplication.translate("MainWindow", "Stable"), "stable")
        type_box.addItem(QCoreApplication.translate("MainWindow", "Development"), "development")
        if development:
            type_box.setCurrentIndex(1)
        self.releases_table.setCellWidget(row, 2, type_box)

        edit_button = QPushButton(QCoreApplication.translate("MainWindow", "Edit"))
        edit_button.clicked.connect(self._release_edit_button_clicked)
        self.releases_table.setCellWidget(row, 3, edit_button)

        remove_button = QPushButton(QCoreApplication.translate("MainWindow", "Remove"))
        remove_button.clicked.connect(self._release_remove_button_clicked)
        self.releases_table.setCellWidget(row, 4, remove_button)

    def _release_edit_button_clicked(self):
        for i in range(self.releases_table.rowCount()):
            if self.releases_table.cellWidget(i, 3) == self.sender():
                self._releases_window.open_window(i)

    def _release_remove_button_clicked(self):
        for i in range(self.releases_table.rowCount()):
            if self.releases_table.cellWidget(i, 4) == self.sender():
                self.releases_table.removeRow(i)
                self.set_file_edited()
                return

    def _release_add_button_clicked(self):
        self.releases_table.insertRow(0)
        self._set_release_row(0)
        self.set_file_edited()

    def _release_import_github(self):
        repo_url, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Enter Repo URL"), QCoreApplication.translate("MainWindow", "Please Enter the URL to the GitHub Repo"))
        if not ok:
            return
        try:
            parsed = urllib.parse.urlparse(repo_url)
            if parsed.netloc != "github.com":
                raise Exception()
            _, owner, repo = parsed.path.split("/")
        except Exception:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Invalid URL"), QCoreApplication.translate("MainWindow", "Could not get the Repo and Owner from the URL"))
            return
        api_data = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases").json()
        if len(api_data) == 0:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Nothing found"), QCoreApplication.translate("MainWindow", "It looks like this Repo doesn't  have any releases"))
            return
        if self.releases_table.rowCount() > 0:
            ans = QMessageBox.question(self, QCoreApplication.translate("MainWindow", "Overwrite evrything"), QCoreApplication.translate("MainWindow", "If you proceed, all your chnages in the release tab will be overwritten. Continue?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                return
            clear_table_widget(self.releases_table)
        for count, i in enumerate(api_data):
            data = {}
            data["url"] = i["html_url"]
            # description_tag = etree.Element("description")
            # paragraph_tag = etree.SubElement(description_tag, "p")
            # paragraph_tag.text = i["body"]
            # data["description"] = description_tag

            #tarball_url =
            self.releases_table.insertRow(count)
            self._set_release_row(count, version = i["tag_name"], date=QDate.fromString(i["published_at"], Qt.DateFormat.ISODate), development=i["prerelease"], data=data)
        self.set_file_edited()

    def _release_import_gitlab(self):
        repo_url, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Enter Repo URL"), QCoreApplication.translate("MainWindow", "Please Enter the URL to the GitLab Repo"))
        if not ok:
            return
        parsed = urllib.parse.urlparse(repo_url)
        host = parsed.scheme + "://" + parsed.netloc
        try:
            r = requests.get(f"{host}/api/v4/projects/{urllib.parse.quote_plus(parsed.path[1:])}/releases")
            assert r.status_code == 200
        except Exception:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Could not get Data"), QCoreApplication.translate("MainWindow", "Could not get release Data for that Repo. Make sure you have the right URL."))
            return
        if self.releases_table.rowCount() > 0:
            ans = QMessageBox.question(self, QCoreApplication.translate("MainWindow", "Overwrite evrything"), QCoreApplication.translate("MainWindow", "If you proceed, all your chnages in the release tab will be overwritten. Continue?"), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ans != QMessageBox.StandardButton.Yes:
                return
            clear_table_widget(self.releases_table)
        for count, i in enumerate(r.json()):
            data = {}
            data["url"] = i["_links"]["self"]

            for source in i["assets"]["sources"]:
                if source["format"] == "tar.gz":
                    artifacts_tag = etree.Element("artifacts")
                    artifacts_tag.append(create_artifact_source_tag(source["url"]))
                    data["artifacts"] = artifacts_tag
                    break

            self.releases_table.insertRow(count)
            self._set_release_row(count, version = i["name"], date=QDate.fromString(i["released_at"], Qt.DateFormat.ISODate), data=data)
        self.set_file_edited()

    def _check_links_url_button_clicked(self):
        for i in self._url_list:
            url = getattr(self, f"{i}_url_edit").text()
            if url == "":
                continue
            if not is_url_reachable(url):
                QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Invalid URL"), QCoreApplication.translate("MainWindow", "The URL {url} does not work").format(url=url))
                return
        QMessageBox.information(self, QCoreApplication.translate("MainWindow", "Everything OK"), QCoreApplication.translate("MainWindow", "All URLs are working"))

    # Categories

    def _update_categorie_remove_button_enabled(self):
        if self.categorie_list.currentRow() == -1:
            self.categorie_remove_button.setEnabled(False)
        else:
            self.categorie_remove_button.setEnabled(True)

    def _add_categorie_button_clicked(self):
        categorie, ok = QInputDialog.getItem(self, QCoreApplication.translate("MainWindow", "Add a Categorie"), QCoreApplication.translate("MainWindow", "Please select a Categorie from the list below"), self._env.categories, 0, False)
        if not ok:
            return
        if list_widget_contains_item(self.categorie_list, categorie):
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Categorie already added"), QCoreApplication.translate("MainWindow", "You can't add the same Categorie twice"))
        else:
            self.categorie_list.addItem(categorie)
            self._update_categorie_remove_button_enabled()
            self.set_file_edited()

    def _remove_categorie_button_clicked(self):
        row = self.categorie_list.currentRow()
        if row == -1:
            return
        self.categorie_list.takeItem(row)
        self._update_categorie_remove_button_enabled()
        self.set_file_edited()

    # Provides

    def _add_provides_row(self, value_type: Optional[str] = None, value: str = ""):
        row = self.provides_table.rowCount()
        self.provides_table.insertRow(row)

        type_box = QComboBox()
        type_box.addItem("mediatype", "mediatype")
        type_box.addItem("library", "library")
        type_box.addItem("binary", "binary")
        type_box.addItem("font", "font")
        type_box.addItem("modalias", "modalias")
        type_box.addItem("firmware", "firmware")
        type_box.addItem("python2", "python2")
        type_box.addItem("python3", "python3")
        type_box.addItem("dbus-user", "dbus-user")
        type_box.addItem("dbus-system", "dbus-system")
        type_box.addItem("id", "id")
        if value_type:
            index = type_box.findData(value_type)
            if index != -1:
                type_box.setCurrentIndex(index)
            else:
                print(f"Unkown provides type {value_type}", file=sys.stderr)
        self.provides_table.setCellWidget(row, 0, type_box)

        self.provides_table.setItem(row, 1, QTableWidgetItem(value))

        remove_button = QPushButton(QCoreApplication.translate("MainWindow", "Remove"))
        remove_button.clicked.connect(self._remove_provides_button_clicked)
        self.provides_table.setCellWidget(row, 2, remove_button)

        self.set_file_edited()

    def _remove_provides_button_clicked(self):
        for i in range(self.provides_table.rowCount()):
            if self.provides_table.cellWidget(i, 2) == self.sender():
                self.provides_table.removeRow(i)
                self.set_file_edited()
                return

    # Keywords

    def _add_keyword(self):
        text, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "New Keyword"), QCoreApplication.translate("MainWindow", "Please enter a new Keyword"))
        if not ok:
            return
        if list_widget_contains_item(self.keyword_list, text):
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Keyword in List"), QCoreApplication.translate("MainWindow", "This Keyword is already in the List"))
            return
        self.keyword_list.addItem(text)
        self._update_keyword_edit_remove_button()
        self.set_file_edited()

    def _edit_keyword(self):
        if self.keyword_list.currentRow() == -1:
            return
        old_text = self.keyword_list.currentItem().text()
        new_text, ok = QInputDialog.getText(self, QCoreApplication.translate("MainWindow", "Edit Keyword"), QCoreApplication.translate("MainWindow", "Please edit the Keyword"), text=old_text)
        if not ok or old_text == new_text:
            return
        if list_widget_contains_item(self.keyword_list, new_text):
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "Keyword in List"), QCoreApplication.translate("MainWindow", "This Keyword is already in the List"))
            return
        self.keyword_list.currentItem().setText(new_text)
        self.set_file_edited()

    def _remove_keyword(self):
        index = self.keyword_list.currentRow()
        if index != -1:
            self.keyword_list.takeItem(index)
            self._update_keyword_edit_remove_button()
            self.set_file_edited()

    def _update_keyword_edit_remove_button(self):
        if self.keyword_list.currentRow() == -1:
            self.keyword_edit_button.setEnabled(False)
            self.keyword_remove_button.setEnabled(False)
        else:
            self.keyword_edit_button.setEnabled(True)
            self.keyword_remove_button.setEnabled(True)

    # Other Functions

    def get_id(self) -> str:
        return self.id_edit.text()

    def reset_data(self):
        for key, value in vars(self).items():
            if isinstance(value, QLineEdit):
                value.setText("")
            elif isinstance(value, QComboBox):
                value.setCurrentIndex(0)
            elif isinstance(value, QPlainTextEdit):
                value.setPlainText("")
            elif isinstance(value, QTableWidget):
                clear_table_widget(value)
            elif isinstance(value, QCheckBox):
                value.setChecked(False)
            elif isinstance(value, QListWidget):
                value.clear()
        self._description_widget.reset_data()
        self.screenshot_list.clear()
        self._relations_widget.reset_data()
        self._oars_widget.reset_data()
        self._name_translations.clear()
        self._summary_translations.clear()
        self._update_categorie_remove_button_enabled()
        self._update_keyword_edit_remove_button()

    # Read

    def _parse_screenshots_tag(self, screenshots_tag: etree._Element):
        for i in screenshots_tag.getchildren():
            new_dict = {}
            new_dict["caption_translations"] = {}

            if i.get("type") == "default":
                new_dict["default"] = True
            else:
                new_dict["default"] = False

            if len(i.getchildren()) == 0:
                new_dict["type"] = "source"
                new_dict["url"] = i.text
                self.screenshot_list.append(new_dict)
                continue

            image_tag = i.find("image")
            new_dict["url"] = image_tag.text

            width = image_tag.get("width")
            if width is not None:
                new_dict["width"] = int(width)
            height = image_tag.get("height")
            if height is not None:
                new_dict["height"] = int(height)

            for caption in i.findall("caption"):
                if caption.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
                    new_dict["caption"] = caption.text
                else:
                    new_dict["caption_translations"][caption.get("{http://www.w3.org/XML/1998/namespace}lang")] = caption.text

            self.screenshot_list.append(new_dict)

        self.update_sceenshot_table()

    def open_file(self, path: str):
        if not os.path.isfile(path):
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "File not found"), QCoreApplication.translate("MainWindow", "The file you are trying to open does not exists"))
            return

        try:
            root = etree.parse(path)
        except etree.XMLSyntaxError as ex:
            QMessageBox.critical(self, QCoreApplication.translate("MainWindow", "XML parsing failed"), ex.msg)
            return

        self.reset_data()

        id_tag = root.find("id")
        if id_tag is not None:
            self.id_edit.setText(id_tag.text)

        for i in root.findall("name"):
            if i.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
                self.name_edit.setText(i.text)
            else:
                self._name_translations[i.get("{http://www.w3.org/XML/1998/namespace}lang")] = i.text

        for i in root.findall("summary"):
            if i.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
                self.summary_edit.setText(i.text)
            else:
                self._summary_translations[i.get("{http://www.w3.org/XML/1998/namespace}lang")] = i.text

        developer_name_tag = root.find("developer_name")
        if developer_name_tag is not None:
            self.developer_name_edit.setText(developer_name_tag.text)

        launchable_tag = root.find("launchable")
        if launchable_tag is not None:
            self.desktop_file_edit.setText(launchable_tag.text)

        metadata_license_tag = root.find("metadata_license")
        if metadata_license_tag is not None:
            index = self.metadata_license_box.findData(metadata_license_tag.text)
            if index != -1:
                self.metadata_license_box.setCurrentIndex(index)

        project_license_tag = root.find("project_license")
        if project_license_tag is not None:
            index = self.project_license_box.findData(project_license_tag.text)
            if index != -1:
                self.project_license_box.setCurrentIndex(index)

        update_contact_tag = root.find("update_contact")
        if update_contact_tag is not None:
            self.update_contact_edit.setText(update_contact_tag.text)

        project_group_tag = root.find("project_group")
        if project_group_tag is not None:
            self.project_group_edit.setText(project_group_tag.text)

        description_tag = root.find("description")
        if description_tag is not None:
            self._description_widget.load_tags(description_tag)

        screenshots_tag = root.find("screenshots")
        if screenshots_tag is not None:
            self._parse_screenshots_tag(screenshots_tag)

        releases_tag = root.find("releases")
        if releases_tag is not None:
            for i in releases_tag.getchildren():
                current_row = self.releases_table.rowCount()
                data = {}
                if i.get("urgency") is not None:
                    data["urgency"] = i.get("urgency")
                url_tag = i.find("url")
                if url_tag is not None:
                    data["url"] = url_tag.text
                description_tag = i.find("description")
                if description_tag is not None:
                    data["description"] = description_tag
                artifacts_tag = i.find("artifacts")
                if artifacts_tag is not None:
                     data["artifacts"] = artifacts_tag
                self.releases_table.insertRow(current_row)
                self._set_release_row(current_row, version=i.get("version"), date=QDate.fromString(i.get("date"), Qt.DateFormat.ISODate), development=(i.get("type") == "development"), data=data)

        categories_tag = root.find("categories")
        if categories_tag is not None:
            for i in categories_tag.getchildren():
                self.categorie_list.addItem(i.text)

        for i in root.findall("url"):
            try:
                getattr(self, i.get("type") + "_url_edit").setText(i.text)
            except AttributeError:
                print(f"Unknown URL type {i.get('type')}", file=sys.stderr)

        for a in ["requires", "recommends", "supports"]:
            current_tag = root.find(a)
            if current_tag is None:
                continue
            for i in current_tag.findall("control"):
                try:
                    box = getattr(self, "control_box_" + i.text.replace("-", "_"))
                    index = box.findData(a)
                    box.setCurrentIndex(index)
                except AttributeError:
                    print(f"Unknown value {i.text} for control tag")
            self._relations_widget.load_data(current_tag)

        content_rating_tag = root.find("content_rating")
        if content_rating_tag is not None:
            self._oars_widget.open_file(content_rating_tag)

        provides_tag = root.find("provides")
        if provides_tag is not None:
            for i in provides_tag.getchildren():
                if i.tag == "dbus":
                    if i.get("type") == "user":
                        self._add_provides_row(value_type="dbus-user", value=i.text)
                    elif i.get("type") == "system":
                        self._add_provides_row(value_type="dbus-system", value=i.text)
                    else:
                        print(f"Invalid dbus type " + i.get("type"), file=sys.stderr)
                else:
                    self._add_provides_row(value_type=i.tag, value=i.text)

        keywords_tag = root.find("keywords")
        if keywords_tag is not None:
            for i in keywords_tag.findall("keyword"):
                self.keyword_list.addItem(i.text)

        self._edited = False

    # Write

    def _write_releases(self, root_tag: etree.Element):
        releases_tag = etree.SubElement(root_tag, "releases")
        for i in get_logical_table_row_list(self.releases_table):
            version = self.releases_table.item(i, 0).text()
            date = self.releases_table.cellWidget(i, 1).date().toString(Qt.DateFormat.ISODate)
            release_type = self.releases_table.cellWidget(i, 2).currentData()
            single_release_tag = etree.SubElement(releases_tag, "release")
            single_release_tag.set("version", version)
            single_release_tag.set("date", date)
            single_release_tag.set("type", release_type)

            data = self.releases_table.item(i, 0).data(42)

            if "urgency" in data:
                single_release_tag.set("urgency", data["urgency"])

            if "url" in data:
                url_tag =  etree.SubElement(single_release_tag, "url")
                url_tag.text = data["url"]

            if "description" in data:
                single_release_tag.append(data["description"])

            if "artifacts" in data:
                single_release_tag.append(data["artifacts"])

    def _write_requires_recommends_supports_tags(self, root_tag: etree._Element, current_type: str):
        current_tag = etree.SubElement(root_tag, current_type)
        for i in self._control_type_list:
            if getattr(self, "control_box_" + i).currentData() == current_type:
                control_tag = etree.SubElement(current_tag, "control")
                control_tag.text = i.replace("_", "-") # For tv-remote - is in a object name not supportet
        self._relations_widget.get_save_data(current_tag, current_type)
        if len(current_tag.getchildren()) == 0:
            root_tag.remove(current_tag)

    def save_file(self, path: str):
        root = etree.Element("component")
        root.set("type", "desktop")

        if self._env.settings.get("addCommentSave"):
            root.append(etree.Comment("Created with jdAppdataEdit " + self._env.version))

        id_tag = etree.SubElement(root, "id")
        id_tag.text = self.id_edit.text()

        name_tag = etree.SubElement(root, "name")
        name_tag.text = self.name_edit.text()
        for key, value in self._name_translations.items():
            name_translation_tag = etree.SubElement(root, "name")
            name_translation_tag.set("{http://www.w3.org/XML/1998/namespace}lang", key)
            name_translation_tag.text = value

        summary_tag = etree.SubElement(root, "summary")
        summary_tag.text = self.summary_edit.text()
        for key, value in self._summary_translations.items():
            summary_translation_tag = etree.SubElement(root, "summary")
            summary_translation_tag.set("{http://www.w3.org/XML/1998/namespace}lang", key)
            summary_translation_tag.text = value

        developer_name_tag = etree.SubElement(root, "developer_name")
        developer_name_tag.text = self.developer_name_edit.text()

        if self.desktop_file_edit.text() != "":
            launchable_tag = etree.SubElement(root, "launchable")
            launchable_tag.set("type", "desktop-id")
            launchable_tag.text = self.desktop_file_edit.text()

        if self.metadata_license_box.currentData() != "unknown":
            metadata_license_tag = etree.SubElement(root, "metadata_license")
            metadata_license_tag.text = self.metadata_license_box.currentData()

        if self.project_license_box.currentData() != "unknown":
            project_license_tag = etree.SubElement(root, "project_license")
            project_license_tag.text = self.project_license_box.currentData()

        if self.update_contact_edit.text() != "":
            update_contact_tag = etree.SubElement(root, "update_contact")
            update_contact_tag.text = self.update_contact_edit.text()

        if self.project_group_edit.text() != "":
            project_group_tag = etree.SubElement(root, "project_group")
            project_group_tag.text = self.project_group_edit.text()

        description_tag = etree.SubElement(root, "description")
        self._description_widget.get_tags(description_tag)

        if len(self.screenshot_list) > 0:
            screenshots_tag = etree.SubElement(root, "screenshots")
            for i in self.screenshot_list:
                single_screenshot_tag = etree.SubElement(screenshots_tag, "screenshot")
                if i["default"]:
                    single_screenshot_tag.set("type", "default")
                if "caption" in i:
                    caption_tag = etree.SubElement(single_screenshot_tag, "caption")
                    caption_tag.text = i["caption"]
                for key, value in i["caption_translations"].items():
                    caption_trans_tag = etree.SubElement(single_screenshot_tag, "caption")
                    caption_trans_tag.set("{http://www.w3.org/XML/1998/namespace}lang", key)
                    caption_trans_tag.text = value
                image_tag = etree.SubElement(single_screenshot_tag, "image")
                image_tag.text = i["url"]
                image_tag.set("type", "source")
                if "width" in i:
                    image_tag.set("width", str(i["width"]))
                if "height" in i:
                    image_tag.set("height", str(i["height"]))

        if self.releases_table.rowCount() > 0:
            self._write_releases(root)

        for i in self._url_list:
            url = getattr(self, f"{i}_url_edit").text()
            if url == "":
                continue
            url_tag = etree.SubElement(root, "url")
            url_tag.set("type", i)
            url_tag.text = url

        if self.categorie_list.count() > 0:
            categories_tag = etree.SubElement(root, "categories")
            for i in range(self.categorie_list.count()):
                single_categorie_tag = etree.SubElement(categories_tag, "category")
                single_categorie_tag.text = self.categorie_list.item(i).text()

        self._write_requires_recommends_supports_tags(root, "requires")
        self._write_requires_recommends_supports_tags(root, "recommends")
        self._write_requires_recommends_supports_tags(root, "supports")

        content_rating_tag =  etree.SubElement(root, "content_rating")
        content_rating_tag.set("type", "oars-1.1" )
        self._oars_widget.save_file(content_rating_tag)

        if self.provides_table.rowCount() > 0:
            provides_tag = etree.SubElement(root, "provides")
            for i in get_logical_table_row_list(self.provides_table):
                provides_type = self.provides_table.cellWidget(i, 0).currentData()
                if provides_type == "dbus-user":
                    single_provides_tag = etree.SubElement(provides_tag, "dbus")
                    single_provides_tag.set("type", "user")
                elif provides_type == "dbus-system":
                    single_provides_tag = etree.SubElement(provides_tag, "dbus")
                    single_provides_tag.set("type", "system")
                else:
                    single_provides_tag = etree.SubElement(provides_tag, provides_type)
                single_provides_tag.text = self.provides_table.item(i, 1).text()

        if self.keyword_list.count() > 0:
            keywords_tag = etree.SubElement(root, "keywords")
            for i in range(self.keyword_list.count()):
                single_keyword_tag = etree.SubElement(keywords_tag, "keyword")
                single_keyword_tag.text = self.keyword_list.item(i).text()

        xml = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="utf-8").decode("utf-8")

        # lxml filters the tags from the description text, so we need to convert them back
        xml = xml.replace("&lt;", "<")
        xml = xml.replace("&gt;", ">")

        with open(path, "w", encoding="utf-8", newline='\n') as f:
            f.write(xml)

    def closeEvent(self, event):
        if self._ask_for_save():
            event.accept()
        else:
            event.ignore()
