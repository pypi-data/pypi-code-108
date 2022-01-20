import json
import re
from collections import defaultdict
from os import stat_result
from pathlib import Path

import requests
from openpecha.serializers import HFMLSerializer
from openpecha.utils import download_pecha, load_yaml

from pedurma import config
from pedurma.exceptions import TextMappingNotFound
from pedurma.pecha import NotesPage, Page, PedurmaText, Text
from pedurma.utils import get_pages, notes_to_editor_view


def get_text_info(text_id, index):
    """Return text span and its uuid from pecha index using text id 

    Args:
        text_id (str): text id
        index (dict): pecha index

    Returns:
        tuple: (uuid, text_ann) if not found ("","")
    """
    texts = index["annotations"]
    for uuid, text in texts.items():
        if text["work_id"] == text_id:
            return (uuid, text)
    return ("", "")


def get_hfml_text(opf_path, text_id, index=None):
    """Return hmfl of text from the pecha opf

    Args:
        opf_path (str): opf path
        text_id (str): text id
        index (dict, optional): pecha index. Defaults to None.

    Returns:
        dict: vol id as key and hfml as the content
    """
    serializer = HFMLSerializer(
        opf_path, text_id=text_id, index_layer=index, layers=["Pagination", "Durchen"]
    )
    serializer.apply_layers()
    hfml_text = serializer.get_result()
    return hfml_text


def get_body_text(text_with_durchen):
    """Extract body text from the text hfml which contains both body and durchen of the text

    Args:
        text_with_durchen (str): hfml of the text

    Returns:
        str: body text from the hfml of text
    """
    body_text = ""
    pages = get_pages(text_with_durchen)
    for page in pages:
        if re.search("<[𰵀-󴉱]?d", page):
            return body_text
        body_text += page
    return body_text


def get_durchen(text_with_durchen):
    """Extract durchen from hfml text which contains both body text and durchen

    Args:
        text_with_durchen (str): hfml of text

    Returns:
        str: durchen of the text
    """
    durchen = ""
    durchen_start = False
    pages = get_pages(text_with_durchen)
    for page in pages:
        if re.search("<[𰵀-󴉱]?d", page) or durchen_start:
            durchen += page
            durchen_start = True
        if re.search("d>", page):
            return durchen
    if not durchen:
        print("INFO: durchen not found..")
    return durchen


def get_page_id(img_num, pagination_layer):
    """Return page uuid of given imgnum from the pagination layer

    Args:
        img_num (int): imgnum
        pagination_layer (dict): pagination layer

    Returns:
        uuid: uuid of the page corresponding to the given imgnum
    """
    paginations = pagination_layer["annotations"]
    for uuid, pagination in paginations.items():
        if pagination["imgnum"] == img_num:
            return uuid
    return ""


def get_link(img_num, vol_meta):
    """Return bdrc image link using imgnum and vol mete data

    Args:
        img_num (int): image number
        vol_meta (dict): vol meta data

    Returns:
        str: image link
    """
    image_grp_id = vol_meta["image_group_id"]
    link = f"https://iiif.bdrc.io/bdr:{image_grp_id}::{image_grp_id}{int(img_num):04}.jpg/full/max/0/default.jpg"
    return link


def get_note_ref(img_num, pagination_layer):
    """Return noteref id of given image number

    Args:
        img_num (int): image number 
        pagination_layer (dict): pagination layer

    Returns:
        uuid: note ref uuid if exist else empty string
    """
    paginations = pagination_layer["annotations"]
    for uuid, pagination in paginations.items():
        if pagination["imgnum"] == img_num:
            try:
                return pagination["note_ref"]
            except Exception:
                return ""
    return ""


def get_note_refs(img_num, pagination_layer):
    """Return note ref of given img num and next img num if respective note refs are different else note ref of given img num is return

    Args:
        img_num (int): image number
        pagination_layer (dict): pagination layer

    Returns:
        list: note refs list
    """
    note_refs = []
    cur_pg_note_ref = get_note_ref(img_num, pagination_layer)
    note_refs.append(cur_pg_note_ref)
    next_pg_note_ref = get_note_ref(img_num + 1, pagination_layer)
    if next_pg_note_ref and cur_pg_note_ref != next_pg_note_ref:
        note_refs.append(next_pg_note_ref)
    return note_refs


