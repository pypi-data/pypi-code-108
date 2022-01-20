import csv
from os import write
from pathlib import Path

from pedurma.docx_serializer import get_docx_text
from pedurma.reconstruction import get_reconstructed_text
from pedurma.text_report import get_text_report


def save_preview_text(text_id, preview_text, output_path):
    for vol_id, vol_text in preview_text.items():
        (output_path / f"{text_id}_{vol_id}.txt").write_text(vol_text, encoding="utf-8")
    print("INFO: Preview saved")


def save_docx_preview(text_id, preview_text, output_path):
    get_docx_text(text_id, preview_text, output_path)
    get_docx_text(text_id, preview_text, output_path, type_="footnotes_at_page_end")
    print("INFO: Preview docx saved")


def save_text_report(text_id, text_report, output_path):
    output_path = str(output_path / f"{text_id}_report.csv")
    header = text_report.keys()
    data = text_report.values()
    with open(output_path, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(data)
    print("INFO: Text report saved")


def get_preview_text(text_id, output_path, pecha_paths=None):
    (Path(output_path) / text_id).mkdir(parents=True, exist_ok=True)
    output_path = output_path / text_id
    preview_text, google_pecha_id = get_reconstructed_text(text_id, pecha_paths)
    text_report = get_text_report(text_id, pecha_paths, preview_text)
    save_preview_text(text_id, preview_text, output_path)
    save_text_report(text_id, text_report, output_path)
    save_docx_preview(text_id, preview_text, output_path)
    return output_path, google_pecha_id
