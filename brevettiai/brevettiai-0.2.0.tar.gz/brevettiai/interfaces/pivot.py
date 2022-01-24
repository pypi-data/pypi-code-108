import json

import pandas as pd

from brevettiai.io import io_tools
from brevettiai.data.sample_tools import join_dataset_meta
from brevettiai.utils.pandas_utils import explode


def pivot_fields(fields, rows=None, cols=None):
    """
    Build pivot export fields dict
    :param fields: field dict, {key:label,...}
    :param rows: iterable of field keys to start in row selector
    :param cols: iterable of field keys to start in column selector
    :return: vue-pivot-table fields dict
    """
    fields = {k: {"key": k, "label": v} if isinstance(v, str) else
              {"key": k, **v}
              for k, v in fields.items()}
    pfields = dict(rowFields=[], colFields=[], fields=[])
    for r in rows or []:
        pfields["rowFields"].append(fields[r])
    for c in cols or []:
        if not (rows and c in rows):
            pfields["colFields"].append(fields[c])
    for k, v in fields.items():
        if not (rows and k in rows) and not (cols and k in cols):
            pfields["fields"].append(v)
    return pfields


def pivot_data(df, fields, datasets=None, tags=None, agg=None):
    """
    Build pivot ready dataframe with precalculated object groups
    :param df: sample dataframe with dataset_id to join on if datasets and tags are not None
    :param fields: field dict, {key:label,...} updated with metadata fields if datasets and tags are not None
    :param datasets: datasets to build metadata from
    :param tags: tag root tree, to find parent tags
    :param agg: Aggregate parameter dictionary, uses count column as default (weight 1 for all samples if nonexistent)
    :return: vue-pivot-table export ready dataframe
    """
    agg = (agg or {}).copy()
    agg["count"] = "sum"
    if "count" not in df:
        df = df.copy()
        df["count"] = 1

    if isinstance(fields, dict):
        fieldlist = list(fields.keys())
    else:
        fieldlist = fields
        fields = {f: f for f in fields}

    if datasets is not None and tags is not None:
        df, meta_fields = join_dataset_meta(df, datasets, tags)
        fieldlist.extend(list(meta_fields.keys()))
        fields.update(meta_fields)

    df = df.applymap(lambda x: tuple(x) if pd.api.types.is_list_like(x) else x)
    df = explode(df[fieldlist + list(agg.keys())], on=fieldlist, duplicate_id="id")

    df = df.groupby(fieldlist + ["id"]).agg(agg).reset_index()
    return df


def get_default_fields(df):
    """
    Build default pivot fields structure from dataframe
    :param df:
    :return:
    """
    fields = {
        "category": {"label": "Category", "sort": [a for b in df.category.unique() for a in b]},
        "folder": "Folder", "dataset_id": "Dataset Id", "purpose": "Purpose"
    }
    return {k: v for k, v in fields.items() if k in df}


def export_pivot_table(pivot_dir, df, fields=None, datasets=None, tags=None, rows=None, cols=None, **data_args):
    """
    Build and export pivot table using :py:func:pivot_data and :py:func:pivot_fields methods
    :param pivot_dir:
    :param df:
    :param fields:
    :param datasets:
    :param tags:
    :param rows:
    :param cols:
    :return:
    """
    fields = fields or get_default_fields(df)

    # Build and export pivot table
    df = pivot_data(df, fields, datasets, tags, **data_args)
    pfields = pivot_fields(fields, rows, cols)

    io_tools.write_file(io_tools.path.join(pivot_dir, "summary_fields.json"), json.dumps(pfields))
    io_tools.write_file(io_tools.path.join(pivot_dir, "classification_summary.json"), json.dumps(df.to_dict("records")))
