import pandas as pd
def explode(df, on=None, fillna="N/A", duplicate_id="id", keep_empty=True):
    """
    Explode all explodable columns in dataframe, see: pd.DataFrame.explode

    Count unique items by grouping on all columns, counting each group size, then dropping duplicate ids
    df.groupby(df.columns.tolist()).size().reset_index(name="count").drop_duplicates("id")["count"].sum()

    :param df:
    :param on: explode on columns
    :param fillna: fill NA's with the following value
    :param duplicate_id: column on return df to set group duplication id or None to avoid grouping
    :param keep_empty: keep empty lists as NAN rows
    :return: see: pd.DataFrame.explode
    """
    on = on or df.columns.tolist()

    # Ensure empty lists are converted to pd.NA to keep them during under explosion
    if keep_empty:
        df = df.mask(df.applymap(pd.api.types.is_list_like) & ~df.fillna(1, inplace=False).astype(bool))

    mask = df[on].applymap(pd.api.types.is_hashable).all(axis=0) & df[on].applymap(pd.api.types.is_list_like).any(axis=0)
    explodable = mask[mask].index.tolist()

    if duplicate_id is not None:
        # nan must be filled to be grouped
        for x in df.select_dtypes("category"):
            if fillna not in df[x].cat.categories:
                df[x].cat.add_categories(fillna, inplace=True)
        df = df.fillna(fillna)
        df[duplicate_id] = df.groupby(on).ngroup()

    for c in explodable:
        df = df.explode(c)

    return df
