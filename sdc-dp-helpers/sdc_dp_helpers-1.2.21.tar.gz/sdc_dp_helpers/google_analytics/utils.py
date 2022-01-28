"""
    utils functions
"""
import yaml


def init_config(file_name: str = "./example.yaml"):
    """
    Util method that creates an example config at the given file_name
    args:
        file_name (str): full path to config YAML file
    """
    config = {
        "dateRanges": [{"startDate": "2020-02-01", "endDate": "2020-02-01"}],
        "samplingLevel": "LARGE",
        "pageSize": 100,
        "chunk_date_range": True,
        "dayFreq": 1,
        "viewIDs": ["<add client viewID here>"],
        "queryConfig": [
            {
                "metrics": [{"expression": "ga:sessions", "alias": "sessions"}],
                "dimensions": [
                    {"name": "ga:date"},
                    {"name": "ga:medium"},
                    {"name": "ga:source"},
                    {"name": "ga:keyword"},
                    {"name": "ga:hostname"},
                    {"name": "ga:deviceCategory"},
                ],
                "orderBys": [{"fieldName": "ga:date", "sortOrder": "DESCENDING"}],
            }
        ],
    }

    # write to file
    with open(file_name, "w") as file_:
        yaml.dump(config, file_)
