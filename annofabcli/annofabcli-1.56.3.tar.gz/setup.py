# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['annofabcli',
 'annofabcli.annotation',
 'annofabcli.annotation_specs',
 'annofabcli.common',
 'annofabcli.experimental',
 'annofabcli.filesystem',
 'annofabcli.input_data',
 'annofabcli.inspection_comment',
 'annofabcli.instruction',
 'annofabcli.job',
 'annofabcli.labor',
 'annofabcli.organization_member',
 'annofabcli.project',
 'annofabcli.project_member',
 'annofabcli.stat_visualization',
 'annofabcli.statistics',
 'annofabcli.statistics.visualization',
 'annofabcli.statistics.visualization.dataframe',
 'annofabcli.supplementary',
 'annofabcli.task',
 'annofabcli.task_history',
 'annofabcli.task_history_event']

package_data = \
{'': ['*'], 'annofabcli': ['data/*']}

install_requires = \
['annofabapi>=0.52.4',
 'bokeh>=2.4,<3.0',
 'dictdiffer',
 'isodate',
 'jmespath',
 'more-itertools',
 'pandas',
 'pillow',
 'pyquery',
 'python-datauri',
 'pyyaml',
 'requests']

entry_points = \
{'console_scripts': ['annofabcli = annofabcli.__main__:main']}

setup_kwargs = {
    'name': 'annofabcli',
    'version': '1.56.3',
    'description': 'Utility Command Line Interface for AnnoFab',
    'long_description': '# annofab-cli\n[AnnoFab](https://annofab.com/)のCLI(Command Line Interface)ツールです。\n「タスクの一括差し戻し」や、「タスク一覧出力」など、AnnoFabの画面で実施するには時間がかかる操作を、コマンドとして提供しています。\n\n[![Build Status](https://app.travis-ci.com/kurusugawa-computer/annofab-cli.svg?branch=master)](https://app.travis-ci.com/kurusugawa-computer/annofab-cli)\n[![PyPI version](https://badge.fury.io/py/annofabcli.svg)](https://badge.fury.io/py/annofabcli)\n[![Python Versions](https://img.shields.io/pypi/pyversions/annofabcli.svg)](https://pypi.org/project/annofabcli/)\n[![Documentation Status](https://readthedocs.org/projects/annofab-cli/badge/?version=latest)](https://annofab-cli.readthedocs.io/ja/latest/?badge=latest)\n\n\n* **AnnoFab:** https://annofab.com/\n* **Documentation:** https://annofab-cli.readthedocs.io/ja/latest/\n\n\n\n\n# 注意\n* 作者または著作権者は、ソフトウェアに関してなんら責任を負いません。\n* 予告なく互換性のない変更がある可能性をご了承ください。\n* AnnoFabプロジェクトに大きな変更を及ぼすコマンドも存在します。間違えて実行してしまわないよう、注意してご利用ください。\n\n\n## 廃止予定\n\n### 2022-02-01 以降\n* `annofabcli statistics visualize`：`--get_labor` オプションを廃止します。替わりに `--labor_csv` を利用してください。\n\n### 2022-04-01 以降\n* python3.7のサポートを廃止して、python3.8以上をサポートするようにします。\n\n\n# Requirements\n* Python 3.7.1+\n\n# Install\n\n```\n$ pip install annofabcli\n```\n\nhttps://pypi.org/project/annofabcli/\n\n## Windows用の実行ファイルを利用する場合\n[GitHubのリリースページ](https://github.com/kurusugawa-computer/annofab-cli/releases)から`annofabcli-vX.X.X-windows.zip`をダウンロードしてください。\nzipの中にある`annofabcli.exe`が実行ファイルになります。\n\n\n## Dockerを利用する場合\n\n```\n$ git clone https://github.com/kurusugawa-computer/annofab-cli.git\n$ cd annofab-cli\n$ chmod u+x docker-build.sh\n$ ./docker-build.sh\n\n$ docker run -it annofab-cli --help\n\n# AnnoFabの認証情報を標準入力から指定する\n$ docker run -it annofab-cli project diff prj1 prj2\nEnter AnnoFab User ID: XXXXXX\nEnter AnnoFab Password: \n\n# AnnoFabの認証情報を環境変数で指定する\n$ docker run -it -e ANNOFAB_USER_ID=XXXX -e ANNOFAB_PASSWORD=YYYYY annofab-cli project diff prj1 prj2\n```\n\n\n## AnnoFabの認証情報の設定\nhttps://annofab-cli.readthedocs.io/ja/latest/user_guide/configurations.html 参照\n\n# 使い方\nhttps://annofab-cli.readthedocs.io/ja/latest/user_guide/index.html 参照\n\n# コマンド一覧\nhttps://annofab-cli.readthedocs.io/ja/latest/command_reference/index.html\n\n\n# よくある使い方\n\n### 受入完了状態のタスクを差し戻す\n"car"ラベルの"occluded"属性のアノテーションルールに間違いがあったため、以下の条件を満たすタスクを一括で差し戻します。\n* "car"ラベルの"occluded"チェックボックスがONのアノテーションが、タスクに1つ以上存在する。\n\n前提条件\n* プロジェクトのオーナが、annofabcliコマンドを実行する\n\n\n```\n# 受入完了のタスクのtask_id一覧を、acceptance_complete_task_id.txtに出力する。\n$ annofabcli task list --project_id prj1  --task_query \'{"status": "complete","phase":"acceptance"}\' \\\n --format task_id_list --output acceptance_complete_task_id.txt\n\n# 受入完了タスクの中で、 "car"ラベルの"occluded"チェックボックスがONのアノテーションの個数を出力する。\n$ annofabcli annotation list_count --project_id prj1 --task_id file://task.txt --output annotation_count.csv \\\n --annotation_query \'{"label_name_en": "car", "attributes":[{"additional_data_definition_name_en": "occluded", "flag": true}]}\'\n\n# annotation_count.csvを表計算ソフトで開き、アノテーションの個数が1個以上のタスクのtask_id一覧を、task_id.txtに保存する。\n\n# task_id.txtに記載されたタスクを差し戻す。検査コメントは「carラベルのoccluded属性を見直してください」。\n# 差し戻したタスクには、最後のannotation phaseを担当したユーザを割り当てる（画面と同じ動き）。\n$ annofabcli task reject --project_id prj1 --task_id file://tasks.txt --cancel_acceptance \\\n  --comment "carラベルのoccluded属性を見直してください"\n\n```\n\n# 補足\n\n# Windowsでannofabcliを使う場合\nWindowsのコマンドプロンプトやPowerShellでannofabcliを使う場合、JSON文字列内の二重引用をエスケープする必要があります。\n\n```\n> annofabcli task list --project_id prj1  --task_query \'{"\\status\\": \\"complete\\"}\'\n```\n',
    'author': 'yuji38kwmt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kurusugawa-computer/annofab-cli',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
