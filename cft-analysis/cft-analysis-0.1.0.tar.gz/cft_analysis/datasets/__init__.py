"""Module including ``tpcp`` Dataset representations.

This module provides two different representations of the dataset:

* ``CftDatasetRaw``: Representation of raw ECG, saliva, and self-report data.
  The following data properties are available in the raw dataset:

  * ``ecg``: ECG for each participant.
  * ``sampling_rate``: Sampling rate of ECG data in Hz
  * ``questionnaire``: Self-report data including demographic information and questionnaires.
  * ``cortisol``: Cortisol samples
  * ``subject_dirs``: List of paths to participants ECG data are stored.
  * ``condition_list``: Mapping of participant IDs to conditions (Control / CFT)

* ``CftDatasetProcessed``: Representation of processed ECG, saliva, and self-report data.
  The following data properties are available in the processed dataset:

  * ``heart_rate``: Average heart rate per (sub)phase for each participant as relative increase to baseline.
  * ``heart_rate_ensemble``: Ensemble heart rate, i.e., resampled time-series heart rate for ensemble plotting
  * ``hrv``: Heart rate variability data per (sub)phase for each participant.
  * ``hr_hrv``: Combined ``heart_rate`` and ``hrv``.
  * ``time_above_baseline``: The relative amount of heart rate (variability) above a specified baseline.
  * ``cft_parameter``: Parameter characterizing the heart rate reaction to the CFT for each participant and CFT
    application, respectively.
  * ``questionnaire``: Self-report data including demographic information and questionnaires.
  * ``questionnaire_recoded``: Self-report data recoded from numeric to categorical format.
  * ``sample_times``: Time point when saliva samples were taken.
  * ``cortisol``: Cortisol samples
  * ``cortisol_features``: Features computed from cortisol samples to characterize the reaction to the MIST and
    possible group differences.


"""

from cft_analysis.datasets._cft_dataset_processed import CftDatasetProcessed
from cft_analysis.datasets._cft_dataset_raw import CftDatasetRaw

__all__ = ["CftDatasetRaw", "CftDatasetProcessed", "helper"]
