import re
from pathlib import Path
from uuid import uuid4

from pedurma.utils import to_yaml


def get_note_layer(note_annotation):
    note_layer = {
        "id": uuid4().hex,
        "annotation_type": "PedurmaNote",
        "revision": "00001",
        "annotations": note_annotation,
    }
    return note_layer


def get_pages(vol_text):
    result = []
    pg_text = ""
    pages = re.split(r"([0-9]+\-[0-9]+)", vol_text)
    for i, page in enumerate(pages[0:]):
        if i % 2 == 0:
            pg_text += page
        else:
            pg_text += page
            result.append(pg_text)
            pg_text = ""
    return result


def get_last_syl_and_note_match(note_pattern, note):
    if re.search(r"ལྟར་བཀོད།", note):
        last_syl = ""
    elif re.search(r"#", note_pattern):
        syls = re.split(r"#", note_pattern)
        last_syl = syls[1]
    else:
        last_syl = note_pattern
    note_match = last_syl + note
    return last_syl, note_match


def parse_note(note, walker, page_content, plus_present):
    note_ann = {}
    note_pattern = re.search(rf"(:\S+)?{note}", page_content)
    if plus_present:
        plus_note = re.sub(r"\+", r"\+", note)
        if re.search(rf"\S+་([^#]\S+་?){plus_note}", page_content):
            note_pattern = re.search(rf"\S+་([^#]\S+་?){plus_note}", page_content)
            last_syl, note_match = get_last_syl_and_note_match(
                note_pattern.group(1), plus_note
            )
            grp_1_loc = page_content.find(last_syl + note)
        else:
            note_pattern = re.search(rf"([^#]\S+་?){plus_note}", page_content)
            if note_pattern:
                grp_1_loc = note_pattern.start()
                last_syl = ""
        ann_start = grp_1_loc + walker + len(last_syl)
        ann_end = ann_start
    else:
        if note_pattern.group(1):
            ann_start = note_pattern.start() + walker
            ann_end = ann_start + len(note_pattern.group(1))
        else:
            if re.search(rf"\S+་([^#]\S+་?){note}", page_content):
                note_pattern = re.search(rf"\S+་([^#]\S+་?){note}", page_content)
                last_syl, note_match = get_last_syl_and_note_match(
                    note_pattern.group(1), note
                )
                grp_1_loc = page_content.find(note_match)
            else:
                note_pattern = re.search(rf"([^#]\S+་?){note}", page_content)
                if note_pattern:
                    grp_1_loc = note_pattern.start()
                    last_syl = note_pattern.group(1)
            ann_start = grp_1_loc + walker
            if note_pattern.group(1):
                ann_end = ann_start + len(last_syl)
            else:
                ann_end = ann_start
    note_ann = {
        "span": {
            "start": ann_start,  # the variant unit or variant location is capture with help of this span
            "end": ann_end,
        },
        "collation_note": note,
    }
    page_content = re.sub(note, "", page_content, 1)
    return note_ann, page_content


def parse_page(page, note_annotation, char_walker):
    cur_note = {}
    page = page.replace("\n", "#")
    page_content = re.sub(r"(\([༠-༩]+\)\s)", "", page)
    notes = re.findall(r"\<.*?\>", page_content)
    for note in notes:
        match = re.search(r"(\<.*?)(\+)(.*?\>)", note)
        if match:
            if match.group(2):
                note_info, page_content = parse_note(
                    note, char_walker, page_content, True
                )
        else:
            note_info, page_content = parse_note(note, char_walker, page_content, False)
        cur_note[uuid4().hex] = note_info
        note_annotation.update(cur_note)
        cur_note = {}
    new_page = base_extract(page)
    return note_annotation, new_page


def base_extract(text):
    text = re.sub(r"#", "\n", text)
    return re.sub(r"(\([༠-༩]+\)\s)?<.*?>", "", text)


def build_note_layer(text):
    char_walker = 0
    note_annotation = {}
    pages = get_pages(text)
    for page in pages:
        page = re.sub(r"([0-9]+\-[0-9]+)", "\n", page)
        note_annotation, new_page = parse_page(page, note_annotation, char_walker)
        char_walker += len(new_page) - 1
    note_layer = get_note_layer(note_annotation)
    return note_layer


def update_hybird_pecha_note_layer(preview_text, hybird_pecha_path, vol_num):
    hybird_pecha_path = Path(hybird_pecha_path)
    note_layer = build_note_layer(preview_text)
    note_yml = to_yaml(note_layer)
    note_yml_path = (
        hybird_pecha_path
        / f"{hybird_pecha_path.stem}.opf"
        / "layers"
        / f"v{vol_num:03}"
        / "PedurmaNote.yml"
    )
    note_yml_path.write_text(note_yml, encoding="utf-8")
