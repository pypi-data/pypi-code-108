import json
import os
import pathlib
from functools import partial
from tkinter import Tk

from Magic import theme, indexer, file_database


def folderchooser() -> None:
    """This function is to add  folder that has to be additionally indexed"""
    from tkinter.filedialog import askdirectory
    folderpath = askdirectory()
    indexer.add_indexer_folders(path = folderpath)


def filesInstaller() -> None:
    """Add all the files that should be initially written"""
    folderpath = pathlib.Path((os.getcwd() + "/resources"))
    if not os.path.exists(folderpath): os.makedirs(folderpath)  # Make the resources folder if it does not exists
    dummytpth = os.getcwd() + "/resources/ dummy.elsa"
    with open(dummytpth, "w") as f: f.write("Hey!The file you are looking is not found.Try again later")
    initpth = os.getcwd() + "/resources/ initial.elsa"
    with open(initpth, "w") as f: f.write(
        "black;purple;light green\n#The order is bg,font color,button colour\n#Please remember to use ';' to separate colours :D")
    indexerpth = os.getcwd() + "/resources/ indexerpaths.elsa"
    with open(indexerpth, "w") as f: json.dump([], f)  # Dumping an empty list for additional indexed paths
    userpth = os.getcwd() + "/resources/ users.elsa"
    with open(userpth, "w") as f: json.dump({"admin": "1234"}, f, indent = 4)
    print("Added initial files")


