import re
from dependencies import aggregation_utils as Au
from dependencies import providers_utils as Pu


def read_csv(_delimiter=",", _s3_path=None, _header_row=True, _spark=None):
    delimiter = _delimiter or ","
    return _spark.read.csv(
        _s3_path,
        sep=delimiter,
        header=_header_row,
        ignoreLeadingWhiteSpace=True,
        ignoreTrailingWhiteSpace=True,
    )


def treat_df_columns(_df):
    return [re.sub('[^a-zA-Z0-9]+', ' ', c).replace(' ', '_').lower() for c in _df.columns]


def extract_data_frame_npi(_name, _s3_path, _debug, _log, _spark):
    _filename = _s3_path.get('filename', None)
    if _filename:
        _proper_s3_name = Au.proper_s3_name(_filename)
    _filetype = _s3_path.get('filetype', None)
    _log.info(f" Input is : {_proper_s3_name} and name {_name} and {_s3_path}")
    if _filetype and _filetype == "csv":
        _header_row = _s3_path.get('header_row', False)
        df = read_csv(_delimiter=",", _s3_path=_proper_s3_name, _header_row=_header_row, _spark=_spark)
        _cols = treat_df_columns(df)
        # Pu.debug_log_with_cnt(f"# {_name} df:", df, _debug, _log)
        # if _debug: df.printSchema()
        # if _debug: _log.info(f" Columns ${_cols}")
        df.toDF(*_cols).createOrReplaceTempView(_name)
    return


def df_to_list_of_dict(_df):
    return [row.asDict() for row in _df.collect()]
