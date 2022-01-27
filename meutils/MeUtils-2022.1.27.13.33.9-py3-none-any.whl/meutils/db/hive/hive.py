import codecs
import logging
import os
import random
import re
import string
from collections import OrderedDict
from time import time

import numpy as np
import pandas as pd
import pyarrow as pa
from tqdm import tqdm

from meutils.db.hive.parsers import ORCParser, ParquetParser, TextParser
from meutils.db.hive.utils import (
    get_create_table_sql_template,
    get_dataframe_dtype_mapping,
    get_delimiter_regex_pattern,
    get_hdfs_regex_pattern,
    get_hdfs_server,
    get_insert_table_sql_template,
    get_jdbc_string,
    get_keytab_username,
    get_raw_connect_command_template,
    get_row_format_serde_classes,
    get_storage_format_type_config,
    get_storage_format_type_regex_pattern,
    get_table_column_name_regex_pattern,
    get_table_delimiter_connect_command_template,
    get_table_info_connect_command_template,
    get_table_partitioned_pattern,
)

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def parse_hdfs_path(line):
    hdfs_pattern = get_hdfs_regex_pattern()
    matched = re.match(hdfs_pattern, line)
    if matched is not None:
        return matched.groups()[0]
    else:
        raise ValueError(f"Failed to parse hdfs path, in: '{line}'!!!")


def parse_storage_format_type(line):
    storage_format_type_pattern = get_storage_format_type_regex_pattern()
    # sft := storage format type
    sft_cfg = get_storage_format_type_config()
    sft_alias_dict = sft_cfg["alias"]
    sft_support_type = sft_cfg["support_type"]

    matched = re.match(storage_format_type_pattern, line)

    if matched is not None:
        sft_raw = matched.groups()[0]
        sft_alias = sft_alias_dict[sft_raw]

        if sft_alias not in sft_support_type:
            raise ValueError(
                'Invalid data storage format type: "{sft}", only supports [{support_type}]!!!'.format(
                    sft=sft_alias, support_type=", ".join(sft_support_type)
                )
            )

        return sft_alias
    else:
        raise ValueError(f"Failed to parse data storage type, in '{line}'!!!")


def parse_delimiter(meta_data):
    delimiter_pattern = get_delimiter_regex_pattern()
    # re.DOTALL: Make the '.' special character match any character at
    # all, including a newline(\n).
    matched = re.match(delimiter_pattern, meta_data, re.DOTALL)
    if matched is not None:
        return matched.groups()[1]

    return None


def parse_table_columns(line, is_partition=False):
    (
        col_name_pattern,
        partition_col_name_pattern,
    ) = get_table_column_name_regex_pattern()

    if is_partition:
        pattern = partition_col_name_pattern
    else:
        pattern = col_name_pattern

    raw_columns = None
    col_matched = re.match(pattern, line)
    if col_matched is not None:
        raw_columns = col_matched.groups()[0]

    if raw_columns is None:
        raise ValueError(f"Failed to parse table schema, in '{line}'!!!")

    name_dtype_dict = parse_column(raw_columns)

    return name_dtype_dict


def parse_is_partitioned(line):

    partitioned_pattern = get_table_partitioned_pattern()
    matched = re.match(partitioned_pattern, line)
    if matched is not None:
        is_partitioned = matched.groups()[0]
    else:
        raise ValueError(f"Failed to parse partition table, in '{line}'!!!")

    if is_partitioned == "false":
        is_partitioned = False
    else:
        is_partitioned = True

    return is_partitioned


