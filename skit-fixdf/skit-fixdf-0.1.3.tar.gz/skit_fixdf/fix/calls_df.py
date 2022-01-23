import json
import os
import tempfile
from typing import List, Optional

import pandas as pd
from loguru import logger
from tqdm import tqdm

from skit_fixdf import constants as const
from skit_fixdf.fix.df import (
    duplicate_columns,
    fix_datetime,
    min_json_whitespace,
    read_df,
    remove_columns,
    remove_rows,
    rename_columns,
    reorder_cols,
)


def add_entities_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create entities column from prediction column.

    :param df: Dataframe.
    :return: Dataframe.
    """
    if const.PREDICTION not in df.columns:
        return df

    df[const.ENTITIES] = None

    for i, value in tqdm(
        df.prediction.iteritems(),
        total=len(df),
        desc="Extract predicted entities into a separate column.",
    ):
        entities = []
        if not isinstance(value, str):
            df.at[i, const.ENTITIES] = json.dumps(entities, ensure_ascii=False)
            continue
        prediction = json.loads(value)
        intents = prediction.get(const.INTENTS, [])
        for intent in intents:
            for slot in intent.get(const.SLOTS, []):
                for entity_value in slot.get(const.VALUES, []):
                    entity = {
                        const.TEXT: entity_value.get(const.BODY),
                        const.TYPE: entity_value.get(const.TYPE)
                        or entity_value.get(const.ENTITY_TYPE)
                        or entity_value.get(const.TRANSCRIPTION),
                        const.SCORE: entity_value.get(const.SCORE, 0),
                        const.VALUE: entity_value.get(const.VALUE),
                    }
                    entities.append(entity)
        df.at[i, const.ENTITIES] = json.dumps(entities, ensure_ascii=False)
    return df


def add_state_transitions_col(
    df: pd.DataFrame, transition_token: str = "->"
) -> pd.DataFrame:
    """
    Create state_transitions_col from states.

    :param df: Source df with states
    :type df: pd.DataFrame
    :return: df with state transitions
    :rtype: pd.DataFrame
    """
    df[const.STATE_TRANSITIONS] = None

    if const.CALL_UUID not in df.columns:
        return df

    if const.STATE not in df.columns:
        return df

    unique_call_ids = df[const.CALL_UUID].unique()
    for call_id in tqdm(
        unique_call_ids, desc="Extract state transitions into a separate column."
    ):
        call_slice = df[df[const.CALL_UUID] == call_id]
        states = call_slice[const.STATE].values
        df.at[call_slice.index, const.STATE_TRANSITIONS] = transition_token.join(states)
    return df


def add_asr_provider_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add asr_provider column to dataframe.

    :param df: Source df with metadata column.
    :type df: pd.DataFrame
    :return: df with asr_provider column
    :rtype: pd.DataFrame
    """
    df[const.ASR_PROVIDER] = None

    if const.METADATA not in df.columns:
        return df

    for i, value in tqdm(
        df.metadata.iteritems(),
        total=len(df),
        desc="Extract asr_provider into a separate column.",
    ):
        value = json.loads(value)
        df.at[i, const.ASR_PROVIDER] = value.get(const.ASR_PROVIDER)
    return df


def add_utterances_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add utterances column to dataframe.

    :param df: Source df with debug_metadata column.
    :type df: pd.DataFrame
    :return: df with utterances column
    :rtype: pd.DataFrame
    """
    df[const.UTTERANCES] = None

    if const.DEBUG_METADATA not in df.columns:
        return df

    for i, value in tqdm(
        df.debug_metadata.iteritems(),
        total=len(df),
        desc="Extract utterances into a separate column.",
    ):
        value = json.loads(value)
        utterances = value.get(const.PLUTE_REQUEST, {}).get(const.ALTERNATIVES, [])
        df.at[i, const.UTTERANCES] = json.dumps(utterances, ensure_ascii=False)
    return df


def prepare_call_df_for_tagging(df_path: str, output_path: Optional[str] = None) -> str:
    """
    Prepare call df for tagging.

    :param df_path: Path where the calls df exists.
    :return: Dataframe.
    :rtype: pd.DataFrame
    """
    df = read_df(df_path)
    logger.debug(f"Read df from {df_path=} of shape={df.shape}")

    df = remove_rows(
        df, [const.SUB_TYPE], const.SUPPORTED_SUB_TYPES(df[const.SUB_TYPE].unique())
    )
    logger.debug(f"After removing selected rows {df.shape}")

    df = duplicate_columns(df, [(const.PREDICTED_INTENT, const.INTENT)])
    logger.debug(f"After duplicating columns {df.shape}")

    df = fix_datetime(df, [const.CREATED_AT])
    logger.debug(f"Fixed datetime {df.shape}")

    df = rename_columns(
        df,
        {
            const.CREATED_AT: const.REFTIME,
            const.VIVA_CALL_DURATION: const.CALL_DURATION,
        },
    )
    df = add_entities_col(df)
    df = add_state_transitions_col(df)
    df = add_asr_provider_col(df)
    df = add_utterances_col(df)
    df = min_json_whitespace(
        df,
        [
            const.METADATA,
            const.ENTITIES,
            const.UTTERANCES,
            const.PREDICTION,
        ],
    )
    df = remove_columns(df, required=const.REQUIRED_COLS)
    df = reorder_cols(df, const.REQUIRED_COLS)

    if not output_path:
        input_file_dir, input_file_name = os.path.split(df_path)
        input_file_name, input_file_ext = os.path.splitext(input_file_name)
        _, output_path = tempfile.mkstemp(
            dir=input_file_dir, prefix=f"{input_file_name}-", suffix=input_file_ext
        )

    df.to_csv(output_path, index=False)
    return output_path
