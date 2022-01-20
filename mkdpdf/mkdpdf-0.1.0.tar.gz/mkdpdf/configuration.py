import datetime
import os

import mkdpdf

# FILE SYSTEM
DIRECTORY_PATH_OUTPUT = os.environ["DIRECTORY_PATH"] if "DIRECTORY_PATH" in os.environ else os.getcwd()
DIRECTORY_PATH_PACKAGE = os.path.dirname(mkdpdf.__file__)
FILENAME = (os.environ["FILENAME"].split(".")[0] if "." in os.environ["FILENAME"] else os.environ["FILENAME"]) if "FILENAME" in os.environ else None

# LAYOUT
DOCUMENT_EXTRA_VERTICAL_MARGIN = 30
DOCUMENT_SIDE_MARGIN = 2
GITFLAVOR_BREAK_RETURN = "\r\n"
GITFLAVOR_RETURN = "\r\n\r\n"
FORMAT = os.environ["FORMAT"] if "FORMAT" in os.environ else "md"
# output render format : input template format
TEMPLATES = {
    "md": "md",
    "pdf": "html"
}

# TIME
DATE_PUBLISH = (datetime.datetime.now().isoformat()).split("T")[0]
