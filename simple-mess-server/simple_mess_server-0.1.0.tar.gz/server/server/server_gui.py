"""
Графический интерфейс для серверной части мессенджера.
Содержит классы для отобрадения следующих окон:
* отображение списка всех клиентов;
* отображение статистики клиентов;
* настройка параметров сервера;
* регистрация пользователя;
* удаление пользователя.
Для создания графического интерфейса используется библиотека PyQt.
"""
import binascii
import hashlib
import os

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QLabel, QTableView, QPushButton, QLineEdit, QFileDialog, QMessageBox, QComboBox
from PyQt5.QtWidgets import QMainWindow, QDialog, QAction, qApp


class MainWindow(QMainWindow):
    """
    Класс главного окна интерфейса сервера
    """
    def __init__(self, database, server, config):
        super().__init__()
        self.database = database
        self.server_thread = server
        self.config = config

        # Кнопки панели инструментов.
        self.refresh_button = QAction('Обновить', self)
        self.statistics_button = QAction('Статистика клиентов', self)
        self.config_button = QAction('Настройки сервера', self)
        self.add_user_button = QAction('Добавить пользователя', self)
        self.del_user_button = QAction('Удалить пользователя', self)

        self.exitAction = QAction('Выход', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        # Панель инструментов
        self.toolbar = self.addToolBar('ToolBar')
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.statistics_button)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.add_user_button)
        self.toolbar.addAction(self.del_user_button)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.config_button)
        self.toolbar.addAction(self.exitAction)

        # Параметры окна
        self.setWindowTitle('Server Info')
        self.setFixedSize(500, 600)

        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        # Таблица активных клиентов
        self.clients_table = QTableView(self)
        self.clients_table.move(10, 45)
        self.clients_table.setFixedSize(480, 530)

        self.statusBar()

        # Запуск таймера для обновления таблицы активных клиентов.
        self.timer = QTimer()
        self.timer.timeout.connect(self.create_users_model)
        self.timer.start(1000)

        # Связываем кнопки с обработчиками
        self.refresh_button.triggered.connect(self.create_users_model)
        self.statistics_button.triggered.connect(self.show_statistics)
        self.config_button.triggered.connect(self.server_config)
        self.add_user_button.triggered.connect(self.add_user)
        self.del_user_button.triggered.connect(self.del_user)

        self.show()

    def create_users_model(self):
        """
        Создаёт таблицу активных пользователей для отображения.
        Содержит поля: Имя Клиента, IP Адрес, Порт, Время подключения.
        """
        user_list = self.database.get_active_users()
        table = QStandardItemModel()
        table.setHorizontalHeaderLabels(['Имя Клиента',
                                         'IP Адрес',
                                         'Порт',
                                         'Время подключения'])
        for row in user_list:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            table.appendRow([user, ip, port, time])

        self.clients_table.setModel(table)
        self.clients_table.resizeColumnsToContents()
        self.clients_table.resizeRowsToContents()

    def show_statistics(self):
        """Создаёт окно со статистикой клиентов."""
        global stat_window
        stat_window = StatisticsWindow(self.database)
        stat_window.show()

    def server_config(self):
        """Создаёт окно с настройками сервера."""
        global config_window
        config_window = ConfigWindow(self.config)

    def add_user(self):
        """Создаёт окно регистрации пользователя."""
        global reg_window
        reg_window = RegisterUserDialog(self.database, self.server_thread)
        reg_window.show()

    def del_user(self):
        """Создаёт окно удаления пользователя."""
        global rem_window
        rem_window = DelUserDialog(self.database, self.server_thread)
        rem_window.show()


class StatisticsWindow(QDialog):
    """
    Окно статистики активности клиентов
    """
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 600)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Кнопка выхода
        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 550)
        self.close_button.clicked.connect(self.close)

        # Таблица статистики
        self.statistics_table = QTableView(self)
        self.statistics_table.move(10, 10)
        self.statistics_table.setFixedSize(580, 500)

        self.create_history_model()

    def create_history_model(self):
        """
        Создаёт таблицу статистики действий пользователей.
        Содержит данные о времени последнего входа клиента,
        количестве отправленных и количестве полученных сообзщений.
        """
        actions_history = self.database.get_actions_history()

        history_list = QStandardItemModel()
        history_list.setHorizontalHeaderLabels(['Имя Клиента',
                                                'Последний вход',
                                                'Сообщений отправлено',
                                                'Сообщений получено'])
        for row in actions_history:
            user, last_seen, sent, accepted = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            accepted = QStandardItem(str(accepted))
            accepted.setEditable(False)
            history_list.appendRow([user, last_seen, sent, accepted])
        self.statistics_table.setModel(history_list)
        self.statistics_table.resizeColumnsToContents()
        self.statistics_table.resizeRowsToContents()


