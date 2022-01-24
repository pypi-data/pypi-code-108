# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['whylogs',
 'whylogs.app',
 'whylogs.cli',
 'whylogs.core',
 'whylogs.core.metrics',
 'whylogs.core.statistics',
 'whylogs.core.statistics.datatypes',
 'whylogs.core.types',
 'whylogs.features',
 'whylogs.io',
 'whylogs.logs',
 'whylogs.mlflow',
 'whylogs.proto',
 'whylogs.util',
 'whylogs.viz',
 'whylogs.viz.matplotlib',
 'whylogs.whylabs_client']

package_data = \
{'': ['*'],
 'whylogs': ['viewer/*',
             'viewer/css/*',
             'viewer/example/*',
             'viewer/fonts/*',
             'viewer/images/*',
             'viewer/js/*']}

install_requires = \
['boto3>=1.14.1',
 'botocore>=1.17.44',
 'click>=7.1.2',
 'jsonschema>=3.2.0',
 'marshmallow>=3.7.1',
 'matplotlib>=3.0.3,<4.0.0',
 'numpy>=1.18.0',
 'pandas>=1.0.0',
 'protobuf>=3.15.5',
 'puremagic>=1.10,<2.0',
 'requests>=2.22.0',
 'smart-open>=4.1.2',
 'tqdm>=4.60.0,<5.0.0',
 'whylabs-client>=0.1.1.dev0,<0.2.0',
 'whylabs-datasketches>=2.2.0b1']

entry_points = \
{'console_scripts': ['whylogs = whylogs.cli:main',
                     'whylogs-demo = whylogs.cli:demo_main']}

