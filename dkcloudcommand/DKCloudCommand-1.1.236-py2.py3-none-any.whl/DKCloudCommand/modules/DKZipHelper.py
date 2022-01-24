import zipfile
from io import BytesIO


class DKZipHelper:
    def __init__(self) -> None:
        pass

    @staticmethod
    def unzip_first_file_as_string_or_unicode(input_data: bytes) -> str:
        zip_raw_data = BytesIO()
        zip_raw_data.write(input_data)
        the_zip_file = zipfile.ZipFile(zip_raw_data)
        info_list = the_zip_file.infolist()
        for item in info_list:
            filename = item.filename
            the_file = the_zip_file.open(filename)
            return the_file.read().decode("utf-8")
