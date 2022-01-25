# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['akerbp', 'akerbp.mlpet', 'akerbp.mlpet.Datasets', 'akerbp.mlpet.tests']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML==5.4.1',
 'cognite-sdk>=2.31.0',
 'imbalanced-learn>=0.8.0',
 'joblib==1.0.1',
 'numpy>=1.19.5',
 'pandas>=1.3.2',
 'scikit-learn>=0.24.2',
 'scipy>=1.7.1']

setup_kwargs = {
    'name': 'akerbp.mlpet',
    'version': '1.1.0',
    'description': 'Package to prepare well log data for ML projects.',
    'long_description': '# akerbp.mlpet\n\nPreprocessing tools for Petrophysics ML projects at Eureka\n\n## Installation\n\n- Install the package by running the following (requires python 3.8 or later)\n\n        pip install akerbp.mlpet\n\n\n## Quick start\n\n- For a short example of how to use the mlpet Dataset class for pre-processing data see below. Please refer to the tests folder of this repository for more examples:\n\n        from akerbp.mlpet import Dataset\n        from akerbp.mlpet import utilities\n\n        # Instantiate an empty dataset object using the example settings and mappings provided\n        ds = Dataset(\n                settings="settings.yaml", # Absolute file paths are preferred\n                mappings="mappings.yaml", # Absolute file paths are preferred\n                folder_path=r"./", # Absolute file paths are preferred\n        )\n\n        # Populate the dataset with data from a file (support for multiple file formats and direct cdf data collection exists)\n        ds.load_from_pickle(r"data.pkl") # Absolute file paths are preferred\n\n        # The original data will be kept in ds.df_original and will remain unchanged\n        print(ds.df_original.head())\n\n        # Split the data into train-validation sets\n        df_train, df_test = utilities.train_test_split(\n                df=ds.df_original,\n                target_column=ds.label_column,\n                id_column=ds.id_column,\n                test_size=0.3,\n        )\n\n        # Preprocess the data for training according to default workflow\n        # print(ds.default_preprocessing_workflow) <- Uncomment to see what the workflow does\n        df_preprocessed = ds.preprocess(df_train)\n\n\nThe procedure will be exactly the same for any other dataset class. The only difference will be in the "settings". For a full list of possible settings keys see either the [built documentation](docs/build/html/akerbp.mlpet.html) or the akerbp.mlpet.Dataset class docstring. Make sure that the curve names are consistent with those in the dataset.\n\nThe loaded data is NOT mapped at load time but rather at preprocessing time (i.e. when preprocess is called).\n\n## API Documentation\n\nFull API documentaion of the package can be found under the [docs](docs/build/html/index.html) folder once you have run the make html command.\n\n## For developers\n\n- to make the API documentation, from the root directory of the project run (assuming you have installed all development dependencies)\n\n        cd docs/\n        make html\n\n- to install mlpet in editable mode for use in another project, there are two\n  possible solutions dependent on the tools being used:\n   1. If the other package uses poetry, please refer to this [guide](https://github.com/python-poetry/poetry/discussions/1135#discussioncomment-145756)\n   2. If you are not using poetry (using conda, pyenv or something else), you will first need to:\n      1. Convert the pyproject.toml script to a setup.py file by running the following line:\n\n                curl -Ls https://raw.githubusercontent.com/sdss/flicamera/main/create_setup.py | python3\n\n      2. You can now pip install -e the package in the relevant virtual environment after you have activated it\n## License\n\nakerbp.mlpet Copyright 2021 AkerBP ASA\n\nLicensed under the Apache License, Version 2.0 (the "License");\nyou may not use this file except in compliance with the License.\nYou may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an "AS IS" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n',
    'author': 'Flavia Dias Casagrande',
    'author_email': 'flavia.dias.casagrande@akerbp.com',
    'maintainer': 'Yann Van Crombrugge',
    'maintainer_email': 'yann.vancrombrugge@akerbp.com',
    'url': 'https://bitbucket.org/akerbp/akerbp.mlpet/src/master/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
