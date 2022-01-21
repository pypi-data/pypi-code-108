from functools import reduce
#from dependencies import aggregation_utils as Au
from datetime import datetime


def save_parquet(repartition=None, partition_by=None, path="", output_data=None, _log=None, mode="append"):
    """
   :params repartition: int , size of repartition
   :params partition_by: array , example [cad_job_id, npi_par]
   :params path: string, s3_path
   :params output_data: dataframe
   :return None
   """

    # location = f"s3a://{path}"
    if repartition and partition_by:
        _log.info(f"Partition by {partition_by}")
        output_data.repartition(*repartition).write.partitionBy(*partition_by).mode(mode). \
            option("header", "true").parquet(path)
        return
    if partition_by:
        _log.info(f"Partition by {partition_by}")
        output_data.write.partitionBy(*partition_by).mode(mode). \
            option("header", "true").parquet(path)
        return
    if repartition:
        output_data.repartition(*repartition).write.mode(mode).option("header", "true").parquet(path)
        return

    output_data.write.mode(mode).option("header", "true").parquet(path)


def save_csv(repartition=None, path="", output_data=None, _log=None, mode="append"):
    """
   :params repartition: int , size of repartition
   :params path: string, s3_path
   :params output_data: dataframe
   :return None
   """
    if repartition:
        _log.info(f"Partition by {repartition}")
        output_data.repartition(repartition).write.format('csv').option('header', "true").mode(mode). \
            option('sep', ',').save(path)
        return

    output_data.write.format('csv').option('header', "true").mode(mode). \
        option('sep', ',').save(path)


def save_repartition(repartition_cols=None, partition_by=None, path="", output_data=None, _log=None, mode="append"):
    """
    :params repartition_cols: array , example [F.col('nipi_par'), F.col('cad_job_id')]
    :params partition_by: array , example [cad_job_id, npi_par]
    :params path: string, s3_path
    :params output_data: dataframe
    :return None
    """
    # location = f"s3a://{path}"
    location = Au.proper_s3_name(path)
    _log.info(f"Partition by {partition_by} and {location}")
    output_data.repartition(*repartition_cols).write.partitionBy(*partition_by).mode(mode). \
        option("header", "true").parquet(location)


def new_query_multiple_dfs(_df1_arrays, _df1_name_arrays, _query, _spark):
    """
    :params _df1_arrays: dataframe in array , example [df1,df2]
    :params _df1_name_arrays: dataframe name in array, example [table1,table2]
    :return dataframe
    """
    for df, df_name in zip(_df1_arrays, _df1_name_arrays):
        df.createOrReplaceTempView(df_name)
    query = _query
    df3 = _spark.sql(query)
    return df3


def add_columns_df(cols_df, source_df, func=None):
    """
    :params cols_df: array , example [("cad_created_at", F.lit(F.current_timestamp())), ("cad_job_id", F.lit(self.cad_job_id))]
    :params source_df: dataframe
    :params func: function, example F.lit(col(col_name)), F.lower(col(col_name))
    :return None
    """
    if func:
        return (reduce(
            lambda memo_df, col_name: memo_df.withColumn(col_name, func(col_name)),
            cols_df,
            source_df
        ))

    return (reduce(
        lambda memo_df, col_name: memo_df.withColumn(col_name[0], col_name[1]),
        cols_df,
        source_df
    ))


def add_columns_df_expr(cols_df, source_df):
    return source_df.selectExpr(*cols_df)


def rename_columns_df(cols_df, source_df):
    return (reduce(
        lambda memo_df, col_name: memo_df.withColumnRenamed(col_name[0], col_name[1]),
        cols_df,
        source_df
    ))


def drop_columns_df(cols_df, source_df):
    return source_df.drop(*cols_df)


def rearrange_columns_df(cols_df, source_df):
    return source_df.select(cols_df)


def show_df(comments="", show_schema=False, no_rows=5, display_all=False, source_df=None, _log=None):
    if source_df:
        if _log is None:
            print(comments)
        else:
            _log.info(comments)
        source_df.show(no_rows, display_all)
        if show_schema:
            source_df.printSchema()


