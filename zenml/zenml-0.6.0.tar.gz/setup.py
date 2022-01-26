# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['zenml',
 'zenml.artifact_stores',
 'zenml.artifacts',
 'zenml.cli',
 'zenml.config',
 'zenml.container_registries',
 'zenml.integrations',
 'zenml.integrations.airflow',
 'zenml.integrations.airflow.orchestrators',
 'zenml.integrations.aws',
 'zenml.integrations.aws.artifact_stores',
 'zenml.integrations.aws.io',
 'zenml.integrations.dash',
 'zenml.integrations.dash.visualizers',
 'zenml.integrations.evidently',
 'zenml.integrations.evidently.steps',
 'zenml.integrations.evidently.visualizers',
 'zenml.integrations.facets',
 'zenml.integrations.facets.visualizers',
 'zenml.integrations.gcp',
 'zenml.integrations.gcp.artifact_stores',
 'zenml.integrations.gcp.io',
 'zenml.integrations.graphviz',
 'zenml.integrations.graphviz.visualizers',
 'zenml.integrations.kubeflow',
 'zenml.integrations.kubeflow.metadata_stores',
 'zenml.integrations.kubeflow.orchestrators',
 'zenml.integrations.mlflow',
 'zenml.integrations.plotly',
 'zenml.integrations.plotly.visualizers',
 'zenml.integrations.pytorch',
 'zenml.integrations.pytorch.materializers',
 'zenml.integrations.pytorch_lightning',
 'zenml.integrations.pytorch_lightning.materializers',
 'zenml.integrations.sklearn',
 'zenml.integrations.sklearn.helpers',
 'zenml.integrations.sklearn.materializers',
 'zenml.integrations.sklearn.steps',
 'zenml.integrations.tensorflow',
 'zenml.integrations.tensorflow.materializers',
 'zenml.integrations.tensorflow.steps',
 'zenml.integrations.whylogs',
 'zenml.integrations.whylogs.materializers',
 'zenml.integrations.whylogs.steps',
 'zenml.integrations.whylogs.visualizers',
 'zenml.io',
 'zenml.materializers',
 'zenml.metadata_stores',
 'zenml.orchestrators',
 'zenml.orchestrators.local',
 'zenml.pipelines',
 'zenml.pipelines.builtin_pipelines',
 'zenml.post_execution',
 'zenml.stack',
 'zenml.steps',
 'zenml.steps.builtin_steps',
 'zenml.steps.step_interfaces',
 'zenml.utils',
 'zenml.visualizers']

package_data = \
{'': ['*']}

install_requires = \
['analytics-python>=1.4.0,<2.0.0',
 'apache-beam>=2.30.0,<3.0.0',
 'click>=8.0.1,<9.0.0',
 'distro>=1.6.0,<2.0.0',
 'gitpython>=3.1.18,<4.0.0',
 'ml-pipelines-sdk>=1.3.0,<2.0.0',
 'pandas>=1.1.5,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'pyyaml>=5.4.1,<6.0.0',
 'rich>=11.0.0,<12.0.0',
 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['zenml = zenml.cli.cli:cli']}

