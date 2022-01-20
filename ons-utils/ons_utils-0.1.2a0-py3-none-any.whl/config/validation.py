"""Validation functions for scenario config files.

Provides:

* :cls:`ConfigValidationError`
* :func:`validate_scan_scenario_config`
* :func:`validate_webscraped_scenario_config`

Both functions return an error message that can be used to raise an
exception. The intention is that the messages from all scenario configs
will be combined before being raised.
"""
from functools import lru_cache
import logging
import os
from typing import Dict, Sequence, Mapping, Union, Hashable, Optional, Tuple

import cerberus
from flatten_dict import flatten
from pyspark.sql import SparkSession

from ons_utils.generic import is_non_string_sequence


Sections = Sequence[Union[str, Tuple[str]]]


# def full_schema(sections: Sequence[str]) -> Dict[str, Dict]:
#     """Return the full schema for the given sections."""
#     schema = non_section_schema()
#     schema.update(consumption_segment_mappers_schema())
#     schema.update({
#         k: v for k, v in schema_sections().items()
#         if k in sections
#     })
#     return schema


# def schema_sections() -> Dict[str, Dict]:
#     """Return a schema with all the sections."""
#     section_schemas = {
#         'preprocessing': preprocessing_schema(),
#         'relaunch_linking': relaunch_linking_schema(),
#         'outlier_detection': outlier_detection_schema(),
#         'averaging': averaging_schema(),
#         'grouping': grouping_schema(),
#         'flag_low_expenditures': flag_low_expenditures_schema(),
#         'indices': indices_schema(),
#     }
#     # For nested schema, needs 'type' and 'schema'.
#     return {
#         section: {
#             'type': 'dict',
#             'required': True,
#             'schema': schema,
#         }
#         for section, schema in section_schemas.items()
#     }



class ConfigValidationError(Exception):
    """Error for Config Validation."""


# def validate_scan_scenario_config(
#     config,
#     spark: Optional[SparkSession] = None,
# ) -> str:
#     """Validate the config using required sections for scanner.

#     Parameters
#     ----------
#     config : Config
#         An instance of the Config object defined in
#         :mod:`cprices.config`. Haven't imported for type hint due to
#         co-dependency causing an issue.
#     spark : SparkSession
#        Used to validate Hive table existence.

#     Returns
#     -------
#     str
#         An error message with all validation errors. Returns an empty
#         string if no errors.
#     """
#     return get_all_errors(
#         config,
#         sections=[
#             # 'input_data',
#             'preprocessing',
#             'relaunch_linking',
#             'outlier_detection',
#             'averaging',
#             'flag_low_expenditures',
#             'indices',
#         ],
#         hive_table_sections=[
#             'consumption_segment_mappers',
#             ('relaunch_linking', 'mappers'),
#         ],
#         spark=spark,
#     )


def validate_webscraped_scenario_config(
    config,
    spark: Optional[SparkSession] = None,
) -> str:
    """Validate the config using required sections for web scraped.

    Parameters
    ----------
    config : Config
        An instance of the Config object defined in
        :mod:`cprices.config`. Haven't imported for type hint due to
        co-dependency causing an issue.
    spark : SparkSession
        Used to validate Hive table existence.

    Returns
    -------
    str
        An error message with all validation errors. Returns an empty
        string if no errors.
    """
    return get_all_errors(
        config,
        sections=[
            # 'input_data',
            'preprocessing',
            'outlier_detection',
            'averaging',
            'grouping',
            'indices',
        ],
        hive_table_sections=[
            'consumption_segment_mappers',
            ('grouping', 'mappers'),
        ],
        spark=spark,
    )


def get_all_errors(
    config,
    sections: Sequence[str],
    hdfs_file_sections: Optional[Sections] = None,
    hive_table_sections: Optional[Sections] = None,
    spark: Optional[SparkSession] = None,
) -> str:
    """Combine cerberus and mapper error messages.

    Parameters
    ----------
    config : Config
        An instance of the Config object defined in
        :mod:`cprices.config`. Haven't imported for type hint due to
        co-dependency causing an issue.
    sections : sequence of str
        List of config sections to build the full schema. Schema
        sections must be defined in :mod:`cprices.validation_schemas`.
    hdfs_file_sections : sequence of (str or tuple of str), optional
        List of config sections that contain a mapping of label -> HDFS
        filepath. Checks for file existence. Nested sections of
        arbitrary depth can be checked if passed as a tuple (section,
        inner_section).
    hive_table_sections : sequence of (str or tuple of str), optional
        List of config sections that contain a mapping of label ->
        database_name.table_name. Checks for table existence. Nested
        sections of arbitrary depth can be checked if passed as a tuple
        (section, inner_section).
    spark : SparkSession, optional
        Used to validate Hive table existence.

    Returns
    -------
    str
        A single string of all errors, including cerberus errors on
        standard config sections, and filepath/table existence errors
        for any HDFS files or Hive tables.
    """
    if hive_table_sections and not spark:
        raise ValueError(
            "a spark session needs to be passed to spark if"
            " hive_table_sections is passed"
        )
    # Get section errors.
    schema = full_schema(sections)
    err_msgs = get_cerberus_errors(vars(config), schema)

    if hdfs_file_sections:
        err_msgs += get_hdfs_filepath_errors(config, hdfs_file_sections)
    if hive_table_sections:
        err_msgs += get_hive_table_errors(spark, config, hive_table_sections)

    # Get header.
    if err_msgs:
        header = get_underlined_header(
            f"Validation errors for config {config.name}"
        )
        err_msgs = ['\n' + header] + err_msgs

    # Combine.
    return '\n'.join(err_msgs)


