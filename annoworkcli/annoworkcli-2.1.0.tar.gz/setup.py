# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['annoworkcli',
 'annoworkcli.account',
 'annoworkcli.actual_working_time',
 'annoworkcli.annofab',
 'annoworkcli.common',
 'annoworkcli.expected_working_time',
 'annoworkcli.job',
 'annoworkcli.my',
 'annoworkcli.organization',
 'annoworkcli.organization_member',
 'annoworkcli.organization_tag',
 'annoworkcli.schedule']

package_data = \
{'': ['*'], 'annoworkcli': ['data/*']}

install_requires = \
['annofabapi>=0.52.4',
 'annofabcli>=1.55.0',
 'annoworkapi>=2.0',
 'isodate',
 'more-itertools',
 'pandas',
 'pyyaml']

entry_points = \
{'console_scripts': ['annoworkcli = annoworkcli.__main__:main']}

setup_kwargs = {
    'name': 'annoworkcli',
    'version': '2.1.0',
    'description': '',
    'long_description': '\n# annowork-cli\nAnnoWorkのCLIです。\n\n\n[![Build Status](https://app.travis-ci.com/kurusugawa-computer/annowork-cli.svg?branch=main)](https://app.travis-ci.com/kurusugawa-computer/annowork-cli)\n[![CodeQL](https://github.com/kurusugawa-computer/annowork-cli/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/kurusugawa-computer/annowork-cli/actions/workflows/codeql-analysis.yml)\n[![PyPI version](https://badge.fury.io/py/annoworkcli.svg)](https://badge.fury.io/py/annoworkcli)\n[![Python Versions](https://img.shields.io/pypi/pyversions/annoworkcli.svg)](https://pypi.org/project/annoworkcli/)\n[![Documentation Status](https://readthedocs.org/projects/annowork-cli/badge/?version=latest)](https://annowork-cli.readthedocs.io/ja/latest/?badge=latest)\n\n\n# Requirements\n* Python3.8+\n\n\n# Install\n```\n$ pip install annoworkcli\n```\n\n\n# Usage\n\n\n## 認証情報の設定\n\n### `.netrc`\n\n`$HOME/.netrc`ファイルに以下を記載する。\n\n```\nmachine annowork.com\nlogin annowork_user_id\npassword annowork_password\n```\n\n\n### 環境変数\n* 環境変数`ANNOWORK_USER_ID` , `ANNOWORK_PASSWORD`\n\n### `annoworkcli annofab`コマンドを利用する場合\n`annoworkcli annofab`コマンドはannofabのwebapiにアクセスするため、annofabのwebapiの認証情報を指定する必要があります。\n* 環境変数`ANNOFAB_USER_ID` , `ANNOFAB_PASSWORD`\n* `$HOME/.netrc`ファイル\n\n```\nmachine annofab.com\nlogin annofab_user_id\npassword annofab_password\n```\n\n\n\n\n## コマンドの使い方\n\n```\nvagrant@example:~$ annoworkcli -h\nusage: annoworkcli [-h] [--version] {account,actual_working_time,annofab,expected_working_time,job,migration,my,organization_member,organization_tag,schedule} ...\n\nCommand Line Interface for AnnoFab\n\npositional arguments:\n  {account,actual_working_time,annofab,expected_working_time,job,migration,my,organization_member,organization_tag,schedule}\n    account             ユーザアカウントに関するサブコマンド\n\n    actual_working_time\n                        実績作業時間関係のサブコマンド\n\n    annofab             AnnoFabにアクセスするサブコマンド\n\n    expected_working_time\n                        予定稼働時間関係のサブコマンド\n\n    job                 ジョブ関係のサブコマンド\n\n    my                  自分自身に関するサブコマンド\n\n    organization_member\n                        組織メンバ関係のサブコマンド\n\n    organization_tag    組織タグ関係のサブコマンド\n\n    schedule            作業計画関係のサブコマンド\n\noptional arguments:\n  -h, --help            show this help message and exit\n\n  --version             show program\'s version number and exit\n```\n\n\n```\n$ annoworkcli organization_member list -h\nusage: annoworkcli organization_member list [-h] [--endpoint_url ENDPOINT_URL | --is_development | --is_staging] -org ORGANIZATION_ID\n                                            [-org_tag ORGANIZATION_TAG_ID [ORGANIZATION_TAG_ID ...]] [-o OUTPUT] [-f {csv,json}]\n\n組織メンバの一覧を出力します。無効化されたメンバも出力します。\n\noptional arguments:\n  -h, --help            show this help message and exit\n\n  --endpoint_url ENDPOINT_URL\n                        AnnoWork WebAPIのエンドポイントを指定します。指定しない場合は\'https://annowork.com\'です。 (default: None)\n\n  -org ORGANIZATION_ID, --organization_id ORGANIZATION_ID\n                        対象の組織ID (default: None)\n\n  -org_tag ORGANIZATION_TAG_ID [ORGANIZATION_TAG_ID ...], --organization_tag_id ORGANIZATION_TAG_ID [ORGANIZATION_TAG_ID ...]\n                        指定した組織タグが付与された組織メンバを出力します。 (default: None)\n\n  -o OUTPUT, --output OUTPUT\n                        出力先 (default: None)\n\n  -f {csv,json}, --format {csv,json}\n                        出力先 (default: csv)\n```\n\n```\n# CSV出力\n$ annoworkcli organization_member list -org org -o out.csv\n$ cat out.csv\norganization_member_id,organization_id,account_id,user_id,username,role,status,created_datetime,updated_datetime,organization_tag_ids,organization_tag_names,inactivated_datetime\n12345678-abcd-1234-abcd-1234abcd5678,org,12345678-abcd-1234-abcd-1234abcd5678,alice,Alice,manager,active,2021-11-04T04:27:57.702Z,2021-11-04T04:27:57.702Z,[\'company_kurusugawa\'],[\'company:来栖川電算\'],\n...\n\n\n# CSV出力\n$ annoworkcli organization_member list -org org -o out.json -f json\n$ cat out.json\n[\n  {\n    "organization_member_id": "12345678-abcd-1234-abcd-1234abcd5678",\n    "organization_id": "org",\n    "account_id": "12345678-abcd-1234-abcd-1234abcd5678",\n    "user_id": "alice",\n    "username": "Alice",\n    "role": "worker",\n    "status": "active",\n    "created_datetime": "2021-10-28T06:48:40.077Z",\n    "updated_datetime": "2021-11-09T01:07:30.766Z",\n    "inactivated_datetime": NaN,\n    "organization_tag_ids": [\n      "company_kurusugawa",\n      "type_monitored"\n    ],\n    "organization_tag_names": [\n      "company:来栖川電算",\n      "type:monitored"\n    ]\n  },\n  ...\n```\n\n\n\n\n### 開発環境に対して操作する場合\n\n```\n$ annoworkcli member list --output foo.csv --is_development \n```\n\n\n\n# VSCode Devcontainerを使って開発する方法\n1. 以下の環境変数を定義します。\n    * `ANNOFAB_USER_ID`\n    * `ANNOFAB_PASSWORD`\n    * `ANNOWORK_USER_ID`\n    * `ANNOWORK_PASSWORD`\n\n2. VSCodeのdevcontainerを起動します。\n\n\n\n',
    'author': 'yuji38kwmt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kurusugawa-computer/annowork-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
