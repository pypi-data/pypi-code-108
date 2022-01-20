import copy
from pathlib import Path

from openpecha.blupdate import Blupdate, update_ann_layer
from openpecha.github_utils import commit
from openpecha.utils import download_pecha, dump_yaml, load_yaml

from pedurma.texts import get_pecha_paths, remove_last_pages, serialize_text_obj
from pedurma.utils import from_yaml, notes_to_original_view


def get_old_vol(pecha_opf_path, pecha_id, text_vol_span):
    """Generate old base text in which text is located

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id 
        text_vol_span (list): list of volume ids in which text is located

    Returns:
        dict: volid as key and base as value
    """
    old_vols = {}
    for vol_id in text_vol_span:
        old_vols[vol_id] = Path(
            f"{pecha_opf_path}/{pecha_id}.opf/base/{vol_id}.txt"
        ).read_text(encoding="utf-8")
    return old_vols


def get_old_text_base(old_pecha_idx, old_vol_base, text_id, text_vol_num):
    """Return old text base

    Args:
        old_pecha_idx (dict): old index
        old_vol_base (dict): old vol base and its vol id
        text_id (str): text id
        text_vol_num (str): text vol id

    Returns:
        str: text basetext in that volume
    """
    text_span = old_pecha_idx["annotations"][text_id]["span"]
    for vol_span in text_span:
        if vol_span["vol"] == text_vol_num:
            return old_vol_base[vol_span["start"] : vol_span["end"] + 1]
    return ""


def get_new_vol(old_vols, old_pecha_idx, text_obj):
    """Return new base text by replacing updated text from text object

    Args:
        old_vols (dict): old vol and its id
        old_pecha_idx (dict): old pecha index
        text_obj (obj): text object

    Returns:
        dict: new basetext and its id
    """
    new_vols = {}
    new_text = serialize_text_obj(text_obj)
    for vol_id, new_text_base in new_text.items():
        vol_num = int(vol_id[1:])
        old_vol_base = old_vols[vol_id]
        old_text_base = get_old_text_base(
            old_pecha_idx, old_vol_base, text_obj.id, vol_num
        )
        old_text_base = old_text_base.strip()
        new_text_base = new_text_base.strip()
        new_vol_base = old_vol_base.replace(old_text_base, new_text_base)
        new_vols[vol_id] = new_vol_base
    return new_vols


def get_text_vol_span(pecha_idx, text_uuid):
    """Return list of volume ids in which text span

    Args:
        pecha_idx (dict): pecha index
        text_uuid (uuid): text uuid

    Returns:
        list: vol ids
    """
    text_vol_span = []
    for span in pecha_idx["annotations"][text_uuid]["span"]:
        vol_num = span["vol"]
        text_vol_span.append(f"v{int(vol_num):03}")
    return text_vol_span


def update_base(pecha_opf_path, pecha_id, text_obj, old_pecha_idx):
    """Update base text using text obj

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        text_obj (obj): text object
        old_pecha_idx (dict): old pecha index
    """
    text_vol_span = get_text_vol_span(old_pecha_idx, text_obj.id)
    old_vols = get_old_vol(pecha_opf_path, pecha_id, text_vol_span)
    new_vols = get_new_vol(old_vols, old_pecha_idx, text_obj)
    for vol_id, new_vol_base in new_vols.items():
        Path(f"{pecha_opf_path}/{pecha_id}.opf/base/{vol_id}.txt").write_text(
            new_vol_base, encoding="utf-8"
        )
        print(f"INFO: {vol_id} base updated..")


def get_old_layers(pecha_opf_path, pecha_id, vol_id):
    """Return all the layers belonging in volume

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        vol_id (str): volume id

    Returns:
        dict: layer name as key and layer annotations as value
    """
    old_layers = {}
    layer_paths = list(
        Path(f"{pecha_opf_path}/{pecha_id}.opf/layers/{vol_id}").iterdir()
    )
    for layer_path in layer_paths:
        layer_name = layer_path.stem
        layer_content = from_yaml(layer_path)
        old_layers[layer_name] = layer_content
    return old_layers


def update_layer(pecha_opf_path, pecha_id, vol_id, old_layers, updater):
    """Update particular layers belonging in given volume id 

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        vol_id (str): volume id
        old_layers (dict): layer name as key and annotations as value
        updater (obj): updater object
    """
    for layer_name, old_layer in old_layers.items():
        if layer_name not in ["Pagination", "Durchen", "PedurmaNote"]:
            update_ann_layer(old_layer, updater)
            new_layer_path = Path(
                f"{pecha_opf_path}/{pecha_id}.opf/layers/{vol_id}/{layer_name}.yml"
            )
            dump_yaml(old_layer, new_layer_path)
            print(f"INFO: {vol_id} {layer_name} has been updated...")


