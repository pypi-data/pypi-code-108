import sys
import os
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt


class AboutWidget(QWidget):
    AUTHORS = [
        ["Aleksandr Sinitca", "Saint Petersburg Electrotechnical University \"LETI\", Russia",
            "amsinitca@etu.ru"],
        ["Mikhail Bogachev", "Saint Petersburg Electrotechnical University \"LETI\", Russia",
            "rogex@yandex.com"],
        ["Dmitry Kaplun", "Saint Petersburg Electrotechnical University \"LETI\", Russia",
            "dikaplun@etu.ru"],
        # ["Name","affiliation","e-mail"],
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self._res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "resources")
        self.initUI()

    def initUI(self):
        self.setWindowTitle("About")
        self.main_layout = QVBoxLayout()
        #self.images_layout = QGridLayout()

        # self.main_layout.addLayout(self.images_layout)

        self.affiliation_widget = QTextEdit()
        self.affiliation_widget.setReadOnly(True)
        self.affiliation_widget.setTextInteractionFlags(
            Qt.LinksAccessibleByMouse)
        organisation = []
        for author in self.AUTHORS:
            if author[1] not in organisation:
                organisation.append(author[1])
        for author in self.AUTHORS:
            org_ind = organisation.index(author[1]) + 1
            s = "{name}<sup>{org_ind}</sup>, <a href=\"mailto:{mail}\">{mail}</a> <br> \n".format(
                name=author[0], org_ind=org_ind, mail=author[2])
            self.affiliation_widget.insertHtml(s)
        self.affiliation_widget.insertHtml("<br>")
        for ind, org in enumerate(organisation):
            ind += 1
            s = "{ind}) {org} <br>".format(ind=ind, org=org)
            self.affiliation_widget.insertHtml(s)

        s = "<br><br> Licensed under GNU GPLv3 License <br> <a href=\"https://gitlab.com/digiratory/biomedimaging/bcanalyzer\">https://gitlab.com/digiratory/biomedimaging/bcanalyzer</a> <br>"
        self.affiliation_widget.insertHtml(s)
        self.affiliation_widget.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(self.affiliation_widget)
        self.setLayout(self.main_layout)
        self.setWindowFlag(Qt.Dialog and Qt.MSWindowsFixedSizeDialogHint)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    app = AboutWidget()
    app.show()
    qapp.exec_()