def get_clean_page(page):
    """Remove all the hfml annotation in page

    Args:
        page (ste): page content

    Returns:
        str: clean page
    """
    pat_list = {
        "page_pattern": r"〔[𰵀-󴉱]?\d+〕",
        "topic_pattern": r"\{([𰵀-󴉱])?\w+\}",
        "start_durchen_pattern": r"\<([𰵀-󴉱])?d",
        "end_durchen_pattern": r"d\>",
        "sub_topic_pattern": r"\{([𰵀-󴉱])?\w+\-\w+\}",
    }
    base_page = page
    for ann, ann_pat in pat_list.items():
        base_page = re.sub(ann_pat, "", base_page)
    base_page = base_page.strip()
    return base_page


def get_page_num(page):
    """Extract real page number from page contentusing regex

    Args:
        page (str): page content

    Returns:
        int: page number
    """
    page_num = 1
    page_ann = re.search(r"\d+-(\d+)", page)
    if page_ann:
        page_num = int(page_ann.group(1))
    return page_num


def get_page_obj(page, vol_meta, tag, pagination_layer):
    """Return page object by processing page hfml text

    Args:
        page (str): page hfml
        vol_meta (dict): volume meta data
        tag (str): tag can be either text or note
        pagination_layer (dict): pagination layer

    Returns:
        obj: page object
    """
    img_num = int(re.search(r"〔[𰵀-󴉱]?(\d+)〕", page).group(1))
    page_num = 0
    page_id = get_page_id(img_num, pagination_layer)
    page_content = get_clean_page(page)
    page_link = get_link(img_num, vol_meta)
    note_ref = get_note_refs(img_num, pagination_layer)
    if page_content == "":
        page_obj = None
    else:
        if tag == "note":
            page_obj = NotesPage(
                id=page_id,
                page_no=page_num,
                content=page_content,
                name=f"Page {img_num}",
                vol=vol_meta["volume_number"],
                image_link=page_link,
            )
        else:
            page_obj = Page(
                id=page_id,
                page_no=page_num,
                content=page_content,
                name=f"Page {img_num}",
                vol=vol_meta["volume_number"],
                image_link=page_link,
                note_ref=note_ref,
            )

    return page_obj


def add_start_page_number(pages):
    start_page_number = get_page_num(pages[0].content)
    pages[0].page_no = start_page_number
    return pages, start_page_number


def get_page_obj_list(text, vol_meta, pagination_layer, tag="text"):
    """Return page object list of the given hfml text according to tag

    Args:
        text (hfml): hfml text
        vol_meta (dict): volume meta data
        pagination_layer (dict): pagiantion layer
        tag (str, optional): if note return list of note obj else page object. Defaults to "text".

    Returns:
        list: list of either page obj or note obj
    """
    page_obj_list = []
    start_page_number = 0
    pages = get_pages(text)
    for page in pages:
        pg_obj = get_page_obj(page, vol_meta, tag, pagination_layer)
        if pg_obj:
            page_obj_list.append(pg_obj)
    if tag == "text":
        page_obj_list, start_page_number = add_start_page_number(page_obj_list)
    return page_obj_list, start_page_number


def get_vol_meta(vol_num, pecha_meta):
    """Extract volume meta from pecha meta data using volume number

    Args:
        vol_num (int): volume number
        pecha_meta (dict): pecha meta data

    Returns:
        dict: volume meta of the given volume number
    """
    vol_meta = {}
    vol_num = int(vol_num[1:])
    text_vols = pecha_meta["source_metadata"].get("volumes", {})
    if text_vols:
        for vol_id, vol in text_vols.items():
            if vol["volume_number"] == vol_num:
                vol_meta = vol
    return vol_meta


def get_first_note_pg(notes, vol_meta):
    """Return first note page object of the working volume

    Args:
        notes (list): list of notes object
        vol_meta (dict): working volume meta data

    Returns:
        obj: note object
    """
    for note in notes:
        if int(note.vol) == vol_meta["volume_number"]:
            return note
    return None


def get_cur_vol_notes(notes, vol_meta):
    """Return list of notes obj which belogs to vol mentioned in vol meta

    Args:
        notes (list[note obj]): list of note objects
        vol_meta (dict): contents volume meta data

    Returns:
        list: list of notes object
    """
    cur_vol_notes = []
    for note in notes:
        if int(note.vol) == vol_meta["volume_number"]:
            cur_vol_notes.append(note)
    return cur_vol_notes


def get_last_page_note_ref(cur_vol_notes):
    """Generate list of note refs for thelast extra page object

    Args:
        notes (list): list of note object
        vol_meta (dict): volume meta data

    Returns:
        lsit: list of note refs
    """
    last_page_note_refs = []
    if len(cur_vol_notes) >= 2:
        last_page_note_refs = [cur_vol_notes[-2].id, cur_vol_notes[-1].id, "--"]
    elif len(cur_vol_notes) == 1:
        last_page_note_refs = [cur_vol_notes[-1].id, "--"]
    else:
        last_page_note_refs = ["--"]
    return last_page_note_refs