def get_table_info(cluster_name, database_name, table_name):
    hive_jdbc_dict = get_jdbc_string()
    conn_cmd_template = get_table_info_connect_command_template()

    (
        col_name_pattern,
        partition_col_name_pattern,
    ) = get_table_column_name_regex_pattern()

    valid_cluster_names = hive_jdbc_dict.keys()
    if cluster_name not in valid_cluster_names:
        raise ValueError(
            "Invalid cluster name:{}, not in [{}]!!!".format(
                cluster_name, ",".join(valid_cluster_names)
            )
        )

    jdbc_str = hive_jdbc_dict[cluster_name]

    # init variable
    hdfs_path = ""
    sft_alias = ""
    name_dtype_dict = OrderedDict()
    part_name_dtype_dict = None
    is_partitioned = False

    with os.popen(
        conn_cmd_template.format(
            jdbc_str=jdbc_str, database_name=database_name, table_name=table_name
        )
    ) as pipe:
        info = pipe.readlines()

    # check if info is empty
    if not info:
        raise ValueError("Please make sure that you have uploaded the keytab!!!")

    for line in info:
        if "hdfs://" in line:
            hdfs_path = parse_hdfs_path(line)
        elif "outputformat:" in line:
            sft_alias = parse_storage_format_type(line)
        elif "columns:struct columns" in line:
            name_dtype_dict = parse_table_columns(line, is_partition=False)
        elif "partitionColumns:struct partition_columns" in line:
            part_name_dtype_dict = parse_table_columns(line, is_partition=True)
        elif "partitioned:" in line:
            is_partitioned = parse_is_partitioned(line)

    return hdfs_path, sft_alias, name_dtype_dict, part_name_dtype_dict, is_partitioned


def parse_column(raw_columns):
    # raw_columns example: " string a, i32 b, byte c"

    dtype_mapping = get_dataframe_dtype_mapping(is_df_to_hive=False)
    supported_hive_table_dtypes = dtype_mapping.keys()
    tmp = [
        each.strip().split(" ") for each in raw_columns.strip().split(", ")
    ]  # [["string", "a"], ["i32", "b"], ["byte", "c"], ["decimal(10, 0)", "d"]]
    name_dtype_dict = OrderedDict()
    for _hive_table_dtype, _col_name in tmp:
        # {"a": object, "b": np.int32, "c": np.int8, "d": np.float64}
        if _hive_table_dtype in supported_hive_table_dtypes:
            _dataframe_dtype = dtype_mapping[_hive_table_dtype]
        elif _hive_table_dtype.startswith("decimal"):
            _dataframe_dtype = np.float64
        else:
            _dataframe_dtype = object

        name_dtype_dict[_col_name] = _dataframe_dtype

    return name_dtype_dict


def dataframe_type_conversion(dataframe, table_columns_n_dtypes):
    valid_int_types = ["int8", "int16", "int32", "int64"]
    valid_float_types = ["float32", "float64"]

    for _col_name, _col_dtype in table_columns_n_dtypes.items():
        _col_dtype = np.dtype(_col_dtype)
        _pd_auto_infer_dtype = dataframe.dtypes[_col_name]
        if _col_dtype == _pd_auto_infer_dtype:
            continue

        # try to cast `_col_name` to the raw type
        try:
            logging.info(f"Try to cast the column: `{_col_name}` to the type: `{_col_dtype.name}`")
            dataframe = dataframe.astype({_col_name: _col_dtype}, copy=False)
            logging.info(f"The column: `{_col_name}` has been casted to the type: `{_col_dtype.name}` successfully")
            cast_result = True
        except ValueError as ve:
            logging.warning(f"Failed to cast the column: `{_col_name}` to the type: `{_col_dtype.name}` due to some dirty data!")
            cast_result = False

        # try to cast int-based column to np.float64
        if (not cast_result) and (_col_dtype.name in valid_int_types) and (dataframe.dtypes[_col_name].name not in valid_float_types):
            try:
                logging.info(f"Try to cast the column: `{_col_name}` to the type: `float64`")
                dataframe = dataframe.astype({_col_name: np.float64}, copy=False)
            except ValueError as ve:
                logging.info(f"Failed to cast the column: `{_col_name}` to the type: `float64` due to some dirty data! Remain the current type: `{_pd_auto_infer_dtype.name}`")

    return dataframe

def get_table_delimiter(cluster_name, database_name, table_name):
    hive_jdbc_dict = get_jdbc_string()
    delimiter_conn_cmd_template = get_table_delimiter_connect_command_template()

    valid_cluster_names = hive_jdbc_dict.keys()
    if cluster_name not in valid_cluster_names:
        raise ValueError(
            "Invalid cluster name:{}, not in [{}]!!!".format(
                cluster_name, ",".join(valid_cluster_names)
            )
        )

    jdbc_str = hive_jdbc_dict[cluster_name]

    serde_classes = get_row_format_serde_classes()

    delimiter_conn_cmd = delimiter_conn_cmd_template.format(
        jdbc_str=jdbc_str, database_name=database_name, table_name=table_name
    )

    with os.popen(delimiter_conn_cmd) as pipe:
        table_metadata = pipe.read()

    is_unknown_serde = True
    for serde_cls in serde_classes:
        if serde_cls in table_metadata:
            is_unknown_serde = False
            break

    if is_unknown_serde:
        logging.warning("Metadata of table: `{}`:".format(table_name))
        print(table_metadata)
        raise ValueError("Delimter Not Found!!! Please set delimiter manually!!!")

    delimiter = parse_delimiter(table_metadata)
    if delimiter is None:
        delimiter = "\u0001"  # default

    # decode
    delimiter = codecs.decode(delimiter, "unicode_escape")

    return delimiter


