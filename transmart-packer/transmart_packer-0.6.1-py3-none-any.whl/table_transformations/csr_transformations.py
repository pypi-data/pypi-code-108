import re
from typing import List, Dict, Any, Optional

import pandas
from pandas import DataFrame
import numpy
import logging

from packer.table_transformations.utils import get_index_of_string_prefix

logger = logging.getLogger(__name__)
try:
    from transmart.api.v2.data_structures import ObservationSet
except ImportError as e:
    logging.warning(f'Import errors for {__file__!r}: {str(e)}')

DATE_FORMAT = '%Y-%m-%d'
MULTI_VALUE_SEPARATOR = ';'
SUBJECT_ID_FIELD = 'patient.subjectIds.SUBJ_ID'
ID_COLUMN_MAPPING = {SUBJECT_ID_FIELD: 'Subject Id',
                     'Diagnosis': 'Diagnosis Id',
                     'Biosource': 'Biosource Id',
                     'Biomaterial': 'Biomaterial Id',
                     'Radiology': 'Radiology Id',
                     'Study': 'Study Id',
                     }
ID_COLUMNS = ID_COLUMN_MAPPING.values()
COLUMN_ORDER_BY_CONCEPT_CODE_PREFIX = ['Individual'] + list(ID_COLUMN_MAPPING.keys())[1:]


def get_id_columns(df: DataFrame) -> List[str]:
    return [column for column in ID_COLUMNS if column in set(df.columns)]


def from_obs_json_to_export_csr_df(obs_json: Dict) -> DataFrame:
    """
    :param obs_json: json returned by transmart v2/observations call
    :return: data frame that has 4 (subject, diagnosis, biosource, biomaterial) index columns.
    The rest of columns represent concepts (aka variables)
    """
    df = ObservationSet(obs_json).dataframe
    df = transform_obs_df(df)
    return df


def transform_obs_df(df: DataFrame) -> DataFrame:
    concept_pat_to_name = _concept_path_to_name(df)
    # Transform sample data and data outside of the sample hierarchy (study, radiology) separately
    sample_df = df
    study_df = None
    radiology_df = None

    # Split Sample data and Radiology data
    if 'Radiology' in df.columns:
        sample_df = df[df['Radiology'].isnull()]
        sample_df.drop(columns=['Radiology'], inplace=True)
        radiology_df = df[df['Radiology'].notnull()]
        non_radiology_columns = [c for c in ID_COLUMN_MAPPING.keys() - [SUBJECT_ID_FIELD, 'Diagnosis', 'Radiology'] if
                                 c in df.columns]
        radiology_df.drop(columns=non_radiology_columns, inplace=True)

    # Split Sample data and Study data
    if 'Study' in df.columns:
        df = sample_df
        sample_df = df[df['Study'].isnull()]
        sample_df.drop(columns=['Study'], inplace=True)
        study_df = df[df['Study'].notnull()]
        non_study_columns = [c for c in ID_COLUMN_MAPPING.keys() - [SUBJECT_ID_FIELD, 'Study'] if c in df.columns]
        study_df.drop(columns=non_study_columns, inplace=True)

    # Transform sample data
    df = from_obs_df_to_csr_df(sample_df)

    # Transform Radiology data and merge back with Sample data
    if radiology_df is not None:
        empty_diagnosis_in_sample_df = 'Diagnosis Id' in df.index.names \
                                and all(x == '' for x in df.copy().reset_index()['Diagnosis Id'].values)
        if 'Diagnosis Id' not in df.index.names or empty_diagnosis_in_sample_df:
            df = merge_non_hierarchical_entity_df(df, radiology_df, 'Radiology Id', ['Subject Id'])
            # If diagnosis-related concepts are not part of sample data, Diagnosis ID column should not be included in results
            if empty_diagnosis_in_sample_df is True:
                df.drop(columns=['Diagnosis Id'], inplace=True)
            df.set_index(get_id_columns(df), inplace=True)
        else:
            df = merge_non_hierarchical_entity_df(df, radiology_df, 'Radiology Id', ['Subject Id', 'Diagnosis Id'])
            df.set_index(get_id_columns(df), inplace=True)

    # Transform Study data and merge back with Sample data
    if study_df is not None:
        df = merge_non_hierarchical_entity_df(df, study_df, 'Study Id', ['Subject Id'])
        df.set_index(get_id_columns(df), inplace=True)

    df = df.rename(index=str, columns=concept_pat_to_name)
    df = format_columns(df)
    return df


