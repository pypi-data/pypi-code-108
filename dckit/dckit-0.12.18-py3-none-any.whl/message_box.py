"""Helper functions for displaying message boxes"""
from PyQt5.QtWidgets import QMessageBox


def error(message, info=None, details=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Errors occured")
    msg.setText(message)
    if info:
        msg.setInformativeText(info)
    if details:
        msg.setDetailedText(details)
    msg.exec_()


def ignored(message, info=None, details=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Ignored datasets")
    msg.setText(message)
    if info:
        msg.setInformativeText(info)
    if details:
        msg.setDetailedText(details)
    msg.exec_()


def nothing_todo(message="Nothing to do!"):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(message)
    msg.setWindowTitle("Warning")
    msg.exec_()


def success(message, details=None):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Success")
    msg.setText(message)
    if details:
        msg.setDetailedText(details)
    msg.exec_()
