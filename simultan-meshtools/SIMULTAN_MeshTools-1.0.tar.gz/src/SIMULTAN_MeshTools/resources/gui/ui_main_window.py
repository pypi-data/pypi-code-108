# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.2.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDockWidget, QGridLayout,
    QLabel, QLineEdit, QListView, QMainWindow,
    QMenuBar, QPlainTextEdit, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTabWidget, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 731)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setPointSize(14)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        font1 = QFont()
        font1.setPointSize(12)
        self.tabWidget.setFont(font1)
        self.project_tab = QWidget()
        self.project_tab.setObjectName(u"project_tab")
        self.gridLayout_2 = QGridLayout(self.project_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_3 = QLabel(self.project_tab)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 2, 1, 1, 1)

        self.label_4 = QLabel(self.project_tab)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 3, 1, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout_2.addItem(self.verticalSpacer_2, 0, 1, 1, 5)

        self.label_2 = QLabel(self.project_tab)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 1, 1, 1, 1)

        self.cp_pushButton = QPushButton(self.project_tab)
        self.cp_pushButton.setObjectName(u"cp_pushButton")

        self.gridLayout_2.addWidget(self.cp_pushButton, 1, 5, 1, 1)

        self.save_pushButton = QPushButton(self.project_tab)
        self.save_pushButton.setObjectName(u"save_pushButton")

        self.gridLayout_2.addWidget(self.save_pushButton, 6, 2, 1, 1)

        self.load_project_pushButton = QPushButton(self.project_tab)
        self.load_project_pushButton.setObjectName(u"load_project_pushButton")

        self.gridLayout_2.addWidget(self.load_project_pushButton, 6, 1, 1, 1)

        self.password_lineEdit = QLineEdit(self.project_tab)
        self.password_lineEdit.setObjectName(u"password_lineEdit")

        self.gridLayout_2.addWidget(self.password_lineEdit, 3, 2, 1, 4)

        self.project_lineEdit = QLineEdit(self.project_tab)
        self.project_lineEdit.setObjectName(u"project_lineEdit")

        self.gridLayout_2.addWidget(self.project_lineEdit, 1, 2, 1, 3)

        self.user_lineEdit = QLineEdit(self.project_tab)
        self.user_lineEdit.setObjectName(u"user_lineEdit")

        self.gridLayout_2.addWidget(self.user_lineEdit, 2, 2, 1, 4)

        self.close_project_pushButton = QPushButton(self.project_tab)
        self.close_project_pushButton.setObjectName(u"close_project_pushButton")

        self.gridLayout_2.addWidget(self.close_project_pushButton, 6, 3, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout_2.addItem(self.verticalSpacer_3, 5, 1, 1, 1)

        self.verticalSpacer_7 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_2.addItem(self.verticalSpacer_7, 7, 2, 1, 1)

        self.tabWidget.addTab(self.project_tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.gridLayout_3 = QGridLayout(self.tab_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalSpacer_5 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout_3.addItem(self.verticalSpacer_5, 8, 0, 1, 4)

        self.tables_listView = QListView(self.tab_2)
        self.tables_listView.setObjectName(u"tables_listView")
        self.tables_listView.setMinimumSize(QSize(0, 100))

        self.gridLayout_3.addWidget(self.tables_listView, 7, 0, 1, 4)

        self.label_8 = QLabel(self.tab_2)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_3.addWidget(self.label_8, 6, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout_3.addItem(self.verticalSpacer_4, 2, 0, 1, 4)

        self.geometry_comboBox = QComboBox(self.tab_2)
        self.geometry_comboBox.setObjectName(u"geometry_comboBox")

        self.gridLayout_3.addWidget(self.geometry_comboBox, 1, 0, 1, 4)

        self.label_6 = QLabel(self.tab_2)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_3.addWidget(self.label_6, 9, 0, 1, 1)

        self.label_5 = QLabel(self.tab_2)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 2)

        self.mesh_output_lineEdit = QLineEdit(self.tab_2)
        self.mesh_output_lineEdit.setObjectName(u"mesh_output_lineEdit")

        self.gridLayout_3.addWidget(self.mesh_output_lineEdit, 11, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout_3.addItem(self.verticalSpacer, 14, 0, 1, 4)

        self.label_7 = QLabel(self.tab_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 11, 0, 1, 1)

        self.select_file_pushButton = QPushButton(self.tab_2)
        self.select_file_pushButton.setObjectName(u"select_file_pushButton")

        self.gridLayout_3.addWidget(self.select_file_pushButton, 11, 2, 1, 1)

        self.save_mesh_pushButton = QPushButton(self.tab_2)
        self.save_mesh_pushButton.setObjectName(u"save_mesh_pushButton")

        self.gridLayout_3.addWidget(self.save_mesh_pushButton, 13, 0, 1, 1)

        self.mesh_format_comboBox = QComboBox(self.tab_2)
        self.mesh_format_comboBox.addItem("")
        self.mesh_format_comboBox.addItem("")
        self.mesh_format_comboBox.setObjectName(u"mesh_format_comboBox")

        self.gridLayout_3.addWidget(self.mesh_format_comboBox, 10, 1, 1, 1)

        self.label_9 = QLabel(self.tab_2)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_3.addWidget(self.label_9, 10, 0, 1, 1)

        self.verticalSpacer_6 = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout_3.addItem(self.verticalSpacer_6, 12, 0, 1, 1)

        self.tabWidget.addTab(self.tab_2, "")

        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 26))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.log_dockWidget = QDockWidget(MainWindow)
        self.log_dockWidget.setObjectName(u"log_dockWidget")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout_4 = QGridLayout(self.dockWidgetContents)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.log_plainTextEdit = QPlainTextEdit(self.dockWidgetContents)
        self.log_plainTextEdit.setObjectName(u"log_plainTextEdit")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.log_plainTextEdit.sizePolicy().hasHeightForWidth())
        self.log_plainTextEdit.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.log_plainTextEdit, 0, 0, 1, 1)

        self.log_dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, self.log_dockWidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"SIMULTAN mesh tools", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"User:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Password:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Simultan Project", None))
        self.cp_pushButton.setText(QCoreApplication.translate("MainWindow", u"Select project", None))
        self.save_pushButton.setText(QCoreApplication.translate("MainWindow", u"Save project", None))
        self.load_project_pushButton.setText(QCoreApplication.translate("MainWindow", u"Load Project", None))
        self.close_project_pushButton.setText(QCoreApplication.translate("MainWindow", u"Close project", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.project_tab), QCoreApplication.translate("MainWindow", u"Project", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Map Tables:", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Create Mesh:", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Geometry:", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Output file:", None))
        self.select_file_pushButton.setText(QCoreApplication.translate("MainWindow", u"Select file", None))
        self.save_mesh_pushButton.setText(QCoreApplication.translate("MainWindow", u"Save mesh", None))
        self.mesh_format_comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"vtk", None))
        self.mesh_format_comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"xdmf", None))

        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Output format:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Mesh", None))
        self.log_dockWidget.setWindowTitle(QCoreApplication.translate("MainWindow", u"Log", None))
    # retranslateUi

