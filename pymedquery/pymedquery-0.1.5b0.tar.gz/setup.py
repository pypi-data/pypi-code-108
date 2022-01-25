# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pymedquery',
 'pymedquery.config',
 'pymedquery.docs',
 'pymedquery.sql.default',
 'pymedquery.src']

package_data = \
{'': ['*'],
 'pymedquery': ['data/processed/*',
                'data/sql/*',
                'sql/tables/auth/*',
                'sql/tables/etl/*'],
 'pymedquery.docs': ['proj_logging/*']}

install_requires = \
['colorlog>=5.0.1,<6.0.0',
 'joblib>=1.0.1,<2.0.0',
 'minio>=7.1.0,<8.0.0',
 'numpy>=1.21.0,<2.0.0',
 'passlib>=1.7.4,<2.0.0',
 'psycopg2-binary>=2.9.1,<3.0.0',
 'python-dotenv>=0.18.0,<0.19.0',
 'tqdm>=4.61.2,<5.0.0']

entry_points = \
{'console_scripts': ['mq-init = pymedquery.mqInit:run_setup']}

setup_kwargs = {
    'name': 'pymedquery',
    'version': '0.1.5b0',
    'description': 'This is a python client for the medical-database MedQuery',
    'long_description': '# pyMedQuery <img align="right" width="150" alt="20200907_104224" src="https://user-images.githubusercontent.com/29639563/125202990-9fcd9200-e276-11eb-8e00-bde211ebe0c1.png">\n<img src="./py_medquery/docs/coverage.svg"> [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)\n[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)\n[![PyPI status](https://img.shields.io/pypi/status/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)\n\n*pyMedQuery* is the sweet sweet database client for python that allows authenticated users to access the crai-medical-imaging-database. The main reason for *pyMedQuery* to exist is to efficiently enable database access via python code that can be integrated into machine learning projects, production systems and data analysis pipelines. We are using SSL/TLS for safe connections and client certifications for authentication in order to keep the database connection highly secure. \n\n###### Note: Only OUH affiliated and CRAI members can gain access to the medical database as of now.\n\nThe average user is expected to instantiate the `PyMedQuery()` class and run the methods `extract` or `batch_extract` to extract the necessary data for their given project. If the user wants to use the default SQL script then set the argument `get_all` to true in the `(batch_)extract` method and specify which projectID the data should relate to. The method will then extract all the data belonging to that projectID. Other users might find it usefull to write custom SQL scripts where the argument `format_params` can be passed into the extraction for flexible formating of SQL queries. This is especially useful for applications and pipelines.\n\nMore functionalities are coming to *pyMedQuery* in later beta version where `(batch_)upload` and `move_data` will be part of the release. If you have any feedback or ideas to new features or bugs then please get in contact with us.\n\n*pyMedQuery* is meant to be a simple and friendly. We hope you\'ll like it! Check out the tutorial script for some examples. Also note that advanced user can directly connect to the RDBMS and data lake for more complex operations.   \n\n### Quickstart Guide\n\n#### 1. installing and completing the settings (this is a one time procedure)\n\n1. Use poetry or any other kind of dependency manager to install the package.\n\n```$ poetry add pymedquery```\n\n2. If you are using poetry then run the `medqueryInit` script to setup the database authentication. (A valid username, password and cert files are currently required in forehand) The setup script will guide you through the authentication. A more streamlined way to authenticate via a MedQuery\'s CLI is in the roadmap for 2022.\n\n<details>\n<summary>Open this drop down if you want to do the authentication manually or you are on Windows:</summary>\n<br>\n\n2. Store the certification and key files for postgres somwhere safe on your machine. (you will receive the database credentials from the admins)\n\n3. Set environment variables on your system for the file paths that point to the cert and key files you received for the database. We recommended to put the commands in your .zshrc or .bashrc.\n\n```\n$ echo \'export PGSSLCERT=file_path_to_client_crt\' >> ~/<.your_rc_file>\n$ echo \'export PGSSLROOTCERT=file_path_to_ca_crt\' >> ~/<.your_rc_file>\n$ echo \'export PGSSLKEY=file_path_to_client_key\' >> ~/<.your_rc_file>\n```\n\nSet correct permissions on your client key in order for the database to read it.\n```\n$ chmod 600 $PGSSLKEY\n```\n\nDo the equivalent on windows with\n\n```\nsetx PGSSLCERT file_path_to_client_crt\nsetx PPGSSLROOTCERT file_path_to_ca_crt\nsetx PGSSLKEY file_path_to_client_key\n```\n\n<details>\n<summary>Windows is not a straight forward when setting 600 permission but you can follow these steps:</summary>\n<br>\n\n- Right-click on the target file and select properties then select Security Tab\n\n- Click Advanced and then make sure inheritance is disabled.\n\n- Click apply and then click Edit in the security menu\n\n- Remove all users except Admin user, which should have full control *Admin account should have all checkboxes checked on Allow column except special permission.\n\n- Click Apply and then click OK :)\n        \n<br>\n</details>\n\n\n4. Also include the username and password in your rc file as environment variables:\n\n```\n<your-rc-file>\n# (env vars to fill out that pyMedQuery will pick up on)\nexport MQUSER=\'username-to-medquery\'\nexport MQPWD=\'password-to-medquery\'\nexport DATABASE=\'medquery\'\nexport MQACCESS_KEY=\'access_key\'\nexport MQSECRET_KEY=\'secret_key\'\n```\n##### NOTE! The env var names is a strict convention. The program will not work if you use other names.\n\n<br>\n</details>\n\n#### 2. Examples of how to run the basics\n\n0.  Extracting a small data sample by using the default SQL script and a certain project id\n\n```python\nfrom pymedquery import pymq\n\n# instantiate the class\npymq = pymq.PyMedQuery()\nsmall_data_sample = pymq.extract(get_all=True, project_id=\'fancyID\')\n        # do more stuff here\n        # save processed data to your local disk with e.g. pickle\n```\n\n\n1.  Extracting a small data sample with a custom and formatable SQL script  \n\n```python\nfrom pymedquery import pymq\nfrom config import config\n\nsql_file_path =  # file-path-to-the-pre-written-sql-script\n# instantiate the class\npymq = pymq.PyMedQuery()\n        \n# The formatable parameters will be inserted into the custom SQL scrip and thus extracting data belonging to\n# \'fancy_id\' from only the year 2012 and for only women between 40 and 49. The SQL script must include the\n# format syntax {project_id}, {start_time}..., etc. for the filtering to happen.\nFORMAT_PARAMS = {\n        \'project_id\': \'fancy_id\',\n        \'start_time\': \'2012-01-01\',\n        \'end_time\': \'2012-12-31\',\n        \'gender\': \'F\',\n        \'age_group\': \'40-49\'\n        }\n        \n# Note that the SQL file path is given by a configuartion script called config \nsmall_data_sample = pymq.extract(get_all=False, format_params=FORMAT_PARAMS, sql_file_path=config.SQL_FILE_PATH)\n        # do more stuff\n        # save processed data to local disk with e.g. pickle\n```\n        \n2. Extracting large amounts of data (this step could either be done with a custom SQL file or without. The example is given with the default SQL file for brevity.\n\n```python\nfrom pymedquery import pymq\n\n# instantiate the class\npymq = pymq.PyMedQuery()\n\n# Setting batch size to 20\nlarge_data = pymq.batch_extract(get_all=True, project_id=\'fancyID\', batch_size=20)\nfor batch in large_data:\n        # do more stuff here\n        # iteratively save processed data to your local disk with e.g. pickle\n```\n\n#### 3. Advanced use \n        \n1. Insert records\n\n```python\n\nrecords = [(\'row_value1\', \'row_value2\', \'row_value3\')]\ncols = [\'column1\', \'column2\', \'column3\']\n\ncrud.insert(columns=cols, records=records, batch=False, table=\'table-to-insert\')\n# You have to commit the operation for it to take effect.\ncrud.commit()\n# if you are done with the session then close the db connection\ncrud.close_connection()\n\n```\n\n2. Changing the value for one column on the row/s where the `primary-key` equals certain value/s `primary-key-value`.\n\n\n```python\ncol_to_change =  # list(change-the-value-in-this/these-column/s)\nnew_col_vals =  # new-value/s\nprimary_key =  # list(primarykey/s-to-use)\nprimary_key_value =  # primarykey-value/s-to-use-for-updating\n\ncrud.update(\n           columns=col_to_change, column_values=new_col_vals,\n           primarykeys=primary_key, primary_vals=primary_key_value,\n           table=\'table-to-update\'\n           )\n# You have to commit the operation for it to take effect.\ncrud.commit()\n# if you are done with the session then close the db connection\ncrud.close_connection()\n\n```\n\n3. Delete records for specific `primary-key-value`\n\n```python\n\nprimary_key =  # primarykey/s-to-use  # (if more than one then place them in a list)\nprimary_key_value =  # primarykey-value/s-to-use-for-updating\n\ncrud.delete(primarykey=primary_key, primary_vals=primary_key_value, table=\'table-to-delete-records-on\')\n# You have to commit the operation for it to take effect.\ncrud.commit()\n# if you are done with the session then close the db connection\ncrud.close_connection()\n\n```\n\n##### The project pyMedQuery is primarily developed by the research unit CRAI at the university hospital of Oslo\n\n',
    'author': 'Jon E Nesvold',
    'author_email': 'jon.nesvold@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
