# Standard library imports
import bz2
import io
import json
import os
import pickle
from typing import Set, Dict, Union, List
import sys
from subprocess import check_output, STDOUT

# Third party imports
import numpy as np
import pandas as pd
from pathlib import Path

ConfigType = Dict[str, Dict[str, Union[str, int]]]

def load_config(config_path: Union[str, Path]) -> ConfigType:
    '''Safely load yaml type configurations

    Args:
        config_path (str, Path): path to your secrets

    Returns:
        dict: a dictionary of a certain structure

    Examples:

        .. code-block:: python

            # /opt/settings/config.yml
met            database:
              user: 'root'
            # ----

            from pathlib import Path
            from samesyslib.utils import load_config

            config_path = Path("/opt/settings/config.yml")
            conf = load_config(config_path)

            conf['database']['user']
    '''
    from ruamel import yaml
    with io.open(file=config_path, mode="rt") as config_file:
        return yaml.safe_load(config_file)


def hms_format(seconds: int) -> str:
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:>02.0f}:{:>02.0f}:{:>05.2f}".format(hours, minutes, seconds)


def list_files(dir: Union[str, Path]) -> List[str]:
    from subprocess import check_output
    print(check_output(["ls", dir]).decode("utf8"))
    return check_output(["ls", dir]).decode("utf8").strip().split('\n')


def sql_from_file(filename: Union[str, Path]) -> List[str]:
    with open(filename, 'r') as reader:
        sql_file = reader.read()       # reads as string
    # all SQL commands (split on ';')
    sql_commands = sql_file.split(';')
    return(sql_commands)


def get_col_types(df, columns=None):
    if not columns:
        columns = df.columns
    for col in columns:
        value = df[[col]].values[0][0]
        print(f'{col}: {type(value)}: {value}')


def dataset_summary(data, index_summary=True, detail=False, quick=True):
    import pandas as pd
    if index_summary:
        df = data.copy()
        df = df.reset_index()
    else:
        df = data
    df_s = pd.DataFrame(df.dtypes, columns = ['type'])
    if detail:
        df_s = df_s.merge(df.head(1).T, left_index=True, right_index=True, how = 'outer')
        df_s = df_s.merge(df.tail(1).T, left_index=True, right_index=True, how = 'outer')
        df_s = df_s.merge(pd.DataFrame(df.min(), columns = ['min']), left_index=True, right_index=True, how = 'left')
        df_s = df_s.merge(pd.DataFrame(df.max(), columns = ['max']), left_index=True, right_index=True, how = 'left')
        df_s.columns = ['type', 'first', 'last', 'min', 'max']
    if not quick:
        df_s = df_s.merge(pd.DataFrame(df.mean(numeric_only=None), columns = ['mean']), left_index=True, right_index=True, how = 'outer')
        df_s = df_s.merge(pd.DataFrame(df.std(), columns = ['std']), left_index=True, right_index=True, how = 'outer')
    df_s = df_s.merge(pd.DataFrame(df.nunique(), columns = ['n_uniq']), left_index=True, right_index=True, how = 'outer')
    df_s = df_s.merge(pd.DataFrame(df.isnull().sum(), columns = ['n_miss']), left_index=True, right_index=True, how = 'outer')
    df_s = df_s.merge(pd.DataFrame(df.count(), columns = ['obs']), left_index=True, right_index=True, how = 'outer')
    return df_s


def mysql_engine(params):
    from sqlalchemy import create_engine
    '''
    Automatically setup appropriate connection string for MySQL based
    on params dictionary.
    '''
    connection_string = "mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(
                params['login'], params['password'], params['host'], params['port'], params['schema']
            )
    return create_engine(connection_string, pool_pre_ping=True)


def get_data_from_query(sql_dir, table, conn, verbose=True):
    import time
    sql_file = Path(sql_dir, f'{table}.sql')
    query = sql_from_file(sql_file)[0]
    tic1 = time.perf_counter()
    df = conn.get(query)
    toc1 = time.perf_counter()
    if verbose > 0:
        print(f'Downloaded [{table}]: {df.shape} in {toc1 - tic1:0.4f} seconds')
    return df


def get_git_info(repo_dir:str) -> dict:
    """
    Extract basic git info from CWD
    example:
        repo_dir = os.path.dirname(os.path.realpath(__file__))
    """
    branch = check_output(f"cd {repo_dir};\
                            git rev-parse --abbrev-ref HEAD",
                            shell=True,stderr=STDOUT).decode("utf8").rstrip()
    commit = check_output(f"cd {repo_dir};\
                            git rev-parse --short HEAD",
                            shell=True,stderr=STDOUT).decode("utf8").rstrip()
    return {'branch':branch, 'commit':commit}


def init_metadata(conn:object, table_name: str=None, schema:str=None, metadata: dict=None) -> None:
    """
    Write dictionary into DB table, initializing only passed keys, rest leaving as default/Null
    """
    table_structure = conn.get(
        f"""
        SELECT * FROM {schema}.{table_name} limit 0;
        """
    )
    for key in metadata.keys():
        table_structure.loc[0, key] = metadata[key]
    conn.send_append(table_structure, table_name, schema=schema)

def update_model_metadata(conn:object, run_id:str, key:str, value:object,
 run_id_col:str = None, table_name:str=None, table_schema:str = None) -> None:
    conn.execute(
        f"""
        UPDATE `{table_schema}`.`{table_name}`
        SET {key} = '{value}'
        WHERE {run_id_col} = '{run_id}'
        """,
        verbose = True
    )