def get_page_ann(page):
    """Return page number annotation from the page content

    Args:
        page (obj): page object

    Returns:
        str: page number annotation
    """
    pg_ann = ""
    page_content = page.content
    vol = page.vol
    if re.search(fr"{vol}-\d+", page_content):
        pg_ann = re.search(fr"{vol}-\d+", page_content)[0]
    return pg_ann


def get_last_pg_ann(page):
    """Return last page number annotation from the page content

    Args:
        page (obj): page object

    Returns:
        str: page number annotation
    """
    pg_ann = ""
    page_content = page.content
    vol = page.vol
    if re.search(fr"{vol}-\d+", page_content):
        pg_num = int(re.search(fr"{vol}-(\d+)", page_content).group(1)) + 1
        pg_ann = f"{vol}-{pg_num}"
    return pg_ann


def get_last_pg_content(first_note_pg, pages):
    """Return last extra page content as first note page content but clipped from བསྡུར་མཆན if exist else return the whole note pg content 

    Args:
        first_note_pg (note obj): first note object of work volume

    Returns:
        str: last extra page content
    """
    last_pg_content = first_note_pg.content
    last_pg_content = re.sub("<r.+>", "", last_pg_content)
    pg_ann = get_last_pg_ann(pages[-1])
    if re.search("བསྡུར་མཆན", last_pg_content):
        new_pg_end = re.search("བསྡུར་མཆན", last_pg_content).end()
        last_pg_content = f"{last_pg_content[:new_pg_end]}\n{pg_ann}"
    return last_pg_content


def get_last_page(cur_vol_pages, cur_vol_notes, vol_meta, start_page_number):
    """Generate last extra page object

    Args:
        pages (list): list of page object
        notes (list): list of note object
        vol_meta (dict): volume meta data

    Returns:
        object: page object
    """
    if cur_vol_pages[-1].note_ref[0] != cur_vol_notes[-1].id:
        cur_vol_pages[-1].note_ref.insert(1, cur_vol_notes[-1].id)
    first_note_pg = cur_vol_notes[0]
    pg_content = get_last_pg_content(first_note_pg, cur_vol_pages)
    note_refs = get_last_page_note_ref(cur_vol_notes)
    page_num = get_page_num(pg_content)
    if page_num == 1 or page_num - start_page_number != len(cur_vol_pages):
        page_num = start_page_number + len(cur_vol_pages)
    last_page = Page(
        id=first_note_pg.id,
        page_no=page_num,
        content=pg_content,
        name=first_note_pg.name,
        vol=first_note_pg.vol,
        image_link=first_note_pg.image_link,
        note_ref=note_refs,
    )
    return [last_page]


def construct_text_obj(hfmls, pecha_meta, opf_path):
    """Generate text obj from text hfmls

    Args:
        hfmls (dict): vol as key and text hfml as value
        pecha_meta (dict): pecha meta data
        opf_path (str): opf path

    Returns:
        obj: text object
    """
    pages = []
    notes = []
    for vol_num, hfml_text in hfmls.items():
        start_page_number = 1
        vol_meta = get_vol_meta(vol_num, pecha_meta)
        pagination_layer = load_yaml(
            Path(f"{opf_path}/{pecha_meta['id']}.opf/layers/{vol_num}/Pagination.yml")
        )
        durchen = get_durchen(hfml_text)
        body_text = get_body_text(hfml_text)

        cur_vol_pages, start_page_number = get_page_obj_list(
            body_text, vol_meta, pagination_layer, tag="text"
        )
        pages += cur_vol_pages
        if durchen:
            cur_vol_notes, _ = get_page_obj_list(
                durchen, vol_meta, pagination_layer, tag="note"
            )
            notes += cur_vol_notes
        if notes:
            pages += get_last_page(
                cur_vol_pages, cur_vol_notes, vol_meta, start_page_number
            )
    notes = notes_to_editor_view(notes)
    text_obj = Text(id=pecha_meta["text_uuid"], pages=pages, notes=notes)
    return text_obj


def get_body_text_from_last_page(page):
    """Extract body text from last extra page

    Args:
        page (obj): last extra page object

    Returns:
        str: body text part if any exist else nothing
    """
    body_part = ""
    last_page = page.content
    if re.search("བསྡུར་མཆན", last_page):
        durchen_start_pat = re.search("བསྡུར་མཆན", last_page)
        body_part = last_page[: durchen_start_pat.start()]
    return body_part


