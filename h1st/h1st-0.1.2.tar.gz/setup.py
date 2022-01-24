# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['h1st',
 'h1st.core',
 'h1st.exceptions',
 'h1st.h1flow',
 'h1st.h1flow.ui',
 'h1st.model',
 'h1st.model.ensemble',
 'h1st.model.google_cloud',
 'h1st.model.oracle',
 'h1st.model.repository',
 'h1st.model.repository.storage',
 'h1st.trust']

package_data = \
{'': ['*']}

install_requires = \
['graphviz>=0.19.1,<0.20.0',
 'lime>=0.2.0.1,<0.3.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'pyyaml>=6.0,<7.0',
 's3fs>=2021.11.1,<2022.0.0',
 'scikit-fuzzy>=0.4.2,<0.5.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'shap>=0.40.0,<0.41.0',
 'ulid-py>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'h1st',
    'version': '0.1.2',
    'description': 'Human-First AI (H1ST)',
    'long_description': '## Join the Human-First AI revolution\n_“We humans have .. insight that can then be mixed with powerful AI .. to help move society forward. Second, we also have to build trust directly into our technology .. And third, all of the technology we build must be inclusive and respectful to everyone.”_\n<br/>— Satya Nadella, Microsoft CEO\n\nAs trail-blazers in Industrial AI, our team at Arimo-Panasonic has found Satya Nadella‘s observations to be powerful and prescient. Many hard-won lessons from the field have led us to adopt this approach which we call Human-First AI (`H1st` AI). \n\nToday, we‘re excited to share these ideas and concrete implementation of `H1st` AI with you and the open-source data science community!\n\n## Learn the Key Concepts\nHuman-First AI (`H1st` AI) solves three critical challenges in real-world data science:\n\n1. __Industrial AI needs human insight:__ In so many important applications, there isn‘t enough data for ML. For example, last year‘s product‘s data does not apply to this year‘s new model. Or, equipment not yet shipped obviously have no data history to speak of. `H1st` combines human knowledge and any available data to enable intelligent systems, and companies can achieve earlier time-to-market.\n\n2. __Data scientists need human tools:__ Today‘s tools are to compete rather than to collaborate. When multiple data scientists work on the same project, they are effectively competing to see who can build the better model. `H1st` breaks a large modeling problem into smaller, easier parts. This allows true collaboration and high productivity, in ways similar to well-established software engineering methodology. \n\n3. __AI needs human trust:__ AI models can\'t be deployed when they lack user trust. AI increasingly face regulatory challenges. `H1st` supports model description and explanation at multiple layers, enabling transparent and trustworthy AI.\n\n\n## Get started\n`H1st` runs on Python 3.7 or above. Install with `pip3 install h1st`. For Windows, please use 64bit version and install [VS Build Tools](https://visualstudio.microsoft.com/downloads/) before installing H1st.\n\nSee the [examples/HelloWorld folder](examples/HelloWorld) for simple "Hello world" examples of using \n[H1st rule-based](examples/HelloWorld/rule_based_model.py) & [machine-learned models](examples/HelloWorld/ml_model.py) and using [H1st Graph](examples/HelloWorld/graph.py).\n\nFor a simple real-world data science example using H1st Model API, take a look at the [forecasting example](examples/Forecasting).\n\nTo fully understand H1st philosophy and power, check out the [H1st Automotive Cybersecurity Tutorial](https://h1st.ai).\n\n\n## Read the Tutorials, Wiki, and API Documentation\nWe highly recommend following the [H1st Automotive Cybersecurity Tutorial](https://h1st.ai) as well as the quick-start examples in the [h1st-examples folder](https://github.com/h1st-ai/h1st-examples).\n\nSee the wiki for design consideration e.g. [H1st.AI Model Explained](../../wiki/Human-First-AI-Graph-Explained), [H1st.AI Graph Explained](../../wiki/Human-First-AI-Graph-Explained).\n\nOur full API Documentation is at [docs.h1st.ai](https://docs.h1st.ai/).\n\nSee our public [H1st.AI\'s roadmap](../../wiki/Human-First-AI-Roadmap).\n\n## Join and Learn from Our Open-Source Community\nWe are collaborating with the open-source community. For Arimo-Panasonic, use cases include industrial applications such as Cybersecurity, Predictive Maintenance, Fault Prediction, Home Automation, Avionic & Automotive Experience Management, etc.\n\nWe\'d love to see your use cases and your contributions to open-source `H1st` AI. \n',
    'author': 'h1st-ai',
    'author_email': 'engineering@aitomatic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://h1st.ai',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