def add_columns_df_query(col_transform, source_df, _spark):
    source_df.createOrReplaceTempView("table1")
    query = """
            Select {col_transform} FROM table1
        """.format(col_transform=column_transformations(col_transform))
    print(query)
    return _spark.sql(query)


def column_transformations(cols_df, prefix):
    t = [f"{prefix}.{x}" for x in cols_df]
    return ", ".join(t)


def rename_cad_source_name(source):
    if source:
        return "_".join(source.split("/"))
    return ""


def filter_columns(all_cols, cols_to_filter):
    return [x for x in all_cols if x not in cols_to_filter]


def remove_metadata(meta_cols, df):
    print(meta_cols)
    df2 = df.drop(*meta_cols)
    return df2


def add_prefix(cols, prefix):
    return [f"{prefix}.{x}" for x in cols]


def drop_last_char(s, pattern):
    """
    :params: s :str
    :params: pattern example '_'
    Drop last char at this string with the pattern. Example business_ , pattern='_' return business
    :return s
    """
    if s[-1] == pattern:
        return s[:-1]
    return s


def register_udfs(_spark=None):
    def coverage_mths(coverages):
        """
            This function finds the gap/gaps, merge the coverage months and get the difference between the gaps
            to determine the sum of coverage for client that has gaps/no gap.
            Example: [[1,4],[3,5],[7,12]]. Note; 1 denominates starting from month (1+1) of the client year
            2 is month (2+1) of the client year. The end of year is 12 while starting month is 0.
            For this case, the result of [[1,5], [7,12]] has month differences as [4,5] respectively.
            In this case: the client has a sum of 9 for that client year

            :params coverages: array coverages, example [[1,4],[3,5],[7,12]]
            return int: sum of diff, example 9
        """
        if coverages is None or len(coverages) == 0: return 0
        sorted_coverages = sorted_by_first(coverages)
        merged_coverages = [sorted_coverages[0]]

        for current_coverage_start, current_coverage_end in sorted_coverages[1:]:
            last_merged_coverage_start, last_merged_coverage_end = merged_coverages[-1]
            if current_coverage_start <= last_merged_coverage_end:
                merged_coverages[-1] = [last_merged_coverage_start,
                                        max(last_merged_coverage_end,
                                            current_coverage_end)]
            else:
                merged_coverages.append([current_coverage_start, current_coverage_end])

        return sum_of_diff(merged_coverages)

    _spark.udf.register("coverage_mths", coverage_mths)
    _spark.udf.register("generate_client_year", generate_client_year)


def generate_client_year(client_year, add_or_minus_years):
    """
    :params client_year: string, example 2020-2021
    :params add_or_minus_years:int, example -1
    :return : string, 2019-2020
   """
    years = client_year.split("-")
    return f'{int(years[0]) + add_or_minus_years}-{int(years[-1]) + add_or_minus_years}'


def sorted_by_first(_arr):
    return sorted(_arr, key=lambda x: x[0])


def sum_of_diff(_arr):
    # TODO: check if 0 is acceptable result for this case
    def diff_if_none(x):
        if x[0] and x[1]:
            return x[1] - x[0]
        else:
            return 0

    return sum([diff_if_none(x) for x in _arr])


def alias_names(col_names, aliases):
    return [f"{x}_{c}" for c in col_names for x in aliases]


def client_years(cur_year, num_of_yrs=3):
    """
        :params cur_year: 2020
        :params num_of_yrs: int , 3
        :return array, example ['2019-2020', '2018-2019', '2017-2018']
    """
    return [f"{cur_year - x - 1}-{cur_year - x}" for x in range(num_of_yrs)]


def alias_names_dict(cy, _alias_names, aliases_len):
    """
    :params cy: array client_years, example ['2017-2018']
    :params alias_names: array , example ["current", "prior", "prior2"]
    :params aliases_len: int , length of alias name in this case 3
    :return dict, example {'2019-2020': ['current_num_eligible_months', 'current_is_eligible'],
    '2018-2019': ['prior_num_eligible_months', 'prior_is_eligible'],
    '2017-2018': ['prior2_num_eligible_months', 'prior2_is_eligible']}
    """
    hist = {}
    for cnt_x, x in enumerate(cy):
        hist[x] = [y for cnt_y, y in enumerate(_alias_names) if cnt_y % aliases_len == cnt_x]
    return hist