def update_old_layers(pecha_opf_path, pecha_id, text_obj, old_pecha_idx):
    """Update all the layers related to text object

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        text_obj (obj): text object
        old_pecha_idx (dict): old pecha index
    """
    text_vol_span = get_text_vol_span(old_pecha_idx, text_obj.id)
    old_vols = get_old_vol(pecha_opf_path, pecha_id, text_vol_span)
    new_vols = get_new_vol(old_vols, old_pecha_idx, text_obj)
    for (vol_id, old_vol_base), (_, new_vol_base) in zip(
        old_vols.items(), new_vols.items()
    ):
        updater = Blupdate(old_vol_base, new_vol_base)
        old_layers = get_old_layers(pecha_opf_path, pecha_id, vol_id)
        update_layer(pecha_opf_path, pecha_id, vol_id, old_layers, updater)


def update_other_text_index(old_pecha_idx, text_id, cur_vol_offset, vol_num):
    check_flag = False
    for text_uuid, text in old_pecha_idx["annotations"].items():
        if check_flag:
            for vol_walker, vol_span in enumerate(text["span"]):
                if vol_span["vol"] == vol_num:
                    old_pecha_idx["annotations"][text_uuid]["span"][vol_walker][
                        "start"
                    ] += cur_vol_offset
                    old_pecha_idx["annotations"][text_uuid]["span"][vol_walker][
                        "end"
                    ] += cur_vol_offset
                elif vol_span["vol"] > vol_num:
                    return old_pecha_idx
        if text_uuid == text_id:
            check_flag = True
    return old_pecha_idx


def update_index(pecha_opf_path, pecha_id, text_obj, old_pecha_idx):
    """Update pecha index according to text obj content

    Args:
        pecha_opf_path (str): pecha opf path
        pecha_id (str): pecha id
        text_obj (obj): text object
        old_pecha_idx (dict): old pecha index

    Returns:
        dict: new pecha index
    """
    text_vol_span = get_text_vol_span(old_pecha_idx, text_obj.id)
    old_vols = get_old_vol(pecha_opf_path, pecha_id, text_vol_span)
    new_vols = get_new_vol(old_vols, old_pecha_idx, text_obj)
    for (vol_id, old_vol_base), (_, new_vol_base) in zip(
        old_vols.items(), new_vols.items()
    ):
        check_next_text = True
        vol_num = int(vol_id[1:])
        cur_vol_offset = len(new_vol_base) - len(old_vol_base)
        if cur_vol_offset != 0:
            for vol_walker, vol_span in enumerate(
                old_pecha_idx["annotations"][text_obj.id]["span"]
            ):
                if vol_span["vol"] == vol_num:
                    old_pecha_idx["annotations"][text_obj.id]["span"][vol_walker][
                        "end"
                    ] += cur_vol_offset
                elif vol_span["vol"] > vol_num:
                    check_next_text = False
                    break
            if check_next_text:
                old_pecha_idx = update_other_text_index(
                    old_pecha_idx, text_obj.id, cur_vol_offset, vol_num
                )
    return old_pecha_idx


def update_durchen_span(durchen_layer, text, vol_num, char_walker):
    durchen_start = char_walker
    for note in text.notes:
        if note.vol == vol_num:
            char_walker += len(note.content) + 2
    durchen_end = char_walker - 3
    for id, ann in durchen_layer["annotations"].items():
        durchen_layer["annotations"][id]["span"]["start"] = durchen_start
        durchen_layer["annotations"][id]["span"]["end"] = durchen_end
        break
    return durchen_layer


def update_durchen_layer(text, pecha_id, pecha_opf_path):
    vol_num = text.pages[0].vol
    durchen_layer, durchen_path = get_layer(
        pecha_opf_path, pecha_id, vol_num, "Durchen"
    )
    char_walker = 0
    for page in text.pages:
        if vol_num != page.vol:
            update_durchen_span(durchen_layer, text, vol_num, char_walker)
            char_walker = 0
            vol_num = page.vol
            dump_yaml(durchen_layer, durchen_path)
            durchen_layer, durchen_path = get_layer(
                pecha_opf_path, pecha_id, vol_num, "Durchen"
            )
        char_walker += len(page.content) + 2
    update_durchen_span(durchen_layer, text, vol_num, char_walker)
    dump_yaml(durchen_layer, durchen_path)


def update_page_span(page, prev_page_end, old_page_ann):
    new_page_len = len(page.content)
    new_page_end = prev_page_end + new_page_len
    old_page_ann["span"]["start"] = prev_page_end
    old_page_ann["span"]["end"] = new_page_end
    return old_page_ann, new_page_end + 2


def update_note_span(pagination_layer, text, prev_page_end):
    for note in text.notes:
        old_page_ann = pagination_layer["annotations"].get(note.id, {})
        if old_page_ann:
            pagination_layer["annotations"][note.id], prev_page_end = update_page_span(
                note, prev_page_end, old_page_ann
            )