class ConfigWindow(QDialog):
    """ Окно настроек сервера """
    def __init__(self, config):
        super().__init__()
        self.config = config

        self.setWindowTitle('Параметры сервера')
        self.setFixedSize(365, 260)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        # Настройки базы данных.
        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        def open_file_dialog():
            """ Функция обработчик открытия окна выбора папки """
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_file_dialog)

        # Поле для ввода имени файла
        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)
        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        # Поле для ввода номера порта
        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)
        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        # Метка с адресом для соединений
        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)
        self.ip_label_note = QLabel(' оставьте это поле пустым, чтобы\n '
                                    'принимать соединения с любых адресов.',
                                    self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        # Поле для ввода ip
        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()

        self.db_path.insert(self.config['SETTINGS']['Database_path'])
        self.db_file.insert(self.config['SETTINGS']['Database_file'])
        self.port.insert(self.config['SETTINGS']['Default_port'])
        self.ip.insert(self.config['SETTINGS']['Listen_Address'])
        self.save_btn.clicked.connect(self.save_server_config)

    def save_server_config(self):
        """
        Метод сохранения настроек.
        Проверяет правильность введённых данных и сохраняет файл.
        """
        global config_window
        message = QMessageBox()
        self.config['SETTINGS']['Database_path'] = self.db_path.text()
        self.config['SETTINGS']['Database_file'] = self.db_file.text()
        try:
            port = int(self.port.text())
        except ValueError:
            message.warning(self, 'Ошибка', 'Порт должен быть числом')
        else:
            self.config['SETTINGS']['Listen_Address'] = self.ip.text()
            if 1023 < port < 65536:
                self.config['SETTINGS']['Default_port'] = str(port)
                conf_file_path = os.path.dirname(os.path.realpath(__file__))
                conf_file_path = os.path.join(conf_file_path, '..', 'server.ini')
                with open(f"{conf_file_path}", 'w', encoding='utf-8') as conf:
                    self.config.write(conf)
                    message.information(self, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(self, 'Ошибка', 'Порт должен быть от 1024 до 65536')


class RegisterUserDialog(QDialog):
    """
    Диалоговое окно для регистрации пользователя на сервере.
    """
    def __init__(self, database, server):
        super().__init__()
        self.database = database
        self.server = server

        self.setWindowTitle('Регистрация')
        self.setFixedSize(175, 185)
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.label_username = QLabel('Введите имя пользователя:', self)
        self.label_username.move(10, 10)
        self.label_username.setFixedSize(150, 15)

        self.user_name = QLineEdit(self)
        self.user_name.setFixedSize(154, 20)
        self.user_name.move(10, 30)

        self.label_password = QLabel('Введите пароль:', self)
        self.label_password.move(10, 55)
        self.label_password.setFixedSize(150, 15)

        self.client_password = QLineEdit(self)
        self.client_password.setFixedSize(154, 20)
        self.client_password.move(10, 75)
        self.client_password.setEchoMode(QLineEdit.Password)

        self.label_pass_confirm = QLabel('Повторите пароль:', self)
        self.label_pass_confirm.move(10, 100)
        self.label_pass_confirm.setFixedSize(150, 15)

        self.client_pass_confirm = QLineEdit(self)
        self.client_pass_confirm.setFixedSize(154, 20)
        self.client_pass_confirm.move(10, 120)
        self.client_pass_confirm.setEchoMode(QLineEdit.Password)

        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.move(10, 150)
        self.btn_ok.clicked.connect(self.save_user)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(90, 150)
        self.btn_cancel.clicked.connect(self.close)

        self.messages = QMessageBox()

        self.show()

    def save_user(self):
        """
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        """
        if not self.user_name.text():
            self.messages.critical(self, 'Ошибка', 'Укажите имя пользователя.')
            return

        elif self.client_password.text() != self.client_pass_confirm.text():
            self.messages.critical(self, 'Ошибка', 'Введённые пароли не совпадают.')
            return

        elif self.database.check_user(self.user_name.text()):
            self.messages.critical(self, 'Ошибка', 'Пользователь с таким именем уже существует.')
            return

        else:
            password = self.client_password.text().encode('utf-8')
            salt = self.user_name.text().encode('utf-8')
            password_hash = hashlib.pbkdf2_hmac('sha512', password, salt, 10000)

            self.database.add_user(self.user_name.text(), binascii.hexlify(password_hash))
            self.messages.information(self, 'Успех', 'Пользователь успешно зарегистрирован.')

            self.close()


class DelUserDialog(QDialog):
    """
    Диалоговое окно для удаления пользователя
    """
    def __init__(self, database, server):
        super().__init__()
        self.database = database
        self.server = server

        self.setFixedSize(350, 120)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите пользователя для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)
        self.selector.addItems(self.database.get_all_users())

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)
        self.btn_ok.clicked.connect(self.remove_user)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.messages = QMessageBox()

    def remove_user(self):
        """
        Метод - обработчик удаления пользователя.
        """
        self.database.remove_user(self.selector.currentText())
        if self.selector.currentText() in self.server.names:
            socket = self.server.names[self.selector.currentText()]
            del self.server.names[self.selector.currentText()]
            self.server.remove_client(socket)
        self.messages.information(self, 'Успех', 'Пользователь успешно удалён.')
        self.close()