def read_hive_table(
    cluster_name,
    database_name,
    table_name,
    partition="",
    skip_error_lines=True,
    text_engine="c",
    delimiter=None,
):
    logging.info("Reading Hive Table...")
    tic = time()

    if skip_error_lines not in ["True", "true", "false", "False", True, False]:
        raise ValueError(
            f"Parameter skip_error_lines: {skip_error_lines} is invalid, only supports `True` or `False`!!!"
        )
    if isinstance(skip_error_lines, str):
        if skip_error_lines == "True" or skip_error_lines == "true":
            skip_error_lines = True
        else:
            skip_error_lines = False

    (
        hdfs_path,
        sft_alias,
        table_columns_n_dtypes,
        part_tb_col_n_dtypes,
        is_partitioned,
    ) = get_table_info(cluster_name, database_name, table_name)

    if hdfs_path == "":
        raise ValueError(
            f"There is no Table: {table_name} in Database: {database_name}!!!"
        )

    hfs = pa.hdfs.HadoopFileSystem()

    part_hdfs_path = os.path.join(hdfs_path, partition)
    # cut last "/" for ignore root_path//sub_dir
    if part_hdfs_path[-1] == "/":
        part_hdfs_path = part_hdfs_path[:-1]

    if (not is_partitioned) and partition != "":
        raise ValueError(f"Table: {table_name} is not a partition table!!!")

    # os.path.join(root_path, "") => root_path
    if not hfs.isdir(part_hdfs_path):
        raise ValueError(f"Invalid Partition Table Name: {partition}!!!")
    pd_df_list = []

    if sft_alias == "Text":
        if delimiter is None:
            delimiter = get_table_delimiter(cluster_name, database_name, table_name)

        table_column_names = list(table_columns_n_dtypes.keys())
        if text_engine not in ["c", "python"]:
            raise ValueError(
                f"Invalid text parsing engine: {text_engine}, only supports `c` or `python`!!!"
            )

        logging.info(
            f"Use the `{text_engine}` engine(default: `c`) to "
            "read hive table in text format..."
        )
        logging.warning(
            "`c` engine is faster but may cause some data loss "
            "due to bad lines. `python` is friendly to dirty "
            "data but slower!"
        )
        logging.info("It is strongly recommended to use `Parquet` or `ORC` format to store the table.")

        parser = TextParser(
            delimiter,
            table_column_names,
            table_columns_n_dtypes,
            error_bad_lines=(not skip_error_lines),
            default_engine=text_engine,
        )
    elif sft_alias == "Parquet":
        parser = ParquetParser()
    elif sft_alias == "ORC":
        parser = ORCParser()
    else:
        raise ValueError(f'Invalid Data Storage Format Type: "{sft_alias}"!!!')

    for _root_path, _, _files in hfs.walk(part_hdfs_path):

        if is_partitioned:
            # "root_path/p1=1/p2=3/p3=a"
            # => "/p1=1/p2=3/p3=a"
            # => ["", "p1=1", "p2=3", "p3=a", ""]
            # => ["p1=1", "p2=3", "p3=a"]
            part_list = filter(
                lambda x: x != "" and "=" in x, _root_path[len(hdfs_path) :].split("/"),
            )
            part_list = list(map(lambda x: x.split("="), part_list))
        else:
            part_list = []

        for _file in tqdm(_files):
            file_path = os.path.join(_root_path, _file)
            file_stat = hfs.stat(file_path)
            # example format {"size": 1024, "kind": "file"}
            # skip empty file.
            if file_stat["size"] == 0:
                continue

            # read data
            pd_df_list.append(parser.read(file_path))

            try:
                # set partition table
                for (_part_col, _part_val) in part_list:
                    if part_tb_col_n_dtypes[_part_col] != object:
                        _part_val = part_tb_col_n_dtypes[_part_col](_part_val)
                    pd_df_list[-1][_part_col] = _part_val
            except BaseException as be:
                logging.fatal(
                    f"Failed to set partition table while parsing file: {file_path}!!! "
                )
                raise be

    # check empty list
    if not pd_df_list:
        raise ValueError("Empty table.")

    pd_df = pd.concat(pd_df_list)
    shape = pd_df.shape
    # reset index
    pd_df.index = range(shape[0])

    # cast data type for text-format source table
    if sft_alias == "Text":
        dataframe_type_conversion(pd_df, table_columns_n_dtypes)

    toc = time()

    logging.info("Finish loading, time cost:{:0.3f} sec.".format(toc - tic))

    return pd_df


