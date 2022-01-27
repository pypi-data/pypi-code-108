import os
import json
import argparse

from pathlib import Path
from os.path import basename
from typing import Any, Dict, List, Union
from collections import defaultdict


def castable(obj, cast: Any) -> bool:
    try:
        cast(obj)
        is_castable = True
    except Exception:
        is_castable = False
    finally:
        return is_castable


def load_json(filepath: Union[str, Path]) -> Union[Dict, List, None]:
    ret = None
    try:
        ext = os.path.splitext(filepath)[1].strip()
        if ext == "" or ext == ".json":
            ret = json.load(open(filepath, "r", encoding="utf-8"))
        elif ext == ".jsonl":
            ret = [
                json.load(open(line.strip(), "r", encoding="utf-8"))
                for line in open(filepath, "r", encoding="utf-8").readlines()
            ]
    except json.JSONDecodeError:
        pass
    finally:
        return ret


def load_txt(filepath: Union[str, Path]) -> Union[Dict, List, None]:
    ret = [
        line.strip()
        for line in open(filepath, "r", encoding="utf-8").readlines()
    ]
    return ret


def load_file(filepath: Union[str, Path]) -> Union[Dict, List, None]:
    content = load_json(filepath)
    content = content or load_txt(filepath)
    return content


def produce_taxonomy(
    documents: Union[str, List[Dict]],
    output_dir: str,
    translate_ids: bool = False,
    cat_subcat_rel: int = -1,
    subcat_cat_rel: int = 1,
) -> List[str]:
    if cat_subcat_rel is None:
        cat_subcat_rel = -1
    if subcat_cat_rel is None:
        subcat_cat_rel = 1

    if isinstance(documents, str):
        documents = load_file(documents)

    doc0 = documents[0]
    gen_ids = "category_id" not in doc0 or "subcategory_id" not in doc0
    builder = LabelIndexBuilder(
        cat_subcat_rel=cat_subcat_rel,
        subcat_cat_rel=subcat_cat_rel,
        generate_ids=gen_ids,
    )
    for doc in documents:
        builder.add_document(doc, lower=True)

    cat_labels = builder.get_object("cat_labels")
    subcat_labels = builder.get_object("subcat_labels")
    if translate_ids:
        cat_labels = {k: i for i, k in enumerate(cat_labels.keys())}
        subcat_labels = {k: i for i, k in enumerate(subcat_labels.keys())}

    cat_labels = ("cat_labels", cat_labels)
    subcat_labels = ("subcat_labels", subcat_labels)
    cat2subcat = ("cat2subcat", builder.get_object("cat2subcat"))
    subcat2cat = ("subcat2cat", builder.get_object("subcat2cat"))

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for fp, obj in [cat_labels, subcat_labels, cat2subcat, subcat2cat]:
        filepath = output_dir.joinpath(f"{fp}.json")
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(json.dumps(obj, ensure_ascii=False, indent=2))


"""We expect relations and subrelations to correlate by id (following FoS
taxonomy). I.e.:
    category: "earth sciences", id: "04"
    subcategory: "oceanography", id: "0405"

The id of the category is embedded in the subcategory. If this is not followed
or gen_ids = False (which will autogenerate all ids), when processing a
document, every category and subcategory that appear toghether will correlate.

This is not necessarily bad (specially when docs only have one category), just
be aware.
"""


