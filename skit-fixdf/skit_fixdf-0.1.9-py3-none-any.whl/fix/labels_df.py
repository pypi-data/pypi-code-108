import json
import os
import re
import tempfile
from datetime import datetime
from typing import List, Optional

import pandas as pd
import pytz
import requests
from tqdm import tqdm

from skit_fixdf import constants as const
from skit_fixdf import fix


def make_intent_label_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make intent label df.
    :param df: Dataframe.
    :return: Dataframe.
    :rtype: pd.DataFrame
    """
    df = df[[const.ID, const.TAG]].copy()
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Make intent label df."):
        tag_objects = json.loads(row[const.TAG])
        tags = [tag[const.TYPE] for tag in tag_objects]
        if tags:
            head, _ = tags[0], tags[1:]
            df.at[i, const.INTENT] = head
    return df[[const.ID, const.INTENT]]


# ==========================================================================================
# TODO: This section should be deprecated.
# We are adding it here temporarily because of problems with the tagging interface.
# Once True values are available on the interface, we will let this go.
# Not focusing on code quality for the same reason.

# @deprecate
def detect_language(line):
    line = re.sub(r"[^a-zA-Z\u0900-\u097F]+", " ", line)
    maxchar = max(line)
    if "\u0900" <= maxchar <= "\u097f":
        return "hi"
    elif "a" <= maxchar <= "z":
        return "en"
    return None


# @deprecate
def get_entities_from_duckling(
    duckling_url: str,
    text: str,
    lang: str,
    reftime: int,
    type_: str,
    duckling_token: Optional[str] = None,
):
    if not text or not lang:
        return None

    headers = {"Authorization": f"Bearer {duckling_token}"} if duckling_token else {}

    timezone = "Asia/Kolkata"  # Should be UTC but this is needed internally.
    # Not fixing because this function isn't required.

    payload = {
        const.TEXT: text,
        const.LOCALE: f"{lang}_IN",  # this piece is otherwise problematic (hardcoded "IN")
        # but we want to let go of this function altogether.
        const.TIMEZONE: timezone,
        const.DIMS: json.dumps([type_]),
        const.REFTIME: reftime,
        const.LATENT: False,
    }

    timezone = pytz.timezone(timezone)
    value = None
    response = requests.post(
        duckling_url,
        data=payload,
        headers=headers,
        timeout=5,
    )

    if response.status_code == 200:
        entities_list = response.json()
        if entities_list:
            entity = entities_list[0]
            value_store = entity.get(const.VALUE, {})
            if const.VALUE in value_store:
                value = value_store[const.VALUE]
            elif const.FROM in value_store and const.TO in value_store:
                value = {
                    const.FROM: value_store.get(const.FROM),
                    const.TO: value_store.get(const.TO),
                }
            elif const.FROM in value_store:
                value = {const.FROM: value_store.get(const.FROM)}
            elif const.TO in value_store:
                value = {const.TO: value_store.get(const.TO)}

            if entity[const.DIM] == const.DURATION:
                normalized_value = entity.get(const.VALUE, {}).get(const.NORMALIZED, {})
                if normalized_value.get(const.UNIT) == const.SECOND:
                    value = reftime + normalized_value.get(const.VALUE)
                    try:
                        value = datetime.fromtimestamp(value / 1000, timezone)
                        value = value.isoformat()
                    except ValueError:
                        value = None
    return value


# @deprecate
def make_entity_label_df(
    df: pd.DataFrame, duckling_url: str, duckling_token: Optional[str] = None
) -> pd.DataFrame:
    """
    Make entity label df.
    :param df: Dataframe.
    :return: Dataframe.
    :rtype: pd.DataFrame
    """
    df = df[[const.ID, const.TAG, const.LANGUAGE_CODE, const.REFTIME]].copy()
    for i, row in tqdm(
        df.iterrows(), total=len(df), desc="making duckling hits to get entity values."
    ):
        tags = json.loads(row[const.TAG])
        evaluated_tags = []
        for tag in tags:
            if not tag[const.TYPE] or not tag[const.TEXT]:
                continue
            type_ = None
            value = None
            if tag[const.TYPE].lower() in const.SUPPORTED_ENTITIES:
                type_ = tag[const.TYPE].lower()
                reftime = row[const.REFTIME]
                timestamp = datetime.fromisoformat(reftime).timestamp()
                unix_epoch = int(timestamp * 1000)
                language_code = (
                    row[const.LANGUAGE_CODE]
                    if not pd.isna(row[const.LANGUAGE_CODE])
                    else detect_language(tag[const.TEXT])
                )
                value = get_entities_from_duckling(
                    duckling_url,
                    tag[const.TEXT],
                    language_code,
                    unix_epoch,
                    tag[const.TYPE],
                    duckling_token=duckling_token,
                )
            else:
                type_ = tag[const.TYPE]
                value = tag[const.TEXT]

            if type_ and value:
                evaluated_tags.append(
                    {
                        const.TEXT: tag[const.TEXT],
                        const.TYPE: type_,
                        const.SCORE: tag.get(const.SCORE, 0),
                        const.VALUE: value,
                    }
                )
        df.at[i, const.ENTITIES] = json.dumps(evaluated_tags, ensure_ascii=False)
    return df[[const.ID, const.ENTITIES]]


# The above section is set for deprecation.
# ==========================================================================================


def make_transcription_label_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Make transcription label df.

    :param df: Dataframe.
    :return: Dataframe.
    :rtype: pd.DataFrame
    """
    df = df[[const.ID, const.TAG]].copy()
    df[const.TRANSCRIPTION] = df[const.TAG].apply(
        lambda tag: json.loads(tag).get(const.TEXT) if isinstance(tag, str) else None
    )
    return df[[const.ID, const.TRANSCRIPTION]]


