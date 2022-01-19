from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QLabel, QTableView
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtCore import Qt, QTimer, Slot
import sys
import os
from messenger2.databases.database import ServerDatabase
from messenger2.server.gui.config_window import ConfigWindow
from messenger2.server.gui.history_window import HistoryWindow
from messenger2.server.gui.register_window import RegisterWindow
from messenger2 import config


class ServerWindow(QMainWindow):
    """
    Server main gui window
    """

    def __init__(self, database, core, uic_file=None):
        super(ServerWindow, self).__init__()
        self.setWindowTitle("Server Gui")
        self.resize(700, 500)
        self.database = database
        self.alert = None
        self.core = core
        self.config_window = None
        self.history_window = None
        self.register_window = None
        self.setUi(uic_file)

    def setUi(self, uic_file):
        """
        set up ui form
        :param uic_file: Optional
        :return: None
        """

        actions = []
        self.exit = QAction("Выход", self)
        self.exit.triggered.connect(self.close)
        actions.append(self.exit)

        self.update = QAction("Обновить список", self)
        self.update.triggered.connect(self.update_list)
        actions.append(self.update)

        self.history = QAction("История клиентов", self)
        self.history.triggered.connect(self.get_clients_history)
        actions.append(self.history)

        self.config = QAction("Настройки сервера", self)
        self.config.triggered.connect(self.open_config)
        actions.append(self.config)

        self.register = QAction("Регистрация пользователя", self)
        self.register.triggered.connect(self.register_user)
        actions.append(self.register)

        self._create_menu_bar(actions)
        label = QLabel(text="Список активных контактов", parent=self)
        label.move(10, 15)
        label.resize(200, 30)
        label.setAlignment(Qt.AlignCenter)
        self.table = QTableView(self)
        self.table.move(0, 40)
        self.table.resize(600, 200)
        self.update_list()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_list)
        self.timer.start(20000)

    def _setUserModel(self, users):
        """
        Create main table model
        :param users: user list
        :return: None
        """

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(
            ["Имя", "IP адресс", "Порт", "Время входа"])

        for user in users:
            login = QStandardItem(user[1].login)
            login.setEditable(False)

            ip = QStandardItem(user[0].ip_address)
            ip.setEditable(False)

            port = QStandardItem(str(user[0].port))
            port.setEditable(False)

            log_time = QStandardItem(str(user[0].log_time))
            log_time.setEditable(False)

            model.appendRow([login, ip, port, log_time])

        self.table.setModel(model)

    def _create_menu_bar(self, action_list):
        """
        Set menu bar
        :param action_list: list of actions
        :return: None
        """
        for action in action_list:
            self.menuBar().addAction(action)

    def update_list(self):
        """
        Update users list
        :return: None
        """
        users = self.database.get_active_user_list(join_users=True)
        self._setUserModel(users=users)

    def get_clients_history(self):
        """
        Get clients logging history form server database
        :return: None
        """
        history = self.database.get_history_list(join_users=True)
        print(history)
        self.history_window = HistoryWindow()
        self.history_window.update_history_list(history)
        self.history_window.show()

    def register_user(self):
        """
        open register window
        :return: None
        """
        self.register_window = RegisterWindow(
            database=self.database, core=self.core)
        self.register_window.add_contact.connect(self.add_contact)
        self.register_window.show()

    def open_config(self):
        """
        open config window
        :return: None
        """
        self.config_window = ConfigWindow()
        self.config_window.update_info()
        self.config_window.show()

    @Slot(dict)
    def add_contact(self, contact_dict):
        """
        Add new contact
        :param contact_dict: dict with user and password
        :return: None
        """
        login = contact_dict.get("user")
        password = contact_dict.get("password")
        self.database.register_user(login=login, password=password)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = ServerDatabase(engine=config.TEST_DATABASE_ENGINE)
    db.clear_db()
    user = db.AllUsers(login="gledstoun", password="1111")
    active_user = db.ActiveUsers(port=8888, address='127.0.0.1', user_id=1)
    history = db.UsersHistory(user_id=1, port=7777, address="localhost")
    history_2 = db.UsersHistory(user_id=1, port=7778, address="198.161.0.1")
    db.save([user, active_user, history, history_2])
    window = ServerWindow(
        database=db,
        uic_file=os.path.join(
            os.getcwd(),
            "ui\\server.ui"))
    window.show()
    user = db.AllUsers(login="kaliter", password="1111")
    active_user = db.ActiveUsers(port=8888, address='127.0.0.1', user_id=2)
    db.save([user, active_user])
    sys.exit(app.exec_())
