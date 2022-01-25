"""
Format detection.
"""
import typing
import os
import re
import csv
from collections import namedtuple, defaultdict

FileFormatDescription = namedtuple("FileFormatDescription", "format read_args size avg_line_size")

# values that are unlikely to be header names, i.e. blank or numeric
PTN_NOT_HEADER = re.compile(r'^([-+]?\s*(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?)?$')
# a likely looking single-column CSV file - first line contains a non-delimited string-like value
PTN_SINGLE_COL_CSV = re.compile(r'^(?!([0-9]|\.[0-9]|{|\[))' + r'[^\s,;|:]+[ \t]*\n.*')
PTN_SINGLE_COL_CSV_B = re.compile(rb'^(?!([0-9]|\.[0-9]|{|\[))' + rb'[^\s,;|:]+[ \t]*\n.*')

VALID_CSV_OPTIONS = frozenset({
    "sep", "delimiter", "header", "names", "usecols", "prefix", "mangle_dupe_cols", "dtype", "true_values",
    "false_values", "skipinitialspace", "skiprows", "skipfooter", "na_values", "keep_default_na",
    "na_filter", "skip_blank_lines", "parse_dates", "infer_datetime_format", "keep_date_col", "dayfirst",
    "cache_dates", "compression", "thousands", "decimal", "lineterminator", "quotechar", "quoting",
    "doublequote", "escapechar", "comment", "encoding", "delim_whitespace", "float_precision", "nrows",
    "chunksize",
})
VALID_JSON_OPTIONS = frozenset({
    "orient", "dtype", "convert_dates", "keep_default_dates", "precise_float", "date_unit", "encoding",
    "compression", "lines", "nrows", "chunksize",
})
VALID_HDF_OPTIONS = frozenset({
    "key", "errors", "start", "stop", "chunksize",
})
VALID_EXCEL_OPTIONS = frozenset({
    "sheet_name", "header", "names", "index_col", "usecols", "squeeze", "dtype", "engine", "true_values",
    "false_values", "skiprows", "nrows", "na_values", "keep_default_na",
    "parse_dates", "thousands", "comment", "skipfooter", "convert_float", "mangle_dupe_cols"
})
VALID_PARQUET_OPTIONS = frozenset({
    "engine", "columns", "use_nullable_dtypes",
})
VALID_OPTIONS = {
    "csv": VALID_CSV_OPTIONS,
    "json": VALID_JSON_OPTIONS,
    "hdf": VALID_HDF_OPTIONS,
    "xlsx": VALID_EXCEL_OPTIONS
}


