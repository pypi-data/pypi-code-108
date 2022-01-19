from PySide2.QtWidgets import QDialog, QLineEdit, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog
from PySide2.QtCore import Qt
from messenger2.server.gui.alert_window import AlertWindow
from messenger2 import config


class ConfigWindow(QDialog):
    """
    Config window for changing server configuration
    """
    def __init__(self, parent=None):
        super(ConfigWindow, self).__init__(parent=parent)
        self.setWindowTitle("Server Config")
        self.resize(450, 300)
        self.alert = None
        self.setUi()

    def setUi(self):
        """
        Set up ui
        :return: None
        """
        MainVBox = QVBoxLayout()

        Vbox, self.input_database = self._create_set_line(
            "Путь до базы данных", "Выбрать", self.open_file_dialog)
        MainVBox.addLayout(Vbox)

        Vbox, self.input_database_name = self._create_set_line(
            "Имя базы данных")
        MainVBox.addLayout(Vbox)

        Vbox, self.input_port = self._create_set_line("Номер порта сервера")
        MainVBox.addLayout(Vbox)

        Vbox, self.input_address = self._create_set_line(
            "Какие IP слушаем( по умолчанию все )")
        MainVBox.addLayout(Vbox)

        Vbox = QVBoxLayout()
        Hbox = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        exit_btn = QPushButton("Выйти")
        save_btn.clicked.connect(self.save_settings)
        exit_btn.clicked.connect(self.close)

        Hbox.addWidget(save_btn)
        Hbox.addWidget(exit_btn)
        Vbox.addLayout(Hbox)
        MainVBox.addLayout(Vbox)

        self.setLayout(MainVBox)

    def save_settings(self):
        """
        saving current setting
        :return: None
        """
        settings = config.SETTINGS
        settings["server_port"] = self.input_port.text()
        settings["listen_address"] = self.input_address.text()
        settings["database_path"] = self.input_database.text()
        settings["database_file"] = self.input_database_name.text()
        with open(config.SERVER_INI, "w") as configfile:
            config.config.write(configfile)

        self.alert = AlertWindow(info_msg="настройки сохранены")
        self.alert.show()

    def open_file_dialog(self):
        """
        Open file dialog
        :return: None
        """
        file_dialog = QFileDialog(parent=self)
        file_dialog.show()

    def _create_set_line(
            self,
            text_information,
            button_name=None,
            button_action_fnc=None):
        """
        create basic set line
        :param text_information: text information
        :param button_name: name of active button
        :param button_action_fnc: function to activate after click
        :return: QVboxLayout object
        """
        Vbox = QVBoxLayout()
        info_label = QLabel(text=text_information)
        info_label.setAlignment(Qt.AlignCenter)
        Hbox = QHBoxLayout()
        input_line = QLineEdit()
        Hbox.addWidget(input_line)
        if button_name is not None:
            button = QPushButton(button_name)
            if button_action_fnc is not None:
                button.clicked.connect(button_action_fnc)
            Hbox.addWidget(button)

        Vbox.addWidget(info_label)
        Vbox.addLayout(Hbox)

        return Vbox, input_line

    def update_info(self):
        """
        Update infor in window
        :return: None
        """
        self.input_database.setText(config.DATABASE_PATH)
        self.input_database_name.setText(config.DATABASE_NAME)
        self.input_address.setText(config.LISTEN_ADDRESS)
        self.input_port.setText(str(config.SERVER_PORT))
