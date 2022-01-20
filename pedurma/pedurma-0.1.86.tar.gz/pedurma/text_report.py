import re
from datetime import datetime
from pathlib import Path

from openpecha.utils import load_yaml

from pedurma.texts import get_pecha_paths


def get_metadata(pecha_path):
    pecha_id = Path(pecha_path).stem
    meta_path = Path(pecha_path) / f"{pecha_id}.opf" / "meta.yml"
    metadata = load_yaml(meta_path)
    return metadata


def get_text_title(pecha_path):
    text_title = ""
    opf_meta = get_metadata(pecha_path)
    text_source_metadata = opf_meta.get("source_metadata", {})
    if text_source_metadata:
        text_title = text_source_metadata.get("title", "")
    return text_title


def get_number_of_pages(vol_text):
    pg_anns = re.findall(r"\d+-\d+", vol_text)
    return len(pg_anns)


def get_number_of_footnotes(vol_text):
    footnotes_annotations = re.findall("<.+?>", vol_text)
    return len(footnotes_annotations)


def get_text_report(text_id, pecha_paths, preview_text):
    text_report = {
        "toh_no": text_id,
        "title": None,
        "total_number_of_pages": None,
        "total_number_of_footnotes": None,
        "download_date": None,
    }
    if pecha_paths is None:
        pecha_paths = get_pecha_paths(text_id)
    text_report["title"] = get_text_title(pecha_paths["google"])
    number_of_pages = 0
    number_of_footnotes = 0
    for vol_num, vol_text in preview_text.items():
        number_of_pages += get_number_of_pages(vol_text)
        number_of_footnotes += get_number_of_footnotes(vol_text)
    text_report["total_number_of_pages"] = number_of_pages
    text_report["total_number_of_footnotes"] = number_of_footnotes
    text_report["download_date"] = datetime.now()
    return text_report
