from PyQt5.QtWidgets import QDialog, QPushButton, QLineEdit, QApplication, QLabel, qApp
from PyQt5.QtCore import QEvent


class UserNameDialog(QDialog):
    '''
    Класс реализующий стартовый диалог с запросом логина и пароля
    пользователя.
    '''

    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle('Категорически приветствую!')
        self.setFixedSize(190, 150)

        self.label = QLabel('Представьтесь, пожалуйста:', self)
        self.label.move(10, 10)
        self.label.setFixedSize(190, 10)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(180, 20)
        self.client_name.move(10, 30)

        self.btn_ok = QPushButton('Поехали', self)
        self.btn_ok.move(10, 105)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton('Выход', self)
        self.btn_cancel.move(100, 105)
        self.btn_cancel.clicked.connect(qApp.exit)

        self.label_passwd = QLabel('Введите пароль:', self)
        self.label_passwd.move(10, 55)
        self.label_passwd.setFixedSize(150, 15)

        self.client_passwd = QLineEdit(self)
        self.client_passwd.setFixedSize(180, 20)
        self.client_passwd.move(10, 75)
        self.client_passwd.setEchoMode(QLineEdit.Password)

        self.show()

    # Обработчик кнопки ОК, если поле вводе не пустое, ставим флаг и завершаем приложение.
    def click(self):
        '''Метод обрабтчик кнопки ОК.'''
        if self.client_name.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    app = QApplication([])
    dial = UserNameDialog()
    app.exec_()
