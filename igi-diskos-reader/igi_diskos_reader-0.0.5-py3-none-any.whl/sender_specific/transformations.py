from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Set, Iterable, Sequence, Dict, Optional
import pandas as pd

from igi_diskos_reader.sender_specific.id_decomposition import ANAL_ID_COL, AptAnalId
from igi_diskos_reader.spec import Sender, Block, BlockType
from igi_diskos_reader.utils import get_all_subclasses, split_on_last_occurrence, is_a_suffix

DETECTOR_COL, PEAK_PROPERTY_COL = 'Detector', 'PeakProperty'


def get_transformers(block: Block, sender: Sender) -> Iterable[IBlockTransformer]:
    for transformer in get_all_transformers():
        if transformer.applies(block, sender):
            yield transformer


def apply_transformations(original_df: pd.DataFrame, *transformers: IBlockTransformer) -> pd.DataFrame:
    df = original_df.copy()
    for transformer in transformers:
        df = transformer.apply(df)
    return df


class IBlockTransformer(ABC):
    """
    Base type - we find all based on any subclasses and then filter by block using the
    applies method on each subclass.
    """
    for_block_type: BlockType
    for_sender: Optional[Sender]
    order: int  # if > 1 for a given block this will be used to sort the transformations

    def applies(self, block: Block, sender: Sender) -> bool:
        """
        Default is this transformation relevant for the sender / block type.
        Can be overridden, but keep in mind that blocks will be assessed before
        any transformations have been applied, so you could not use this to identify
        changes made by a transformation.
        """
        return block.block_type == self.for_block_type and \
               (sender == self.for_sender or self.for_sender is None)

    @abstractmethod
    def apply(self, original_df: pd.DataFrame) -> pd.DataFrame:
        pass


class SplitByColsCombineByRows(IBlockTransformer):
    """
    When there are repeating blocks of columns with each set having it's own AnalID, these
    should be split into two tables then combined as rows. The later step to add anal code
    can then re-expand columns if there is more than one anal code. An example of this is
    APT block 25 (Isotope if natural).
    """
    for_block_type: BlockType = BlockType.Observations
    for_sender: Optional[Sender] = Sender.APT
    order: int = 10

    def applies(self, block:Block, sender: Sender) -> bool:
        """
        If it passes the usual base method (match sender & type) and there is > 1 AnalID col.
        """
        if super().applies(block, sender):
            # look for any starting with `AnalID` as dups could have been suffixed _N
            anal_id_cols = [h for h in block.get_headers() if h.startswith(ANAL_ID_COL)]
            return len(anal_id_cols) > 1
        return False

    def apply(self, original_df: pd.DataFrame) -> pd.DataFrame:
        column_map = build_col_groups(original_df, groups_start_with_col=ANAL_ID_COL)
        dfs = self.split_cols(original_df, column_map)
        return pd.concat(dfs).reset_index(drop=True)

    @staticmethod
    def split_cols(df: pd.DataFrame, col_map: Dict[str, Sequence[str]]) -> Sequence[pd.DataFrame]:
        dfs = []  # split data into multiple dfs

        for suffix, cols in col_map.items():
            new_df = df[cols]
            cleaned_cols = [split_on_last_occurrence(c, '_')[0] for c in cols]
            new_df.columns = cleaned_cols  # ensure matching col names ready for concat
            new_df = new_df[new_df[ANAL_ID_COL] != ""]  # filter out empty rows
            dfs.append(new_df)

        # fill any missing cols with empties (all dfs need to be same shape to concat rows)
        for idx, col in enumerate(dfs[0].columns.tolist()):
            for df in dfs:
                if not col in df.columns.tolist():
                    df[col] = ""

        # note - above handles more cols in first set (on end), but not diff order or more
        #        cols in later sets - hence the check and throw if not the same
        for df in dfs[1:]:
            if not dfs[0].columns.tolist() == df.columns.tolist():
                raise NotImplementedError(f"Found a scenario that is not currently handled when "
                                          f"splitting sheet into groups of columns. Expected each "
                                          f"group to have the same columns (in the same order or the "
                                          f"first group to have additional columns on the end. "
                                          f"Ask Chris to update the code for this scenario...\n"
                                          f"Found 1st set: {dfs[0].columns.tolist()}\n"
                                          f"  compared to: {df.columns.tolist()}.")

        return dfs


