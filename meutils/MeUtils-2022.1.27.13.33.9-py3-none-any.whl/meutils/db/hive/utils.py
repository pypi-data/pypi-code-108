import os
import re

import yaml


def get_jdbc_string():
    with open(
        os.path.join(os.path.dirname(__file__), "config/hive_jdbc.yaml")
    ) as yaml_reader:
        jdbc_str_dict = yaml.safe_load(yaml_reader)

    return jdbc_str_dict


def get_storage_format_type_config():
    with open(
        os.path.join(os.path.dirname(__file__), "config/storage_format_type.yaml")
    ) as yaml_reader:
        storage_format_type_cfg = yaml.safe_load(yaml_reader)

    return storage_format_type_cfg


def get_raw_connect_command_template():
    return 'beeline --silent=true -u "{jdbc_str}" -e "{sql}"'


def get_table_info_connect_command_template():

    return 'beeline --silent=true -u "{jdbc_str}" -e "use \`{database_name}\`; show table extended like \'{table_name}\';"'


def get_table_delimiter_connect_command_template():
    return 'beeline --silent=true -u "{jdbc_str}" -e "use \`{database_name}\`; show create table \`{table_name}\`;"'


def get_create_table_sql_template(
    database_name,
    table_name,
    table_schema,
    store_type,
    partition_table_create_schema="",
    temporary=False,
    delimiter="\u0001",
    location="",
):
    # ref: https://cwiki.apache.org/confluence/display/Hive/LanguageManual+DDL
    f_str_temporary = "TEMPORARY" if temporary else ""
    create_table_sql = (
        f"CREATE {f_str_temporary} TABLE `{database_name}`.`{table_name}` ({table_schema})"
    )

    if store_type == "Text":
        create_table_sql = f"{create_table_sql} ROW FORMAT DELIMITED FIELDS TERMINATED BY '{delimiter}'"

    if partition_table_create_schema:
        create_table_sql = (
            f"{create_table_sql} PARTITIONED BY ({partition_table_create_schema})"
        )

    store_type = store_type.upper()
    if store_type == "TEXT":
        store_type = "TEXTFILE"
    create_table_sql = f"{create_table_sql} STORED AS {store_type}"

    if location:
        create_table_sql = f"{create_table_sql} LOCATION '{location}'"

    create_table_sql = f"{create_table_sql};".replace("`", "\`")

    return create_table_sql


def get_insert_table_sql_template(
    write_type,
    database_name,
    table_name,
    partition_table_insert_schema,
    from_database_name,
    from_table_name,
):
    # ref: https://cwiki.apache.org/confluence/pages/viewpage.action?pageId=82903069
    if partition_table_insert_schema:
        insert_table_sql = f"INSERT {write_type} TABLE `{database_name}`.`{table_name}` PARTITION ({partition_table_insert_schema}) select * from `{from_database_name}`.`{from_table_name}`;"
    else:
        insert_table_sql = f"INSERT {write_type} TABLE `{database_name}`.`{table_name}` select * from `{from_database_name}`.`{from_table_name}`;"

    insert_table_sql = insert_table_sql.replace("`", "\`")

    return insert_table_sql


def get_keytab_username():
    username_cmd = 'klist | grep "Default principal"'
    # Default principal: bdms_yangshudong/dev@HADOOP.HZ.NETEASE.COM
    with os.popen(username_cmd) as pipe:
        info = pipe.readlines()
        info = info[0]
        info = info.strip()
        matched = re.match(r"^Default principal: (.*?)/dev@.*?$", info)
        if matched is not None:
            username = matched.groups()[0]
        else:
            raise ValueError(f"Failed to parse default username, in: '{line}'!!!")

    return username


def get_hdfs_server(cluster_name):
    if re.match(r"hz\d+", cluster_name):
        hdfs_server = cluster_name.replace("hz", "hz-cluster")
    else:
        hdfs_server = cluster_name

    return hdfs_server


def get_row_format_serde_classes():
    return [
        "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe",
        "com.netease.backend.bigdata.hive.serde.GenericLogSerDe",
    ]