def add_columns_from_metadata(
    df: pd.DataFrame, columns: List[str], key: str = const.DATA, fn: callable = None
) -> pd.DataFrame:
    """
    Extract value of key in separate columns.

    :param df: Dataframe.
    :return: Dataframe.
    :rtype: pd.DataFrame
    """
    if key not in df.columns:
        return df
    for i, row in tqdm(
        df.iterrows(), total=len(df), desc=f"Add values from json column {key=}."
    ):
        raw_data = fn(row[key]) if fn else row[key]
        for col in columns:
            if isinstance(col, tuple):
                from_col, to_col = col
            else:
                from_col = to_col = col

            df.loc[i, to_col] = None
            if isinstance(raw_data, dict):
                value = raw_data.get(from_col)
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, indent=0)
            else:
                value = None
            df.loc[i, to_col] = value
    return df


def prepare_tagged_df_for_training(
    df_path: str,
    dataset_type: str,
    output_path: Optional[str] = None,
    duckling_url: Optional[str] = None,
    duckling_token: Optional[str] = None,
    delete_file: bool = False,
) -> str:
    """
    Prepare tagged df for training on dialogy.

    :param df_path: Path where tagged dataset exists.
    :type df_path: str
    :return: Dialogy compatible dataset.
    :rtype: pd.DataFrame
    """
    if dataset_type == const.DATASET_TYPE__ENTITY and not duckling_url:
        raise ValueError(
            f"duckling url is required for processing {dataset_type} dataset."
            " Refer to https://github.com/skit-ai/skit-auth for more details."
        )

    df = fix.df.read_df(df_path)
    df = add_columns_from_metadata(
        df,
        const.LABEL_COLS_FROM_METADATA,
        fn=lambda x: json.loads(x) if not pd.isna(x) else dict,
    )
    df = add_columns_from_metadata(
        df,
        [(const.NAME, const.INTENT)],
        key=const.PREDICTION,
        fn=lambda x: json.loads(x) if not pd.isna(x) else dict,
    )

    df = fix.df.json_loads(df, columns=[const.ALTERNATIVES])
    df = fix.df.fix_utterances(df, const.ALTERNATIVES)
    df = fix.df.fix_datetime(df, columns=[const.REFTIME])
    df = fix.df.rename_columns(df, {const.DATA_ID: const.ID, const.ALTERNATIVES: const.UTTERANCES})

    if dataset_type == const.DATASET_TYPE__INTENT:
        label_df = make_intent_label_df(df)
    elif dataset_type == const.DATASET_TYPE__TRANSCRIPTION:
        label_df = make_transcription_label_df(df)
    elif dataset_type == const.DATASET_TYPE__ENTITY:
        label_df = make_entity_label_df(df, duckling_url, duckling_token=duckling_token)
    else:
        raise ValueError(f"Given {dataset_type=} not supported.")

    if label_df.empty:
        raise ValueError(f"No labels found for {dataset_type=}.")

    df = fix.df.remove_columns(df, [const.DATA, const.TAG, const.IS_GOLD])
    df = fix.df.min_json_whitespace(df, columns=[
        const.UTTERANCES,
        const.PREDICTION,
        const.ENTITIES,
        const.TRANSCRIPTION
    ])

    input_file_dir, input_file_name = os.path.split(df_path)
    input_file_name, input_file_ext = os.path.splitext(input_file_name)

    if not output_path:
        _, output_path = tempfile.mkstemp(
            dir=input_file_dir,
            prefix=f"{input_file_name}-labels-{dataset_type}-",
            suffix=input_file_ext,
        )
    updated_df = df.merge(label_df, on=const.ID, how=const.INNER)
    updated_df.to_csv(output_path, index=False)
    if delete_file:
        os.remove(df_path)
    return output_path
