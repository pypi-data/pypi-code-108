import abc
from PySide2 import QtWidgets

from galleries.annotations_parsers.gallery_annots_parsers import GalleryAnnotationsParser


class GalleryAnnotationsParserView(QtWidgets.QWidget):

    @abc.abstractmethod
    def get_parser(self) -> GalleryAnnotationsParser:
        pass

    @abc.abstractmethod
    def populate_with_parser(self, parser: GalleryAnnotationsParser):
        pass

    @abc.abstractmethod
    def clear(self):
        pass

    @abc.abstractmethod
    def is_dirty(self) -> bool:
        pass
