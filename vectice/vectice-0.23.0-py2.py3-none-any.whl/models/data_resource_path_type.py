import mimetypes
from enum import EnumMeta
from typing import Optional

mimetypes.init()
mimetypes.add_type("application/x-ipynb+json", ".ipynb")
mimetypes.add_type("text/csv", ".csv")


class DataResourcePathType(EnumMeta):
    Folder = "Folder"
    CsvFile = "CsvFile"
    ImageFile = "ImageFile"
    ExcelFile = "ExcelFile"
    TextFile = "TextFile"
    MdFile = "MdFile"
    DataSet = "DataSet"
    DataTable = "DataTable"
    File = "File"
    Notebook = "Notebook"

    @classmethod
    def get_file_type(cls, path: str):
        extension: Optional[str] = None
        try:
            extension = path.split(".", 1)[1].lower()
        except Exception:
            extension = None
        if extension == "csv":
            return DataResourcePathType.CsvFile
        # should we check stream with imghdr ?
        elif extension in ["jpg", "jpeg", "png", "webp", "bmp", "xbm", "tiff", "ppm", "pgm", "pbm", "gif", "exr"]:
            return DataResourcePathType.ImageFile
        elif extension == "md":
            return DataResourcePathType.MdFile
        elif extension == "ipynb":
            return DataResourcePathType.Notebook
        elif extension in ["txt", "text"]:
            return DataResourcePathType.TextFile
        elif extension in ["xls", "xlsx"]:
            return DataResourcePathType.ExcelFile
        else:
            return DataResourcePathType.File

    @classmethod
    def get_file_format(cls, path: str):
        return mimetypes.guess_type(path)[0]
