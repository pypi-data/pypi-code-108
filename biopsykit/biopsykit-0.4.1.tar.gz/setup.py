# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['biopsykit',
 'biopsykit.carwatch_logs',
 'biopsykit.classification',
 'biopsykit.classification.model_selection',
 'biopsykit.io',
 'biopsykit.metadata',
 'biopsykit.plotting',
 'biopsykit.protocols',
 'biopsykit.questionnaires',
 'biopsykit.saliva',
 'biopsykit.signals',
 'biopsykit.signals.ecg',
 'biopsykit.signals.eeg',
 'biopsykit.signals.imu',
 'biopsykit.signals.imu.feature_extraction',
 'biopsykit.signals.rsp',
 'biopsykit.sleep',
 'biopsykit.sleep.psg',
 'biopsykit.sleep.sleep_endpoints',
 'biopsykit.sleep.sleep_processing_pipeline',
 'biopsykit.sleep.sleep_wake_detection',
 'biopsykit.sleep.sleep_wake_detection.algorithms',
 'biopsykit.stats',
 'biopsykit.utils']

package_data = \
{'': ['*']}

install_requires = \
['XlsxWriter>=1.4.5,<2.0.0',
 'fau-colors>=1.0.2,<2.0.0',
 'joblib>=1.0.0,<2.0.0',
 'matplotlib>=3,<4',
 'neurokit2>=0.1.3,<0.2.0',
 'nilspodlib>=3.2.2,<4.0.0',
 'numpy>=1,<2',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.2.0,<2.0.0',
 'pingouin>=0.5.0,<0.6.0',
 'scikit-learn>=1.0,<2.0',
 'scipy>=1.7.0,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'statannot>=0.2.3,<0.3.0',
 'statsmodels>=0.12.2,<0.13.0',
 'tqdm>=4.62.0,<5.0.0',
 'xlrd>=2.0.1,<3.0.0']

extras_require = \
{'jupyter': ['IPython>=7.13.0,<8.0.0',
             'ipywidgets>=7.6.3,<8.0.0',
             'ipympl>=0.8.0,<0.9.0'],
 'mne': ['mne>=0.23.0,<0.24.0']}

