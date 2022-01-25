from dask.distributed import Client

client = Client()

import numpy as np
import pandas as pd
from transparentpath import Path

features = list(Path("gs://adv_fuji/adlearn_hpc/X",
                     token="/media/SERVEUR/production/_configs/second-capsule-253207-72efd01e4e7f.json").glob("*.parquet"))[:500]

idxs = [[0, 1, 2, 3], [100, 101, 102, 103], [500, 501, 502, 503]]

def get_mean(feature: Path, idxs) -> pd.DataFrame:
    data = feature.read()
    means = pd.DataFrame(columns=data.columns)
    for i, idx in enumerate(idxs):
        means.loc[i] = data.iloc[i].mean()
    return pd.DataFrame(means.stack(dropna=False), columns=[feature.stem])

idxs_scatter = client.scatter(idxs)
r = client.map(get_mean, features, [idxs_scatter] * len(features))
ss = client.gather(r)
result = pd.concat(ss, axis=1)