def dataframe_to_table_schema(dataframe):
    table_column_names = dataframe.columns
    df_to_hive_mapping = get_dataframe_dtype_mapping(is_df_to_hive=True)

    table_column_types = [x.type for x in dataframe.dtypes.values]

    table_schema = []
    for col_name, col_type in zip(table_column_names, table_column_types):
        # default by string
        col_type = df_to_hive_mapping.get(col_type, "string")
        table_schema.append(f"`{col_name}` {col_type}")
    table_schema = ", ".join(table_schema)

    return table_schema


def get_partition_table_schema(partition_info):
    partition_col_names_list = [x.split("=")[0] for x in partition_info.split("/")]
    partition_col_vals_list = [x.split("=")[1] for x in partition_info.split("/")]
    partition_col_types_list = ["string"] * len(partition_col_names_list)

    partition_table_create_schema = []
    for part_col_name, part_col_type in zip(
        partition_col_names_list, partition_col_types_list
    ):
        partition_table_create_schema.append(f"`{part_col_name}` {part_col_type}")
    partition_table_create_schema = ", ".join(partition_table_create_schema)

    partition_table_insert_schema = []
    for part_col_name, part_col_val in zip(
        partition_col_names_list, partition_col_vals_list
    ):
        partition_table_insert_schema.append(f"`{part_col_name}`='{part_col_val}'")
    partition_table_insert_schema = ", ".join(partition_table_insert_schema)

    return partition_table_create_schema, partition_table_insert_schema


def check_table_schema(raw_table_cols_list, write_table_cols_list):
    raw_table_columns_n_dtypes, raw_part_tb_col_n_dtypes = raw_table_cols_list
    dataframe_table_schema, partition_table_create_schema = write_table_cols_list

    raw_table_columns = [f"`{x}`" for x in raw_table_columns_n_dtypes.keys()]
    dataframe_table_columns = [
        x.split(" ")[0] for x in dataframe_table_schema.split(", ")
    ]

    if len(raw_table_columns) != len(dataframe_table_columns):
        raise ValueError(
            f"Cannot Insert DataFrame Into Target Table, Because Column Number Are Diffrent: DataFrame has {len(raw_table_columns)} Columns, But The Original Table Has {len(dataframe_table_columns)} Columns."
        )

    if raw_table_columns != dataframe_table_columns:
        raise ValueError(
            f"Cannot Insert DataFrame Into Target Table, Because Column Names Are Diffrent: DataFrame Columns Names Are [{', '.join(raw_table_columns)}], But The Original Table Column Names Are [{', '.join(dataframe_table_columns)}]."
        )

    if partition_table_create_schema:
        raw_part_table_columns = [f"`{x}`" for x in raw_part_tb_col_n_dtypes.keys()]
        part_table_columns = [
            x.split(" ")[0] for x in partition_table_create_schema.split(", ")
        ]

        for part_tb_col in part_table_columns:
            if part_tb_col not in raw_part_table_columns:
                raise ValueError(
                    f"Invalid Partition Columns: {part_tb_col}, Only Supports [{', '.join(part_table_columns)}]."
                )