def get_layer(pecha_opf_path, pecha_id, vol_num, layer_name):
    layer_path = (
        Path(pecha_opf_path)
        / f"{pecha_id}.opf"
        / "layers"
        / f"v{int(vol_num):03}"
        / f"{layer_name}.yml"
    )
    layer = load_yaml(layer_path)
    return layer, layer_path


# def get_updated_page_number(old_span, new_pg_ann, updated_pg_number):
#     if (
#         updated_pg_number != 0
#         and old_span["start"] != new_pg_ann["span"]["start"]
#         or old_span["end"] != new_pg_ann["span"]["end"]
#     ):
#         return new_pg_ann["imgnum"]
#     else:
#         return updated_pg_number


def update_page_layer(text, pecha_id, pecha_opf_path):
    vol_num = text.pages[0].vol
    pagination_layer, pagination_path = get_layer(
        pecha_opf_path, pecha_id, vol_num, "Pagination"
    )
    pagination_annotations = pagination_layer.get("annotations", {})
    prev_page_end = 0
    for page in text.pages:
        if vol_num != page.vol:
            update_note_span(pagination_layer, text, prev_page_end)
            prev_page_end = 0
            vol_num = page.vol
            dump_yaml(pagination_layer, pagination_path)
            pagination_layer, pagination_path = get_layer(
                pecha_opf_path, pecha_id, vol_num, "Pagination"
            )
            pagination_annotations = pagination_layer.get("annotations", {})
        old_page_ann = pagination_annotations[page.id]
        old_span = copy.deepcopy(old_page_ann["span"])
        pagination_layer["annotations"][page.id], prev_page_end = update_page_span(
            page, prev_page_end, old_page_ann
        )
    update_note_span(pagination_layer, text, prev_page_end)
    dump_yaml(pagination_layer, pagination_path)


def save_text(pecha_id, text_obj, pecha_opf_path=None, **kwargs):
    """Update pecha opf according to text object content

    Args:
        pecha_id (str): pecha id
        text_obj (text obj): text object
        pecha_opf_path (str, optional): pecha path. Defaults to None.

    Returns:
        path: pecha opf path
    """
    if not pecha_opf_path:
        pecha_opf_path = download_pecha(pecha_id, **kwargs)
    old_pecha_idx = from_yaml(Path(f"{pecha_opf_path}/{pecha_id}.opf/index.yml"))
    prev_pecha_idx = copy.deepcopy(old_pecha_idx)
    text_obj = remove_last_pages(text_obj)
    new_pecha_idx = update_index(pecha_opf_path, pecha_id, text_obj, old_pecha_idx)
    update_old_layers(pecha_opf_path, pecha_id, text_obj, prev_pecha_idx)
    update_base(pecha_opf_path, pecha_id, text_obj, prev_pecha_idx)
    update_page_layer(text_obj, pecha_id, pecha_opf_path)
    update_durchen_layer(text_obj, pecha_id, pecha_opf_path)
    new_pecha_idx_path = Path(f"{pecha_opf_path}/{pecha_id}.opf/index.yml")
    dump_yaml(new_pecha_idx, new_pecha_idx_path)
    # if commit_flag:
    #     commit(pecha_opf_path, f"Page no {updated_page_number} is updated")
    return pecha_opf_path


def get_pedurma_text_mapping(pedurma_text_obj):
    """Pedurma text obj are parse and added pecha path

    Args:
        pedurma_text_obj (obj): pedurma text obj

    Returns:
        dict: ocr engine as key and associated text data as value
    """
    pedurma_text_mapping = {}
    pecha_paths = get_pecha_paths(text_id=pedurma_text_obj.text_id)
    for pecha_src, pecha_path in pecha_paths.items():
        if pecha_src == "namsel":
            text_obj = pedurma_text_obj.namsel
        else:
            text_obj = pedurma_text_obj.google
        pedurma_text_mapping[pecha_src] = {
            "pecha_id": Path(pecha_path).stem,
            "text_obj": text_obj,
            "pecha_path": pecha_path,
        }
    return pedurma_text_mapping


def save_pedurma_text(pedurma_text_obj, pedurma_text_mapping=None):
    """Save changes to respective pedurma opfs according to pedurma text object content

    Args:
        pedurma_text_obj (obj): pedurma text object
        pedurma_text_mapping (dict, optional): pedurma text data mapping. Defaults to None.
    """
    if not pedurma_text_mapping:
        pedurma_text_mapping = get_pedurma_text_mapping(pedurma_text_obj)
    for ocr_engine, pedurma_text in pedurma_text_mapping.items():
        text_obj = pedurma_text["text_obj"]
        text_obj.notes = notes_to_original_view(text_obj.notes, ocr_engine)
        save_text(pedurma_text["pecha_id"], text_obj, pedurma_text["pecha_path"])