class AddIndicatorToHeaders(IBlockTransformer):
    """
    For blocks that have a `PeakProperty` column, this will be stripped and added
    to the headers for that block (to use as a mapping for indicator).
    """
    for_block_type: BlockType = BlockType.Observations
    for_sender: Optional[Sender] = None  # for any sender
    order: int = 20  # before adding analysis
    excl_cols: Set[str] = {ANAL_ID_COL, PEAK_PROPERTY_COL}

    def applies(self, block:Block, sender: Sender) -> bool:
        """
        If it passes the usual base method (match sender & type) and there is > 1 AnalID col.
        """
        if super().applies(block, sender):
            # look for any starting with PEAK_PROPERTY_COL as dups could have been suffixed _N
            ind_cols = [h for h in block.get_headers() if h.startswith(PEAK_PROPERTY_COL)]
            return len(ind_cols) > 0
        return False

    def apply(self, original_df: pd.DataFrame) -> pd.DataFrame:
        df = original_df.copy()

        cols_grps = build_col_groups(df, groups_start_with_col=DETECTOR_COL,
                                     excluded_cols=[ANAL_ID_COL, PEAK_PROPERTY_COL])
        for suffix, cols in cols_grps.items():
            expand_by = f"{PEAK_PROPERTY_COL}_{suffix}" if suffix else PEAK_PROPERTY_COL
            df = AptAnalId.expand_by_col(df, expand_by, cols_to_expand=cols, format_str="{0}[{1}]")
        return df


class ExpandHeadersByAnalCode(IBlockTransformer):
    """
    Append anal_code (extracted from AnalID for APT files) to header names on observation sheets.
    If more than one anal_code in block then expand columns by analysis code.
    Works for APT using AnalCode (extracted from AnalID).
    For all cols except the ID create an expanded col per anal code, then populate
    the data into the expanded column that matches the anal code for each row.
    """
    for_block_type: BlockType = BlockType.Observations
    for_sender: Optional[Sender] = Sender.APT
    order: int = 30
    excl_cols: Set[str] = {ANAL_ID_COL, PEAK_PROPERTY_COL}

    def apply(self, original_df: pd.DataFrame) -> pd.DataFrame:
        df = original_df.copy()
        cols_to_expand = [c for c in df.columns if c != ANAL_ID_COL]
        df = AptAnalId.expand_by_anal_codes(df, cols_to_expand)
        return df
    

class RemoveUnneededSuffixes(IBlockTransformer):
    """
    When columns are initially added for a lock we append a suffix such as _02 to
    prevent duplicates. However, at this stage we have added analysis and indicator
    data to the headers, so some of these suffixes can be safely removed.
    """
    for_block_type: BlockType = BlockType.Observations  # no anal or ind changes ot others
    for_sender: Optional[Sender] = None  # any sender
    order: int = 99

    def apply(self, original_df: pd.DataFrame) -> pd.DataFrame:
        df = original_df.copy()
        adj_cols = []
        for col in df.columns.tolist():
            before_, after_ = split_on_last_occurrence(col, '_')
            if is_a_suffix(after_):
                # add version without suffix if not already seen
                adj_cols.append(col if before_ in adj_cols else before_)
            else:
                adj_cols.append(col)

        df.columns = adj_cols
        return df



def build_col_groups(df: pd.DataFrame, groups_start_with_col: str,
                     excluded_cols: Sequence[str] = None) -> Dict[str, Sequence[str]]:
    if excluded_cols is None: excluded_cols = []
    suffix_to_cols = {}
    cur_suffix = ''
    for col in df.columns:
        if col.startswith(groups_start_with_col):
            _, cur_suffix = split_on_last_occurrence(col, '_')
            suffix_to_cols[cur_suffix] = [col]
        elif any([col.startswith(excl) for excl in excluded_cols]):
            continue
        else:
            suffix_to_cols[cur_suffix].append(col)
    return suffix_to_cols


# reflection to get all Transformation subclasses
def get_all_transformers() -> Sequence[IBlockTransformer]:
    """
    :return: sorted collection of all transformers
    """
    transformer_classes = get_all_subclasses(IBlockTransformer)
    transformer_objects = map(lambda c: c(), transformer_classes)
    return sorted(transformer_objects, key=lambda t: t.order)
