# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['features_creator']

package_data = \
{'': ['*']}

install_requires = \
['Sphinx>=4.4.0,<5.0.0', 'numpy>=1.22.1,<2.0.0', 'pandas>=1.3.5,<2.0.0']

setup_kwargs = {
    'name': 'features-creator',
    'version': '1.1.0',
    'description': 'Helper functions to create new features.',
    'long_description': '# features_creator\n\nHelper functions to create new features for temporal data.\n\n## Contributors\n\n- Nikita Shymberg\n- Rakesh Pandey\n- Son Chau\n- Wenjia Zhu\n\n## Description\n\nThis package aims to speed up and simplify the process of feature engineering for temporal (e.g. weekly or monthly) data.\nIt works with dataframes that have columns whose names follow a pattern and end with a number. For example payment_week_1, payment_week_2, ...\nFor such datasets, commonly engineered features include, among others, the percentage change across time periods, the average across time periods, and the standard deviation across time periods.\n\nThis package defines the following four functions:\n\n- `get_matching_column_names`: Returns a subset of the columns whose names match the pattern. This is a prerequisite for the feature engineering\n- `calculate_average`: Returns the average value across matching columns for each row.\n- `calculate_standard_deviation`: Returns the stadard deviation across matching columns for each row.\n- `calculate_percentage_change`: Returns the percent change across consecutive time periods for each row.\n\n### How does this package fit into the existing ecosystem?\n\nThere are many Python libraries available that facilitate feature engineering,\nthe two most common ones are [Featuretools](https://www.featuretools.com/) and [Feature-engine](https://feature-engine.readthedocs.io/en/1.2.x/).\n`Featuretools` has much more functionality than `features_creator`, but is more heavyweight and comes with a steeper learning curve.\nIt also requires quite a lot of data massaging to get it into the correct format before features can be engineered.\n`Feature-engine` also has a wide variety of functionality, but it is not tailored to temporal data.\n`Feature-engine` is more focused on data imputation, discretization, encoding, and outlier removal.\n\nFor datasets that have columns that follow the pattern `quantity_1`, `quantity_2`, ... `features_creator` is the simplest package for engineering features.\n\n## Installation\n\n```bash\n$ pip install features_creator\n```\n\n## Usage\n\n```python\nimport pandas as pd\nfrom IPython.display import display\nfrom features_creator.features_creator import (\n    get_matching_column_names,\n    calculate_standard_deviation,\n    calculate_average,\n    calculate_percentage_change,\n)\n\n# Example data\ndf = pd.DataFrame(\n    {\n        "subscriber_id": [1, 2, 3],\n        "data_usage1": [10, 5, 3],  # 1 represent data usage in prediction month (m) - 1\n        "data_usage2": [4, 5, 6],  # m - 2\n        "data_usage3": [7, 8, 9],  # m - 3\n        "data_usage4": [10, 11, 12],  # m - 4\n        "data_usage5": [13, 14, 15],  # m - 5\n        "othercolumn": [5, 6, 7],  # Other example column\n        "data_usage_string6": [5, 6, 7],  # Other example column with an integer\n    }\n)\n\n# Get matching column names\ncolumns = get_matching_column_names(df, "data_usage")\n\n# Calculate standard deviation across time periods\ndf["std_monthly_data_usage"] = calculate_standard_deviation(df, "data_usage")\n\n# Calculate average across time periods\ndf["avg_monthly_data_usage"] = calculate_average(df, "data_usage")\n\n# Calculate percentage change 2 months over 2 months\ndf["percent_change_data_usage"] = calculate_percentage_change(\n    df, "data_usage", compare_period=(2, 2)\n)\n\n# Display data\ndisplay(\n    df[[\n        "subscriber_id",\n        "std_monthly_data_usage",\n        "avg_monthly_data_usage",\n        "percent_change_data_usage",\n    ]]\n)\n   subscriber_id  std_monthly_data_usage  avg_monthly_data_usage  percent_change_data_usage\n0              1                3.059412                     8.8                 -17.647059\n1              2                3.498571                     8.6                 -47.368421\n2              3                4.242641                     9.0                 -57.142857\n```\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`features_creator` was created by DSCI_524_GROUP26. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`features_creator` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'DSCI_524_GROUP26',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