def merge_non_hierarchical_entity_df(df: DataFrame, entity_df: Optional[DataFrame], id_column: str, merge_columns: List[str]) -> DataFrame:
    entity_df = from_obs_df_to_csr_df(entity_df)
    if df.empty:
        df = entity_df
        df.reset_index(inplace=True)
        return df

    # Merge non-hierarchical entity data into df, creating a cross-product
    entity_df[id_column] = entity_df.index.get_level_values(id_column)
    return df.reset_index().merge(entity_df, on=merge_columns, how='outer').fillna('')


def from_obs_df_to_csr_df(obs: DataFrame) -> DataFrame:
    if obs.empty:
        logger.warning('Hypercube is empty! Returning empty result.')
        return obs
    # Rename the identifier columns
    obs.rename(index=str, columns=ID_COLUMN_MAPPING, inplace=True)

    # Sort rows to group them by concept and sort each alphabetically by concept name
    obs['order'] = obs['concept.conceptCode'].map(
        lambda x: get_index_of_string_prefix(x, COLUMN_ORDER_BY_CONCEPT_CODE_PREFIX))
    obs.sort_values(['order', 'concept.name'], ascending=[True, True], inplace=True)
    obs.drop('order', axis='columns', inplace=True)

    # Sort data by concept code prefix order and concept path, compute the list concepts for the column headers
    concept_path_col = obs['concept.conceptPath']
    unq_concept_paths_ord = concept_path_col.unique().tolist()
    logger.info('Reformatting columns...')
    id_columns = get_id_columns(obs)
    obs = _reformat_columns(obs, id_columns)
    # Transform concept rows to column headers
    obs_pivot = _concepts_row_to_columns(obs)
    # Propagate data to lower levels and display only rows that represent the lowest level,
    # e.g., add subject-level data to diagnosis rows and remove the subject-level row
    obs_pivot = _merge_redundant_rows(obs_pivot, id_columns)
    # Set columns order to identifiers first and then concepts
    obs_pivot = obs_pivot[id_columns + unq_concept_paths_ord]
    # Replace NAs and NANs in index columns with empty string
    for id_column in id_columns:
        obs_pivot[id_column] = obs_pivot[id_column].fillna('')
    obs_pivot.set_index(id_columns, inplace=True)
    return obs_pivot


def _concept_path_to_name(df: DataFrame) -> dict:
    return dict(zip(df['concept.conceptPath'], df['concept.name']))


def format_columns(df: DataFrame) -> DataFrame:
    """
    :param df: pandas dataframe with various data types of columns
    :return: modified data frame with all columns converted to formatted string
    """
    result_df = DataFrame()
    for col_num, col in enumerate(df.columns):
        # update datetime fields
        if re.match(r'.*\bdate\b.*', col, flags=re.IGNORECASE):
            result_df[col_num] = df.iloc[:, col_num].apply(_to_datetime)
        elif numpy.issubdtype(df.iloc[:, col_num].dtype, numpy.number):
            result_df[col_num] = df.iloc[:, col_num].apply(_num_to_str)
        else:
            result_df[col_num] = df.iloc[:, col_num]
    result_df = result_df.fillna('')
    result_df.columns = df.columns
    return result_df


