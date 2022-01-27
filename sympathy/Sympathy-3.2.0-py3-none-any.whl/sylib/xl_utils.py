# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
from contextlib import contextmanager
import xml.etree.ElementTree as ET
import zipfile


def is_xlsx(filename):
    """Return True file seems to be an xlsx file, False otherwise."""
    return bool(get_xlsx_sheetnames(filename))


def is_xls(filename):
    """Return True file seems to be an xls file, False otherwise."""
    # This header is shared between .doc, .xls, .ppt and other OLECF formats.
    OLECF_HEADER = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # noqa

    # At 512 bytes there should be a "subheader" defining what the specific
    # OLECF format of this file. See:
    # http://www.filesignatures.net/index.php?page=search&search=XLS&mode=EXT
    # and
    # http://www.garykessler.net/library/file_sigs.html
    SUBHEADER_OFFSET = 512  # noqa
    XLS_SUBHEADERS = [  # noqa
        b"\x09\x08\x10\x00\x00\x06\x05\x00",
        b"\xfd\xff\xff\xff\x20\x00\x00\x00",
        b"\xfd\xff\xff\xff\x10",
        b"\xfd\xff\xff\xff\x1f",
        b"\xfd\xff\xff\xff\x22",
        b"\xfd\xff\xff\xff\x23",
        b"\xfd\xff\xff\xff\x28",
        b"\xfd\xff\xff\xff\x29"]
    NON_XLS_SUBHEADERS = [
        b"\xec\xa5\xc1\x00",  # doc
        b"\x00\x6e\x1e\xf0",  # ppt
        b"\x0f\x00\xe8\x03",  # ppt
        b"\xa0\x46\x1d\xf0",  # ppt
        b"\xfd\xff\xff\xff\x0e\x00\x00\x00",  # ppt
        b"\xfd\xff\xff\xff\x1c\x00\x00\x00",  # ppt
        b"\xfd\xff\xff\xff\x43\x00\x00\x00",  # ppt
    ]
    MAX_SUBHEADER_LEN = max([len(subheader) for subheader in XLS_SUBHEADERS])  # noqa

    # Read header and "subheader" from file.
    try:
        with open(filename, 'rb') as f:
            header = f.read(len(OLECF_HEADER))
            f.seek(SUBHEADER_OFFSET)
            subheader = f.read(MAX_SUBHEADER_LEN)
    except:
        return False

    if header == OLECF_HEADER:
        # If a subheader from the approved list exists we accept it as an xls
        # file
        for xls_subheader in XLS_SUBHEADERS:
            if subheader.startswith(xls_subheader):
                return True
        for xls_subheader in XLS_SUBHEADERS:
            if subheader.startswith(xls_subheader):
                return False

        # This seems to be an unknown Microsoft office file type. We don't
        # expect our list of subheaders to be complete, so let's just take a
        # peek at the file extension to try determine if it is an xls file:
        if filename.endswith(".xls"):
            return True

    return False


def get_xlsx_sheetnames(filename):
    # Type of main content relationship in xlsx files.
    WB_REL_TYPE = ("http://schemas.openxmlformats.org/officeDocument/"  # noqa
                   "2006/relationships/officeDocument")

    # Namespace used in workbook file in xlsx files.
    WB_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"  # noqa

    # Get name of main content (workbook) file from main relations file. Main
    # relations file is located at _rels/.rels.
    try:
        zf = zipfile.ZipFile(filename)
        types = ET.fromstring(zf.read('_rels/.rels'))
    except (zipfile.BadZipfile, KeyError, ET.ParseError):
        # Trying to read a file that isn't in the zip archive gives KeyError
        return []

    # The top level tag is <Types>, containing among other things <Override>
    # tags. One of the <Override> tags will have WB_REL_TYPE as its Type
    # attribute and the path to the main content (workbook) file as its Target
    # attribute.
    for child in types:
        if child.get('Type') == WB_REL_TYPE:
            wb_path = child.get('Target')
            break
    else:
        return []

    # Get sheetnames from main content (workbook) file
    try:
        wb_dom = ET.fromstring(zf.read(wb_path))
    except (KeyError, ET.ParseError):
        return []

    # The top level tag is <workbook> which contains among other things a
    # <sheets> tag, which in turn contains a number of <sheet> tags. Each
    # <sheet> tag has a name attribute with the name of that worksheet.
    sheetnames = []
    for sheet in wb_dom.find(WB_NS + 'sheets'):
        sheetname = sheet.get('name')
        if sheetname:
            sheetnames.append(sheetname)
    return sheetnames