def detect_format(
        filename: str, sampler: typing.Union[typing.Callable[[], typing.Union[bytes, bytearray]], bytes, str, bytearray, None]=None,
        sizer: typing.Union[typing.Callable[[], int], typing.Union[int, None]]=None, supplied_options: dict=None,
        fallback_to_text: bool=False
) -> FileFormatDescription:
    """
    General purpose format detector / sniffer.

    :param filename:        Name or URL for file, used specifically and only to guess format from extension.
    :param sampler:         A method that returns a sample, a sample, or None.
    :param sizer:           A method that returns the file's size, the size, or None.
    :param supplied_options:  Caller-supplied formatting options which will override the detection process.
    :param fallback_to_text:  True to assume any unrecognized format that looks like a text file should be read line by line.

    :returns:  A FileFormatDescription, with fields:
                    format              File format: csv, json, ...
                    read_args           Arguments compatible with pandas.read_***() methods.
                    size                File size or None.
                    avg_line_size       Estimated mean size of lines, which can be useful for choosing a processing
                                        technique.
    """
    # determine format of file
    ext = find_url_extension(filename)
    format = ext
    if supplied_options and "format" in supplied_options:
        format = supplied_options["format"]
    read_args = {}
    # normalize the format and infer things
    FORMAT_ALIASES_ETC = {
        "csv": ("csv", {}),
        "json": ("json", {}),
        "yml": ("yaml", {}),
        "tab": ("csv", {"delimiter": "\t"}),
        "tsv": ("csv", {"delimiter": "\t"}),
        "txt": ("csv", {"delimiter": '\n', "names": ["line"]})
    }
    orig_format = (format or "").lower()
    if format:
        format, implied_defaults = FORMAT_ALIASES_ETC.get(format.lower(), (format, {}))    # determine format based on a sample
        read_args.update(implied_defaults)
    size = sizer() if sizer and hasattr(sizer, "__call__") else sizer
    avg_line_size = None
    # use sample of data if available
    # - some formats are not sniffed so we don't sample them
    if sampler and format not in ("yaml", "xlsx", "xls", "parquet") and orig_format not in ("txt",):
        sample = sampler() if hasattr(sampler, "__call__") else sampler
        if not format and looks_like_json(sample, size):
            format = "json"
        elif not format and looks_like_csv(sample):
            format = "csv"
        elif not format and looks_like_hdf(sample):
            format = "hdf"
        if format == "csv":
            apply_csv_read_args(sample, read_args)
        elif format == "json":
            apply_json_read_args(sample, read_args)
        elif format in ("yaml", "xlsx", "xls", "parquet"):
            # no 'fallback-to-text' for any recognized format
            pass
        elif fallback_to_text and looks_like_text_file(sample):
            # a single column called 'line'
            format = "csv"
            read_args.update({"delimiter": '\n', "names": ["line"]})
        # calculate average line size
        avg_line_size = average_line_size(sample)
    # override determined options with supplied values
    if supplied_options:
        # user can supply chunksize in bytes, we will convert it to lines
        chunksize_bytes = supplied_options.pop("chunksize_bytes", None)
        if chunksize_bytes and avg_line_size:
            supplied_options["chunksize"] = max(chunksize_bytes // avg_line_size, 1)
        # FIXME it seems very dangerous to mix supplied and detected options
        #  1) add a 'nosniff' option
        #  2) work through likely cases where we would want to inhibit sniffed options because of a user-provided option
        overrides = dict(supplied_options)
        overrides.pop("format", None)
        read_args.update(overrides)
    # limit to valid options for format
    if format in VALID_OPTIONS:
        valid_opts = VALID_OPTIONS[format]
        invalid = set(read_args) - valid_opts
        if invalid:
            raise ValueError(f"Invalid options for format={format}: {', '.join(invalid)}")
    # return final synopsis
    return FileFormatDescription(format, read_args, size, avg_line_size)


def find_url_extension(url: str) -> str:
    """
    Find the extension of a filename or URL.
    """
    url = url or ""
    if "#" in url:
        url = url.split("#")[0]
    if "?" in url:
        url = url.split("?")[0]
    return os.path.splitext(url)[1].lower().strip(".")


def average_line_size(sample):
    """
    Calculate mean size of whole lines in sample.
    """
    if not sample:
        return
    line_sep = "\n" if isinstance(sample, str) else b"\n"
    lines = sample.split(line_sep)
    if len(lines) == 1:
        # no linefeeds at all >> guess that it is somewhat more than our sample size
        return len(sample) * 3 / 2 + 1
    n_lines = len(lines) - 1
    total_size = len(line_sep.join(lines[:-1]))
    return int(total_size + n_lines//2) // n_lines


def looks_like_csv(sample):
    """
    Detect fairly obvious CSV format.
    :returns:  Separator or None.
    """
    if not sample:
        return
    if isinstance(sample, str):
        eol = "\n"
        DELIMS = ((re.compile(r"\t"), "\t", 2), (re.compile(r","), ",", 2), (re.compile(r"\s+"), "\\s+", 3))
        ptn_single = PTN_SINGLE_COL_CSV
    else:
        eol = b"\n"
        DELIMS = ((re.compile(rb"\t"), "\t", 2), (re.compile(rb","), ",", 2), (re.compile(rb"\s+"), "\\s+", 3))
        ptn_single = PTN_SINGLE_COL_CSV_B
    lines = sample.split(eol)[:10]
    for splitter, sep, threshold in DELIMS:
        n_cols = []
        for line in lines:
            if line:
                n_cols.append(len(splitter.split(line)))
        if min(n_cols) != max(n_cols) or n_cols[0] < threshold:
            continue
        return sep
    if ptn_single.match(sample):
        return "\n"


def looks_like_json(sample, size: int=None):
    """
    Detect fairly obvious JSON format.
    """
    if not sample:
        return False
    if not isinstance(sample, str):
        try:
            sample = sample.decode("utf-8")
        except UnicodeDecodeError:
            # non-unicode >> assume not JSON
            return False
    sample = sample.strip()
    # JSON would always start with one of these
    if not sample.startswith("{") and not sample.startswith("["):
        return False
    # JSON cannot contain non-ascii characters
    if re.search(r'[^\x20-\x7F\r\t\n]', sample):
        return False
    # if we know the size and our sample goes to the end we can check that as well
    if size and len(sample) == size:
        if not sample.endswith("}") and not sample.endswith("]"):
            return False
    # looks like JSON, although it could still be a CSV with bracketed columns like "[col1], [col2]" for which
    #   we have an incomplete sample
    return True


def looks_like_hdf(sample):
    """
    HDF files always start with a specific byte sequence.
    """
    header = b'\x89\x48\x44\x46\x0d\x0a'
    if isinstance(sample, str):
        sample = sample.encode("utf-8", errors='ignore')
    return sample.startswith(header)


def looks_like_text_file(sample):
    """
    Detect a text file, i.e. any kind of file that is not binary.  Such files can be considered, as a fallback, to
    have a single column and no header.
    """
    if not isinstance(sample, str):
        try:
            sample = sample.decode("utf-8")
        except UnicodeDecodeError:
            # non-unicode >> assume not a text file
            return False
    if len(sample) > 10000 and "\n" not in sample:
        return False
    return True


def apply_csv_read_args(sample, read_args):
    """
    Analyze format of a CSV file.
    """
    if not sample:
        return
    if isinstance(sample, (bytes, bytearray)):
        sample = sample.decode("utf-8", errors="ignore")
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample, delimiters=",;| \t:")
    except csv.Error:
        if not alt_delimiter_detection(sample, read_args):
            read_args["delimiter"] = "\n"
            detect_headerless_csv(sample, read_args)
        return
    # leaving out: "lineterminator"
    for name, dflt in {"delimiter": None, "doublequote": None, "escapechar": None, "quotechar": '"', "quoting": 0,
              "skipinitialspace": False}.items():
        v = getattr(dialect, name)
        if v is not dflt:
            read_args[name] = v
    if read_args.get("delimiter") == " ":
        del read_args["delimiter"]
        read_args["delim_whitespace"] = True
    # special case: no delimiters at all
    detect_headerless_csv(sample, read_args)


def apply_json_read_args(sample, read_args):
    """
    Analyze format of JSON data.
    """
    if not sample:
        return
    if isinstance(sample, (bytes, bytearray)):
        sample = sample.decode("utf-8", errors="ignore")
    partial_line = not sample.endswith("\n")
    lines = [line.strip() for line in sample.strip().split("\n")]
    if partial_line and len(lines) > 2:
        lines = lines[:-1]
    # single JSON object or array per line
    if all(line.startswith("{") and line.endswith("}") for line in lines):
        read_args["lines"] = True
    if all(line.startswith("[") and line.endswith("[") for line in lines):
        read_args["lines"] = True


def alt_delimiter_detection(sample, read_args):
    """
    Sniffer doesn't always detect delimiters very well.
    """
    per_delim = defaultdict(list)
    delims = [(ptn, re.compile(ptn)) for ptn in (",", ";", "\t", r"\s+", "\\|")]
    lines = sample.split("\n")
    for line in lines:
        for delim, delim_ptn in delims:
            n_cols = len(delim_ptn.split(line))
            if n_cols > 1:
                per_delim[delim].append(n_cols)
    rankings = []
    import numpy
    for delim, counts in per_delim.items():
        if len(counts) < len(lines)/2:
            continue
        rankings.append((
            -numpy.std(counts),
            -len(counts),
            delim
        ))
    rankings.sort()
    if rankings:
        read_args["delimiter"] = rankings[0][2]
        return True
    return False


def detect_headerless_csv(sample, read_args):
    """
    Detect a CSV file with no header.
    """
    first_line = sample.split("\n")[0]
    delim = read_args.get("delimiter", ' ')
    if delim == ' ':
        cols = re.split(r'\s+', first_line)
    else:
        cols = first_line.split(delim)
    if all(map(lambda col: PTN_NOT_HEADER.match(col), cols)):
        read_args["header"] = None
        read_args["names"] = ["col_%d" % (n+1) for n in range(len(cols))]