def _num_to_str(x):
    if pandas.isnull(x):
        return ''
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def _merge_redundant_rows(data: DataFrame, id_columns: List[str]) -> DataFrame:
    if data.empty:
        return data
    # sort rows by identifying columns, merging of rows strongly depends on sorting
    rows = data.sort_values(id_columns, na_position='last').to_dict('records')
    result_rows = [rows[0]]
    for row in rows[1:]:
        row_copied = False
        for result_row in reversed(result_rows):
            if _is_ancestor_row(row, result_row, id_columns):
                _propagate_value_to_descendant_row(row, result_row, id_columns)
                row_copied = True
            else:
                break
        if not row_copied:
            result_rows.append(row)
    return DataFrame(result_rows)


def _is_ancestor_row(ancestor_row_candidate: Dict[str, Any],
                     row: Dict[str, Any],
                     id_columns: List[str]) -> bool:
    """
    Checks if the identifier values of the row equal the identifier values
    of the candidate ancestor row, ignoring missing values in the ancestor.
    E.g., {SubjectId: 1, DiagnosisId: None} is an ancestor of {SubjectId: 1, DiagnosisId: 3},
      {SubjectId: 1, DiagnosisId: None, BiosourceId: None} is an ancestor of
      {SubjectId: 1, DiagnosisId: None, BiosourceId: 5}.
    :param ancestor_row_candidate: the row to check if it is an ancestor
    :param row: the row to compare against, which should be more specific but not conflicting with the ancestor
    :param id_columns: the id columns to compare (in order)
    :return: true iff the ancestor_row_candidate is an ancestor of the row.
    """
    for id_column in id_columns:
        if pandas.isnull(ancestor_row_candidate[id_column]):
            continue
        if ancestor_row_candidate[id_column] != row[id_column]:
            return False
    return True


def _propagate_value_to_descendant_row(ancestor_row, descendant_row, id_columns: List[str]):
    for column, value in ancestor_row.items():
        if column in id_columns or pandas.isnull(value):
            # skip
            continue
        if column not in descendant_row or pandas.isnull(descendant_row[column]):
            # copy missing value
            descendant_row[column] = value
        elif column in descendant_row and (value not in descendant_row[column].split(MULTI_VALUE_SEPARATOR)):
            # merge different values with separator
            descendant_row[column] = descendant_row[column] + MULTI_VALUE_SEPARATOR + value


def _to_datetime(date_str, string_format=DATE_FORMAT):
    if pandas.notnull(date_str) and date_str is not None and date_str != '':
        try:
            return pandas.to_datetime(date_str).strftime(string_format)
        except:
            return date_str
    else:
        return date_str


def _reformat_columns(obs, id_columns: List[str]):
    # rename columns and set indexes
    obs.reset_index(inplace=True)
    headers = id_columns + ['concept.conceptPath']

    # prepare 'value' column
    if {'stringValue', 'numericValue'}.issubset(obs.columns):
        # merge stringValue and numericValue into value column
        obs['value'] = obs['stringValue'].fillna(obs['numericValue'])
        obs.drop(['stringValue', 'numericValue'], axis=1, inplace=True)
    elif 'stringValue' in obs:
        obs.rename(columns={"stringValue": "value"}, inplace=True)
    elif 'numericValue' in obs:
        obs.rename(columns={"numericValue": "value"}, inplace=True)
    else:
        obs['value'] = ''
    obs = obs.set_index(headers, append=True)[['value']]
    return obs


def _concepts_row_to_columns(obs: DataFrame) -> DataFrame:
    # use unstack to move the last level of the index to column names
    obs_pivot = obs.unstack(level=-1)
    # update column names by dropping value level
    obs_pivot.columns = obs_pivot.columns.droplevel(level=0)
    # fix indexes
    obs_pivot.reset_index(inplace=True)
    obs_pivot.drop(obs_pivot.columns[[0]], axis=1, inplace=True)
    return obs_pivot