def install_files() -> None:
    """This function handles the main GUI work for initial setup"""
    from PyQt5 import QtCore, QtGui, QtWidgets
    class Ui_MainWindow(object):
        def __init__(self):
            # Need to destroy Tk() else, when font etc is selected a Tk window will be shown.So we create self.tkin
            # This Tk window wont be closed thus causing problem with tkinter of Elsa when actually run
            self.tkin, self.state = Tk(), False
            # state == False means user forcefully closed the initial setup
            # state == True means setup completed successfully

        def setupUi(self, MainWindow):
            MainWindow.resize(800, 600)
            self.initialiseWidgets()
            self.SettingUpLinkages()

        def initialiseWidgets(self):
            self.centralwidget = QtWidgets.QWidget(MainWindow)
            self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
            self.stackedWidget.setGeometry(QtCore.QRect(10, 10, 791, 581))
            self.StartPage = QtWidgets.QWidget()
            self.StartPageConitnueButton = QtWidgets.QPushButton(self.StartPage)
            self.StartPageConitnueButton.setGeometry(QtCore.QRect(630, 480, 131, 61))
            self.ElsaTitleLogo = QtWidgets.QLabel(self.StartPage)
            self.ElsaTitleLogo.setGeometry(QtCore.QRect(150, 60, 621, 191))
            font = QtGui.QFont()
            font.setFamily("Riviera")
            font.setPointSize(120)
            font.setBold(False)
            font.setWeight(50)
            self.ElsaTitleLogo.setFont(font)
            self.stackedWidget.addWidget(self.StartPage)
            self.LiscencePage = QtWidgets.QWidget()
            self.LicenceLabel = QtWidgets.QLabel(self.LiscencePage)
            self.LicenceLabel.setGeometry(QtCore.QRect(-10, -90, 771, 581))
            self.LicenceLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.AgreeRadioButton = QtWidgets.QRadioButton(self.LiscencePage)
            self.AgreeRadioButton.setGeometry(QtCore.QRect(50, 420, 131, 41))
            self.DisAgreeRadioButton = QtWidgets.QRadioButton(self.LiscencePage)
            self.DisAgreeRadioButton.setGeometry(QtCore.QRect(50, 450, 131, 41))
            self.LicenceContinueButton = QtWidgets.QPushButton(self.LiscencePage)
            self.LicenceContinueButton.setGeometry(QtCore.QRect(630, 510, 101, 51))
            self.stackedWidget.addWidget(self.LiscencePage)
            self.AddUserPage = QtWidgets.QWidget()
            self.EnterUsernameTextBox, self.EnterPasswordTextBox = QtWidgets.QLineEdit(self.AddUserPage), QtWidgets.QLineEdit(self.AddUserPage)
            self.EnterUsernameTextBox.setGeometry(QtCore.QRect(330, 150, 281, 31))
            self.EnterPasswordTextBox.setGeometry(QtCore.QRect(330, 210, 281, 31))
            self.EnterUserNameLabel, self.EnterPasswordLabel = QtWidgets.QLabel(self.AddUserPage), QtWidgets.QLabel(self.AddUserPage)
            self.EnterUserNameLabel.setGeometry(QtCore.QRect(160, 150, 151, 31))
            font = QtGui.QFont()
            font.setPointSize(12)
            self.EnterUserNameLabel.setFont(font)
            self.EnterPasswordLabel.setGeometry(QtCore.QRect(160, 210, 151, 31))
            self.EnterPasswordLabel.setFont(font)
            self.AddNewUserTitleLabel = QtWidgets.QLabel(self.AddUserPage)
            self.AddNewUserTitleLabel.setGeometry(QtCore.QRect(110, 50, 521, 61))
            self.font = QtGui.QFont()
            self.font.setPointSize(28)
            self.font.setBold(True)
            self.font.setWeight(75)
            self.AddNewUserTitleLabel.setFont(self.font)
            self.AddNewUserTitleLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.AddUserContinueButton = QtWidgets.QPushButton(self.AddUserPage)
            self.AddUserContinueButton.setGeometry(QtCore.QRect(620, 500, 121, 41))
            self.stackedWidget.addWidget(self.AddUserPage)
            self.OthersPage = QtWidgets.QWidget()
            self.ButtonColorButton, self.TextColorButton, self.BackGroundColorButton = QtWidgets.QPushButton(self.OthersPage), QtWidgets.QPushButton(
                self.OthersPage), QtWidgets.QPushButton(self.OthersPage)
            self.ButtonColorButton.setGeometry(QtCore.QRect(290, 230, 181, 61))
            self.TextColorButton.setGeometry(QtCore.QRect(290, 90, 181, 61))
            self.BackGroundColorButton.setGeometry(QtCore.QRect(290, 160, 181, 61))
            self.NewThemeLabel = QtWidgets.QLabel(self.OthersPage)
            self.NewThemeLabel.setGeometry(QtCore.QRect(210, 10, 371, 91))
            self.font.setPointSize(18)
            self.NewThemeLabel.setFont(self.font)
            self.AddnFolderLabel = QtWidgets.QLabel(self.OthersPage)
            self.AddnFolderLabel.setGeometry(QtCore.QRect(130, 300, 521, 91))
            self.AddnFolderLabel.setFont(self.font)
            self.AddnFolderLabel.setAlignment(QtCore.Qt.AlignCenter)
            self.AddFolderButton = QtWidgets.QPushButton(self.OthersPage)
            self.AddFolderButton.setGeometry(QtCore.QRect(300, 380, 181, 61))
            self.ContinueOtherButton = QtWidgets.QPushButton(self.OthersPage)
            self.ContinueOtherButton.setGeometry(QtCore.QRect(600, 510, 181, 61))
            self.stackedWidget.addWidget(self.OthersPage)
            MainWindow.setCentralWidget(self.centralwidget)
            self.retranslateUi(MainWindow)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)

        def SettingUpLinkages(self):
            # ...disabling Licnece Button...
            self.LicenceContinueButton.setDisabled(True)
            # ....continue Buttons.........
            self.StartPageConitnueButton.clicked.connect(
                partial(self.stackedWidget.setCurrentIndex, 1))
            self.LicenceContinueButton.clicked.connect(self.LicenseAcceptEvent)
            self.AddUserContinueButton.clicked.connect(self.adduserevent)
            self.ContinueOtherButton.clicked.connect(self.finishInitialSetup)
            # ....Radio Buttons......
            self.AgreeRadioButton.clicked.connect(
                partial(self.LicenceContinueButton.setDisabled, False))
            self.DisAgreeRadioButton.clicked.connect(
                partial(self.LicenceContinueButton.setDisabled, True))

            # .....Theme Buttons.....
            self.BackGroundColorButton.clicked.connect(theme.new_background_colour)
            self.TextColorButton.clicked.connect(theme.new_font_colour)
            self.ButtonColorButton.clicked.connect(theme.new_button_colour)
            # ....Indexer Button.......
            self.AddFolderButton.clicked.connect(folderchooser)

        def LicenseAcceptEvent(self):
            self.stackedWidget.setCurrentIndex(2)
            filesInstaller()

        def finishInitialSetup(self):
            # Setting state=True so that it indicates that setup was successful and not closed by the user
            self.state = True
            # deleteing tkin so that the background window
            # of askdirectory() and colorchooser() are destroyed properly
            self.tkin.destroy()
            MainWindow.close()

        def adduserevent(self):
            usrname = self.EnterUsernameTextBox.text()
            passwd = self.EnterPasswordTextBox.text()
            code = file_database.write_to_file(usrname, passwd)
            if code == 1:
                self.stackedWidget.setCurrentIndex(3)
            else:
                self.ErrorLabel = QtWidgets.QLabel(self.AddUserPage)
                self.ErrorLabel.setFont(self.font)
                self.ErrorLabel.setGeometry(QtCore.QRect(160, 450, 500, 31))
                self.ErrorLabel.setText("Sorry!Please try another username.This username is reserved")
                self.ErrorLabel.show()

        def retranslateUi(self, MainWindow):
            MainWindow.setWindowTitle("Elsa-Initial Setup")
            self.StartPageConitnueButton.setText("Continue")
            self.ElsaTitleLogo.setText("Elsa")
            self.LicenceLabel.setText("MIT License\n\nCopyright (c) 2021 George Rahul\n"
                                      "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
                                      "of this software and associated documentation files (the \"Software\"), to deal\n"
                                      "in the Software without restriction, including without limitation the rights\n"
                                      "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
                                      "copies of the Software, and to permit persons to whom the Software is\n"
                                      "furnished to do so, subject to the following conditions:\n\n"
                                      "The above copyright notice and this permission notice shall be included in all\n"
                                      "copies or substantial portions of the Software.\n\n"
                                      "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
                                      "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
                                      "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
                                      "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
                                      "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
                                      "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
                                      "SOFTWARE.")
            self.AgreeRadioButton.setText("I Agree")
            self.DisAgreeRadioButton.setText("I Disagree")
            self.LicenceContinueButton.setText("Continue")
            self.EnterUserNameLabel.setText("Enter Username:")
            self.EnterPasswordLabel.setText("Enter Password:")
            self.AddNewUserTitleLabel.setText("Add New User")
            self.AddUserContinueButton.setText("Continue")
            self.ButtonColorButton.setText("Button Color")
            self.TextColorButton.setText("Text Color")
            self.BackGroundColorButton.setText("Background Color")
            self.NewThemeLabel.setText("Select  A New Theme")
            self.AddnFolderLabel.setText("Add Additional Folders To Index")
            self.AddFolderButton.setText("Add Folder")
            self.ContinueOtherButton.setText("Finish")

    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow := QtWidgets.QMainWindow())
    MainWindow.show()
    app.exec_()
    if ui.state is False: sys.exit(1)
    print("Initial setup finished successfully")
    del app, MainWindow, ui