def write_hive_table(
    dataframe,
    cluster_name,
    database_name,
    table_name,
    partition="",
    mode="insert",
    store_type="parquet",
):

    tic = time()

    # check dataframe
    from pandas import DataFrame

    if not isinstance(dataframe, DataFrame):
        raise ValueError("Invalid Data Type, Only Supports `Pandas.DataFrame`!!!")

    logging.info("Writing Hive Table...")
    logging.info("It may take a few minutes to write table, please wait patiently...")

    if mode not in ["insert", "overwrite"]:
        raise ValueError(
            "Invalid Mode: {}, Only Supports `insert` or `overwrite`!!!".format(mode)
        )

    store_type = store_type.upper()
    if store_type not in ["PARQUET", "ORC"]:
        raise ValueError(
            "Invalid storage type: {}, Only Supports `parquet` or `orc`!!!"
        )

    (
        hdfs_path,
        sft_alias,
        table_columns_n_dtypes,
        part_tb_col_n_dtypes,
        is_partitioned,
    ) = get_table_info(cluster_name, database_name, table_name)

    is_table_exists = False if hdfs_path == "" else True

    if mode == "insert" and (not is_table_exists):
        raise ValueError(
            "Cannot `Insert` Data To A Table({}) That Does Not Exist.".format(
                table_name
            )
        )

    # 1. create temp dir and put dataframe to temp_dir
    hfs = pa.hdfs.HadoopFileSystem()

    keytab_username = get_keytab_username()
    hdfs_server = get_hdfs_server(cluster_name)

    # hdfs_temp_dir should be unique
    while True:
        random_string = "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )
        hdfs_temp_dir = (
            f"hdfs://{hdfs_server}/user/{keytab_username}/temp_{random_string}/"
        )
        if hfs.exists(hdfs_temp_dir):
            logging.warning("Making temp hdfs dir failed, please waiting for retry.")
        else:
            hfs.mkdir(hdfs_temp_dir)
            break

    # set \u0001(\x01) as default delimiter
    default_delimiter = "\u0001"
    dataframe.to_csv(
        f"{hdfs_temp_dir}/tmp.csv", sep=default_delimiter, header=False, index=False
    )

    # 2. create sqls
    dataframe_table_schema = dataframe_to_table_schema(dataframe)
    partition_table_create_schema = partition_table_insert_schema = ""
    if partition:
        (
            partition_table_create_schema,
            partition_table_insert_schema,
        ) = get_partition_table_schema(partition)

    if is_table_exists:
        # check if dataframe_table_schema is equal to raw_table_schema
        check_table_schema(
            [table_columns_n_dtypes, part_tb_col_n_dtypes],
            [dataframe_table_schema, partition_table_create_schema],
        )

    hive_jdbc_dict = get_jdbc_string()
    jdbc_str = hive_jdbc_dict[cluster_name]

    write_table_sqls_list = []

    ## 2.1 create temp table
    temp_table_name = f"temp_easydata_{random_string}"
    create_temp_table_sql = get_create_table_sql_template(
        database_name,
        temp_table_name,
        dataframe_table_schema,
        store_type="text",
        partition_table_create_schema="",
        temporary=True,
        delimiter=default_delimiter,
        location=hdfs_temp_dir,
    )
    write_table_sqls_list.append(create_temp_table_sql)

    ## 2.2 create real table from temp table
    if not is_table_exists:
        # create a real table if table does not exist
        create_real_table_sql = get_create_table_sql_template(
            database_name,
            table_name,
            dataframe_table_schema,
            store_type=store_type,
            partition_table_create_schema=partition_table_create_schema,
            temporary=False,
            delimiter=default_delimiter,
            location="",
        )
        write_table_sqls_list.append(create_real_table_sql)

    if mode == "overwrite":
        write_type = "OVERWRITE"
    elif mode == "insert":
        write_type = "INTO"

    insert_table_sql = get_insert_table_sql_template(
        write_type,
        database_name,
        table_name,
        partition_table_insert_schema,
        database_name,
        temp_table_name,
    )
    write_table_sqls_list.append(insert_table_sql)

    write_table_sqls = " ".join(write_table_sqls_list)

    # 3. execute sql
    connect_command_template = get_raw_connect_command_template()
    with os.popen(
        connect_command_template.format(jdbc_str=jdbc_str, sql=write_table_sqls)
    ) as pipe:
        create_table_logs = pipe.readlines()

    # 4. check table result
    (
        hdfs_path,
        sft_alias,
        table_columns_n_dtypes,
        part_tb_col_n_dtypes,
        is_partitioned,
    ) = get_table_info(cluster_name, database_name, table_name)

    if hdfs_path == "":
        logging.fatal("CREATE TABLE FAILED!")
        logging.fatal(create_table_logs)
        raise ValueError("CREATE TABLE FAILED! Check The Log For More Informations.")

    toc = time()

    logging.info("Finish writing, time cost:{:0.3f} sec.".format(toc - tic))
