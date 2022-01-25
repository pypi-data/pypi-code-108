from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set
import pandas as pd
import traceback

from igi_diskos_reader.sender_specific import ANAL_ID_COL, FRAC_ID_COL
from igi_diskos_reader.sender_specific.id_decomposition import AptAnalId
from igi_diskos_reader.sender_specific.transformations import get_transformers, apply_transformations
from igi_diskos_reader.spec import Sender, ParsedDiskosFile, Block, BlockType

# starts with most expanded
from igi_diskos_reader.utils import split_on_last_occurrence

STD_MERGE_COLS: List[str] = [ANAL_ID_COL, FRAC_ID_COL, 'SampleID', 'SiteID']
IGI_ID = 'IgiID'  # used for what we class as 1 "row" in our data model i.e.
                  # group on sample, fraction and repeat, but not on analysis
IGI_FRAC_ID = 'IgiFracID'
ANAL_METADATA_COLS: List[str] = ['ALaboratory', 'ADate', 'AInstrument', 'AComments']


def try_create_combined_df(parsed_diskos_file: ParsedDiskosFile) -> Tuple[bool, Optional[pd.DataFrame]]:
    """
    Create a combined dataframe from the blocks within a parsed diskos file.
    :param parsed_diskos_file: ParsedDiskosFile
    :return: (completed: bool, comb_df: Dataframe)
    """
    merge = get_merge(parsed_diskos_file.file_def.sender)

    for block in parsed_diskos_file.blocks:
        if not merge.failed:
            transformers = get_transformers(block, parsed_diskos_file.file_def.sender)
            transformed_df = apply_transformations(block.as_dataframe, *transformers)
            merge.join(transformed_df, block)

    completed = not merge.failed
    return completed, merge.comb_df


def get_merge(sender: Sender) -> DataFrameMerger:
    if sender == sender.APT:
        return CustomIgiRefDataFrameMerger()
    else:
        return DataFrameMerger()


@dataclass
class DataFrameMerger():
    comb_df: pd.DataFrame = field(default=None)
    failed: bool = field(default_factory=lambda: False)
    merge_cols: List[str] = field(default_factory=lambda: STD_MERGE_COLS.copy())
    metadata_merge_cols: Set[str] = field(default_factory=set)

    def join(self, df: pd.DataFrame, block: Block) -> None:
        name, block_no = block.block_def.description, block.block_def.block_no
        try:
            if self.comb_df is None or self.comb_df.empty:
                self.comb_df = df
            else:
                df = self._custom_pre_merge_steps(df, block)  # ** delegate to specific sender versions **
                id_merge_col = ""
                for id_merge_col in self.merge_cols:
                    if id_merge_col in self.comb_df and (id_merge_col in df
                                                         or df.index.name == id_merge_col):
                        merge_on = self.get_merge_cols(id_merge_col, df)
                        print(f'trying to merge in block {block_no}({name}) on {merge_on}')
                        self.comb_df = self.comb_df.merge(df, how='left', on=merge_on)
                        break
                #print(f"  shape before dedup: {self.comb_df.shape}")  #tmp
                self.comb_df = self.comb_df.sort_values(by=[id_merge_col]).drop_duplicates()
                #print(f"  shape after dedup: {self.comb_df.shape}")   #tmp
            self._custom_post_merge_steps()
        except Exception:
            self.failed = True
            print(f"\n** Failed to merge block {block_no}({name}), will continue  "
                  f"with individual sheets, but suppress combined sheet. **\n")
            print("-" * 60)
            traceback.print_exc()  # used to get full stack trace
            print("-" * 60)

    def get_merge_cols(self, id_merge_col: str, df: pd.DataFrame) -> List[str]:
        """
        Include any columns that are in both the new and the combined data frames.
        We could just merge on the id in both, but that leads to duplicate cols.
        """
        new_df_cols = set(df.columns)
        comb_df_cols = set(self.comb_df.columns)
        incl = self.metadata_merge_cols.intersection(new_df_cols).intersection(comb_df_cols)
        return  [id_merge_col] + list(incl)

    def _custom_pre_merge_steps(self, df: pd.DataFrame, block: Block) -> pd.DataFrame:
        return df

    def _custom_post_merge_steps(self):
        pass


