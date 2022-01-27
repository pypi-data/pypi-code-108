import struct
import gzip


def unpack(ios, struct_format, size, list_return=False):
    """
    Use a given struct formatting to unpack a byte code

    Struct formatting
    ------------------
    https://docs.python.org/3/library/struct.html

    :param ios: Buffered I/O implementation using an in-memory bytes buffer.
    :type ios: _io.BytesIO

    :param struct_format: The string representation of the format to use in struct format. See struct formatting for
        a list of example codes.
    :type struct_format: str

    :param size: The byte size
    :type size: int

    :param list_return: If more than one object is set to be returned, they can be returned as list rather than just
        extracting the first element
    :type list_return: bool

    :return: Whatever was unpacked
    :rtype: Any
    """
    if list_return:
        return struct.unpack(struct_format, ios.read(size))
    else:
        return struct.unpack(struct_format, ios.read(size))[0]


def read_text(ios, size):
    """
    Unpack text of byte size 'size', search for the first Null character as the end point of the string from the
    byte extracted.

    :param ios: Buffered I/O implementation using an in-memory bytes buffer.
    :type ios: _io.BytesIO

    :param size: The byte size to extract
    :type size: int

    :return: The none Null components of the extracted byte in a byte format
    :rtype: byte
    """

    src = unpack(ios, f"{size}s", size)
    pos = src.find(b"\x00")

    if pos == -1:
        return src
    else:
        return src[:pos]


def open_setter(path):
    """
    Some files may be zipped, opens files according to the zip status

    :param path: File path
    :type path: Path
    :return: gzip.open if the file is gzipped else open
    """
    if path.suffix == ".gz":
        return gzip.open
    else:
        return open


def decode_line(line, zip_status, splitter=None):
    """
    Some files may be zipped, when we open zipped files we will need to decode them

    # Todo: What type is line / return?
    :param line: Current line from open file, zipped or otherwise

    :param zip_status: If the file is zipped or not
    :type zip_status: bool

    :param splitter: If you want to split the decoded line on a custom splitter, submit it this
    :type splitter: None | str

    :return: decoded line from the open file
    """
    if splitter:
        if zip_status:
            return line.decode("utf-8").split(splitter)
        else:
            return line.split(splitter)
    else:
        if zip_status:
            return line.decode("utf-8").split()
        else:
            return line.split()