def split_array_into_batches(shop_list:object, batch_size: int):
    if shop_list.shape[0] > batch_size:
        return np.array_split(shop_list.values, np.ceil(shop_list.shape[0]/batch_size))
    else:
        return np.array_split(shop_list.values, 1)


def save_bzipped(obj: object, filename: object, protocol: int=-1):
    """
    Save python object into pickle and compress it
    """
    with bz2.BZ2File(filename, 'wb') as f:
        pickle.dump(obj, f, protocol)


def load_bzipped(data: object):
    """
    Reverse save_bzipped operation
    """
    return pickle.loads(bz2.decompress(data))


def read_batched_shops_data(conn: object, batch: list, table_schema: str, table_name: str, run_id_col: str = None, run_id: str = None):
    shops = ','.join(batch.astype(str))
    if run_id_col is not None:
        tbl = conn.get(f"""SELECT *
                           FROM {table_schema}.{table_name}
                           WHERE {run_id_col} = '{run_id}'
                           AND shop_id in ({shops});
                        """, optimize_verbose=False, timing_verbose=False)
    else:
        tbl = conn.get(f"""SELECT *
                           FROM {table_schema}.{table_name}
                           WHERE shop_id in ({shops});
                        """, optimize_verbose=False, timing_verbose=False)
    return tbl


def preprocess_activities(shop_data:pd.DataFrame, activities_column:str='occasion_type_id', prefix:str='event_'):
    """
    Function to tranform activities in v1_daily_feature/v1_daily_future_features stored as list
    into dummy variables used in xgboost model.
    """
    activities = pd.get_dummies(shop_data.set_index('date')\
        [activities_column].apply(lambda x: json.loads(x) if pd.notnull(x) else None).explode())
    #rename columns
    activities.columns = [prefix+str(col) for col in activities.columns]
    # remove duplicated rows
    activities = activities.groupby(activities.index).agg('max')

    if activities.columns.size > 0:
        dt_col = []
        for col in activities.columns:

            grouper = (activities[col]==0).cumsum()

            cum_val = activities[[col]].groupby( grouper ).cumsum()
            cum_val['grouper'] = grouper

            cum_val = cum_val.join(cum_val.groupby('grouper')[col].agg(max_value=('max')), on=['grouper'], how='left').drop('grouper', axis=1)
            cum_val[col] = (cum_val[col]/cum_val['max_value'])
            dt_col.append(cum_val[[col]])
        activities = pd.concat(dt_col, axis=1).fillna(0)
    return activities


def join_shops_for_query(tbl:pd.Series) -> str:
    return ', '.join([str(x) for x in list(tbl.unique())])


def reduce_intersecting_shops(d:dict) -> set:
    return reduce(set.intersection, (set(val.index) for val in d.values()))


def join_coordinates(tbl:pd.DataFrame) -> pd.Series:
    return tbl.latitude.astype(str) + ", " + tbl.longitude.astype(str)


def remove_special_char(my_str:str, replace_ws:bool=False, escape_punct:bool=True) -> str:
    if isinstance(my_str, float):
        my_str = str(my_str)
    my_str = unidecode(my_str)
    if escape_punct:
        chars = re.escape(string.punctuation)
        my_str = re.sub(r'['+chars+']', '',my_str)
    my_str = re.sub('  ', ' ',my_str)
    if replace_ws:
        my_str = re.sub(' ', '\\\s?',my_str)
    return my_str.lower()


def list_to_dict(category_list:list) -> dict:
    return dict(zip([category_list], [1]))


def estimate_similarity(df:pd.DataFrame, fill_na:bool=False):
    """Estimates similarity matrix according to euclidean distance.
     The result is scaled to 0-1.
     Argument provided whether to fill NA's as 0's.
    """
    df = df.reset_index(level=0)
    if fill_na:
        df = df.fillna(0)
    df = df.set_index('shop_id')
    if 'index' in df.columns:
        df = df.drop(columns=['index'])
    shop_index = df.index.values
    x = df.to_numpy(copy=True)
    dist = nan_euclidean_distances(x, x)
    max_dist = np.nanmax(dist)
    sim = (max_dist-dist)/max_dist
    return sim, shop_index


def cartesian_product(left: pd.DataFrame, right: pd.DataFrame):
    return left.assign(key=1).merge(right.assign(key=1), on='key').drop('key', 1)


def filter_rows_and_cols(df: pd.DataFrame, filter_list: list):
    """Filtering both rows and cols by provided name list.
    """
    return df.loc[df.index.isin(filter_list),
                  df.columns.astype(int).isin(filter_list)]


def percentile(n: int):
    """Percentile function that can be passed to pandas agg() function
    AND changes column name.
    """
    def percentile_(x):
        return x.quantile(n)
    percentile_.__name__ = 'q%s' % n
    return percentile_


def get_branch_commit_from_mapping(query, conn):
    result_set = conn.execute(query, verbose=True).first()
    assert result_set is not None, 'No git branch and commit info saved in metadata mapping'

    result = dict(result_set)
    branch_info = json.loads(result['git_branch_map'])
    commit_info = json.loads(result['git_commit_map'])

    return branch_info, commit_info


def custom_round(x, base=0.25):
    return base * round(float(x)/base)