class LabelIndexBuilder(object):
    def __init__(
        self,
        cat_subcat_rel: int = -1,
        subcat_cat_rel: int = 1,
        generate_ids: bool = True,
    ) -> None:
        """
        Relationships can be M-N.
        Where infinity is represented by -1.
        Default implies categories entail many subcategory, but subcategories
        can only be present in one category.
        """
        self.cat_subcat_rel = cat_subcat_rel
        self.subcat_cat_rel = subcat_cat_rel
        self.cat_labels = dict()
        self.subcat_labels = dict()
        self.cat2subcat = dict() if cat_subcat_rel == 1 else defaultdict(set)
        self.subcat2cat = dict() if subcat_cat_rel == 1 else defaultdict(set)
        self.gen_ids = generate_ids

    def _check_enoent(self, obj: str, src: str, dst: str) -> None:
        throw = False
        if obj == "cat":
            if dst in self.cat2subcat and self.cat2subcat[src] != dst:
                throw = True
        elif obj == "subcat":
            if dst in self.subcat2cat and self.subcat2cat[src] != dst:
                throw = True

        if throw:
            raise ValueError(
                f"Object '{src}' relates to {self.cat2subcat[src]} but"
                f"found relation to '{dst}'. Did you mean to have relation"
                " 1-N?"
            )

    def _check_rel(self, obj: str, src: str, dst: str) -> None:
        throw = False
        if obj == "cat":
            rel = self.cat_subcat_rel
            if rel > 1 and dst not in self.cat2subcat[src]:
                if len(self.cat2subcat[src]) + 1 > rel:
                    throw = True
        elif obj == "subcat":
            rel = self.subcat_cat_rel
            if rel > 1 and dst not in self.subcat2cat[src]:
                if len(self.subcat2cat[src]) + 1 > rel:
                    throw = True

        if throw:
            raise ValueError(
                f"Object '{src}' already has {rel} relations, adding {dst}"
                " would break this limitation! Maybe increase the relation?"
            )

    def _get_field(
        self, document: dict, field: str, lower: bool = True
    ) -> List[Union[str, None]]:
        values = document.get(field, None)
        if values is not None:
            if not isinstance(values, (list, tuple)):
                values = [values]

            for idx in range(len(values)):
                values[idx] = str(values[idx]).strip()
                if lower:
                    values[idx] = values[idx].lower()

        return values

    def _get_data(
        self, document: dict, lower: bool = True
    ) -> List[Union[str, None]]:
        cats = self._get_field(document, "category", lower)
        cat_ids = None
        if cats is not None:
            if not self.gen_ids:
                cat_ids = self._get_field(document, "category_id", lower)
                assert(len(cats) == len(cat_ids))

        subcats = self._get_field(document, "subcategory", lower)
        subcat_ids = None
        if subcats is not None:
            if not self.gen_ids:
                subcat_ids = self._get_field(document, "subcategory_id", lower)
                assert(len(subcats) == len(subcat_ids))

        return cats, cat_ids, subcats, subcat_ids

    def _gen_id(self, obj: str, item: str) -> str:
        id = None
        if obj == "cat":
            self_obj = self.cat_labels
        else:
            self_obj = self.subcat_labels

        if item in self_obj:
            id = self_obj[item]
        else:
            id = len(self_obj)

        return id

    def _add_subrel(self, obj: str, src: str, dst: str) -> None:
        if dst is not None:
            rel = self.cat_subcat_rel if obj == "cat" else self.subcat_cat_rel
            self_obj = self.cat2subcat if obj == "cat" else self.subcat2cat
            if rel == 1:
                self._check_enoent(obj, src, dst)
                self_obj[src] = dst
            else:
                self._check_rel(obj, src, dst)
                self_obj[src].add(dst)

    def _add_rel(
        self,
        obj: str,
        src: str,
        src_id: str,
    ) -> None:
        if src is not None:
            self_obj = self.cat_labels if obj == "cat" else self.subcat_labels
            if src not in self_obj:
                self_obj[src] = src_id
            elif self_obj[src] != src_id:
                raise ValueError(
                    "Tried to add two different ids to the same relation! "
                    f"{src}: {self_obj[src]}, new {src_id}"
                )

    def add_document(self, document: dict, lower: bool = True) -> None:
        cats, cat_ids, subcats, subcat_ids = self._get_data(document, lower)
        if cat_ids is None:
            cat_ids = [None] * len(cats)

        if subcat_ids is None:
            subcat_ids = [None] * len(subcats)

        for cat, cat_id in zip(cats, cat_ids):
            if cat_id is None:
                cat_id = self._gen_id("cat", cat)

            self._add_rel("cat", cat, cat_id)
            for subcat, subcat_id in zip(subcats, subcat_ids):
                # if auto-generating ids or subcat entailed in cat
                if self.gen_ids or subcat_id[:2] == cat_id:
                    self._add_subrel("cat", cat, subcat)

        for subcat, subcat_id in zip(subcats, subcat_ids):
            if subcat_id is None:
                subcat_id = self._gen_id("subcat", subcat)

            self._add_rel("subcat", subcat, subcat_id)
            for cat, cat_id in zip(cats, cat_ids):
                if self.gen_ids or subcat_id[:2] == cat_id:
                    self._add_subrel("subcat", subcat, cat)

    def get_object(self, obj: str) -> Dict:
        ret = getattr(self, obj)
        if "2" in obj:
            fkey = list(ret.keys())[0]
            if isinstance(ret[fkey], set):
                for key, value in ret.items():
                    ret[key] = list(value)

        return ret


"""Utility class to build an index like {category|subcategory: index}
Capable of tranlating to/from (sub)category to index. Ideally idices are
recognizable because can be casted to integers. If this is not the case, just
preserves given dict from file.
"""


