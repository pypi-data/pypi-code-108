from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel , qApp
from PyQt5.QtCore import QEvent


# Стартовый диалог с выбором имени пользователя
class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Привет')
        self.setFixedSize(255, 190)

        self.label = QLabel('Введите имя пользователя: ', self)
        self.label.move(10, 10)
        self.label.setFixedSize(200, 20)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.btn_ok = QPushButton('Начать', self)
        self.btn_ok.move(10, 60)
        self.btn_ok.clicked.connect(self.click)
        self.btn_ok.setStyleSheet("background-color: green ")

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(120, 60)
        self.btn_cancel.clicked.connect(qApp.exit)
        self.btn_cancel.setStyleSheet("background-color: grey ")

        self.label_passwd = QLabel('Введите пароль:', self)
        self.label_passwd.move(10, 110)
        self.label_passwd.setFixedSize(150, 15)

        self.client_passwd = QLineEdit(self)
        self.client_passwd.setFixedSize(154, 30)
        self.client_passwd.move(10, 125)
        self.client_passwd.setEchoMode(QLineEdit.Password)

        self.show()

    # Обработчик кнопки ОК, если поле вводе не пустое, ставим флаг и завершаем приложение.
    def click(self):
        '''Метод обрабтчик кнопки ОК.'''
        if self.client_name.text() and self.client_passwd.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
