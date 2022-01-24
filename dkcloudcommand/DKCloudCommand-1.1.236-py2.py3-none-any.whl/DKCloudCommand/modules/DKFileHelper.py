import codecs
import json
import os
import shutil

from datetime import datetime
from typing import Union, Optional

from DKCommon.DKFileEncode import DKFileEncode


class DKFileHelper:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_file_date(file_path: str) -> Optional[datetime.date]:
        if not os.path.exists(file_path):
            return None

        if not os.path.isfile(file_path):
            return None

        return datetime.fromtimestamp(os.path.getmtime(file_path)).date()

    @staticmethod
    def is_file_contents_binary(file_contents: str) -> bool:
        try:
            file_contents.encode("utf8")
            return False
        except Exception:
            return True

    @staticmethod
    def create_dir_if_not_exists(directory: str) -> None:
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def create_path_if_not_exists(full_path: str) -> None:
        if not os.path.exists(full_path):
            os.makedirs(full_path)

    @staticmethod
    def clear_dir(directory: str) -> None:
        if os.path.exists(directory):
            shutil.rmtree(directory)

    @staticmethod
    def read_file(
        full_path: str, encoding: Optional[str] = None, b64_encode_binary_files: bool = False
    ) -> Union[str, bytes]:
        if not os.path.isfile(full_path):
            return ""
        if encoding is None:
            encoding = DKFileEncode.infer_encoding(full_path)

        if "utf-8" == encoding:
            try:
                with codecs.open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                message = str(e)
                message += f"{os.linesep}File name: {full_path}"
                raise Exception(message)
        else:
            with open(full_path, "rb") as the_file:
                file_contents = the_file.read()
                if b64_encode_binary_files:
                    return DKFileEncode.b64encode(file_contents)
                else:
                    return file_contents

    @staticmethod
    def write_file(full_path: str, contents: str, encoding: Optional[str] = None) -> None:
        path, file_name = os.path.split(full_path)
        if path is not None and path != "":
            DKFileHelper.create_path_if_not_exists(path)
        if isinstance(contents, dict):
            contents = json.dumps(contents)
        with open(full_path, "wb+") as the_file:
            the_file.seek(0)
            the_file.truncate()
            if encoding == "base64" and contents is not None:
                the_file.write(DKFileEncode.b64decode(contents))
            elif contents is not None:
                if isinstance(contents, str):
                    contents = contents.encode("utf-8")
                the_file.write(contents)
