import os
from pathlib import Path
from PySide2 import QtWidgets, QtCore

from galleries.annotations_parsers.file_name_parser import FileNameSepParser, GalleryAnnotationsParser
from mnd_qtutils.qtutils import setup_widget_from_ui
from propsettings_qt.object_drawers.object_drawer import ObjectDrawer

from galleries_qt.gallery_annotations_parser_view import GalleryAnnotationsParserView


class FileNameParserWidget(GalleryAnnotationsParserView, ObjectDrawer):

    SEP = ';'

    def __init__(self, parent=None):
        super(FileNameParserWidget, self).__init__(parent=parent)

        self._parser: FileNameSepParser = None
        self._dirty: bool = False

        ui_file_path = os.path.join(Path(__file__).parent, 'file_name_parser_widget.ui')
        self._widget: QtWidgets.QWidget = setup_widget_from_ui(ui_file_path, self)

        self._sep_edit: QtWidgets.QLineEdit = self._widget.sep_edit
        self._sep_edit.textEdited.connect(self._on_sep_changed)

        self._annot_edit: QtWidgets.QTextEdit = self._widget.annot_edit
        self._annot_edit.textChanged.connect(self._on_annots_changed)

    def get_parser(self) -> GalleryAnnotationsParser:
        sep = self._sep_edit.text()
        annots_names = self._get_annots()
        parser = FileNameSepParser(annots_names, sep)
        return parser

    def populate_with_parser(self, parser: FileNameSepParser):
        self._sep_edit.setText(parser.sep)
        annots = f'{self.SEP}'.join(parser.annot_names)
        self._annot_edit.setText(annots)
        self._dirty = False

    def draw_object(self, parser: FileNameSepParser):
        self._parser = parser
        self._sep_edit.setText(parser.sep)
        annots = f'{self.SEP}'.join(parser.annot_names)
        self._annot_edit.setText(annots)
        self._dirty = False

    def clear(self):
        self._sep_edit.setText('')
        self._annot_edit.setText('')
        self._dirty = False

    def is_dirty(self) -> bool:
        return self._dirty

    def _get_annots(self):
        annots_text = self._annot_edit.toPlainText()
        annots = annots_text.split(self.SEP)
        return annots

    @QtCore.Slot()
    def _on_sep_changed(self, new_sep: str):
        self._parser.sep = new_sep

    @QtCore.Slot()
    def _on_annots_changed(self):
        annots_names = self._get_annots()
        self._parser.annot_names = annots_names


if __name__ == '__main__':
    import sys
    from PySide2.QtWidgets import QApplication
    from PySide2.QtWidgets import QWidget, QVBoxLayout

    app = QApplication(sys.argv)

    window = QWidget()
    window.setMinimumSize(100, 100)
    layout = QVBoxLayout()
    window.setLayout(layout)

    panel = FileNameParserWidget()
    layout.addWidget(panel)

    window.show()

    sys.exit(app.exec_())