setup_kwargs = {
    'name': 'zenml',
    'version': '0.6.0',
    'description': 'ZenML: Write production-ready ML code.',
    'long_description': '<div align="center">\n    <img src="https://zenml.io/assets/social/github.svg">\n</div>\n\n# 👀 What is ZenML?\n\n**ZenML** is an extensible, open-source MLOps framework to create production-ready machine learning pipelines. Built for data scientists, it has a simple, flexible syntax, is cloud- and tool-agnostic, and has interfaces/abstractions that are catered towards ML workflows.\n\nAt its core, **ZenML pipelines execute ML-specific workflows** from sourcing data to splitting, preprocessing, training, all the way to the evaluation of results and even serving. There are many built-in batteries to support common ML development tasks. ZenML is not here to replace the great tools that solve these individual problems. Rather, it **integrates natively with popular ML tooling** and gives standard abstraction to write your workflows.\n\n🎉 **Version 0.6.0 out now!** [Check out the release notes here](https://github.com/zenml-io/zenml/releases).\n\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zenml)](https://pypi.org/project/zenml/)\n[![PyPI Status](https://pepy.tech/badge/zenml)](https://pepy.tech/project/zenml)\n![GitHub](https://img.shields.io/github/license/zenml-io/zenml)\n[![Codecov](https://codecov.io/gh/zenml-io/zenml/branch/main/graph/badge.svg)](https://codecov.io/gh/zenml-io/zenml)\n[![Interrogate](docs/interrogate.svg)](https://interrogate.readthedocs.io/en/latest/)\n![Main Workflow Tests](https://github.com/zenml-io/zenml/actions/workflows/main.yml/badge.svg)\n\n<div align="center">\nJoin our <a href="https://zenml.io/slack-invite" target="_blank">\n    <img width="25" src="https://cdn3.iconfinder.com/data/icons/logos-and-brands-adobe/512/306_Slack-512.png" alt="Slack"/>\n<b>Slack Community</b> </a> and become part of the ZenML family\n</div>\n<div align="center"> Give us a \n    <img width="25" src="https://cdn.iconscout.com/icon/free/png-256/github-153-675523.png" alt="Slack"/>\n<b>GitHub star</b> to show your love\n</div>\n<div align="center"> \n    <b>NEW: </b> <a href="https://zenml.io/discussion" target="_blank"><img width="25" src="https://cdn1.iconfinder.com/data/icons/social-17/48/like-512.png" alt="Vote"/><b> Vote</b></a> on the next ZenML features \n</div>\n\n<br>\n\n![Before and after ZenML](docs/book/assets/sam-side-by-side-full-text.png)\n\n# 🤖 Why use ZenML?\n\nZenML pipelines are designed to be written early on the development lifecycle. Data scientists can explore their pipelines as they develop towards production, switching stacks from local to cloud deployments with ease. You can read more about why we started building ZenML [on our blog](https://blog.zenml.io/why-zenml/). By using ZenML in the early stages of your project, you get the following benefits:\n\n- **Reproducibility** of training and inference workflows\n- A **simple and clear** way to represent the steps of your pipeline in code\n- **Plug-and-play integrations**: bring all your favorite tools together\n- Easy switching between local and cloud stacks\n- Painless **deployment and configuration** of infrastructure\n- **Scale up** your stack transparently and logically to suit your training and deployment needs\n\n# 📖 Learn More\n\n| ZenML Resources | Description |\n| ------------- | - |\n| 🧘\u200d♀️ **[ZenML 101]** | New to ZenML? Here\'s everything you need to know! |\n| ⚛️ **[Core Concepts]** | Some key terms and concepts we use. |\n| 🗃 **[Functional API Guide]** | Build production ML pipelines with simple functions. |\n| 🚀 **[New in v0.6.0]** | New features, bug fixes. |\n| 🗳 **[Vote for Features]** | Pick what we work on next! |\n| 📓 **[Docs]** | Full documentation for creating your own ZenML pipelines. |\n| 📒 **[API Reference]** | The detailed reference for ZenML\'s API. |\n| ⚽️ **[Examples]** | Learn best through examples where ZenML is used? We\'ve got you covered. |\n| 📬 **[Blog]** | Use cases of ZenML and technical deep dives on how we built it. |\n| 🔈 **[Podcast]** | Conversations with leaders in ML, released every 2 weeks. |\n| 📣 **[Newsletter]** | We build ZenML in public. Subscribe to learn how we work. |\n| 💬 **[Join Slack]** | Need help with your specific use case? Say hi on Slack! |\n| 🗺 **[Roadmap]** | See where ZenML is working to build new features. |\n| 🙋\u200d♀️ **[Contribute]** | How to contribute to the ZenML project and code base. |\n\n[ZenML 101]: https://docs.zenml.io/\n[Core Concepts]: https://docs.zenml.io/core-concepts\n[Functional API Guide]: https://docs.zenml.io/v/docs/guides/functional-api\n[New in v0.6.0]: https://github.com/zenml-io/zenml/releases\n[Vote for Features]: https://zenml.io/discussion\n[Docs]: https://docs.zenml.io/\n[API Reference]: https://apidocs.zenml.io/\n[Examples]: https://github.com/zenml-io/zenml/tree/main/examples\n[Blog]: https://blog.zenml.io/\n[Podcast]: https://podcast.zenml.io/\n[Newsletter]: https://zenml.io/newsletter/\n[Join Slack]: https://zenml.io/slack-invite/\n[Roadmap]: https://zenml.io/roadmap\n[Contribute]: https://github.com/zenml-io/zenml/blob/main/CONTRIBUTING.md\n\n# 🎮 Features\n\n### 1. 🗃 Use Caching across (Pipelines As) Experiments\n\nZenML makes sure for every pipeline you can trust that:\n\n- Code is versioned\n- Data is versioned\n- Models are versioned\n- Configurations are versioned\n\nYou can utilize caching to help iterate quickly through ML experiments. (Read [our blogpost](https://blog.zenml.io/caching-ml-pipelines/) to learn more!)\n\n### 2. ♻️ Leverage Powerful Integrations\n\nOnce code is organized into a ZenML pipeline, you can supercharge your ML development with [powerful integrations](https://docs.zenml.io/features/integrations) on multiple [MLOps stacks](https://docs.zenml.io/core-concepts). There are lots of moving parts for all the MLOps tooling and infrastructure you require for ML in production and ZenML aims to bring it all together under one roof.\n\nWe currently support [Airflow](https://airflow.apache.org/) and [Kubeflow](https://www.kubeflow.org/) as third-party orchestrators for your ML pipeline code. ZenML steps can be built from any of the other tools you usually use in your ML workflows, from [`scikit-learn`](https://scikit-learn.org/stable/) to [`PyTorch`](https://pytorch.org/) or [`TensorFlow`](https://www.tensorflow.org/).\n\n![ZenML is the glue](docs/book/assets/zenml-is-the-glue.jpeg)\n\n### 3. ☁️ Scale to the Cloud\n\nSwitching from local experiments to cloud-based pipelines doesn\'t need to be complicated. ZenML supports running pipelines on Kubernetes clusters in the cloud through our [Kubeflow](https://www.kubeflow.org/) integration. Switching from your local stack to a cloud stack is easy to do with our CLI tool.\n\n### 4. 🧩 Visualize the Steps of your Pipeline\n\nIt’s not uncommon for pipelines to be made up of many steps, and those steps can interact and intersect with one another in often complex patterns. We’ve built a way for you to inspect what’s going on with your ZenML pipeline:\n\n![Here\'s what the pipeline lineage tracking visualizer looks like](https://blog.zenml.io/assets/posts/release_0_5_4/zenml_lineage.gif)\n\n### 5. 📊 Visualize Statistics\n\nNow you can use awesome third-party libraries to visualize ZenML steps and artifacts. We support the facets visualization for statistics out of the box, to find data drift between your training and test sets.\n\nWe use the built-in FacetStatisticsVisualizer using the [Facets Overview](https://pypi.org/project/facets-overview/) integration.\n\n![Here’s what the statistics visualizer looks like](https://blog.zenml.io/assets/posts/release_0_5_3/stats.gif)\n\n### 6. 🧐 Introspect your Pipeline Results\n\nOnce you\'ve run your experiment, you need a way of seeing what was produced and how it was produced. We offer a flexible interface to support [post-execution workflows](https://docs.zenml.io/v/docs/guides/post-execution-workflow). This allows you to access any of the artifacts produced by pipeline steps as well as any associated metadata.\n\n```python\npipeline = repo.get_pipeline(pipeline_name=..., stack_key=...) # access a pipeline by name and/or stack key\nruns = pipeline.runs  # all runs of a pipeline chronologically ordered\nrun = runs[-1]  # latest run\nsteps = run.steps  # all steps of a pipeline\nstep = steps[0] \noutput = step.output\ndf = output.read(materializer_class=PandasMaterializer)\ndf.head()\n```\n\n### 7. 🛠 Configure Pipeline Runs with YAML Code\n\nNot everyone wants to keep their configuration of pipeline runs in the same place as the active code defining steps. You can define the particular customization of runs with YAML code if that\'s your jam!\n\n\n```yaml\nsteps:\n  step_name:\n    parameters:\n      parameter_name: parameter_value\n      some_other_parameter_name: 2\n  some_other_step_name:\n    ...\n```\n\n# 🤸 Getting Started\n\n## 💾 Install ZenML\n\n*Requirements*: ZenML supports Python 3.6, 3.7 and 3.8.\n\nZenML is available for easy installation into your environment via PyPI:\n\n```bash\npip install zenml\n```\n\nAlternatively, if you’re feeling brave, feel free to install the bleeding edge:\n**NOTE:** Do so on your own risk, no guarantees given!\n\n```bash\npip install git+https://github.com/zenml-io/zenml.git@main --upgrade\n```\n\nZenML is also available as a Docker image hosted publicly on [DockerHub](https://hub.docker.com/r/zenmldocker/zenml). \nUse the following command to get started in a bash environment:\n\n```shell\ndocker run -it zenmldocker/zenml /bin/bash\n```\n\n## 🚅 Quickstart\n\nThe quickest way to get started is to create a simple pipeline.\n\n#### Step 1: Initialize a ZenML repo\n\n```bash\nzenml init\nzenml integration install sklearn # we use scikit-learn for this example\n```\n\n#### Step 2: Assemble, run, and evaluate your pipeline locally\n\n```python\nimport numpy as np\nfrom sklearn.base import ClassifierMixin\n\nfrom zenml.integrations.sklearn.helpers.digits import get_digits, get_digits_model\nfrom zenml.pipelines import pipeline\nfrom zenml.steps import step, Output\n\n@step\ndef importer() -> Output(\n    X_train=np.ndarray, X_test=np.ndarray, y_train=np.ndarray, y_test=np.ndarray\n):\n    """Loads the digits array as normal numpy arrays."""\n    X_train, X_test, y_train, y_test = get_digits()\n    return X_train, X_test, y_train, y_test\n\n\n@step\ndef trainer(\n    X_train: np.ndarray,\n    y_train: np.ndarray,\n) -> ClassifierMixin:\n    """Train a simple sklearn classifier for the digits dataset."""\n    model = get_digits_model()\n    model.fit(X_train, y_train)\n    return model\n\n\n@step\ndef evaluator(\n    X_test: np.ndarray,\n    y_test: np.ndarray,\n    model: ClassifierMixin,\n) -> float:\n    """Calculate the accuracy on the test set"""\n    test_acc = model.score(X_test, y_test)\n    print(f"Test accuracy: {test_acc}")\n    return test_acc\n\n\n@pipeline\ndef mnist_pipeline(\n    importer,\n    trainer,\n    evaluator,\n):\n    """Links all the steps together in a pipeline"""\n    X_train, X_test, y_train, y_test = importer()\n    model = trainer(X_train=X_train, y_train=y_train)\n    evaluator(X_test=X_test, y_test=y_test, model=model)\n\n\npipeline = mnist_pipeline(\n    importer=importer(),\n    trainer=trainer(),\n    evaluator=evaluator(),\n)\npipeline.run()\n```\n\n# 🗺 Roadmap\n\nZenML is being built in public. The [roadmap](https://zenml.io/roadmap) is a regularly updated source of truth for the ZenML community to understand where the product is going in the short, medium, and long term.\n\nZenML is managed by a [core team](https://zenml.io/team) of developers that are responsible for making key decisions and incorporating feedback from the community. The team oversees feedback via various channels, and you can directly influence the roadmap as follows:\n\n- Vote on your most wanted feature on our [Discussion board](https://zenml.io/discussion).\n- Create a [Feature Request](https://github.com/zenml-io/zenml/issues/new/choose) in the [GitHub board](https://github.com/zenml-io/zenml/issues).\n- Start a thread in our [Slack channel](https://zenml.io/slack-invite).\n\n# 🙋\u200d♀️ Contributing & Community\n\nWe would love to develop ZenML together with our community! Best way to get started is to select any issue from the [`good-first-issue` label](https://github.com/zenml-io/zenml/labels/good%20first%20issue). If you would like to contribute, please review our [Contributing Guide](CONTRIBUTING.md) for all relevant details.\n\n<br>\n\n![Repobeats analytics image](https://repobeats.axiom.co/api/embed/635c57b743efe649cadceba6a2e6a956663f96dd.svg "Repobeats analytics image")\n\n# 🆘 Where to get help\n\nFirst point of call should be [our Slack group](https://zenml.io/slack-invite/). Ask your questions about bugs or specific use cases and someone from the core team will respond.\n\n# 📜 License\n\nZenML is distributed under the terms of the Apache License Version 2.0. A complete version of the license is available in the [LICENSE.md](LICENSE.md) in this repository. Any contribution made to this project will be licensed under the Apache License Version 2.0.\n',
    'author': 'ZenML GmbH',
    'author_email': 'info@zenml.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://zenml.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.9',
}


setup(**setup_kwargs)
