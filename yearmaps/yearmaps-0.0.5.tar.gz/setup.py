# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yearmaps', 'yearmaps.interface', 'yearmaps.provider', 'yearmaps.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click>=8.0.3,<9.0.0',
 'index.py>=0.21.11,<0.22.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.22.1,<2.0.0',
 'requests>=2.27.1,<3.0.0',
 'schedule>=1.1.0,<2.0.0',
 'uvicorn>=0.17.0,<0.18.0']

entry_points = \
{'console_scripts': ['yearmaps = yearmaps.script:main',
                     'yearmaps-server = yearmaps.server:cli']}

setup_kwargs = {
    'name': 'yearmaps',
    'version': '0.0.5',
    'description': 'Generate heat map of a year.',
    'long_description': '# YearMaps\n\n生成一年的热力图。\n\n![image](https://user-images.githubusercontent.com/31370133/150357084-f0ddb8f5-26c0-4526-9f3e-bc1e3aa1784a.png)\n\n# 安装\n\n```bash\npip[3] install --user yearmaps\n```\n\n# 使用\n\n```bash\nUsage: yearmaps [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  -d, --data-dir TEXT             Directory to store datas  [default: ~/.yearmaps]\n  -o, --output-dir TEXT           Directory to store output  [default: $(pwd)]\n  -f, --file-type [svg|png]       File type to export  [default: svg]\n  -m, --mode [till_now|year]      Generate mode of the program  [default: till_now]\n  -y, --year INTEGER              Year to generate, this option will override mode to "year"\n  -c, --color [red|pink|purple|deeppurple|indigo|blue|lightblue|cyan|teal|green|lightgreen|lime|yellow|amber|orange|deeporange|brown|grey|bluegrey]\n                                  Color to override provider default color\n  --help                          Show this message and exit.\n\nCommands:\n  bbdc    不背单词\n  bili    Bilibili\n  cf      Codeforces\n  github  GitHub\n  \n# 服务器模式\n\nUsage: yearmaps-server [OPTIONS]\n\nOptions:\n  -l, --host TEXT     Host to listen on.\n  -p, --port INTEGER  Port to listen on.\n  -f, --config TEXT   Path to config file.  [default: $(pwd)/yearmaps.yml]\n  --help              Show this message and exit.\n```\n\n## 子模块\n\n### 不背单词\n\n<details>\n\n```bash\nUsage: yearmaps bbdc [OPTIONS]\n\n  不背单词\n\nOptions:\n  -i, --id TEXT           不背单词用户 ID  [required]\n  -t, --gtype [time|word] 图数据类型\n  --help                  Show this message and exit.\n```\n\n![bbdc](https://user-images.githubusercontent.com/31370133/150357416-36b3bd83-aa8c-4065-aabb-f130f0392476.png)\n\n</details>\n\n### bilibili\n\n<details>\n  \n```bash\nUsage: yearmaps bili [OPTIONS]\n\n  bilibili\n\nOptions:\n  -i, --id TEXT       bilibili uid  [required]\n  -t, --gtype [video] 图数据类型\n  --help              Show this message and exit.\n```\n  \n![image](https://user-images.githubusercontent.com/50107074/150572220-781dd51f-fd9c-47cf-b78a-cac1def2fd91.png)\n  \n</details>\n\n### Codeforces\n\n<details>\n\n```bash\nUsage: yearmaps cf [OPTIONS]\n\n  Codeforces\n\nOptions:\n  -u, --user TEXT      Codeforces user name  [required]\n  -t, --gtype [all|ac] 图数据类型\n  --help               Show this message and exit.\n```\n\n\n![image](https://user-images.githubusercontent.com/31370133/150477193-6740583e-f3b8-48a3-b92c-f40b4af010b8.png)\n\n</details>\n\n### GitHub\n\n<details>\n\n```bash\nUsage: yearmaps github [OPTIONS]\n\n  GitHub\n\nOptions:\n  -u, --user TEXT       GitHub user name  [required]\n  -k, --token TEXT      GitHub access token  [required]\n  -t, --gtype [contrib] 图数据类型\n  --help                Show this message and exit.\n```\n\n![image](https://user-images.githubusercontent.com/31370133/150357084-f0ddb8f5-26c0-4526-9f3e-bc1e3aa1784a.png)\n\n</details>\n',
    'author': 'Zxilly',
    'author_email': 'zxilly@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zxilly/yearmaps',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
