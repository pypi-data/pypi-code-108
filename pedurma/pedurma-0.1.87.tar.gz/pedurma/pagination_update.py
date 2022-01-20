from pathlib import Path

from pedurma.notes import get_pecha_paths
from pedurma.texts import get_text_info
from pedurma.utils import from_yaml, to_yaml


def get_start_page(pagination, start):
    pages = pagination["annotations"]
    for uuid, page in pages.items():
        if page["span"]["end"] > start:
            return page["imgnum"]
    return ""


def get_pg_offset(first_pg_ref, span, pagination_layer):
    start = span["start"]
    start_page = get_start_page(pagination_layer, start)
    return start_page - first_pg_ref


def update_pagination_annotation(durchen_pg_ref_uuid, pg_num, paginations):
    for uuid, pagination in paginations.items():
        if pagination["imgnum"] == pg_num:
            paginations[uuid]["note_ref"] = durchen_pg_ref_uuid
            return paginations
    return paginations


def get_page_uuid(pg_num, paginations):
    """Get page annotation uuid

    Args:
        pg_num (int): img num
        paginations (dict): pagination layer

    Returns:
        uuid: uuid of page annotation of pg num
    """
    for uuid, pagination in paginations.items():
        if pagination["imgnum"] == pg_num:
            return uuid
    return ""


def add_note_pg_ref(page_to_edit, pagination_layer):
    """Add note page reference to body pages

    Args:
        page_to_edit (obj): page to edit object
        pagination_layer (dict): pagination layer

    Returns:
        dict: new pagination layer
    """
    try:
        start_pg = int(page_to_edit.ref_start_page_no)
        end_pg = int(page_to_edit.ref_end_page_no)
    except Exception:
        return pagination_layer
    durchen_image_num = page_to_edit.image_no
    offset = durchen_image_num - int(page_to_edit.page_no)
    paginations = pagination_layer["annotations"]
    durchen_pg_ref_uuid = get_page_uuid(durchen_image_num, paginations)
    if start_pg != 0 and end_pg != 0:
        for pg in range(start_pg, end_pg + 1):
            pg_num = pg + offset
            paginations = update_pagination_annotation(
                durchen_pg_ref_uuid, pg_num, paginations
            )
    pagination_layer["annotations"] = paginations
    return pagination_layer


def is_valid_page_to_edit(prev_pg_to_edit, pg_to_edit):
    """Check if the page is valid to edit or not

    Args:
        prev_pg_to_edit (obj): page to edit object of previous page
        pg_to_edit (obj): page to edit object of current page

    Returns:
        boolean: true if valid else false
    """
    try:
        prev_pg_ref_end = int(prev_pg_to_edit.ref_end_page_no)
        cur_pg_ref_start = int(pg_to_edit.ref_start_page_no)
        cur_pg_ref_end = int(pg_to_edit.ref_end_page_no)
    except Exception:
        return False
    if prev_pg_to_edit == pg_to_edit:
        if cur_pg_ref_end >= cur_pg_ref_start:
            return True
        else:
            return False
    elif prev_pg_to_edit.vol != pg_to_edit.vol and cur_pg_ref_start <= cur_pg_ref_end:
        return True
    elif cur_pg_ref_start <= cur_pg_ref_end and prev_pg_ref_end <= cur_pg_ref_start:
        return True
    else:
        return False


def update_pg_ref(vol, pages_to_edit, pagination_layer):
    """Add page ref to page annotations

    Args:
        vol (int): volume number
        pages_to_edit (obj): pages to edit object
        pagination_layer (dict): old pagination layer

    Returns:
        dict: updated pagination layer
    """
    prev_pg_edit = pages_to_edit[0]
    for page_to_edit in pages_to_edit:
        if vol == page_to_edit.vol:
            if is_valid_page_to_edit(prev_pg_edit, page_to_edit):
                pagination_layer = add_note_pg_ref(page_to_edit, pagination_layer)
        prev_pg_edit = page_to_edit
    return pagination_layer


def update_pagination(pecha_id, text_id, pedurma_edit_notes, index, pecha_path):
    """Update pagination layer volume by volume

    Args:
        pecha_id (str): pecha uuid
        text_id (str): text id
        pedurma_edit_notes (obj): pedurma edit notes obj
        index (dict): indexing of text in pecha
        pecha_path (path): pecha path 

    Yields:
        [int, dict]: volume number and updated pagination
    """
    text_uuid, text_info = get_text_info(text_id, index)
    for span in text_info["span"]:
        vol = span["vol"]
        pagination_layer = from_yaml(
            (pecha_path / f"{pecha_id}.opf/layers/v{int(vol):03}/Pagination.yml")
        )
        pagination_layer = update_pg_ref(vol, pedurma_edit_notes, pagination_layer)
        yield vol, pagination_layer


def update_text_pagination(text_id, pedurma_edit_notes, text_mapping=None):
    """Update pagination of pecha with note ref

    Args:
        text_id (str): text id
        pedurma_edit_notes (obj): pedurma edit notes obj
    """
    pecha_paths = get_pecha_paths(text_id, text_mapping)
    for pecha_type, pecha_path in pecha_paths.items():
        pecha_path = Path(pecha_path)
        pecha_id = pecha_path.stem
        index = from_yaml((pecha_path / f"{pecha_id}.opf/index.yml"))
        for vol, new_pagination in update_pagination(
            pecha_id, text_id, pedurma_edit_notes, index, pecha_path
        ):
            new_pagination_yml = to_yaml(new_pagination)
            (
                pecha_path / f"{pecha_id}.opf/layers/v{int(vol):03}/Pagination.yml"
            ).write_text(new_pagination_yml, encoding="utf-8")
