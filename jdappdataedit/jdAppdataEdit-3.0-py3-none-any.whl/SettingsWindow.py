from PyQt6.QtCore import QCoreApplication, QLocale
from .Functions import select_combo_box_data
from PyQt6.QtWidgets import QDialog
from PyQt6 import uic
import os


class SettingsWindow(QDialog):
    def __init__(self, env, main_window):
        super().__init__()
        uic.loadUi(os.path.join(env.program_dir, "SettingsWindow.ui"), self)

        self._env = env
        self._main_window = main_window

        self.language_box.addItem(QCoreApplication.translate("SettingsWindow", "System language"), "default")
        self.language_box.addItem("Englisch", "en")
        for i in os.listdir(os.path.join(env.program_dir, "i18n")):
            if i.endswith(".qm"):
                self.language_box.addItem(QLocale.languageToString(QLocale(i[14:-3]).language()), i[14:-3])

        self.window_title_box.addItem(QCoreApplication.translate("SettingsWindow", "Nothing"), "none")
        self.window_title_box.addItem(QCoreApplication.translate("SettingsWindow", "Filename"), "filename")
        self.window_title_box.addItem(QCoreApplication.translate("SettingsWindow", "Path"), "path")

        self.reset_button.clicked.connect(self._reset_button_clicked)
        self.ok_button.clicked.connect(self._ok_button_clicked)
        self.cancel_button.clicked.connect(self.close)

    def _update_widgets(self):
        index = self.language_box.findData(self._env.settings.get("language"))
        if index == -1:
            self.language_box.setCurrentIndex(0)
        else:
            self.language_box.setCurrentIndex(index)

        self.recent_files_spin_box.setValue(self._env.settings.get("recentFilesLength"))
        select_combo_box_data(self.window_title_box, self._env.settings.get("windowTitleType"))
        self.check_save_check_box.setChecked(self._env.settings.get("checkSaveBeforeClosing"))
        self.title_edited_check_box.setChecked(self._env.settings.get("showEditedTitle"))
        self.add_comment_check_box.setChecked(self._env.settings.get("addCommentSave"))

    def _reset_button_clicked(self):
        self._env.settings.reset()
        self._update_widgets()

    def _ok_button_clicked(self):
        self._env.settings.set("language", self.language_box.currentData())
        self._env.settings.set("recentFilesLength",  self.recent_files_spin_box.value())
        self._env.settings.set("windowTitleType",  self.window_title_box.currentData())
        self._env.settings.set("checkSaveBeforeClosing", self.check_save_check_box.isChecked())
        self._env.settings.set("showEditedTitle", self.title_edited_check_box.isChecked())
        self._env.settings.set("addCommentSave", self.add_comment_check_box.isChecked())

        self._env.recent_files = self._env.recent_files[:self._env.settings.get("recentFilesLength")]
        self._env.save_recent_files()

        self._main_window.update_window_title()

        self._env.settings.save(os.path.join(self._env.data_dir, "settings.json"))
        self.close()

    def open_window(self):
        self._update_widgets()
        self.exec()
