'''This module processing the start dialog for user authorization'''

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, \
                            qApp, QApplication


class StartUserNameEnteringWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_button_pressed = False

        self.setWindowTitle('Welcome!')
        self.setFixedSize(175, 135)

        self.label = QLabel('Enter username:', self)
        self.label.move(10, 10)
        self.label.setFixedSize(150, 10)

        self.client_name = QLineEdit(self)
        self.client_name.move(10, 30)
        self.client_name.setFixedSize(154, 20)

        self.ok_button = QPushButton('Start', self)
        self.ok_button.move(10, 105)
        self.ok_button.clicked.connect(self.click)

        self.cancel_button = QPushButton('Exit', self)
        self.cancel_button.move(90, 105)
        self.cancel_button.clicked.connect(qApp.exit)

        self.label_password = QLabel('Enter password:', self)
        self.label_password.move(10, 55)
        self.label_password.setFixedSize(150, 15)

        self.client_password = QLineEdit(self)
        self.client_password.move(10, 75)
        self.client_password.setFixedSize(154, 20)
        self.client_password.setEchoMode(QLineEdit.Password)

        self.show()

    def click(self):
        if self.client_name.text() and self.client_password.text():
            self.ok_button_pressed = True
            qApp.exit()


if __name__ == '__main__':
    APP = QApplication([])
    start_window_obj = StartUserNameEnteringWindow()
    APP.exec_()

