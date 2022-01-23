"""Helper functions for loading data."""
import warnings
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple, Union

import pandas as pd
from biopsykit.io import load_pandas_dict_excel
from biopsykit.io.nilspod import load_csv_nilspod, load_dataset_nilspod
from biopsykit.utils._types import str_t
from biopsykit.utils.datatype_helper import SubjectDataDict
from nilspodlib.legacy import CorruptedPackageWarning, LegacyWarning
from tqdm.auto import tqdm

from cft_analysis._types import path_t

__all__ = ["load_ecg_raw_data_folder", "load_subject_data_dicts"]


def load_ecg_raw_data_folder(
    base_path: path_t,
    subject_id: str,
    phases: Sequence[str],
    selected_phases: Optional[str_t] = None,
    datastreams: Optional[Union[str, Sequence[str]]] = None,
) -> Dict[str, pd.DataFrame]:
    """Load all NilsPod datasets from one folder, convert them into dataframes, and combine them into a dictionary.

    This function can for example be used when single NilsPod sessions (datasets) were recorded
    for different study phases.

    ..note:: This function is different from the function :func:`biopsykit.io.nilspod.load_folder_nilspod` in the way
    that is does not only scan for .bin files, but also for .csv files containing NilsPod data. Due to data recording
    mistakes during the study some files were accidentally recorded as .csv files instead of .bin files,
    which will be accounted for in this function.

    Parameters
    ----------
    base_path : :class:`~pathlib.Path` or str
        base path to data folder
    subject_id : str
        Subject ID
    phases: list
        list of phase names corresponding to the files in the folder
    selected_phases: list
        list of phase names to load into the dictionary
    datastreams : str or list of str, optional
        list of datastreams if only specific datastreams of the dataset object should be imported or
        ``None`` to load all datastreams. Datastreams that are not part of the current dataset will be silently ignored.
        Default: ``None``

    Returns
    -------
    dataset_dict : dict
        dictionary with phase names as keys and pandas dataframes with sensor recordings as values.

    Raises
    ------
    ValueError
        if ``folder_path`` does not contain any NilsPod files, the number of phases does not match the number of
        datasets in the folder, or if the sampling rates of the files in the folder are not the same

    """
    # ensure pathlib
    data_path = Path(base_path).joinpath(f"ecg/{subject_id}/raw")
    # look for all NilsPod binary and csv files in the folder
    dataset_list = sorted(list(data_path.glob("*.bin")) + list(sorted(data_path.glob("*.csv"))))

    if isinstance(selected_phases, str):
        selected_phases = [selected_phases]

    if len(dataset_list) == 0:
        raise ValueError("No NilsPod files found in folder!")

    # ignore legacy and package warnings from nilspodlib since it comes from a firmware bug that we can ignore when
    # cutting away the last second of the data
    warnings.filterwarnings("ignore", category=CorruptedPackageWarning)
    warnings.filterwarnings("ignore", category=LegacyWarning)
    dataset_list = [
        load_dataset_nilspod(
            file_path=dataset_path,
            handle_counter_inconsistency="ignore",
            legacy_support="resolve",
            datastreams=datastreams,
        )
        if dataset_path.suffix == ".bin"
        else load_csv_nilspod(file_path=dataset_path)
        for dataset_path in dataset_list
    ]
    # remove the last second of the dataframe
    dataset_list = [(data.iloc[: -int(fs)], fs) for (data, fs) in dataset_list]
    dataset_dict = {phase: df for phase, (df, fs) in zip(phases, dataset_list)}

    if selected_phases is not None:
        dataset_dict = {phase: dataset_dict[phase] for phase in selected_phases}

    return dataset_dict


def load_subject_data_dicts(dataset: "CftDatasetRaw") -> Tuple[SubjectDataDict, SubjectDataDict]:  # noqa: F821
    """Load ``SubjectDataDict`` with heart rate and r-peak data.

    Parameters
    ----------
    dataset : :class:`~cft_analysis.datasets.CftDatasetRaw`
        dataset object to extract file paths from

    Returns
    -------
    subject_data_dict_hr : :obj:`~biopsykit.utils.datatype_helper.SubjectDataDict`
        ``SubjectDataDict`` containing heart rate data of all subjects
    subject_data_dict_rpeaks : :obj:`~biopsykit.utils.datatype_helper.SubjectDataDict`
        ``SubjectDataDict`` containing r-peak data of all subjects

    """
    subject_data_dict_hr = {}
    subject_data_dict_rpeaks = {}

    subject_dirs = dataset.subject_dirs
    for subject_dir in tqdm(subject_dirs):
        subject_id = subject_dir.name

        hr_path = subject_dir.joinpath("processed")
        hr_filename = hr_path.joinpath("hr_result_{}.xlsx".format(subject_id))
        rpeaks_filename = hr_path.joinpath("rpeaks_result_{}.xlsx".format(subject_id))

        hr_dict = load_pandas_dict_excel(hr_filename)
        rpeaks_dict = load_pandas_dict_excel(rpeaks_filename)

        subject_data_dict_hr[subject_id] = hr_dict
        subject_data_dict_rpeaks[subject_id] = rpeaks_dict

    return subject_data_dict_hr, subject_data_dict_rpeaks


def load_subject_continuous_hrv_data(dataset: "CftDatasetRaw") -> Dict[str, Dict[str, pd.DataFrame]]:  # noqa: F821
    """Load continuous heart rate variability data.

    Parameters
    ----------
    dataset : :class:`~cft_analysis.datasets.CftDatasetRaw`
        dataset object to extract file paths from

    Returns
    -------
    dict
        nested dictionary with continuous heart rate variability data for each participant (first dict level) and
        for each phase (second dict level)

    """
    subject_data_dict_hrv = {}

    subject_dirs = dataset.subject_dirs
    for subject_dir in tqdm(subject_dirs):
        subject_id = subject_dir.name
        hr_path = subject_dir.joinpath("processed")

        subject_data_dict_hrv[subject_id] = load_pandas_dict_excel(
            hr_path.joinpath("hrv_continuous_{}.xlsx".format(subject_id)), index_col=0
        )
    return subject_data_dict_hrv
