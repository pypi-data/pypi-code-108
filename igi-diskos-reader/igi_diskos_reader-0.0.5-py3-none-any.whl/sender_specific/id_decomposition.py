from typing import Sequence

import pandas as pd
from dataclasses import dataclass, field

from igi_diskos_reader.sender_specific import ANAL_ID_COL
from igi_diskos_reader.utils import split_on_last_occurrence, is_a_suffix


@dataclass
class AptAnalId:
    """
    APT use a specific format for their "AnalID" mde up of 4 parts:
    1) SampleId (numeric digits)
    2) Whole or fraction ('W' for whole or 'A', 'B', ... for each fraction
    3) Analysis code e.g. "RE" for rock eval - not always 2 digits
    4) Repeat ref ('A' for first run, 'B', 'C', ... to indicate repeats (single chr).

    Igi treat a sample / row as the combination of the above excluding the analysis code
    as the values for multiple analyses can be merged onto a single row.
    """
    anal_id: str  # the input
    # the parts making up the id
    sample_id: str = field(init=False)
    frac_ref: str = field(init=False)
    anal_code: str = field(init=False)
    repeat_ref: str = field(init=False)
    ANAL_CODE_COL: str = 'AnalCode'

    def __post_init__(self):
        self.sample_id = ''.join([i for i in self.anal_id if i.isdigit()])
        rem = self.anal_id[len(self.sample_id):]
        self.frac_ref, rem = rem[0], rem[1:]
        self.anal_code, self.repeat_ref = rem[:-1], rem[-1]

    @property
    def igi_id(self)-> str:
        """
        The ref for a single "row" in IGI. Combines all parts except anal_code (to allow us to
        merge multiple analyses for the same sample/fraction/repeat on a single row).
        """
        return f"{self.sample_id}{self.frac_ref}{self.repeat_ref}"

    @staticmethod
    def expand_by_anal_codes(orig_df: pd.DataFrame, cols_to_expand: Sequence[str]) -> pd.DataFrame:
        df = orig_df.copy()
        df[AptAnalId.ANAL_CODE_COL] = df[ANAL_ID_COL].apply(lambda id: AptAnalId(id).anal_code)
        exp_df = AptAnalId.expand_by_col(df, AptAnalId.ANAL_CODE_COL, cols_to_expand)
        return exp_df
    
    @staticmethod
    def expand_by_col(df: pd.DataFrame, expand_by: str, cols_to_expand: Sequence[str],
                      drop_expand_by_and_orig_cols_to_expand: bool = True,
                      format_str: str = "{0}.{1}") -> pd.DataFrame:
        def get_val_if_code_matches(row):
            return row[col] if row[expand_by] == code else ''

        for code in df[expand_by].unique():
            for col in cols_to_expand:
                before_, after_ = split_on_last_occurrence(col, '_')
                new_col_name = format_str.format(col, code)
                if is_a_suffix(after_):
                    new_col_name = format_str.format(before_, code)
                    # suffix on end to make it easier to clear later if col name is unique without it
                    new_col_name += f"_{after_}"
                else :
                    new_col_name = format_str.format(col, code)
                df[new_col_name] = df.apply(get_val_if_code_matches, axis=1)

        # drop original unexpanded cols and anal code added in the expansion
        if drop_expand_by_and_orig_cols_to_expand:
            cols_to_drop = [expand_by] + list(cols_to_expand)
            df.drop(columns=cols_to_drop, inplace=True)
        return df