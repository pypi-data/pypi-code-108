# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dRFEtools']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.3.4,<4.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'plotnine>=0.7.1,<0.8.0',
 'scikit-learn>=1.0,<2.0',
 'scipy>=1.6.0,<2.0.0',
 'statsmodels>=0.12.2,<0.13.0']

setup_kwargs = {
    'name': 'drfetools',
    'version': '0.1.16',
    'description': 'A package for preforming dynamic recursive feature elimination with sklearn.',
    'long_description': '# dRFEtools - dynamic Recursive Feature Elimination\n\n`dRFEtools` is a package for dynamic recursive feature elimination with\nsklearn. Currently supporting random forest classification and regression,\nand linear models (linear, lasso, ridge, and elastic net).\n\nAuthors: Apuã Paquola, Kynon Jade Benjamin, and Tarun Katipalli\n\nPackage developed in Python 3.7+.\n\nIn addition to scikit-learn, `dRFEtools` is also built with NumPy, SciPy,\nPandas, matplotlib, plotnine, and statsmodels.\n\nThis package has several function to run dynamic recursive feature elimination\n(dRFE) for random forest and linear model classifier and regression models. For\nrandom forest, it assumes Out-of-Bag (OOB) is set to True. For linear models,\nit generates a developmental set. For both classification and regression, three\nmeasurements are calculated for feature selection:\n\nClassification:\n\n1.  Normalized mutual information\n2.  Accuracy\n3.  Area under the curve (AUC) ROC curve\n\nRegression:\n\n1.  R2 (this can be negative if model is arbitrarily worse)\n2.  Explained variance\n3.  Mean squared error\n\nThe package has been split in to three additional scripts for:\n\n1.  Random forest feature elimination (AP)\n2.  Linear model regression feature elimination (KJB)\n3.  Rank features function (TK)\n4.  Lowess redundant selection (KJB)\n\n# Table of Contents\n\n1.  [Citation](#org7b64d47)\n2.  [Installation](#org04443e4)\n3.  [Reference Manual](#org5afd041)\n    1.  [dRFEtools main functions](#org6171433)\n    2.  [Redundant features functions](#org3cfdf65)\n    3.  [Plotting functions](#org8ecca01)\n    4.  [Metric functions](#org377b1aa)\n    5.  [Linear model classes for dRFE](#org288aaeb)\n    6.  [SVM model classes for dRFE](#org1313shi)\n    7.  [Random forest helper functions](#orga29d49b)\n    8.  [Linear model helper functions](#orgbda21bf)\n\n<a id="org7b64d47"></a>\n\n## Citation\n\nIf using please cite: [![DOI](https://zenodo.org/badge/402494754.svg)](https://zenodo.org/badge/latestdoi/402494754).\n\n\n<a id="org04443e4"></a>\n\n## Installation\n\n`pip install --user dRFEtools`\n\n\n<a id="org5afd041"></a>\n\n## Reference Manual\n\n\n<a id="org6171433"></a>\n\n### dRFEtools main functions\n\n1.  dRFE - Random Forest\n\n    `rf_rfe`\n\n    Runs random forest feature elimination step over iterator process.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n    -   X: a data frame of training data\n    -   Y: a vector of sample labels from training data set\n    -   features: a vector of feature names\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   elimination_rate: percent rate to reduce feature list. default .2\n    -   RANK: Output feature ranking. default=True (Boolean)\n\n    **Yields:**\n\n    -   dict: a dictionary with number of features, normalized mutual information score, accuracy score, and array of the indexes for features to keep\n\n2.  dRFE - Linear Models\n\n    `dev_rfe`\n\n    Runs recursive feature elimination for linear model step over iterator\n    process assuming developmental set is needed.\n\n    **Args:**\n\n    -   estimator: regressor or classifier linear model object\n    -   X: a data frame of training data\n    -   Y: a vector of sample labels from training data set\n    -   features: a vector of feature names\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   elimination_rate: percent rate to reduce feature list. default .2\n    -   dev_size: developmental set size. default \'0.20\'\n    -   RANK: run feature ranking, default \'True\'\n    -   SEED: random state. default \'True\'\n\n    **Yields:**\n\n    -   dict: a dictionary with number of features, r2 score, mean square error,\n        expalined variance, and array of the indices for features to keep\n\n3.  Feature Rank Function\n\n    `feature_rank_fnc`\n\n    This function ranks features within the feature elimination loop.\n\n    **Args:**\n\n    -   features: A vector of feature names\n    -   rank: A vector with feature ranks based on absolute value of feature importance\n    -   n_features_to_keep: Number of features to keep. (Int)\n    -   fold: Fold to analyzed. (Int)\n    -   out_dir: Output directory for text file. Default \'.\'\n    -   RANK: Boolean (True or False)\n\n    **Yields:**\n\n    -   Text file: Ranked features by fold tab-delimited text file, only if RANK=True\n\n4.  N Feature Iterator\n\n    `n_features_iter`\n\n    Determines the features to keep.\n\n    **Args:**\n\n    -   nf: current number of features\n    -   keep_rate: percentage of features to keep\n\n    **Yields:**\n\n    -   int: number of features to keep\n\n\n<a id="org3cfdf65"></a>\n\n### Redundant features functions\n\n1.  Run lowess\n\n    `run_lowess`\n\n    This function runs the lowess function and caches it to memory.\n\n    **Args:**\n\n    -   x: the x-values of the observed points\n    -   y: the y-values of the observed points\n    -   frac: the fraction of the data used when estimating each y-value. default 3/10\n\n    **Yields:**\n\n    -   z: 2D array of results\n\n2.  Convert array to tuple\n\n    `array_to_tuple`\n\n    This function attempts to convert a numpy array to a tuple.\n\n    **Args:**\n\n    -   np_array: numpy array\n\n    **Yields:**\n\n    -   tuple\n\n3.  Extract dRFE as a dataframe\n\n    `get_elim_df_ordered`\n\n    This function converts the dRFE dictionary to a pandas dataframe.\n\n    **Args:**\n\n    -   d: dRFE dictionary\n    -   multi: is this for multiple classes. (True or False)\n\n    **Yields:**\n\n    -   df_elim: dRFE as a dataframe with log10 transformed features\n\n4.  Calculate lowess curve\n\n    `cal_lowess`\n\n    This function calculates the lowess curve.\n\n    **Args:**\n\n    -   d: dRFE dictionary\n    -   frac: the fraction of the data used when estimating each y-value\n    -   multi: is this for multiple classes. (True or False)\n\n    **Yields:**\n\n    -   x: dRFE log10 transformed features\n    -   y: dRFE metrics\n    -   z: 2D numpy array with lowess curve\n    -   xnew: increased intervals\n    -   ynew: interpolated metrics for xnew\n\n5.  Calculate lowess curve for log10\n\n    `cal_lowess`\n\n    This function calculates the rate of change on the lowess fitted curve with\n    log10 transformated input.\n\n    **Args:**\n\n    -   d: dRFE dictionary\n    -   frac: the fraction of the data used when estimating each y-value\n    -   multi: is this for multiple classes. default False\n\n    **Yields:**\n\n    -   data frame: dataframe with n_features, lowess value, and rate of change (DxDy)\n\n6.  Extract max lowess\n\n    `extract_max_lowess`\n\n    This function extracts the max features based on rate of change of log10\n    transformed lowess fit curve.\n\n    **Args:**\n\n    -   d: dRFE dictionary\n    -   frac: the fraction of the data used when estimating each y-value. default 3/10\n    -   multi: is this for multiple classes. default False\n\n    **Yields:**\n\n    -   int: number of max features (smallest subset)\n\n7.  Extract redundant lowess\n\n    `extract_redundant_lowess`\n\n    This function extracts the redundant features based on rate of change of log10\n    transformed lowess fit curve.\n\n    **Args:**\n\n    -   d: dRFE dictionary\n    -   frac: the fraction of the data used when estimating each y-value. default 3/10\n    -   step_size: rate of change step size to analyze for extraction. default 0.05\n    -   multi: is this for multiple classes. default False\n\n    **Yields:**\n\n    -   int: number of redundant features\n\n8.  Optimize lowess plot\n\n    `plot_with_lowess_vline`\n\n    Redundant set selection optimization plot. This will be ROC AUC for multiple\n    classification (3+), NMI for binary classification, or R2 for regression. The\n    plot returned has fraction and step size as well as lowess smoothed curve and\n    indication of predicted redundant set.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   frac: the fraction of the data used when estimating each y-value. default 3/10\n    -   step_size: rate of change step size to analyze for extraction. default 0.05\n    -   classify: is this a classification algorithm. default True\n    -   multi: does this have multiple (3+) classes. default True\n\n    **Yields:**\n\n    -   graph: plot of dRFE with estimated redundant set indicated as well as fraction and set size used. It automatically saves files as pdf, png, and svg\n\n9.  Plot lowess vline\n\n    `plot_with_lowess_vline`\n\n    Plot feature elimination results with the redundant set indicated. This will be\n    ROC AUC for multiple classification (3+), NMI for binary classification, or R2\n    for regression.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   frac: the fraction of the data used when estimating each y-value. default 3/10\n    -   step_size: rate of change step size to analyze for extraction. default 0.05\n    -   classify: is this a classification algorithm. default True\n    -   multi: does this have multiple (3+) classes. default True\n\n    **Yields:**\n\n    -   graph: plot of dRFE with estimated redundant set indicated, automatically saves files as pdf, png, and svg\n\n\n<a id="org8ecca01"></a>\n\n### Plotting functions\n\n1.  Save plots\n\n    `save_plots`\n\n    This function save plot as svg, png, and pdf with specific label and dimension.\n\n    **Args:**\n\n    -   p: plotnine object\n    -   fn: file name without extensions\n    -   w: width, default 7\n    -   h: height, default 7\n\n    **Yields:** SVG, PNG, and PDF of plotnine object\n\n2.  Plot dRFE Accuracy\n\n    `plot_acc`\n\n    Plot feature elimination results for accuracy.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n\n    **Yields:**\n\n    -   graph: plot of feature by accuracy, automatically saves files as pdf, png, and svg\n\n3.  Plot dRFE NMI\n\n    `plot_nmi`\n\n    Plot feature elimination results for normalized mutual information.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n\n    **Yields:**\n\n    -   graph: plot of feature by NMI, automatically saves files as pdf, png, and svg\n\n4.  Plot dRFE ROC AUC\n\n    `plot_roc`\n\n    Plot feature elimination results for AUC ROC curve.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n\n    **Yields:**\n\n    -   graph: plot of feature by AUC, automatically saves files as pdf, png, and svg\n\n5.  Plot dRFE R2\n\n    `plot_r2`\n\n    Plot feature elimination results for R2 score. Note that this can be negative\n    if model is arbitarily worse.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n\n    **Yields:**\n\n    -   graph: plot of feature by R2, automatically saves files as pdf, png, and svg\n\n6.  Plot dRFE MSE\n\n    `plot_mse`\n\n    Plot feature elimination results for mean squared error score.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n\n    **Yields:**\n\n    -   graph: plot of feature by mean squared error, automatically saves files as pdf, png, and svg\n\n7.  Plot dRFE Explained Variance\n\n    `plot_evar`\n\n    Plot feature elimination results for explained variance score.\n\n    **Args:**\n\n    -   d: feature elimination class dictionary\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n\n    **Yields:**\n\n    -   graph: plot of feature by explained variance, automatically saves files as pdf, png, and svg\n\n\n<a id="org377b1aa"></a>\n\n### Metric functions\n\n1.  OOB Prediction\n\n    `oob_predictions`\n\n    Extracts out-of-bag (OOB) predictions from random forest classifier classes.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n\n    **Yields:**\n\n    -   vector: OOB predicted labels\n\n2.  OOB Accuracy Score\n\n    `oob_score_accuracy`\n\n    Calculates the accuracy score from the OOB predictions.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: accuracy score\n\n3.  OOB Normalized Mutual Information Score\n\n    `oob_score_nmi`\n\n    Calculates the normalized mutual information score from the OOB predictions.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: normalized mutual information score\n\n4.  OOB Area Under ROC Curve Score\n\n    `oob_score_roc`\n\n    Calculates the area under the ROC curve score for the OOB predictions.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: AUC ROC score\n\n5.  OOB R2 Score\n\n    `oob_score_r2`\n\n    Calculates the r2 score from the OOB predictions.\n\n    **Args:**\n\n    -   estimator: Random forest regressor object\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: r2 score\n\n6.  OOB Mean Squared Error Score\n\n    `oob_score_mse`\n\n    Calculates the mean squared error score from the OOB predictions.\n\n    **Args:**\n\n    -   estimator: Random forest regressor object\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: mean squared error score\n\n7.  OOB Explained Variance Score\n\n    `oob_score_evar`\n\n    Calculates the explained variance score for the OOB predictions.\n\n    **Args:**\n\n    -   estimator: Random forest regressor object\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: explained variance score\n\n8.  Developmental Test Set Predictions\n\n    `dev_predictions`\n\n    Extracts predictions using a development fold for linear\n    regressor.\n\n    **Args:**\n\n    -   estimator: Linear model regression classifier object\n    -   X: a data frame of normalized values from developmental dataset\n\n    **Yields:**\n\n    -   vector: Development set predicted labels\n\n9.  Developmental Test Set R2 Score\n\n    `dev_score_r2`\n\n    Calculates the r2 score from the developmental dataset\n    predictions.\n\n    **Args:**\n\n    -   estimator: Linear model regressor object\n    -   X: a data frame of normalized values from developmental dataset\n    -   Y: a vector of sample labels from developmental dataset\n\n    **Yields:**\n\n    -   float: r2 score\n\n10. Developmental Test Set Mean Squared Error Score\n\n    `dev_score_mse`\n\n    Calculates the mean squared error score from the developmental dataset\n    predictions.\n\n    **Args:**\n\n    -   estimator: Linear model regressor object\n    -   X: a data frame of normalized values from developmental dataset\n    -   Y: a vector of sample labels from developmental dataset\n\n    **Yields:**\n\n    -   float: mean squared error score\n\n11. Developmental Test Set Explained Variance Score\n\n    `dev_score_evar`\n\n    Calculates the explained variance score for the develomental dataset predictions.\n\n    **Args:**\n\n    -   estimator: Linear model regressor object\n    -   X: a data frame of normalized values from developmental dataset\n    -   Y: a vector of sample labels from developmental data set\n\n    **Yields:**\n\n    -   float: explained variance score\n\n12.  DEV Accuracy Score\n\n    `dev_score_accuracy`\n\n    Calculates the accuracy score from the DEV predictions.\n\n    **Args:**\n\n    -   estimator: Linear model classifier object\n    -   X: a data frame of normalized values from developmental dataset\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: accuracy score\n\n13.  DEV Normalized Mutual Information Score\n\n    `dev_score_nmi`\n\n    Calculates the normalized mutual information score from the DEV predictions.\n\n    **Args:**\n\n    -   estimator: Linear model classifier object\n    -   X: a data frame of normalized values from developmental dataset\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: normalized mutual information score\n\n14.  DEV Area Under ROC Curve Score\n\n    `dev_score_roc`\n\n    Calculates the area under the ROC curve score for the DEV predictions.\n\n    **Args:**\n\n    -   estimator: Linear model classifier object\n    -   X: a data frame of normalized values from developmental dataset\n    -   Y: a vector of sample labels from training data set\n\n    **Yields:**\n\n    -   float: AUC ROC score\n\n<a id="org288aaeb"></a>\n\n### Linear model classes for dRFE\n\n1.  Lasso Class\n\n    `Lasso` and `LassoCV`\n\n    Add feature importance to Lasso class similar to\n    random forest output. LassoCV uses cross-validation for alpha tuning.\n\n2.  Ridge Class\n\n    `Ridge` and `RidgeCV`\n\n    Add feature importance to Ridge class similar to\n    random forest output. LassoCV uses cross-validation for alpha tuning.\n\n3.  ElasticNet Class\n\n    `ElasticNet` and `ElasticNetCV`\n\n    Add feature importance to ElasticNet class similar to\n    random forest output. ElasticNetCV uses cross-validation to chose alpha.\n\n4.  LinearRegression Class\n\n    `LinearRegression`\n\n    Add feature importance to LinearRegression class similar to\n    random forest output.\n\n5. LogisticRegression\n\n    `LogisticRegression`\n\n    Adds feature importance to LogisticRegression class similar to\n    random forest output. This was originally modified from Apua\n    Paquola script.\n\n<a id="org1313shi"></a>\n\n### SVM model classes for dRFE\n\n1.  LinearSVC Class\n\n    `LinearSVC`\n\n    Add feature importance to linear SVC class similar to\n    random forest output.\n\n2.  LinearSVR Class\n\n    `LinearSVR`\n\n    Add feature importance to linear SVR class similar to\n    random forest output.\n\n3.  SGDClassifier Class\n\n    `SGDClassifier`\n\n    Add feature importance to stochastic gradient descent classification\n    class similar to random forest output.\n\n4.  SGDRegressor Class\n\n    `SGDRegressor`\n\n    Add feature importance to stochastic gradient descent regression\n    class similar to random forest output.\n\n<a id="orga29d49b"></a>\n\n### Random forest helper functions\n\n1.  dRFE Subfunction\n\n    `rf_fe`\n\n    Iterate over features to by eliminated by step.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n    -   X: a data frame of training data\n    -   Y: a vector of sample labels from training data set\n    -   n_features_iter: iterator for number of features to keep loop\n    -   features: a vector of feature names\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   RANK: Boolean (True or False)\n\n    **Yields:**\n\n    -   list: a list with number of features, normalized mutual information score, accuracy score, and array of the indices for features to keep\n\n2.  dRFE Step function\n\n    `rf_fe_step`\n\n    Apply random forest to training data, rank features, conduct feature elimination.\n\n    **Args:**\n\n    -   estimator: Random forest classifier object\n    -   X: a data frame of training data\n    -   Y: a vector of sample labels from training data set\n    -   n_features_to_keep: number of features to keep\n    -   features: a vector of feature names\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   RANK: Boolean (True or False)\n\n    **Yields:**\n\n    -   dict: a dictionary with number of features, normalized mutual information score, accuracy score, and selected features\n\n\n<a id="orgbda21bf"></a>\n\n### Linear model helper functions\n\n1.  dRFE Subfunction\n\n    `regr_fe`\n\n    Iterate over features to by eliminated by step.\n\n    **Args:**\n\n    -   estimator: regressor or classifier linear model object\n    -   X: a data frame of training data\n    -   Y: a vector of sample labels from training data set\n    -   n_features_iter: iterator for number of features to keep loop\n    -   features: a vector of feature names\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   dev_size: developmental test set propotion of training\n    -   SEED: random state\n    -   RANK: Boolean (True or False)\n\n    **Yields:**\n\n    -   list: a list with number of features, r2 score, mean square error, expalined variance, and array of the indices for features to keep\n\n2.  dRFE Step function\n\n    `regr_fe_step`\n\n    Split training data into developmental dataset and apply estimator\n    to developmental dataset, rank features, and conduct feature\n    elimination, single steps.\n\n    **Args:**\n\n    -   estimator: regressor or classifier linear model object\n    -   X: a data frame of training data\n    -   Y: a vector of sample labels from training data set\n    -   n_features_to_keep: number of features to keep\n    -   features: a vector of feature names\n    -   fold: current fold\n    -   out_dir: output directory. default \'.\'\n    -   dev_size: developmental test set propotion of training\n    -   SEED: random state\n    -   RANK: Boolean (True or False)\n\n    **Yields:**\n\n    -   dict: a dictionary with number of features, r2 score, mean square error, expalined variance, and selected features\n',
    'author': 'Kynon JM Benjamin',
    'author_email': 'kj.benjamin90@gmail.com',
    'maintainer': 'Kynon JM Benjamin',
    'maintainer_email': 'kj.benjamin90@gmail.com',
    'url': 'https://github.com/paquolalab/dRFEtools.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
