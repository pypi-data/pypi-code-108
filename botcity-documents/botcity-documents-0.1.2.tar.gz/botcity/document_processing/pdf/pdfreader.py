from pdfminer.layout import LAParams

from ..parser import DocumentParser
from . import _priv_pdfreader


class PDFReader:
    def __init__(self) -> None:
        self._layout_params = LAParams(line_margin=0.1)
        self._page = None
        self._page_idx = None
        self._start_y = 0

    @property
    def page_width(self) -> float:
        """PDF Page width.
        """
        return self._page.width if self._page else 0.0

    @property
    def page_height(self) -> float:
        """PDF Page height.
        """
        return self._page.height if self._page else 0.0

    def read_file(self, file: str) -> DocumentParser:
        """Read the given PDF file and returns a new instance of the DocumentParser.

        Args:
            file (str): PDF file path.

        Returns:
            DocumentParser: The document parser to be used.
        """
        return _priv_pdfreader.read_file(self, file)