def get_cerberus_errors(config: Mapping, schema: Mapping) -> Sequence[str]:
    """Validate the config using the cerberus schema and output errors."""
    v = cerberus.Validator(schema, allow_unknown=True)

    err_msgs = []
    if not v.validate(config):
        # Get the errors in a suitable format.
        errs = flatten(remove_list_wrappers(v.errors), reducer='dot')
        for param, msg in errs.items():
            err_msgs.append(f"parameter {param}: {msg}")

    return err_msgs


def get_hdfs_filepath_errors(config, sections: Sections) -> Sequence[str]:
    """Validate that the HDFS filepaths exist and output error messages."""
    # Get mapper errors.
    mapper_err_msgs = []
    for section in sections:
        if is_non_string_sequence(section):
            to_validate = get_inner(config, section)
        else:
            to_validate = getattr(config, section)

        err_msgs = validate_hdfs_filepaths(to_validate)
        if err_msgs:
            mapper_err_msgs.append(
                "\n".join(['\n' + section + ' errors:'] + err_msgs)
            )

    return mapper_err_msgs


def get_hive_table_errors(
    spark: SparkSession,
    config,
    sections: Sections,
) -> Sequence[str]:
    """Validate that the Hive tables exist and output error messages."""
    hive_table_err_msgs = []
    for section in sections:
        if is_non_string_sequence(section):
            switch = getattr(config, section[0]).get('active')
            if switch is not None and switch is False:
                continue

            to_validate = get_inner(config, section)
            section = '.'.join(section)
        else:
            switch = getattr(config, section).get('active')
            if switch is not None and switch is False:
                continue

            to_validate = getattr(config, section)
        err_msgs = validate_hive_tables(spark, to_validate)
        if err_msgs:
            hive_table_err_msgs.append(
                "\n".join(['\n' + section + ' errors:'] + err_msgs)
            )

    return hive_table_err_msgs


def get_inner(config, section: Sections):
    """Recursive function to get the inner section for validation."""
    section, inner = section
    if is_non_string_sequence(inner):
        return get_inner(inner)
    return getattr(config, section)[inner]


def validate_hive_tables(
    spark: SparkSession,
    tables: Mapping[Hashable, str],
) -> Sequence[str]:
    """Validate a dict of Hive tables and output resulting errors."""
    err_msgs = []
    for key, table_spec in flatten(tables).items():
        # The table spec is in the format database_name.table_name, so
        # need to split on the period.
        if not hive_table_exists(spark, *table_spec.split('.')):
            err_msgs.append(
                f"{key}: table at {table_spec} does not exist."
            )

    return err_msgs


def validate_hdfs_filepaths(
    filepaths: Mapping[Hashable, str]
) -> Sequence[str]:
    """Validate a dict of filepaths and output resulting errors."""
    err_msgs = []
    logger = logging.getLogger()

    for key, path in flatten(filepaths).items():
        if not file_exists_on_hdfs(path):
            err_msgs.append(
                f"{key}: file at {path} does not exist."
            )

    logger.debug(file_exists_on_hdfs.cache_info())
    return err_msgs


@lru_cache(maxsize=32)
def file_exists_on_hdfs(path: str) -> bool:
    return hdfs.path.isfile(path)


def hive_table_exists(spark, database: str, table: str) -> bool:
    """Checks the Spark catalog and returns True if a table exists."""
    return spark._jsparkSession.catalog().tableExists(database, table)


def get_underlined_header(header: str, char: str = '-') -> str:
    """Underline the header with given char."""
    underline = char * len(header)
    return '\n'.join([header, underline])


def remove_list_wrappers(
    d: Mapping[str, Union[Sequence[str], Sequence[Mapping]]],
) -> Dict[str, Union[str, Dict]]:
    """Remove list wrappers from dict values recursively.

    The output from cerberus.errors is a dict with the
    values wrapped in a list. This outputs a nested dict.
    """
    new_d = {}
    for k, v in d.items():
        # Access first element in list.
        v = v[0]
        if isinstance(v, dict):
            # Remove list wrappers from the inner dicts too.
            new_d.update({k: remove_list_wrappers(v)})
        else:
            new_d.update({k: v})

    return new_d


if __name__ == "__main__":
    from pyspark.sql import SparkSession
    spark = (
        SparkSession.builder.appName('test-small')
        .config("spark.executor.memory", "1g")
        .config("spark.executor.cores", 1)
        .config("spark.dynamicAllocation.enabled", "true")
        .config("spark.dynamicAllocation.maxExecutors", 3)
        .config("spark.sql.shuffle.partitions", 12)
        .config("spark.shuffle.service.enabled", "true")
        .config("spark.ui.showConsoleProgress", "false")
        .config('spark.executorEnv.ARROW_PRE_0_15_IPC_FORMAT', 1)
        .config('spark.workerEnv.ARROW_PRE_0_15_IPC_FORMAT', 1)
        .enableHiveSupport()
        .getOrCreate()
    )
    from cprices.config import ScanScenarioConfig, WebScrapedScenarioConfig
    sc_config = ScanScenarioConfig('scenario_scan', subdir='scanner')
    print(validate_scan_scenario_config(sc_config, spark))

    sc_config = WebScrapedScenarioConfig('scenario_web', subdir='web_scraped')
    print(validate_webscraped_scenario_config(sc_config, spark))
