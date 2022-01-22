import pandas as pd


def binarize(subset, tag_name, index=None, is_label=True):
    if index is None:
        fnames = subset.tags.index
        y = pd.concat([binarize(subset, tag_name, fname, is_label)
                       for fname in fnames],
                      axis=1, keys=fnames).T
        return y

    labels = subset.tags[tag_name].loc[index]
    if not isinstance(labels, list):
        labels = [labels]

    y_index = subset.dataset.label_set
    label_set = y_index if is_label else range(len(y_index))
    y = pd.Series(label_set, index=y_index, name=index)
    y = y.isin(labels).astype(float)
    return y