setup_kwargs = {
    'name': 'whylogs',
    'version': '0.6.23',
    'description': 'Profile and monitor your ML data pipeline end-to-end',
    'long_description': '# whylogs: A Data and Machine Learning Logging Standard\n\n\n[![License](http://img.shields.io/:license-Apache%202-blue.svg)](https://github.com/whylabs/whylogs-python/blob/mainline/LICENSE)\n[![PyPI version](https://badge.fury.io/py/whylogs.svg)](https://badge.fury.io/py/whylogs)\n[![Coverage Status](https://coveralls.io/repos/github/whylabs/whylogs/badge.svg?branch=mainline)](https://coveralls.io/github/whylabs/whylogs?branch=mainline)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/4490/badge)](https://bestpractices.coreinfrastructure.org/projects/4490)\n[![PyPi Downloads](https://pepy.tech/badge/whylogs)](https://pepy.tech/project/whylogs)\n![CI](https://github.com/whylabs/whylogs-python/workflows/whylogs%20CI/badge.svg)\n[![Maintainability](https://api.codeclimate.com/v1/badges/442f6ca3dca1e583a488/maintainability)](https://codeclimate.com/github/whylabs/whylogs-python/maintainability)\n\n\nwhylogs is an open source standard for data and ML logging\n\nwhylogs logging agent is the easiest way to enable logging, testing, and monitoring in an ML/AI application. The lightweight agent profiles data in real time, collecting thousands of metrics from structured data, unstructured data, and ML model predictions with zero configuration. \n\nwhylogs can be installed in any Python, Java or Spark environment; it can be deployed as a container and run as a sidecar; or invoked through various ML tools (see integrations). \n\nwhylogs is designed by data scientists, ML engineers and distributed systems engineers to log data in the most cost-effective, scalable and accurate manner. No sampling. No post-processing. No manual configurations.\n\nwhylogs is released under the Apache 2.0 open source license. It supports many languages and is easy to extend. This repo contains the whylogs CLI, language SDKs, and individual libraries are in their own repos.\n\nThis repository contains both a [Python implementation](https://github.com/whylabs/whylogs/tree/mainline/src/whylogs) and a [Java implementation](https://github.com/whylabs/whylogs/tree/mainline/java).\n\nIf you have any questions, comments, or just want to hang out with us, please join [our Slack channel](http://join.slack.whylabs.ai/).\n\n\n- [Getting started](#getting-started)\n- [Features](#features)\n- [Data Types](#data-types)\n- [Integrations](#integrations)\n- [Examples](#examples)\n- [Community](#community)\n- [Roadmap](#roadmap)\n- [Contribute](#contribute)\n\n\n## Getting started<a name="getting-started" />\n\n\n### Using pip\n\nInstall whylogs using the pip package manager by running\n\n```\npip install whylogs\n```\n\n### From source \n\n- Download the source code by cloning the repository or by pressing [Download ZIP](https://github.com/whylabs/whylogs-python/archive/master.zip) on this page. \n- You\'ll need to install poetry in order to install dependencies using the lock file in this project. Follow [their docs](https://python-poetry.org/docs/) to get it set up.\n- Run the following command at the root of the source code:\n\n```\nmake install # installs dependencies\nmake         # builds the wheel\n```\n\n## Quickly Logging Data\n\nwhylogs is easy to get up and runnings\n\n```python\nfrom whylogs import get_or_create_session\nimport pandas as pd\n\nsession = get_or_create_session()\n\ndf = pd.read_csv("path/to/file.csv")\n\nwith session.logger(dataset_name="my_dataset") as logger:\n    \n    #dataframe\n    logger.log_dataframe(df)\n\n    #dict\n    logger.log({"name": 1})\n\n    #images\n    logger.log_image("path/to/image.png")\n```\n\nwhylogs collects approximate statistics and sketches of data on a column-basis into a statistical profile. These metrics include:\n\n- Simple counters: boolean, null values, data types.\n- Summary statistics: sum, min, max, median, variance.\n- Unique value counter or cardinality: tracks an approximate unique value of your feature using HyperLogLog algorithm.\n- Histograms for numerical features. whyLogs binary output can be queried to with dynamic binning based on the shape of your data.\n- Top frequent items (default is 128). Note that this configuration affects the memory footprint, especially for text features.\n\n\n### Multiple Profile Plots\n\nTo view your logger profiles you can use, methods within `whylogs.viz`: \n\n```python\nvizualization = ProfileVisualizer()\nvizualization.set_profiles([profile_day_1, profile_day_2])\nfigure= vizualization.plot_distribution("<feature_name>")\nfigure.savefig("/my/image/path.png")\n```\n\nIndividual profiles are saved to disk, AWS S3, or WhyLabs API, automatically when loggers are closed, per the configuration found in the Session configuration.\n\nCurrent profiles from active loggers can be loaded from memory with:\n```python\nprofile = logger.profile()\n```\n\n### Profile Viewer\n\nYou can also load a local profile viewer, where you upload the `json` summary file. The default path for the json files is set as `output/{dataset_name}/{session_id}/json/dataset_profile.json`.\n\n```python\nfrom whylogs.viz import profile_viewer\nprofile_viewer()\n```\n\nThis will open a viewer on your default browser where you can load a profile json summary, using the `Select JSON profile` button:\nOnce the json is selected you can view your profile\'s features and \nassociated and statistics.\n\n<img src="https://whylabs-public.s3-us-west-2.amazonaws.com/assets/whylogs-viewer.gif" title="whylogs HTML viewer demo">\n\n## Documentation \n\nThe [documentation](https://docs.whylabs.ai/docs/) of this package is generated automatically. \n\n## Features\n\n- Accurate data profiling: whylogs calculates statistics from 100% of the data, never requiring sampling, ensuring an accurate representation of data distributions\n- Lightweight runtime: whylogs utilizes approximate statistical methods to achieve minimal memory footprint that scales with the number of features in the data\n- Any architecture: whylogs scales with your system, from local development mode to live production systems in multi-node clusters, and works well with batch and streaming architectures\n- Configuration-free: whylogs infers the schema of the data, requiring zero manual configuration to get started\n- Tiny storage footprint: whylogs turns data batches and streams into statistical fingerprints, 10-100MB uncompressed\n- Unlimited metrics: whylogs collects all possible statistical metrics about structured or unstructured data\n\n\n## Data Types<a name="data-types" />\nWhylogs supports both structured and unstructured data, specifically: \n\n| Data type  | Features | Notebook Example |\n| --- | --- | ---|\n|Structured Data | Distribution, cardinality, schema, counts, missing values | [Getting started with structured data](https://github.com/whylabs/whylogs-examples/blob/mainline/python/GettingStarted.ipynb) | \n| Images | exif metadata, derived pixels features,  bounding boxes | [Getting started with images](https://github.com/whylabs/whylogs-examples/blob/mainline/python/Logging_Images.ipynb) |\n| Video  | In development  | [Github Issue #214](https://github.com/whylabs/whylogs/issues/214) |\n| Tensors | derived 1d features (more in developement) | [Github Issue #216](https://github.com/whylabs/whylogs/issues/216) |\n| Text | top k values, counts, cardinality | [String Features](https://github.com/whylabs/whylogs/blob/mainline/examples/String_Features.ipynb) |\n| Audio | In developement | [Github Issue #212](https://github.com/whylabs/whylogs/issues/212) | \n\n\n## Integrations\n\n![current integration](images/integrations.001.png)\n| Integration | Features | Resources |\n| --- | --- | ---  | \n| Spark | Run whylogs in Apache Spark environment|  <ul><li>[Code Example](https://github.com/whylabs/whylogs-examples/blob/mainline/scala/src/main/scala/WhyLogsDemo.scala)</li></ul> | \n| Pandas | Log and monitor any pandas dataframe |  <ul><li>[Notebook Example](https://github.com/whylabs/whylogs-examples/blob/mainline/python/logging_example.ipynb)</li><li>[whylogs: Embrace Data Logging](https://whylabs.ai/blog/posts/whylogs-embrace-data-logging)</li></ul>  |\n| Kafka | Log and monitor Kafka topics with whylogs| <ul><li>[Notebook Example](https://github.com/whylabs/whylogs-examples/blob/mainline/python/Kafka.ipynb)</li><li> [Integrating whylogs into your Kafka ML Pipeline](https://whylabs.ai/blog/posts/integrating-whylogs-into-your-kafka-ml-pipeline) </li></ul>|\n| MLflow | Enhance MLflow metrics with whylogs:  | <ul><li>[Notebook Example](https://github.com/whylabs/whylogs-examples/blob/mainline/python/MLFlow%20Integration%20Example.ipynb)</li><li>[Streamlining data monitoring with whylogs and MLflow](https://whylabs.ai/blog/posts/on-model-lifecycle-and-monitoring)</li></ul> |\n| Github actions | Unit test data with whylogs and github actions| <ul><li>[Notebook Example](https://github.com/whylabs/whylogs-examples/tree/mainline/github-actions)</li></ul> |\n| RAPIDS |  Use whylogs in RAPIDS environment | <ul><li>[Notebook Example](https://github.com/whylabs/whylogs-examples/blob/mainline/python/RAPIDS%20GPU%20Integration%20Example.ipynb)</li><li>[Monitoring High-Performance Machine Learning Models with RAPIDS and whylogs](https://whylabs.ai/blog/posts/monitoring-high-performance-machine-learning-models-with-rapids-and-whylogs)</li></ul> |\n| Java | Run whylogs in Java environment| <ul><li>[Notebook Example](https://github.com/whylabs/whylogs-examples/blob/mainline/java/demo1/src/main/java/com/whylogs/examples/WhyLogsDemo.java)</li></ul>  |\n| Docker | Run whylogs as in Docker |  <ul><li>[Rest Container](https://docs.whylabs.ai/docs/integrations-rest-container)</li></ul>| \n| AWS S3 |  Store whylogs profiles in S3 | <ul><li>[S3 example](https://github.com/whylabs/whylogs-examples/blob/mainline/python/S3%20example.ipynb)</li></ul>\n\n## Examples\nFor a full set of our examples, please check out [whylogs-examples](https://github.com/whylabs/whylogs-examples).\n\nCheck out our example notebooks with Binder: [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/whylabs/whylogs-examples/HEAD)\n- [Getting Started notebook](https://github.com/whylabs/whylogs-examples/blob/mainline/python/GettingStarted.ipynb)\n- [Logging Example notebook](https://github.com/whylabs/whylogs-examples/blob/mainline/python/logging_example.ipynb)\n- [Logging Images](https://github.com/whylabs/whylogs-examples/blob/mainline/python/Logging_Images.ipynb)\n- [MLflow Integration](https://github.com/whylabs/whylogs-examples/blob/mainline/python/MLFlow%20Integration%20Example.ipynb)\n\n\n## Roadmap\n\nwhylogs is maintained by [WhyLabs](https://whylabs.ai).\n\n## Community\n\nIf you have any questions, comments, or just want to hang out with us, please join [our Slack channel](http://join.slack.whylabs.ai/).\n\n## Contribute\n\nWe welcome contributions to whylogs. Please see our [contribution guide](https://github.com/whylabs/whylogs/blob/mainline/CONTRIBUTING.md) and our [development guide](https://github.com/whylabs/whylogs/blob/mainline/DEVELOPMENT.md) for details.\n',
    'author': 'WhyLabs.ai',
    'author_email': 'support@whylabs.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://docs.whylabs.ai',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<3.10',
}


setup(**setup_kwargs)
