from PySide2.QtWidgets import QDialog, QVBoxLayout, QTableView
from PySide2.QtGui import QStandardItemModel, QStandardItem


class HistoryWindow(QDialog):
    """
    Show clients logging history
    """
    def __init__(self):
        super(HistoryWindow, self).__init__()
        self.resize(450, 300)
        self.table = QTableView()
        self.alert = None
        Vbox = QVBoxLayout()
        Vbox.addWidget(self.table)
        self.setLayout(Vbox)

    def update_history_list(self, history):
        """
        set history list
        :param history: history array
        :return: None
        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Имя", "IP", "Port", "Время входа"])

        for his in history:
            name = QStandardItem(his[1])
            ip = QStandardItem(his[0].ip_address)
            port = QStandardItem(str(his[0].port))
            log_time = QStandardItem(str(his[0].log_time))
            model.appendRow([name, ip, port, log_time])

        self.table.setModel(model)