setup_kwargs = {
    'name': 'biopsykit',
    'version': '0.4.1',
    'description': 'A Python package for the analysis of biopsychological data.',
    'long_description': '# BioPsyKit\n\n[![PyPI](https://img.shields.io/pypi/v/biopsykit)](https://pypi.org/project/biopsykit/)\n[![status](https://joss.theoj.org/papers/4769dbce3a25db943d7e3a23578becd1/status.svg)](https://joss.theoj.org/papers/4769dbce3a25db943d7e3a23578becd1)\n![GitHub](https://img.shields.io/github/license/mad-lab-fau/biopsykit)\n[![Documentation Status](https://readthedocs.org/projects/biopsykit/badge/?version=latest)](https://biopsykit.readthedocs.io/en/latest/?badge=latest)\n[![Test and Lint](https://github.com/mad-lab-fau/BioPsyKit/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/mad-lab-fau/BioPsyKit/actions/workflows/test-and-lint.yml)\n[![codecov](https://codecov.io/gh/mad-lab-fau/BioPsyKit/branch/main/graph/badge.svg?token=IK0QBHQKCO)](https://codecov.io/gh/mad-lab-fau/BioPsyKit)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/biopsykit)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mad-lab-fau/biopsykit)\n\nA Python package for the analysis of biopsychological data.\n\nWith this package you have everything you need for analyzing biopsychological data, including:\n* Data processing pipelines for various physiological signals (ECG, EEG, Respiration, Motion, ...).\n* Algorithms and data processing pipelines for sleep/wake prediction and computation of sleep endpoints \n  based on activity or IMU data.\n* Functions to import and process data from sleep trackers (e.g., Withings Sleep Analyzer)\n* Functions for processing and analysis of salivary biomarker data (cortisol, amylase).\n* Implementation of various psychological and HCI-related questionnaires.\n* Implementation of classes representing different psychological protocols \n  (e.g., TSST, MIST, Cortisol Awakening Response Assessment, etc.)\n* Functions for easily setting up statistical analysis pipelines.\n* Functions for setting up and evaluating machine learning pipelines.\n* Plotting wrappers optimized for displaying biopsychological data.\n\n## Details\n\n### Analysis of Physiological Signals\n#### ECG Processing\n`BioPsyKit` provides a whole ECG data processing pipeline, consisting of:\n* Loading ECG data from:\n    * Generic `.csv` files\n    * NilsPod binary (`.bin`) files (requires [`NilsPodLib`](https://github.com/mad-lab-fau/NilsPodLib))\n    * Other sensor types (_coming soon_)\n* Splitting data into single study parts (based on time intervals) that will be analyzed separately\n* Performing ECG processing, including:\n    * R peak detection (using [`Neurokit`](https://github.com/neuropsychology/NeuroKit))\n    * R peak outlier removal and interpolation\n    * HRV feature computation\n    * ECG-derived respiration (EDR) estimation for respiration rate and respiratory sinus arrhythmia (RSA) \n      (_experimental_)\n    * Instantaneous heart rate resampling \n    * Computing aggregated results (e.g., mean and standard error) per study part\n* Creating plots for visualizing processing results\n\n#### Quick Example\n```python\nfrom biopsykit.signals.ecg import EcgProcessor\nfrom biopsykit.example_data import get_ecg_example\n\necg_data, sampling_rate = get_ecg_example()\n\nep = EcgProcessor(ecg_data, sampling_rate)\nep.ecg_process()\n\nprint(ep.ecg_result)\n```\n\n... more biosignals coming soon!\n\n### Sleep/Wake Prediction\n`BioPsyKit` allows to process sleep data collected from IMU or activity sensors (e.g., Actigraphs). This includes:\n* Detection of wear periods\n* Detection of time spent in bed\n* Detection of sleep and wake phases\n* Computation of sleep endpoints (e.g., sleep and wake onset, net sleep duration wake after sleep onset, etc.)\n\n\n#### Quick Example\n```python\nimport biopsykit as bp\nfrom biopsykit.example_data import get_sleep_imu_example\n\nimu_data, sampling_rate = get_sleep_imu_example()\n\nsleep_results = bp.sleep.sleep_processing_pipeline.predict_pipeline_acceleration(imu_data, sampling_rate)\nsleep_endpoints = sleep_results["sleep_endpoints"]\n\nprint(sleep_endpoints)\n```\n\n### Salivary Biomarker Analysis\n`BioPsyKit` provides several methods for the analysis of salivary biomarkers (e.g. cortisol and amylase), such as:\n* Import data from Excel and csv files into a standardized format\n* Compute standard features (maximum increase, slope, area-under-the-curve, mean, standard deviation, ...)\n\n#### Quick Example\n```python\nimport biopsykit as bp\nfrom biopsykit.example_data import get_saliva_example\n\nsaliva_data = get_saliva_example(sample_times=[-20, 0, 10, 20, 30, 40, 50])\n\nmax_inc = bp.saliva.max_increase(saliva_data)\n# remove the first saliva sample (t=-20) from computing the AUC\nauc = bp.saliva.auc(saliva_data, remove_s0=True)\n\nprint(max_inc)\nprint(auc)\n```\n\n### Questionnaires\n`BioPsyKit` implements various established psychological (state and trait) questionnaires, such as:\n* Perceived Stress Scale (PSS)\n* Positive and Negative Affect Schedule (PANAS)\n* Self-Compassion Scale (SCS)\n* Big Five Inventory (BFI)\n* State Trait Depression and Anxiety Questionnaire (STADI)\n* Trier Inventory for Chronic Stress (TICS)\n* Primary Appraisal Secondary Appraisal Scale (PASA)\n* ...\n\n#### Quick Example\n```python\nimport biopsykit as bp\nfrom biopsykit.example_data import get_questionnaire_example\n\ndata = get_questionnaire_example()\n\npss_data = data.filter(like="PSS")\npss_result = bp.questionnaires.pss(pss_data)\n\nprint(pss_result)\n```\n\n#### List Supported Questionnaires\n```python\nimport biopsykit as bp\n\nprint(bp.questionnaires.utils.get_supported_questionnaires())\n```\n\n### Psychological Protocols\n`BioPsyKit` implements methods for easy handling and analysis of data recorded with several established psychological \nprotocols, such as:\n* Montreal Imaging Stress Task (MIST)\n* Trier Social Stress Test (TSST)\n* Cortisol Awakening Response Assessment (CAR)\n* ...\n\n#### Quick Example\n```python\nfrom biopsykit.protocols import TSST\nfrom biopsykit.example_data import get_saliva_example\nfrom biopsykit.example_data import get_hr_subject_data_dict_example\n# specify TSST structure and the durations of the single phases\nstructure = {\n   "Pre": None,\n   "TSST": {\n       "Preparation": 300,\n       "Talk": 300,\n       "Math": 300\n   },\n   "Post": None\n}\ntsst = TSST(name="TSST", structure=structure)\n\nsaliva_data = get_saliva_example(sample_times=[-20, 0, 10, 20, 30, 40, 50])\nhr_subject_data_dict = get_hr_subject_data_dict_example()\n# add saliva data collected during the whole TSST procedure\ntsst.add_saliva_data(saliva_data, saliva_type="cortisol")\n# add heart rate data collected during the "TSST" study part\ntsst.add_hr_data(hr_subject_data_dict, study_part="TSST")\n# compute heart rate results: normalize ECG data relative to "Preparation" phase; afterwards, use data from the \n# "Talk" and "Math" phases and compute the average heart rate for each subject and study phase, respectively\ntsst.compute_hr_results(\n    result_id="hr_mean",\n    study_part="TSST",\n    normalize_to=True,\n    select_phases=True,\n    mean_per_subject=True,\n    params={\n        "normalize_to": "Preparation",\n        "select_phases": ["Talk", "Math"]\n    }\n)\n```\n\n### Statistical Analysis\n`BioPsyKit` implements methods for simplified statistical analysis of biopsychological data by offering an \nobject-oriented interface for setting up statistical analysis pipelines, displaying the results, and adding \nstatistical significance brackets to plots.\n\n#### Quick Example\n\n```python\nimport matplotlib.pyplot as plt\nfrom biopsykit.stats import StatsPipeline\nfrom biopsykit.plotting import multi_feature_boxplot\nfrom biopsykit.example_data import get_stats_example\n\ndata = get_stats_example()\n\n# configure statistical analysis pipeline which consists of checking for normal distribution and performing paired \n# t-tests (within-variable: time) on each questionnaire subscale separately (grouping data by subscale).\npipeline = StatsPipeline(\n    steps=[("prep", "normality"), ("test", "pairwise_ttests")],\n    params={"dv": "PANAS", "groupby": "subscale", "subject": "subject", "within": "time"}\n)\n\n# apply statistics pipeline on data\npipeline.apply(data)\n\n# plot data and add statistical significance brackets from statistical analysis pipeline\nfig, axs = plt.subplots(ncols=3)\nfeatures = ["NegativeAffect", "PositiveAffect", "Total"]\n# generate statistical significance brackets\nbox_pairs, pvalues = pipeline.sig_brackets(\n    "test", stats_effect_type="within", plot_type="single", x="time", features=features, subplots=True\n)\n# plot data\nmulti_feature_boxplot(\n    data=data, x="time", y="PANAS", features=features, group="subscale", order=["pre", "post"],\n    stats_kwargs={"box_pairs": box_pairs, "pvalues": pvalues}, ax=axs\n)\n```\n\n\n### Machine Learning Analysis\n`BioPsyKit` implements methods for simplified and systematic evaluation of different machine learning pipelines.\n\n#### Quick Example\n```python\n# Utils\nfrom sklearn.datasets import load_breast_cancer\n# Preprocessing & Feature Selection\nfrom sklearn.feature_selection import SelectKBest\nfrom sklearn.preprocessing import MinMaxScaler, StandardScaler\n# Classification\nfrom sklearn.neighbors import KNeighborsClassifier\nfrom sklearn.tree import DecisionTreeClassifier\n# Cross-Validation\nfrom sklearn.model_selection import KFold\n\nfrom biopsykit.classification.model_selection import SklearnPipelinePermuter\n\n# load example dataset\nbreast_cancer = load_breast_cancer()\nX = breast_cancer.data\ny = breast_cancer.target\n\n# specify estimator combinations\nmodel_dict = {\n    "scaler": {\n        "StandardScaler": StandardScaler(),\n        "MinMaxScaler": MinMaxScaler()\n    },\n    "reduce_dim": {\n        "SelectKBest": SelectKBest(),\n    },\n    "clf" : {\n        "KNeighborsClassifier": KNeighborsClassifier(),\n        "DecisionTreeClassifier": DecisionTreeClassifier(),\n    }\n}\n# specify hyperparameter for grid search\nparams_dict = {\n    "StandardScaler": None,\n    "MinMaxScaler": None,\n    "SelectKBest": { "k": [2, 4, "all"] },\n    "KNeighborsClassifier": { "n_neighbors": [2, 4], "weights": ["uniform", "distance"] },\n    "DecisionTreeClassifier": {"criterion": [\'gini\', \'entropy\'], "max_depth": [2, 4] },\n}\n\npipeline_permuter = SklearnPipelinePermuter(model_dict, params_dict)\npipeline_permuter.fit(X, y, outer_cv=KFold(5), inner_cv=KFold(5))\n\n# print mean performance scores for each pipeline and parameter combinations, averaged over all outer CV folds\nprint(pipeline_permuter.mean_pipeline_score_results())\n# print overall best-performing pipeline and the performances over all outer CV folds\nprint(pipeline_permuter.best_pipeline())\n# print summary of all relevant metrics for the best pipeline for each evaluated pipeline combination\nprint(pipeline_permuter.metric_summary())\n```\n\n\n## Installation\n\n``BioPsyKit`` requires Python >=3.7. First, install a compatible version of Python. Then install ``BioPsyKit`` via pip. \n\nInstallation from [PyPi](https://pypi.org/): \n```bash\npip install biopsykit\n```\n\nInstallation from [PyPi](https://pypi.org/) with extras \n(e.g., `jupyter` to directly install all required dependencies for the use with Jupyter Lab): \n```bash\npip install "biopsykit[jupyter]"\n```\n\nInstallation from local repository copy:\n```bash\ngit clone https://github.com/mad-lab-fau/BioPsyKit.git\ncd BioPsyKit\npip install .\n```\n\n\n### For Developer\n\nIf you are a developer and want to contribute to ``BioPsyKit`` you can install an editable version of the package from \na local copy of the repository.\n\nBioPsyKit uses [poetry](https://python-poetry.org) to manage dependencies and packaging. Once you installed poetry, \nrun the following commands to clone the repository, initialize a virtual env and install all development dependencies:\n\n#### Without Extras\n```bash\ngit clone https://github.com/mad-lab-fau/BioPsyKit.git\ncd BioPsyKit\npoetry install\n```\n\n#### With all Extras (e.g., extended functionalities for IPython/Jupyter Notebooks)\n```bash\ngit clone https://github.com/mad-lab-fau/BioPsyKit.git\ncd BioPsyKit\npoetry install -E mne -E jupyter \n```\n\nTo run any of the tools required for the development workflow, use the `poe` commands of the \n[poethepoet](https://github.com/nat-n/poethepoet) task runner:\n\n```bash\n$ poe\ndocs                 Build the html docs using Sphinx.\nformat               Reformat all files using black.\nformat_check         Check, but not change, formatting using black.\nlint                 Lint all files with Prospector.\ntest                 Run Pytest with coverage.\nupdate_version       Bump the version in pyproject.toml and biopsykit.__init__ .\n```\n\n----\n**Note**: In order to build the documentation, you need to additionally install [pandoc](https://pandoc.org/installing.html).\n\n----\n\nSee the [Contributing Guidelines](https://biopsykit.readthedocs.io/en/latest/source/contributing/CONTRIBUTING.html) for further information.\n\n\n\n## Examples\nSee the [Examples Gallery](https://biopsykit.readthedocs.io/en/latest/examples/index.html) for example on how to use BioPsyKit.\n\n\n## Citing BioPsyKit\n\nIf you use `BioPsyKit` in your work, please report the version you used in the text. Additionally, please also cite the corresponding paper:\n\n```\nRicher et al., (2021). BioPsyKit: A Python package for the analysis of biopsychological data. Journal of Open Source Software, 6(66), 3702, https://doi.org/10.21105/joss.03702\n```\n\n\nIf you use a specific algorithm please also to make sure you cite the original paper of the algorithm! We recommend the following citation style:\n\n```\nWe used the algorithm proposed by Author et al. [paper-citation], implemented by the BioPsykit package [biopsykit-citation].\n```\n',
    'author': 'Robert Richer',
    'author_email': 'robert.richer@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mad-lab-fau/biopsykit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
