from pedurma.pecha import ProofreadNotePage
from pedurma.utils import from_yaml


def get_note_page_img_link(text_id, pg_num, repo_path):
    text_meta = from_yaml((repo_path / text_id / "meta.yml"))
    image_grp_id = text_meta.get("img_grp_id", "")
    img_link = f"https://iiif.bdrc.io/bdr:{image_grp_id}::{image_grp_id}{int(pg_num):04}.jpg/full/max/0/default.jpg"
    return img_link


def get_note_page(text_id, cur_pg_num, repo_path=None):
    try:
        manual_note = (
            repo_path / text_id / "manual_notes" / f"{cur_pg_num:04}.txt"
        ).read_text(encoding="utf-8")
    except Exception:
        manual_note = ""
    google_note = (
        repo_path / text_id / "google_notes" / f"{cur_pg_num:04}.txt"
    ).read_text(encoding="utf-8")
    img_link = get_note_page_img_link(text_id, cur_pg_num, repo_path)

    page = ProofreadNotePage(
        manual=manual_note, google=google_note, img_link=img_link, page_num=cur_pg_num
    )
    return page


def get_note_pages(text_id, repo_path):
    note_pages = []
    page_paths = list((repo_path / text_id / "google_notes").iterdir())
    page_paths.sort()
    for page_path in page_paths:
        page_num = int(page_path.stem)
        note_pages.append(get_note_page(text_id, page_num, repo_path))
    return note_pages


def update_note_page(text_id, page: ProofreadNotePage, repo_path=None):
    new_manual_note_page = page.manual
    cur_pg_num = page.page_num
    (repo_path / text_id / "manual_notes" / f"{cur_pg_num:04}.txt").write_text(
        new_manual_note_page, encoding="utf-8"
    )
    print(f"INFO: {cur_pg_num} updated")
