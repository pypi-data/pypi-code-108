"""Method(s) for extracting CFT parameter."""
__all__ = ["cft_parameter_per_phase"]

import pandas as pd
from biopsykit.protocols import CFT
from biopsykit.utils.data_processing import select_dict_phases
from biopsykit.utils.datatype_helper import SubjectConditionDataFrame, SubjectDataDict
from tqdm.auto import tqdm


def cft_parameter_per_phase(
    hr_subject_data_dict: SubjectDataDict, cft_subject_list: SubjectConditionDataFrame
) -> pd.DataFrame:
    """Compute CFT parameter for each phase where the CFT was applied.

    Parameters
    ----------
    hr_subject_data_dict : :obj:`~biopsykit.utils.datatype_helper.HeartRateSubjectDict`
        ``HeartRateSubjectDict`` as returned by :func:`~cft_analysis.datasets.helper.load_subject_data_dicts`
    cft_subject_list : :obj:`biopsykit.utils.datatype_helper.SubjectConditionDataFrame`
        list of subject IDs belonging to the CFT condition

    Returns
    -------
    :class:`~pandas.DataFrame`
        dataframe with CFT parameters

    """
    subject_dict_result = {}

    # select all only MIST phases to split into subphases
    hr_subject_data_dict = select_dict_phases(hr_subject_data_dict, ["MIST1", "MIST2", "MIST3"])

    for subject_id, hr_data_dict in tqdm(list(hr_subject_data_dict.items())):
        if subject_id not in cft_subject_list.index:
            continue
        list_cft_params = []
        for phase, hr_data_phase in hr_data_dict.items():
            cft = CFT(structure={"Baseline": 60, "CFT": 120})
            cft_parameter = cft.compute_cft_parameter(hr_data_phase, index=phase)
            cft_parameter.index.names = ["phase"]
            list_cft_params.append(cft_parameter)

        df_cft_params = pd.concat(list_cft_params)
        subject_dict_result[subject_id] = df_cft_params

    return pd.concat(subject_dict_result, names=["subject"])
