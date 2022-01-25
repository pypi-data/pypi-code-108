import sys
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox, QPushButton, QApplication
from PyQt5.QtCore import Qt


class DelContactDialog(QDialog):
    """
    Диалоговое окно выбора контакта для удаления
    """
    def __init__(self, database):
        super().__init__()
        self.database = database

        self.setFixedSize(230, 110)
        self.setWindowTitle('Удаление контакта')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите контакт для удаления:', self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(210, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(90, 30)
        self.btn_ok.move(20, 65)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(90, 30)
        self.btn_cancel.move(120, 65)
        self.btn_cancel.clicked.connect(self.close)

        self.selector.addItems(sorted(self.database.get_contacts()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    from client_db import ClientStorage
    db = ClientStorage('test1')
    window = DelContactDialog(db)
    window.show()
    app.exec_()
