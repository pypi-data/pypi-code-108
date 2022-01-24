from typing import List
from qtpy import QtWidgets


def open_files(
    parent: QtWidgets.QWidget,
    window_name: str,
    types_name: str = "Videos",
    file_types: List[str] = None,
):
    """
    creates a QfileDialog with text label for types_name file_types
    :param parent: the parent QtWidget
    :param window_name: the name of the dialog window
    :param types_name: the name of the group of file types you want to accept
    :param file_types: the file extensions you want to accept
    :return: A list of paths to files that were selected
    """
    if file_types is None:
        file_types = ["mp4", "avi", "m4v"]
    file_types_str = types_name + " ("
    for f_type in file_types:
        file_types_str += "*." + f_type + " "
    file_types_str += ");; @All Files (*)"
    files, _ = QtWidgets.QFileDialog.getOpenFileNames(
        parent,
        window_name,
        "",
        file_types_str,
        options=QtWidgets.QFileDialog.Options(),
    )
    return files


def open_dir(parent: QtWidgets.QWidget, window_name):
    """
    Opens a directory
    :param parent: the parent QWidget that launches the file dialog
    :param window_name: the name of the file dialog window
    :return: the path to the opened directory
    """
    files_dir, _ = QtWidgets.QFileDialog.getExistingDirectory(
        parent,
        window_name,
    )
    return files_dir