@dataclass
class CustomIgiRefDataFrameMerger(DataFrameMerger):
    comb_df: pd.DataFrame = field(default=None)
    expanded_metadata_df: pd.DataFrame = field(default=None)
    failed: bool = field(default_factory=lambda: False)
    merge_cols: List[str] = field(default_factory=lambda: [IGI_ID, IGI_FRAC_ID] + STD_MERGE_COLS[2:])
    metadata_merge_cols: Set[str] = field(default_factory=set)

    def _custom_pre_merge_steps(self, df: pd.DataFrame, block: Block) -> pd.DataFrame:
        # before excl_unmergeable_cols - metadata cols & AnalID needed!
        if block.block_type == BlockType.Analysis:
            self._build_expanded_metadata(df)
        elif block.block_type == BlockType.Observations:
            df = self._merge_in_metadata(df)  # merge relevant metadata into df before merging this into main

        df = self.remap_ids(df)
        df = self.excl_unmergeable_cols(df)

        if block.block_type == BlockType.Observations and self.has_non_unique_ids(df, IGI_ID):
            df = df.groupby(IGI_ID).aggregate(''.join)

        return df

    def _custom_post_merge_steps(self):
        pass

    def _build_expanded_metadata(self, analysis_df: pd.DataFrame):
        df = AptAnalId.expand_by_anal_codes(orig_df=analysis_df, cols_to_expand=ANAL_METADATA_COLS)
        self.expanded_metadata_df = df

    def _merge_in_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        analysis_codes = df[ANAL_ID_COL].apply(lambda id: AptAnalId(id).anal_code).unique()
        relevant_metadata_cols = [c for c in self.expanded_metadata_df.columns
                                 if any([c.endswith(a) for a in analysis_codes])]
        relevant_metadata = self.expanded_metadata_df[[ANAL_ID_COL] + relevant_metadata_cols]
        df = df.merge(relevant_metadata, on=ANAL_ID_COL, how='left')
        self.metadata_merge_cols.update(set(relevant_metadata_cols))
        return df

    @staticmethod
    def has_non_unique_ids(df: pd.DataFrame, id_col: str):
        rows, _ = df.shape
        unique_ids = df[id_col].nunique()
        return rows > unique_ids

    @staticmethod
    def remap_ids(df: pd.DataFrame) -> pd.DataFrame:
        if ANAL_ID_COL in df.columns:
            df[IGI_ID] = df[ANAL_ID_COL].apply(lambda anal_id: AptAnalId(anal_id).igi_id)
        if FRAC_ID_COL in df.columns:
            df[IGI_FRAC_ID] = df[FRAC_ID_COL].apply(CustomIgiRefDataFrameMerger.get_igi_frac_id)
        return df

    @staticmethod
    def get_igi_frac_id(frac_id: str) -> str :
        sample_id = ''.join([i for i in frac_id if i.isdigit()])
        frac_ref = frac_id[len(sample_id):][0]
        return f"{sample_id}{frac_ref}"

    @staticmethod
    def excl_unmergeable_cols(df) -> pd.DataFrame:
        excl = [ANAL_ID_COL, FRAC_ID_COL, 'FracRefNumber', 'FractionType', 'AnalType'] + ANAL_METADATA_COLS

        def should_exclude(col: str, excl: str):
            """
            Exclude any that match exactly or match with <match>_N.
            """
            before_, after_ = split_on_last_occurrence(col, '_')
            exclude = col == excl or (col == before_ and after_.isdecimal())
            return exclude

        cols_to_drop = [c for c in df if any([should_exclude(c, x) for x in excl])]
        if cols_to_drop:
            df.drop(columns=cols_to_drop, inplace=True)
        return df
