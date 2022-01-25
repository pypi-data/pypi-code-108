# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bender',
 'bender.data_exporter',
 'bender.data_importer',
 'bender.data_importer.tests',
 'bender.evaluator',
 'bender.explorer',
 'bender.explorer.tests',
 'bender.exporter',
 'bender.metric',
 'bender.metric.tests',
 'bender.model_exporter',
 'bender.model_exporter.tests',
 'bender.model_loader',
 'bender.model_trainer',
 'bender.model_trainer.tests',
 'bender.pipeline',
 'bender.pipeline.tests',
 'bender.split_strategy',
 'bender.split_strategy.tests',
 'bender.tests',
 'bender.trained_model',
 'bender.trained_model.tests',
 'bender.transformation',
 'bender.transformation.tests']

package_data = \
{'': ['*']}

install_requires = \
['aioaws>=0.12,<0.13',
 'asyncpg>=0.24.0,<0.25.0',
 'databases>=0.5.3,<0.6.0',
 'matplotlib>=3.4.3,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'sklearn>=0.0,<0.1',
 'xgboost>=1.5.0,<2.0.0']

setup_kwargs = {
    'name': 'benderml',
    'version': '0.1.11',
    'description': 'A Python package that makes ML processes easier, faster and less error prone',
    'long_description': '# Bender 🤖\n\nA Python package for faster, safer, and simpler ML processes.\n\n## Installation\n\n`pip install benderml`\n\n**Usage:**\n\n```python\nfrom bender.importers import DataImporters\n\npre_processed_data = await DataImporters.csv("file/to/data.csv").process([...]).run()\n```\n\n## Why use `bender`?\n\nBender will make your machine learning processes, faster, safer, simpler while at the same time making it easy and flexible. This is done by providing a set base component, around the core processes that will take place in a ML pipeline process. While also helping you with type hints about what your next move could be.\n\n## Pipeline Safety\n\nThe whole pipeline is build using generics from Python\'s typing system. Resulting in an improved developer experience, as the compiler can know if your pipeline\'s logic makes sense before it has started.\n\n## Load a data set\n\nBender makes most of the `sklearn` datasets available through the `DataImporters.data_set(...)` importer. Here will you need to pass an enum to define which dataset you want. It is also possible to load the data from sql, append different data sources and cache, and it is as simple as:\n```python\nfrom bender.importers import DataImporters\n\n# Predifined data set\nDataImporters.data_set(DataSets.IRIS)\n\n# Load SQL\nDataImporters.sql("url", "SELECT ...")\n\n# Cache a sql import\nDataImporters.sql("url", "SELECT ...")\n    .cached("path/to/cache")\n    .append(\n        # Add more data from a different source (with same features)\n        DataImporters.sql(...)\n    )\n```\n\n## Processing\nWhen the data has been loaded is usually the next set to process the data in some way. `bender` will therefore provide different components that transforms features. Therefore making it easier to keep your logic consistent over multiple projects.\n\n```python\nfrom bender.transformations import Transformations\n\nDataImporters.data_set(DataSets.IRIS)\n    .process([\n        # pl exp = e^(petal length)\n        Transformations.exp_shift(\'petal length (cm)\', output=\'pl exp\'),\n\n        # Alternative to `exp_shift`\n        Transformations.compute(\'pl exp\', lambda df: np.exp(df[\'petal length (cm)\'])),\n\n        # purchases = mean value of the json price values\n        Transformations.unpack_json("purchases", key="price", output_feature="price", policy=UnpackPolicy.median_number()),\n\n        ...\n    ])\n```\n\n## EDA\n\nFor view how the data is distribuated, is it also possible to explore the data.\n\n```python\nfrom bender.explorers import Explorers\n\nawait (DataImporters.data_set(DataSets.IRIS)\n    .process([...])\n    .explore([\n        # Display all features in a hist\n        Explorers.histogram(target=\'target\'),\n\n        # Display corr matrix and logs which features you could remove\n        Explorers.correlation(input_features),\n\n        # View how features relate in 2D\n        Explorers.pair_plot(\'target\'),\n    ])\n```\n\n## Splitting into train and test sets\nThere are many ways we can train and test, it is therefore easy to choose and switch between how it is done with `bender`.\n\n```python\nfrom bender.split_strategies import SplitStrategies\n\nawait (DataImporters.data_set(DataSets.IRIS)\n    .process([...])\n\n    # Have 70% as train and 30 as test\n    .split(SplitStrategies.ratio(0.7))\n\n    # Have 70% of each target group in train and the rest in test\n    .split(SplitStrategies.uniform_ratio("target", 0.7))\n\n    # Sorts by the key and taks the first 70% as train\n    .split(SplitStrategies.sorted_ratio("target", 0.7))\n```\n\n## Training\nAfter you have split the data set into train and test, then you can train with the following.\n\n```python\nfrom bender.model_trainers import Trainers\n\nawait (DataImporters.data_set(DataSets.IRIS)\n    .split(...)\n    .train(\n        # train kneighbours on the train test\n        Trainers.kneighbours(),\n        input_features=[...],\n        target_feature="target"\n    )\n```\n\n## Evaluate\nAfter you have a model will it be smart to test how well it works.\n\n```python\nfrom bender.evaluators import Evaluators\n\nawait (DataImporters.data_set(DataSets.IRIS)\n    .split(...)\n    .train(...)\n    .evaluate([\n        # Only present the confusion matrix\n        Evaluators.confusion_matrix(),\n        Evaluators.roc_curve(),\n        Evaluators.precision_recall(),\n    ])\n```\n\n## Save model\nAt last would you need to store the model. You can therefore select one of manny exporters.\n```python\nfrom bender.exporters import Exporters\n\nawait (DataImporters.data_set(DataSets.IRIS)\n    .split(...)\n    .train(...)\n    .export_model(Exporters.aws_s3(...))\n```\n\n## Predict\n```python\nModelLoaders\n    .aws_s3("path/to/model", s3_config)\n    .import_data(\n        DataImporters.sql(sql_url, sql_query)\n    )\n    .predict()\n```\n\n## Extract result\n```python\nModelLoaders\n    .aws_s3(...)\n    .import_data(...)\n    .predict()\n    .extract(prediction_as="target", metadata=[\'entry_id\'], exporter=DataExporters.disk("predictions.csv"))\n```\n\n## Examples\nAn example of the IRIS data set which trains a model to perfection\n\n```python\nawait (DataImporters.data_set(DataSets.IRIS)\n    .process([\n        Transformations.exp_shift(\'petal length (cm)\', output=\'pl exp\'),\n        Transformations.exp_shift(\'petal width (cm)\', output=\'pw exp\'),\n    ])\n    .explore([\n        Explorers.histogram(target=\'target\'),\n        Explorers.correlation(input_features),\n        Explorers.pair_plot(\'target\'),\n    ])\n    .split(SplitStrategies.uniform_ratio("target", 0.7))\n    .train(Trainers.kneighbours(), input_features=input_features, target_feature="target")\n    .evaluate([\n        Evaluators.confusion_matrix()\n    ])\n    .metric(Metrics.log_loss())\n    .run())\n```\n\n## XGBoost Example\nBelow is a simple example for training a XGBoosted tree\n```python\nDataImporters.sql(sql_url, sql_query)\n\n    .process([ # Preproces the data\n        # Extract advanced information from json data\n        Transformations.unpack_json("purchases", key="price", output_feature="price", policy=UnpackPolicy.median_number())\n\n        Transformations.log_normal_shift("y_values", "y_log"),\n\n        # Get date values from a date feature\n        Transformations.date_component("month", "date", output_feature="month_value"),\n    ])\n    .split(SplitStrategies.ratio(0.7))\n\n    # Train a XGBoosted Tree model\n    .train(\n        Trainers.xgboost(),\n        input_features=[\'y_log\', \'price\', \'month_value\', \'country\', ...],\n        target_feature=\'did_buy_product_x\'\n    )\n    .evaluate([\n        Evaluators.roc_curve(),\n        Evaluators.confusion_matrix(),\n        Evaluators.precision_recall(\n            # Overwrite where to export the evaluated result\n            Exporter.disk("precision-recall.png")\n        ),\n    ])\n```\n\n## Predicting Example\n\nBelow will a model be loaded from a AWS S3 bucket, preprocess the data, and predict the output.\nThis will also make sure that the features are valid before predicting.\n\n```python\nModelLoaders\n    # Fetch Model\n    .aws_s3("path/to/model", s3_config)\n\n    # Load data\n    .import_data(\n        DataImporters.sql(sql_url, sql_query)\n            # Caching import localy for 1 day\n            .cached("cache/path")\n    )\n    # Preproces the data\n    .process([\n        Transformations.unpack_json(...),\n        ...\n    ])\n    # Predict the values\n    .predict()\n```\n',
    'author': 'Mats E. Mollestad',
    'author_email': 'mats@mollestad.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/otovo/bender',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.7,<4.0.0',
}


setup(**setup_kwargs)
