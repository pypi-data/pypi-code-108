# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resistant_documents_client', 'resistant_documents_client.tests']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'resistant-documents-client',
    'version': '1.0a0',
    'description': 'Resistant.ai document forjerry python client for convenient integration with REST API service.',
    'long_description': '# Resistant documents client\n\nThis tool facilitates communication with the [resistant.ai](https://resistant.ai/products/documents/) document forjerry analysis service using\nPython. [Here](https://pdf.resistant.ai/docs/v1.html) you can find a description of the underlying REST service. Below we describe the Python\ninterface. For a detailed description, go directly to the referenced API docs.\n\n## Prerequisites\n\nYou will need one string to perform further steps which you receive during the customer onboarding process.\n\n- API_KEY\n\n## Basic usage\n\nThe following example runs fraud analysis on a given document. It is the most usual usage of the API.\n\n```python\nfrom bp_pdf_forgery_client.client import BpPdfForgeryClient\n\nclient = BpPdfForgeryClient(api_key="YOUR_API_KEY")\nwith open("local_file.pdf", "rb") as fp:\n    report = client.analyze(fp.read(), query_id="local_file.pdf")\n\nprint(report)\n``` \n\n## Customized usage\n\nSuppose you want to customize parameters of the process or perform another type of analysis. Below we describe what are the particular steps which you\nhave to run.\n\n### Create client with you credentials\n\n```python\nclient = BpPdfForgeryClient(api_key="YOUR_API_KEY")\n```\n\n### Create submission with pipeline setup\n\n```python\nwith open("local_file.pdf", "rb") as fp:\n    my_submission_id = client.submit(fp.read(), query_id="local_file.pdf", pipeline_configuration="CONTENT_AFTER_FRAUD_AFTER_QUALITY")\n```\n\nPossible pipeline configurations are listed in REST API docs.\n### Retrieve analysis result\nYou can retrieve only those types of analysis which were specified in previous `pipeline_configuration`.\n\n```python\nresult_results = client.results(submission_id=my_submission_id)\nresult_content = client.content(submission_id=my_submission_id)\nresult_quality = client.quality(submission_id=my_submission_id)\n\nprint(result_content)\nprint(result_fraud)\nprint(result_quality)\n```\nThese methods also accept `max_num_retries`, which represents how many times will the client poll the server before failing (because the communication is asynchronous). It might be customized but has a default\nvalue. Other parameters correspond to the ones in the REST API docs.\n\n### Presigned url\n```python\ndata = client.presign(submission_id=my_submission_id, expiration=600)\npresigned_url = data["presigned_url"]\n```\nThis method lets you generate a link for anybody else to access the analysis result. You can set expiration to this temporary generated link in the parameter `expiration`. Note that the value is in seconds with lower bound `1` and upper bound `604800` (one week).\n',
    'author': 'Resistant.ai',
    'author_email': 'sales@resistant.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
