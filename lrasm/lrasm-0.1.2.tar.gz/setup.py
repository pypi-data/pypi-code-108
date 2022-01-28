# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lrasm']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'scipy>=1.7.3,<2.0.0',
 'sklearn>=0.0,<0.1',
 'statsmodels>=0.13.1,<0.14.0']

setup_kwargs = {
    'name': 'lrasm',
    'version': '0.1.2',
    'description': 'A package containing functions to test linearity assumptions for linear regression performed on single or multiple linear regression for a specified dataset',
    'long_description': '# lrasm\n\n# Package for testing linear and multiple linear regression assumptions\n\n\nThis package is built to contain functions to be able to quickly and easily test the linearity assumptions befre preforming linear regression or multiple linear regression for a specified dataset. \n\nThe three assumptions should be satisfied to ensure the effectiveness of a linear regression model for a particular dataset and are described as follows:\n\n-   **No Multicollinearity**: individual predictors within a model should not be linearly correlated to avoid unstable linear estimators\n\n-   **Constant Variance of Residuals (homoscedasticity)**: Since data should be individually and identically distributed, the residuals should be independent of fitted values\n\n-   **Normality of residuals**: Since the conditional expectation of the predicted value should be normal, the error terms of the resulting model should also be normally distributed\n\nThe package contains 3 functions one for checking multicolliniarity, one for checking constant variance and one for checking normality in the residuals.\n\nFunction 1: Multicolliniarity.\n\n- Takes in a pandas dataframe and a VIF threshold and checks if any of the calculated vif values exceed the given threshold. If so, the function will advise the user that this assumtion is violated, and vice versa.\n\n- Returns the Calculated VIF values and a statement telling the user whether or not the assumpton is violated.\n\nFunction 2: Constant Variance.\n\n- Takes in a pandas dataframe containing predictors, a pandas series containing the response, and a variability threshold and checks if the variabiliy of the residuals is contant by comparing it to the given threshold. If the threshold is exceeded the function will advise the user that this assumtion is violated, and vice versa.\n\n- Returns a plot of the fitted values vs residuals, the calculated variability value  and a statement telling the user whether or not the assumpton is violated.\n\nFunction 3: Normality.\n\n- Takes in a pandas dataframe containing predictors, a pandas series containing the response, and a P-value threshold, and preforms a shapiro wilk test for normality. If the P-value of the test does not exceed the threshold, the function will advise the user that this assumtion is violated, and vice versa.\n\n- Returns the Calculated P-value and a statement telling the user whether or not the assumpton is violated.\n\n## Installation\n\n```bash\n$ pip install git+https://github.com/UBC-MDS/lrasm\n```\n\n## Usage\n\n`lrasm` can be used to check linear regression assumptions as follows:\n\n```\nfrom lrasm.homoscedasticity_tst import homoscedasticity_test\nfrom lrasm.multicollinearity_tst import multicollinearity_test\nfrom lrasm.normality_tst import normality_test\nfrom sklearn import datasets\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n# Import/Process Test data:\n\ndata = datasets.load_iris()\niris_df = pd.DataFrame(data=data.data, columns=data.feature_names)\nX = iris_df.drop("sepal width (cm)", axis = 1)\ny = iris_df["petal width (cm)"]\n\n# Test for Normality:\n\np_value, res = normality_test(X, y)\n\n# Test for Homoscedasticity:\n\ncorr_df, plot = homoscedasticity_test(X, y)\n\n# Test for Multicollinearity:\n\nvif_df = multicollinearity_test(X, VIF_thresh = 10)\n```\n\n## Ecosystem\n\nAs of January 2022, there are no other packages that we have found which explicitly evaluate the assumptions made by linear regression. The LR_assumption_test package seeks to fill in this gap and build upon existing python packages. This package aggregates the functions offered by scikit-learn, statsmodels, scipy.stats, matplotlib and more, seeking to build upon them for the purpose of evaluating linear regression models. This is intended to make it more accessible for users to access the functionality of the previously mentioned packages, as well as improve the clarity of results.\n\n## Contributing\n\nAuthors: Yair Guterman, Hatef Rahmani, Song Bo Andy Yang  \nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`lrasm` was created by Yair Guterman, Hatef Rahmani, Song Bo Andy Yang . It is licensed under the terms of the MIT license.\n\n## Credits\n`lrasm` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'Yair Guterman, Hatef Rahmani, Song Bo Andy Yang ',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
