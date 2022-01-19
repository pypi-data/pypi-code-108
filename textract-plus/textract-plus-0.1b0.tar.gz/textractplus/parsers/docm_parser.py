from docx2python import docx2python

from .utils import BaseParser

class Parser(BaseParser):
    """Extract text from docm file using docx2python."""
    def extract(self, filename, **kwargs):
        return docx2python(filename).text