def get_note_text_from_first_note_page(note):
    """Extract note text from first note page as it might content body text

    Args:
        note (obj): note object

    Returns:
        str: note text from the first note page as it might content body text
    """
    first_page = note.content
    note_part = first_page
    if re.search("བསྡུར་མཆན", first_page):
        durchen_start_pat = re.search("བསྡུར་མཆན", first_page)
        note_part = first_page[durchen_start_pat.start() :]
    return note_part


def get_first_note_content(page, note):
    """First note page content is combined by body text from the last extra page object and note text from the first note page object

    Args:
        page (obj): last extra page object
        note (obj): first note page object

    Returns:
        str: update first note page content
    """
    first_note_content = ""
    body_part = get_body_text_from_last_page(page)
    note_part = get_note_text_from_first_note_page(note)
    first_note_content = body_part + note_part
    return first_note_content


def merge_last_pg_with_note_pg(text, page):
    """Merge last extra page content to first note page content

    Args:
        text (obj): text object
        page (obj): last extra page object
    """
    first_note = None
    for pg_walker, note in enumerate(text.notes):
        if note.vol == page.vol:
            first_note = note
            break
    text.notes[pg_walker].content = get_first_note_content(page, first_note)


def remove_last_pages(text):
    """Updating first note page content using last extra page object and remove last extra page object 

    Args:
        text (obj): text object

    Returns:
        obj: updated text object
    """
    new_pages = []
    for pg_walker, page in enumerate(text.pages):
        if "--" in page.note_ref:
            merge_last_pg_with_note_pg(text, page)
            continue
        new_pages.append(page)
    new_text = Text(id=text.id, pages=new_pages, notes=text.notes)
    return new_text


def serialize_text_obj(text):
    """Serialize text object to hfml

    Args:
        text (obj): text object

    Returns:
        dict: vol as key and value as hfml
    """
    text_hfml = defaultdict(str)
    pages = text.pages
    notes = text.notes
    for page in pages:
        text_hfml[f"v{int(page.vol):03}"] += f"{page.content}\n\n"
    for note in notes:
        text_hfml[f"v{int(note.vol):03}"] += f"{note.content}\n\n"
    return text_hfml


def get_durchen_page_objs(page, notes):
    note_objs = []
    for note in notes:
        if note.id in page.note_ref:
            note_objs.append(note)
    return note_objs


def get_pecha_paths(text_id, text_mapping=None):
    """Return instace pecha path of the given text id

    Args:
        text_id (str): text id
        text_mapping (dict, optional): text id ad key and another dictionary as value where key is instance name and value is intance pecha id. Defaults to None.

    Raises:
        TextMappingNotFound: if text id doesn't exist in the mapping file raise this expection

    Returns:
        dict: instance name and pecha path
    """
    pecha_paths = {"namsel": None, "google": None}
    if not text_mapping:
        text_mapping = requests.get(config.TEXT_LIST_URL)
        text_mapping = json.loads(text_mapping.text)
    text_info = text_mapping.get(text_id, {})
    if text_info:
        pecha_paths["namsel"] = download_pecha(text_info["namsel"])
        pecha_paths["google"] = download_pecha(text_info["google"])
    else:
        raise TextMappingNotFound
    return pecha_paths


def get_text_obj(pecha_id, text_id, pecha_path=None):
    """Return text obj of given text id belonging in given pecha path

    Args:
        pecha_id (str): pecha id
        text_id (str): text id
        pecha_path (str, optional): pecha path. Defaults to None.

    Returns:
        obj: text object
    """
    if not pecha_path:
        pecha_path = download_pecha(pecha_id, needs_update=False)
    pecha_meta = load_yaml(Path(f"{pecha_path}/{pecha_id}.opf/meta.yml"))
    index = load_yaml(Path(f"{pecha_path}/{pecha_id}.opf/index.yml"))
    hfmls = get_hfml_text(f"{pecha_path}/{pecha_id}.opf/", text_id, index)
    text_uuid, text = get_text_info(text_id, index)
    pecha_meta["text_uuid"] = text_uuid
    text = construct_text_obj(hfmls, pecha_meta, pecha_path)
    return text


def get_pedurma_text_obj(text_id, pecha_paths=None):
    """Return pedurma text object of given text id

    Args:
        text_id (str): text id
        pecha_paths (str, optional): pecha path. Defaults to None.

    Returns:
        obj: pedurma text object
    """
    if not pecha_paths:
        pecha_paths = get_pecha_paths(text_id)
    text = {}
    for pecha_src, pecha_path in pecha_paths.items():
        pecha_id = Path(pecha_path).stem
        text[pecha_src] = get_text_obj(pecha_id, text_id, pecha_path)
    pedurma_text = PedurmaText(
        text_id=text_id, namsel=text["namsel"], google=text["google"]
    )
    return pedurma_text
