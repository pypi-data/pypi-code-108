"""
    CONFIG UTILITIES
        - classes that parse your config file, build a query iterable and yield queries
"""
import numpy as np
import pandas as pd
import yaml


def _prepare_chunked_dates(start_date: str, end_date: str, day_freq: int):
    """
    Split up dates in to multiple startDate, endDate pairs which are dayFreq apart
    args:
        start_date (str) : startDate of date range
        end_date (str) : endDate of date range
        day_freq (int)  : gap between startDate, endDate within each pairs
    return:
        dateRanges (list of dict)
    """
    dates = pd.Series(pd.date_range(start=start_date, end=end_date))
    date_freq = dates.groupby(np.arange(len(dates)) // day_freq).agg(["first", "last"])
    return (
        date_freq.rename(columns={"first": "startDate", "last": "endDate"})
        .astype(str)
        .to_dict("records")
    )


def _restructure_date_ranges(config):
    """
    Restructure dateRanges in to multiple pairs gapped by dayFreq
    args:
        config (dict): config file containing dayFreq, dateRanges keys
    return:
        config (dict)
    """
    # dynamic get kwargs or else set to default
    day_freq = config.pop("dayFreq", "1d")
    start_date = config.get("dateRanges", [])[0].get("startDate", None)
    end_date = config.get("dateRanges", [])[0].get("endDate", None)
    # restructure dateRanges
    date_ranges = _prepare_chunked_dates(start_date, end_date, day_freq)
    # update dateRanges in config
    config.update({"dateRanges": date_ranges})
    return config


# pylint: disable=invalid-name, unused-argument
def _generate_queries(
    viewIDs: list,
    queryConfig: list,
    dateRanges: list,
    pageSize: int = 10000,
    samplingLevel: str = "LARGE",
    **kwargs
):
    """
    Use the Analytics Service Object to query the
    Google Analytics Reporting API V4.
    args:
        viewIDs (list): list of google analytics view ids
        queryConfig (list): Google query config containing metrics, dimensions, etc.
        dateRanges (list): set of start & end dates.
        pageSize (int): (default: 10000) number of samples per pagination step
        samplingLevel (str): (default:LARGE) sampling level of the query
    yields:
        query generator of queries to run
    """
    # static variables
    for vid in viewIDs:
        for _, single_query in enumerate(queryConfig):
            for date_range in dateRanges:
                print("creating a [fields] query")
                fields = {
                    "viewId": vid,
                    "dateRanges": date_range,
                    **single_query,
                    "samplingLevel": samplingLevel,
                    "pageSize": pageSize,
                }
                # building similar queries per vid
                yield [fields]


def _parser(file_name):
    """Parse config in to dictionary"""
    # load config
    with open(file_name, "r") as file_:
        return yaml.safe_load(file_)


class GAConfigManager:
    """
    Class that parses config .yaml for queries, reader, writer
    Uses these configs to build required query objects.
    """

    def __init__(self, file_name):
        # load config
        self.config = _parser(file_name=file_name)
        if self.config.pop("chunk_date_range", False):
            self.config = _restructure_date_ranges(self.config)
        # get query generator
        self.query_gen, self.additional_args = self._builder(self.config)

    def _builder(self, config):
        """Config builder method to generate query configs"""
        additional_args = {}
        # get metadata
        metadata = {
            "dateRanges": self.config.get("dateRanges", None),
            "samplingLevel": self.config.get("samplingLevel", None),
            "pageSize": self.config.get("pageSize", None),
        }
        additional_args.update({"metadata": metadata})
        return _generate_queries(**config), additional_args

    def get_query(self):
        """Get a Generator for the queries to be executed"""
        return self.query_gen

    def get_additional_args(self):
        """Getter method to get additional arguments"""
        return self.additional_args
