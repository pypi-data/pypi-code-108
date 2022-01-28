import io
import json
import platform
import re
import stat
import subprocess
import tempfile
import zipfile
from pathlib import Path
from uuid import uuid4

import requests
import yaml

from pedurma import config

PLATFORM_TYPE = platform.system()
BASE_DIR = Path.home() / ".antx"


def get_unique_id():
    return uuid4().hex


def get_pages(vol_text):
    result = []
    pg_text = ""
    pages = re.split(r"(〔[𰵀-󴉱]?\d+〕)", vol_text)
    for i, page in enumerate(pages[1:]):
        if i % 2 == 0:
            pg_text += page
        else:
            pg_text += page
            result.append(pg_text)
            pg_text = ""
    return result


def translate_tib_number(footnotes_marker):
    """Translate tibetan numeral in footnotes marker to roman number.

    Args:
        footnotes_marker (str): footnotes marker
    Returns:
        str: footnotes marker having numbers in roman numeral
    """
    value = ""
    if re.search(r"\d+\S+(\d+)", footnotes_marker):
        return value
    tib_num = {
        "༠": "0",
        "༡": "1",
        "༢": "2",
        "༣": "3",
        "༤": "4",
        "༥": "5",
        "༦": "6",
        "༧": "7",
        "༨": "8",
        "༩": "9",
    }
    numbers = re.finditer(r"\d", footnotes_marker)
    if numbers:
        for number in numbers:
            if re.search(r"[༠-༩]", number[0]):
                value += tib_num.get(number[0])
            else:
                value += number[0]
    return value


def from_yaml(yml_path):
    return yaml.load(yml_path.read_text(encoding="utf-8"), Loader=yaml.CLoader)


def to_yaml(dict_):
    return yaml.dump(dict_, sort_keys=False, allow_unicode=True, Dumper=yaml.CDumper)


def get_pecha_id(text_id, text_mapping=None):
    if not text_mapping:
        text_mapping = requests.get(config.NOTE_REF_NOT_FOUND_TEXT_LIST_URL)
        text_mapping = json.loads(text_mapping.text)
    text_info = text_mapping.get(text_id, {})
    pecha_id = text_info.get("namsel", "")
    return pecha_id


def to_editor(note):
    """Convert note page content to more readable view

    Args:
        note (str): note page content

    Returns:
        str: reformated note page content
    """
    repl_list = config.CHENYIK2EDITOR
    if "<r" in note:
        repl_list = config.CHENDRANG2EDITOR
    for old, new in repl_list:
        note = re.sub(old, new, note)
    return note


def notes_to_editor_view(notes):
    """Convert notes object content to more readble view

    Args:
        notes (list): list of note object

    Returns:
        list: list of note object
    """
    for note in notes:
        note.content = to_editor(note.content)
    return notes


def from_editor(note, type_):
    """Convert editor view note to its original format

    Args:
        note (str): editor view of note page content
        type_ (str): type of orc engine

    Returns:
        str: original note page content
    """
    repl_list = config.EDITOR2CHENYIK
    if type_ == "namsel":
        repl_list = config.EDITOR2CHENDRANG
    for old, new in repl_list:
        note = re.sub(old, new, note)
    return note


def notes_to_original_view(notes, type_):
    """Convert notes of editor view to original view

    Args:
        notes (list): list of note object
        type_ (str): orc engine type

    Returns:
        list: list of note object
    """
    for note in notes:
        note.content = from_editor(note.content, type_)
    return notes


def get_bin_metadata():
    """Return platfrom_type and binary_name."""
    if "Windows" in PLATFORM_TYPE:
        return "windows", "dmp.exe"
    elif "Drawin" in PLATFORM_TYPE:
        return "macos", "dmp"
    else:
        return "linux", "dmp"


def get_dmp_bin_url(platform_type):
    response = requests.get(
        "https://api.github.com/repos/Esukhia/node-dmp-cli/releases/latest"
    )
    version = response.json()["tag_name"]
    return (
        f"https://github.com/Esukhia/node-dmp-cli/releases/download/{version}/{platform_type}.zip",
        version,
    )


def get_dmp_exe_path():
    out_dir = BASE_DIR / "bin"
    out_dir.mkdir(exist_ok=True, parents=True)

    platform_type, binary_name = get_bin_metadata()
    binary_path = out_dir / binary_name
    if binary_path.is_file():
        return binary_path

    url, version = get_dmp_bin_url(platform_type)
    print(f"[INFO] Downloading node-dmp-cli-{version} ...")
    r = requests.get(url, stream=True, timeout=50)

    # attempt 50 times to download the zip
    check = zipfile.is_zipfile(io.BytesIO(r.content))
    attempts = 0
    while not check and attempts < 50:
        r = requests.get(url, stream=True, timeout=50)
        check = zipfile.is_zipfile(io.BytesIO(r.content))
        attempts += 1

    if not check:
        raise IOError("the .zip file couldn't be downloaded.")
    else:
        # extract the zip in the current folder
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(path=str(out_dir))

    print("[INFO] Download completed!")

    # make the binary executable
    binary_path.chmod(
        binary_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )
    return str(binary_path)


class optimized_diff_match_patch:
    def __init__(self):
        self.binary_path = get_dmp_exe_path()

    @staticmethod
    def _save_text(text1, text2):
        tmpdir = Path(tempfile.gettempdir())
        text1_path = tmpdir / "text1.txt"
        text2_path = tmpdir / "text2.txt"
        text1_path.write_text(text1, encoding="utf-8")
        text2_path.write_text(text2, encoding="utf-8")
        return str(text1_path), str(text2_path)

    @staticmethod
    def _delete_text(text1_path, text2_path):
        Path(text1_path).unlink()
        Path(text2_path).unlink()

    @staticmethod
    def _unescape_lr(diffs):
        """Unescape the line-return."""
        for diff_type, diff_text in diffs:
            if "Windows" in PLATFORM_TYPE:
                yield (diff_type, diff_text.replace("\r\\n", "\n"))
            else:
                yield (diff_type, diff_text.replace("\\n", "\n"))

    def diff_main(self, text1, text2):
        text1_path, text2_path = self._save_text(text1, text2)
        process = subprocess.Popen(
            [str(self.binary_path), "diff", text1_path, text2_path],
            stdout=subprocess.PIPE,
        )
        stdout = process.communicate()[0]
        diffs = json.loads(stdout)
        diffs = self._unescape_lr(diffs)
        self._delete_text(text1_path, text2_path)
        return diffs
