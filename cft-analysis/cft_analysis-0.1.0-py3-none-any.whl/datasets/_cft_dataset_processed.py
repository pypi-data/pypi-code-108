"""Dataset representing processed data of the CFT dataset."""
import warnings
from typing import Optional, Sequence, Union

import biopsykit as bp
import pandas as pd
from biopsykit.io import load_long_format_csv, load_questionnaire_data
from biopsykit.utils.dataframe_handling import multi_xs
from tpcp import Dataset

from cft_analysis._types import path_t


class CftDatasetProcessed(Dataset):
    """Representation of processed data (heart rate (variability), saliva, self-reports) from the CFT study.

    Data are only loaded once the respective attributes are accessed.

    Parameters
    ----------
    base_path
        The base folder where the dataset can be found.
    exclude_subjects:
        ``True`` to exclude selected participants from the dataset
        (since they are outlier or there were problems during data collection), ``False`` to load and use data from
        all participants.
        Default: ``True``

    """

    EXCLUDED_SUBJECTS: Sequence[str]  # pylint:disable=invalid-name
    base_path: path_t
    cft_hr_features_filename: str = "ecg/cft_hr_features_merged.csv"
    exclude_subjects: bool
    _saliva_sample_times: Sequence[int] = [-30, -1, 0, 10, 20, 30, 40]

    def __init__(
        self,
        base_path: path_t,
        groupby_cols: Optional[Sequence[str]] = None,
        subset_index: Optional[Sequence[str]] = None,
        exclude_subjects: Optional[bool] = True,
    ):
        super().__init__(groupby_cols=groupby_cols, subset_index=subset_index)
        # ensure pathlib
        self.base_path = base_path
        self.exclude_subjects = exclude_subjects
        self._exclude_subjects()

    def _exclude_subjects(self):
        if self.exclude_subjects:
            file_path = self.base_path.joinpath("excluded_subjects.csv")
            if not file_path.exists():
                warnings.warn("File containing subject IDs to be excluded not found. Loading data of all subjects...")
            excluded_subjects = pd.read_csv(file_path).sort_values(by="subject")
            self.EXCLUDED_SUBJECTS = list(excluded_subjects["subject"])  # pylint:disable=invalid-name

    def create_index(self) -> pd.DataFrame:
        cft_hr_features = pd.read_csv(self.base_path.joinpath(self.cft_hr_features_filename))
        index_cols = ["condition", "subject", "phase", "subphase"]
        index = cft_hr_features[index_cols].set_index(index_cols)
        if self.exclude_subjects:
            index = index.drop(self.EXCLUDED_SUBJECTS, level="subject")
        index = index.reset_index()
        return index

    @property
    def heart_rate(self) -> pd.DataFrame:
        """Load and return heart rate data.

        It is provided as the relative heart rate increase to the baseline for each participant,
        averaged per (sub)phase.

        Returns
        -------
        dataframe
            heart rate per participant and (sub)phase

        """
        return self._slice_hr_data("HR")

    @property
    def heart_rate_ensemble(self) -> pd.DataFrame:
        """Load and return ensemble heart rate.

        This function returns *ensemble heart rate* data, i.e., time-series data where the data of each participant
        has equal length, allowing to merge it into one dataframe and visualize is in a *ensemble plot*.

        """
        if self.is_single(None) or self.is_single("subphase"):
            raise ValueError("hr_ensemble data can not be accessed for individual subphases!")
        ensemble_dict = bp.io.load_pandas_dict_excel(self.base_path.joinpath("ecg/cft_hr_ensemble.xlsx"))
        phases = self.index["phase"].unique()
        subjects = self.index["subject"].unique()
        ensemble_dict = {key: ensemble_dict[key] for key in phases if key in ensemble_dict.keys()}
        ensemble_dict = {key: val[subjects] for key, val in ensemble_dict.items()}
        data = pd.concat(ensemble_dict, names=["phase"])
        data.columns.name = "subject"
        return data

    @property
    def hrv(self) -> pd.DataFrame:
        """Load and return heart rate variability data."""
        return self._slice_hr_data("HRV")

    @property
    def hr_hrv(self) -> pd.DataFrame:
        """Load and return combined heart rate and heart rate variability data."""
        return self._slice_hr_data(["HR", "HRV"])

    @property
    def time_above_baseline(self) -> pd.DataFrame:
        """Load and return the relative time of heart rate above a specified baseline."""
        return self._slice_hr_data("Time_BL_Glo")

    @property
    def cft_parameter(self) -> pd.DataFrame:
        """Load and return CFT parameter characterizing the physiological reaction to each CFT."""
        return self._slice_hr_data("CFT")

    @property
    def questionnaire(self):
        """Load and return questionnaire data."""
        return self._load_questionnaire_data()

    @property
    def questionnaire_recoded(self):
        """Load and return questionnaire data recoded from numerical to categorical data using the codebook."""
        data = self._load_questionnaire_data()
        codebook = bp.io.load_codebook(self.base_path.joinpath("questionnaire/codebook.csv"))
        return bp.utils.dataframe_handling.apply_codebook(data, codebook)

    @property
    def sample_times(self) -> Sequence[int]:
        """Return saliva sampling times."""
        return self._saliva_sample_times

    @property
    def cortisol(self) -> pd.DataFrame:
        """Load and return cortisol data."""
        return self._load_saliva_data("cortisol")

    @property
    def cortisol_features(self) -> pd.DataFrame:
        """Load and return features computed from cortisol data."""
        return self._load_saliva_feature_data("cortisol")

    def _load_cft_hr_features(self) -> pd.DataFrame:
        return load_long_format_csv(self.base_path.joinpath(self.cft_hr_features_filename))

    def _get_index(self) -> pd.DataFrame:
        index = self.index.drop_duplicates()
        index = index.set_index(list(index.columns))
        return index

    def _slice_hr_data(self, category: Union[str, Sequence[str]]) -> pd.DataFrame:
        data = self._load_cft_hr_features()
        data = multi_xs(data, category, level="category")
        index = self._get_index()
        return index.join(data).dropna()

    def _load_questionnaire_data(self) -> pd.DataFrame:
        self._assert_is_single_helper("questionnaire")
        data_path = self.base_path.joinpath("questionnaire/questionnaire_data.csv")

        data = load_questionnaire_data(data_path)
        subject_ids = self.index["subject"].unique()
        data = data.loc[subject_ids]

        condition = self.index["condition"].unique()
        return multi_xs(data, condition, level="condition")

    def _load_saliva_data(self, saliva_type: str) -> pd.DataFrame:
        self._assert_is_single_helper(saliva_type)
        data_path = self.base_path.joinpath(f"saliva/{saliva_type}_samples.csv")
        data = load_long_format_csv(data_path)
        subject_ids = self.index["subject"].unique()
        conditions = self.index["condition"].unique()
        return multi_xs(multi_xs(data, subject_ids, level="subject"), conditions, level="condition")

    def _load_saliva_feature_data(self, saliva_type: str) -> pd.DataFrame:
        self._assert_is_single_helper(saliva_type)
        data_path = self.base_path.joinpath(f"saliva/{saliva_type}_features.csv")
        data = load_long_format_csv(data_path)
        subject_ids = self.index["subject"].unique()
        conditions = self.index["condition"].unique()
        return multi_xs(multi_xs(data, subject_ids, level="subject"), conditions, level="condition")

    def _assert_is_single_helper(self, data_type: str):
        if any(
            [
                self.is_single(None),
                self.is_single(["subject", "condition", "phase"]),
                self.is_single(["subject", "condition", "subphase"]),
                self.is_single("phase"),
                self.is_single("subphase"),
            ]
        ):
            raise ValueError(f"{data_type} data can not be accessed for individual phases or subphases!")