class LabelIndex(object):
    """
    Ideally, every category (of the taxonomy) should be indexed with an
    integer-like identifier. LabelIndexes relies on casting those to int to
    separate (sub)categories from their labels/index.
    """

    def __init__(self, index_file, conversion_file=None):
        self.index_file = index_file
        self.conversion_file = conversion_file

        self.index, self.reverse_index = self.load_index(self.index_file)
        if conversion_file is not None:
            conv_table, conv_rev_table = self.load_index(conversion_file)
            self.conv_table, self.conv_rev_table = conv_table, conv_rev_table

    def load_index(self, filepath):
        """Builds an index like {name: id}
        It has to check if names were stored as keys or not (ids are keys)
        """
        # best effort, first json, then txt, then fail
        index = None
        ext = os.path.splitext(filepath)[1]
        if ext.strip() == "" and not Path(filepath).exists():
            for ext in ["json", "txt"]:
                fpath = f"{filepath}.{ext}"
                if Path(fpath).exists():
                    filepath = fpath
                    break

        index = load_file(filepath)
        if index is None:
            raise RuntimeError(
                f"Unable to load index from {filepath}"
            )

        if isinstance(index, list):
            index = {value: str(idx) for idx, value in enumerate(index)}
        elif isinstance(index, dict):
            f_key, f_value = [(key, value) for key, value in index.items()][0]
            # if indexed with {name: id} or
            # unable to parse neither as int (leave as it comes)
            if castable(f_value, int) or not castable(f_key, int):
                names = index.keys()
                ids = index.values()
            else:
                names = index.values()
                ids = index.keys()

            index = {key: value for key, value in zip(names, ids)}

        reverse = self.build_inverse(index)
        return index, reverse

    def build_inverse(self, index):
        f_value = [value for value in index.values()][0]
        unique_keys = isinstance(f_value, (str, int))
        if unique_keys:
            reverse_index = {value: key for key, value in index.items()}
        else:
            reverse_index = defaultdict(list)
            for key, values in index.items():
                for val in values:
                    reverse_index[val].append(key)

        return reverse_index

    def _get_from_dict(self, item, src_dict):
        """This can silently fail if assigned ids contain the given one.
        E.g.: Request ID=10 by number, which should yield the id of 10th
        element in the dict, but, if key "10" exists, it will retrieve it
        though we may not want that.
        """
        ret = None
        item_str = str(item)
        if item_str in src_dict:
            ret = src_dict[item_str]
        elif castable(item_str, int):
            item_int = int(item_str)
            if item_int < len(src_dict):
                item_str = list(src_dict.keys())[item_int]
                ret = src_dict[item_str]

        if ret is None:
            raise ValueError(f"Key '{item}' not found in Index!")

        return ret

    def __getitem__(self, item):
        return self._get_from_dict(item, self.index)

    def reverse(self, idx):
        return self._get_from_dict(idx, self.reverse_index)

    def convert(self, name):
        return self.conv_table[str(name)]

    def convert_reverse(self, name_or_idx):
        return self.conv_rev_table[str(name_or_idx)]


