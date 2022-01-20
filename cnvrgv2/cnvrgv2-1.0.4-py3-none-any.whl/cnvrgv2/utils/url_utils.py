import re
import base64
import mimetypes
import os


def urljoin(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    @param args: strings to join into a url
    @return: Valid url string
    """

    joined_url = "/".join(map(lambda x: str(x).strip('/'), args))
    return format_url(joined_url)


def format_url(url):
    # remove double slashes from the url to support oauth proxy
    return re.sub(r'[\/]{2,}', "/", url).replace("http:/", "http://").replace("https:/", "https://")


def encode_base64(file_path, encoding_type="utf-8"):
    """
    Base 64 converter
    @param file_path: A file path
    @param encoding_type: Type of encoding, default utf-8
    @return: An object including filename, type, size and base64 content like a File spec
    """
    if file_path:
        file = open(file_path, "rb")
        binary_file = file.read()
        file_type = mimetypes.guess_type(file_path)[0]

        return {
            "filename": os.path.basename(file_path),
            "type": file_type,
            "size": os.path.getsize(file_path),
            "content": "data:" + file_type + ";base64," + (base64.b64encode(binary_file)).decode(encoding_type)
        }
