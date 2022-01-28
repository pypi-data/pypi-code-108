from pathlib import Path

import yaml
from pydantic.networks import AnyHttpUrl

from pedurma.pecha import PageWithNote
from pedurma.reinsertion import reinsert_pedurma_notes
from pedurma.utils import from_yaml, to_yaml


class Pedurma:
    def __init__(self, project_name: str, base_path: Path):
        self.project_name = project_name
        self.base_path = base_path / project_name
        self.meta = {
            "work_id": "W1PD95844",
            "img_grp_offset": 845,
            "pref": "I1PD95",
        }  # tenjur meta

    def get_vol_num(self, text_id: str) -> int:
        text_infos = text_id.split("_")
        vol_num = text_infos[1]
        return int(vol_num)

    def get_page_meta(self, text_id: str, page_id: str) -> dict:
        page_meta = {}
        vol_num = self.get_vol_num(text_id)
        page_meta["vol"] = vol_num
        page_meta["page_num"] = page_id
        return page_meta

    def get_page_content(self, text_id: str, page_id: str) -> str:
        page_content = (self.base_path / f"{text_id}/pages/{page_id}.txt").read_text(
            encoding="utf-8"
        )
        return page_content

    def get_page_note(self, text_id: str, page_id: str) -> str:
        page_content = from_yaml((self.base_path / f"{text_id}/notes/{page_id}.yml"))
        return page_content

    def get_image_link(self, page_meta: dict) -> AnyHttpUrl:
        vol = page_meta["vol"]
        pg_num = page_meta["page_num"]
        img_group_offset = self.meta["img_grp_offset"]
        pref = self.meta["pref"]
        igroup = f"{pref}{img_group_offset+vol}"
        link = f"https://iiif.bdrc.io/bdr:{igroup}::{igroup}{int(pg_num):04}.jpg/full/max/0/default.jpg"
        return link

    def get_page(self, text_id: str, page_id: str) -> PageWithNote:
        page_meta = self.get_page_meta(text_id, page_id)
        page_content = self.get_page_content(text_id, page_id)
        page_image_link = self.get_image_link(page_meta)
        page_note = self.get_page_note(text_id, page_id)
        note = to_yaml(page_note["notes"])
        note_image_link = page_note["note_pg_link"]
        page = PageWithNote(
            text_id=text_id,
            page_id=page_id,
            content=page_content,
            page_image_link=page_image_link,
            note=note,
            note_image_link=note_image_link,
        )
        return page

    def save_page(self, page: PageWithNote):
        text_id = page.text_id
        page_id = page.page_id
        # Page content save
        new_page_content = page.content
        (self.base_path / f"{text_id}/pages/{page_id}.txt").write_text(
            new_page_content, encoding="utf-8"
        )
        # Note content save
        new_note = yaml.load(page.note, Loader=yaml.CLoader)
        page_note = self.get_page_note(text_id, page_id)
        page_note["notes"] = new_note
        new_page_note = to_yaml(page_note)
        (self.base_path / f"{text_id}/notes/{page_id}.yml").write_text(
            new_page_note, encoding="utf-8"
        )

    def get_preview(self, page: PageWithNote) -> str:
        pg_content = page.content
        notes = yaml.load(page.note, Loader=yaml.CLoader)
        preview_pg = reinsert_pedurma_notes(pg_content, notes)
        return preview_pg

    def get_collation_text(self, text_id: str) -> str:
        collation_text = ""
        page_ids = list((self.base_path / f"{text_id}/notes").iterdir())
        page_ids.sort()
        page_ids = [page_id.stem for page_id in page_ids]
        for page_id in page_ids:
            page_obj = self.get_page(text_id, page_id)
            collation_text += f"{self.get_preview(page_obj)}\n\n"
        return collation_text
