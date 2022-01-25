"""This root level directives are imported from submodules. They are made
available here as well to keep the number of imports to a minimum for most
applications.
"""

from .base import SquirroClient
from .document_uploader import DocumentUploader
from .exceptions import *
from .item_uploader import ItemUploader

__version__ ="3.4.5"