class Taxonomy(object):
    # ToDo := Explicit kwargs, it meeessy to parse names from kwargs (plus no
    # engine will autocomplete options)
    # Deprecated, here for backwards compat:
    # category_index_file, subcategory_index_file
    # Accepts:
    # - category_index: LabelIndex preconfigured
    # - subcategory_index: LabelIndex preconfigured
    # --------- OR ---------
    # - category_index_file: str or Path pointing to the relevant file
    # - category_conversion_file (optional, IDEM)
    # - subcategory_index_file: str or Path pointing to the relevant file
    # - subcategory_conversion_file (optional, IDEM)
    # --------- OR ---------
    # - data_path string or Path pointing to a directory containing:
    #   cat_labels[.json|.txt]
    #   cat2subcat.json (optional)
    #   subcat_labels[.json|.txt]
    #   subcat2cat.json (optional)
    def __init__(
        self, data_path: Union[str, Path, None] = None, **kwargs
    ) -> None:
        self.cat_index = self._parse_input_index(
            "category", data_path, **kwargs
        )
        self.subcat_index = self._parse_input_index(
            "subcategory", data_path, **kwargs
        )

    def _parse_input_index(
        self, index_name: str, data_path: Union[str, Path, None], **kwargs,
    ) -> LabelIndex:
        index = kwargs.pop(f"{index_name}_index", None)
        index_file, conversion_file = None, None
        if index is None or not isinstance(index, LabelIndex):
            index_file = kwargs.pop(f"{index_name}_index_file", None)
            if index_file is not None:
                conversion_file = kwargs.pop(
                    f"{index_name}_conversion_file", None
                )

        data_path = Path(data_path) if data_path is not None else data_path
        fname = index_name.replace("egory", "")
        opposite = "subcat" if fname == "cat" else "cat"
        labels_name = f"{fname}_labels"
        conv_name = f"{fname}2{opposite}.json"
        if index_file is None and data_path is not None:
            index_file = data_path.joinpath(labels_name)
            conversion_file = data_path.joinpath(conv_name)
            if not conversion_file.exists():
                conversion_file = None

        if not isinstance(index, LabelIndex) and index_file is None:
            raise ValueError(
                f"You must provide one of these for indexing {index_name}:\n"
                f" - A full `LabelIndex` ({index_name}_index)\n"
                f" - A {labels_name} file path ({index_name}_index_file) and "
                f"optionally a {conv_name} for conversions "
                f"({index_name}_conversion_file)\n"
                f" - A data path (data_path) to search for {labels_name} and, "
                f"optionally, {conv_name} files"
            )

        if index is None:
            index = LabelIndex(
                index_file=index_file, conversion_file=conversion_file
            )

        return index

    def _category(self, cat_or_label, index):
        return str(index.reverse(cat_or_label))

    def _label(self, label_or_cat, index):
        return int(index[label_or_cat])

    @property
    def num_categories(self):
        if self.cat_index is None:
            raise RuntimeError(
                "There is no category index!"
            )

        return len(self.cat_index.index)

    @property
    def num_subcategories(self):
        if self.subcat_index is None:
            raise RuntimeError(
                "There is no subcategory index!"
            )

        return len(self.subcat_index.index)

    @staticmethod
    def from_hf_datasets(data_path):
        import sys
        import importlib
        from datasets import DownloadManager
        # can be local path or pip-package (:
        if Path(data_path).is_dir():
            data_path = str(data_path).strip()
            if data_path.endswith("/"):
                data_path = data_path[:-1]

            sys.path.append(data_path)
            module_name = basename(data_path)
        else:
            module_name = data_path

        data_module = importlib.import_module(module_name)
        downloader = getattr(data_module, "custom_download")
        dlm = DownloadManager()
        downloaded = downloader(dlm)
        return Taxonomy(
            category_index_file=downloaded["cat_labels"],
            category_conversion_file=downloaded["cat2subcat"],
            subcategory_index_file=downloaded["subcat_labels"],
            subcategory_conversion_file=downloaded["subcat2cat"],
        )

    def get_category_names(self):
        return list(self.cat_index.index.keys())

    def get_subcategory_names(self):
        return list(self.subcat_index.index.keys())

    def cat2label(self, cat):
        return self._label(cat, self.cat_index)

    def label2cat(self, label):
        return self._category(label, self.cat_index)

    def subcat2label(self, cat):
        return self._label(cat, self.subcat_index)

    def label2subcat(self, label):
        return self._category(label, self.subcat_index)

    def cat2subcat(self, cat_or_label):
        if self.cat_index.conv_table is None:
            raise RuntimeError(
                "Category Index must contain a conversion table to use "
                "`cat2subcat`!"
            )

        cat = self._category(cat_or_label, self.cat_index)
        return self.cat_index.convert(cat)

    def cat2subcatlabel(self, cat_or_label):
        if self.subcat_index is None:
            raise RuntimeError(
                "You must provide a subcategory index to use "
                "`cat2subcatlabel`!"
            )

        subcats = self.cat2subcat(cat_or_label)
        if isinstance(subcats, str):
            subcats = [subcats]

        sub_labels = [self._label(sub, self.subcat_index) for sub in subcats]
        return sub_labels if len(sub_labels) > 1 else sub_labels[0]

    def subcat2cat(self, subcat_or_label):
        if self.subcat_index is None or self.subcat_index.conv_table is None:
            raise RuntimeError(
                "You must provide a subcategory index with a conversion table"
                " to use `subcat2cat`!"
            )
        subcat = self._category(subcat_or_label, self.subcat_index)
        return self.subcat_index.convert(subcat)

    def subcat2catlabel(self, subcat_or_label):
        if self.subcat_index is None:
            raise RuntimeError(
                "You must provide a subcategory index to use "
                "`subcat2catlabel`!"
            )

        cats = self.subcat2cat(subcat_or_label)
        if isinstance(cats, str):
            cats = [cats]

        cat_labels = [self._label(cat, self.cat_index) for cat in cats]
        return cat_labels if len(cat_labels) > 1 else cat_labels[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", required=True, type=str, help="Input data to process"
    )
    parser.add_argument(
        "-t", "--translate_ids", action="store_true",
        help="Whether to translate all ids when finished parsing. This is used"
        " to generate integers, sequential ids that can be used later in"
        " `datasets`"
    )
    parser.add_argument(
        "-o", "--output_dir", required=True, type=str,
        help="Output directory to store the taxonomy",
    )
    parser.add_argument(
        "--relation", required=False, type=int, default=None,
        help="Relation between categories and subcategories"
    )

    args = parser.parse_args()
    produce_taxonomy(
        documents=args.input,
        output_dir=args.output_dir,
        translate_ids=args.translate_ids,
        cat_subcat_rel=args.relation,
        subcat_cat_rel=args.relation,
    )
