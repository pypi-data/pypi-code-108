import pandas as pd
from inspect import isfunction


def make_longform_schema(schema):
    schema_out = {}
    for k, v in schema.items():
        if isinstance(v, dict):
            schema_out[k] = v
        elif isinstance(v, str):
            schema_out[k] = {"type": "rename", "from": v}
        elif isfunction(v):
            schema_out[k] = {"type": "apply", "func": v}
        else:
            raise ValueError(
                "Schema values must be a dict, string, or applyable function"
            )
    return schema_out


def _do_rename(df_in, k, v):
    if v.get("fill_missing", True):
        try:
            return df_in[v["from"]]
        except:
            return pd.NA
    else:
        return df_in[v["from"]]


def _do_apply(df_in, k, v):
    if v.get("fill_missing", True):
        try:
            return df_in.apply(v["func"], axis=1)
        except:
            return pd.NA
    else:
        return df_in.apply(v["func"], axis=1)


def _do_transform(df_in, k, v):
    if v.get("fill_missing", True):
        try:
            return df_in.groupby(v["groupby"]).transform(v["action"])[v["column"]]
        except:
            return pd.NA
    else:
        return df_in.groupby(v["groupby"]).transform(v["action"])[v["column"]]


def _remap(values, remap_dict, strict_remap):
    if strict_remap:
        func = lambda x: remap_dict.get(x, pd.NA)
    else:
        func = lambda x: remap_dict.get(x) if x in remap_dict else x

    return [func(x) for x in values]


class DataframeBridge(object):
    _apply_lookup = {
        "rename": _do_rename,
        "apply": _do_apply,
        "transform": _do_transform,
    }

    def __init__(self, schema):
        schema = make_longform_schema(schema)
        self._schema = schema

    @property
    def output_columns(self):
        return list(self._schema.keys())

    def reformat(self, df_in):
        """Reformat dataframe according to the schema"""
        df_out = pd.DataFrame(index=df_in.index, columns=[])
        for k, v in self._schema.items():
            df_out[k] = self._apply_lookup[v["type"]](df_in, k, v)
            if v.get("remap_dict"):
                df_out[k] = _remap(
                    df_out[k], v.get("remap_dict"), v.get("strict_remap", True)
                )
            if v.get("column_type"):
                df_out[k] = df_out[k].astype(v.get("column_type"))
        return df_out
