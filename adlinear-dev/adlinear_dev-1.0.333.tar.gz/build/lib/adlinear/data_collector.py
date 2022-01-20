import functools
from transparentpath import Path
import pandas as pd
import numpy as np
import numpy.random
import dotenv
import argparse


# from dask.distributed import Client
# from dask import distributed as dst
#

# from transparentpath import Path
# import dask.dataframe as dd
#
# client = Client("tcp://127.0.0.1:33869")
#
# dfs_path = Path("/home/cgeissler/Documents/Tests")
# ddf = dd.read_parquet(dfs_path)
#
# ddf.loc["2020-01-01":"2020-01-03"].groupby('feature_name').mean().compute()
#
#
# # In[4]:
#
#
# ind = (((ddf.groupby('feature_name').count().sum(axis=1) / (ddf.index.nunique() * ddf.shape[1])) > 0.5)).compute()
# ind.loc[ind].index.to_list()
# ddf = ddf.loc[ddf['feature_name'].isin(ind.loc[ind].index.to_list())].compute()
#
#
# # In[5]:
#
#
# a = (ddf.groupby('feature_name').max().max(axis=1)) / 2 + (ddf.groupby('feature_name').min().min(axis=1)) / 2
# b = (ddf.groupby('feature_name').max().max(axis=1)) / 2 - (ddf.groupby('feature_name').min().min(axis=1)) / 2
# ind = ddf.index
# ddf = ddf.set_index('feature_name')
# for l in a.index:
#     ddf.loc[l] = (ddf.loc[l] - a[l]) / b[l]
# ddf = ddf.reset_index()
# ddf.index = ind

Path.set_global_fs("gcs", bucket="nmf_experiments_dev", token="../cred_gcs.json")
dotenv.load_dotenv()


def collect_optimal_k_outputs() -> pd.DataFrame:

    outputpath = Path("screeplots")
    return pd.concat([afile.read(index_col=0) for afile in outputpath.glob("*.csv")], axis='index')


def collect_features_mean_values(data_path: Path, **kwargs) -> pd.DataFrame:
    # exclusion_list=None, period="", mode: str = "mean")
    """

    collect_features_mean_values: collects files into a single matrix
    Each file represent the time history of a given feature.
    The structure of the file must comply with:
    An increasing series of dates as index;
    Object names as columns

    :Parameters
    ----------

    data_path: a directory path indicating the location of data.
        All files must be located in data_path
    exclusion_list: list of strings to avoid in data_path

    period: time interval used to group the observations.
    If unspecified or '', the whole index will be kept for each feature.
    Otherwise, a time interval.

    mode: 'mean' (default), 'first' or 'last' to determine which value to extract

    :returns:
    a DataFrame containing the features (attributes) as columns, the observations (e.g stocks) as lines
    """

    # total files list
    exclusion_list = kwargs.get("exclusion_list", None)
    measurement_dates = kwargs.get("dates", None)
    mode = kwargs.get("mode", "mean")
    do_save = kwargs.get("save", True)
    out_path = kwargs.get("out_path", "")
    if exclusion_list is None:
        exclusion_list = []
    flist = [
        x
        for x in data_path.glob("*")
        if functools.reduce(lambda x, y: x and y, [str(x).find(excl) < 0 for excl in exclusion_list], True)
    ]
    matrix = pd.DataFrame(index=[], columns=[])
    nmax = 0
    for fl in flist:
        feature = fl.stem
        hdf = pd.read_csv(data_path / fl, index_col=0, parse_dates=True).fillna(method="ffill")
        if measurement_dates != "" and measurement_dates is not None:
            hdf = hdf.loc[measurement_dates, :]
            str_dates = f"Set_{len(hdf.index)}_dates"
        else:
            str_dates = ""
        if mode == "mean":
            hdf = pd.DataFrame(hdf.mean(axis=0))
        elif mode == "first":  # last
            hdf = pd.DataFrame(hdf.iloc[0])
        elif mode == "last":
            hdf = pd.DataFrame(hdf.iloc[-1])
        elif mode == "random":
            irnd = numpy.random.Generator.choice(range(len(hdf.index)), 1)[0]
            hdf = pd.DataFrame(hdf.iloc[irnd])
        hdf.columns = [feature]
        if nmax > 0 and len(hdf) >= nmax + 50:
            print((len(hdf), "stocks before."))
            hdf = hdf.loc[matrix.index, :]
            print((len(hdf), "stocks after."))

        if len(hdf) > nmax:
            nmax = len(hdf)
        matrix = pd.concat([matrix, hdf], axis=1, sort=False)
        if do_save:
            mat_name = f"Features_from_{data_path}_{mode}"
            if str_dates != "":
                mat_name += f"at_{str_dates}__.csv"
            matrix.to_csv(Path(out_path) / mat_name)

    return matrix.dropna(how="all")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Output files collector",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-o", "--output", type=str, default="output.csv", help="Output localization")
    args = parser.parse_args()
    output = Path(args.output)

    df_outputs = collect_optimal_k_outputs()
    output.write(df_outputs)
    pass
