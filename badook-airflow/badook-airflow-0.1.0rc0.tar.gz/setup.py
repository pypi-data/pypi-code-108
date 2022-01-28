# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['badook_airflow', 'badook_airflow.hooks', 'badook_airflow.operators']

package_data = \
{'': ['*'], 'badook_airflow.hooks': ['config/*']}

install_requires = \
['apache-airflow>=2.1.2,<3.0.0',
 'badook-tests>=0.2.0-rc.5,<0.3.0',
 'cached-property>=1.5.2,<2.0.0',
 'log-symbols>=0.0.14,<0.0.15',
 'spinners>=0.0.24,<0.0.25']

setup_kwargs = {
    'name': 'badook-airflow',
    'version': '0.1.0rc0',
    'description': 'Apache Airflow integration for badook tests',
    'long_description': '# badook Airflow\n\n## Dag code example:\n\n```\nfrom airflow import DAG\nfrom airflow.utils.dates import days_ago\n\nfrom badook_airflow.operators.badook_operator import BadookTestOperator\n\n\ndefault_args = {\n    \'owner\': \'airflow\',\n    \'start_date\': days_ago(0)\n}\n\nwith DAG(\n    dag_id=\'badook_test_runner\',\n    default_args=default_args,\n    schedule_interval=\'@once\'\n) as dag:\n    badook_test = BadookTestOperator(\n        target_directory=\'test_dir\',\n        data_cluster_url=\'https://test.url\',\n        management_cluster_url=\'https://test.managment.url\',\n        client_id=\'APIKEY\',\n        client_secret=\'SECRETKEY\',\n        task_id="run_tests"\n    )\n    badook_test\n```\n',
    'author': 'badook engineering',
    'author_email': 'engineering@badook.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/badook-ai/badook-airflow',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.8.0',
}


setup(**setup_kwargs)