def get_hdfs_regex_pattern():
    # hdfs path example: `| location:hdfs://hz-cluster8/user/bdms_yangshudong/text_data              |\n`

    # (1) .* for match every chars(numbers), .*? for no-grid search.
    # (2) \s for match space, \s+ for match multi-spaces.
    # (3) ^ for match head, and $ for match end.
    return r"^\|\s+location:(hdfs://.*?)\s+\|\n$"


def get_storage_format_type_regex_pattern():
    # 5 data storage format types offered by mammut
    #     TEXTFILE: org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat(Support)
    #     PARQUET: org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat(Support)
    #     ORC: org.apache.hadoop.hive.ql.io.orc.OrcOutputFormat
    #     AVRO: org.apache.hadoop.hive.ql.io.avro.AvroContainerOutputFormat
    #     SEQUENCEFILE: org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat

    # storage format type example: `| outputformat:org.apache.hadoop.hive.ql.io.HiveSequenceFileOutputFormat  |\n`

    # (1) .* for match every chars(numbers), .*? for no-grid search.
    # (2) \s for match space, \s+ for match multi-spaces.
    # (3) ^ for match head, and $ for match end.

    return r"^\|\s+outputformat:(org\.apache\.hadoop\.hive\.ql\.io.*?)\s+\|\n$"


def get_delimiter_regex_pattern():
    # delimiter line example: `|   'field.delim'=',',                                            |\n"`

    # (1) .* for match every chars(numbers), .*? for no-grid search.
    # (2) \s for match space, \s+ for match multi-spaces.
    # (3) ^ for match head, and $ for match end.

    return r".*?'(field.delim|fields.terminated.by)'='(.*?)'"


def get_table_column_name_regex_pattern():
    # columns example: `| columns:struct columns { string a, string b, string c}                              |\n`
    # partition columns example: `| partitionColumns:struct partition_columns { string p1, string p2, string p3}        |\n`

    # (1) .* for match every chars(numbers), .*? for no-grid search.
    # (2) \s for match space, \s+ for match multi-spaces.
    # (3) ^ for match head, and $ for match end.

    return (
        r"^\|\s+columns:struct columns \{\s+(.*?)\}\s+\|\n$",
        r"^\|\s+partitionColumns:struct partition_columns \{\s+(.*?)\}\s+\|\n$",
    )


def get_table_partitioned_pattern():
    # partitioned example: `| partitioned:false                                 |\n`

    # (1) .* for match every chars(numbers), .*? for no-grid search.
    # (2) \s for match space, \s+ for match multi-spaces.
    # (3) ^ for match head, and $ for match end.

    return r"^\|\s+partitioned:(false|true) \s+\|\n$"


def get_dataframe_dtype_mapping(is_df_to_hive=True):
    # There are 14 dtypes(string, int, date, float, double,
    #   tinyint, smallint, bigint, boolean, binary, timestamp, decimal, varchar, char) in hive table.

    # For now, pandas only support part of them(np.int[8,16,32,64], np.float[16,32,64], np.datetime, np.bool, ...), other dtype will mapping to np.object.

    import numpy as np

    if is_df_to_hive:
        mapping = {
            np.int8: "TINYINT",  # byte <=> TINYINT
            np.int16: "SMALLINT",  # i16 <=> SMALLINT
            np.int32: "INT",  # i32 <=> INT
            np.int64: "BIGINT",  # i64 <=> BIGINT
            np.float32: "float",  # float <=> FLOAT
            np.float64: "double",  # double <=> DOUBLE
            bool: "bool",  # bool <=> bool
            np.datetime64: "date",
        }
    else:
        mapping = {
            "byte": np.int8,  # byte <=> TINYINT
            "i16": np.int16,  # i16 <=> SMALLINT
            "i32": np.int32,  # i32 <=> INT
            "i64": np.int64,  # i64 <=> BIGINT
            "float": np.float32,  # float <=> FLOAT
            "double": np.float64,  # double <=> DOUBLE
            "bool": bool,  # bool <=> bool
            "date": np.datetime64,
        }

    return mapping
