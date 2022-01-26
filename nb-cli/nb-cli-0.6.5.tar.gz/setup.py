# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nb_cli',
 'nb_cli.commands',
 'nb_cli.handlers',
 'nb_cli.plugin.hooks',
 'nb_cli.project.hooks',
 'nb_cli.prompts']

package_data = \
{'': ['*'],
 'nb_cli': ['adapter/*',
            'adapter/{{cookiecutter.adapter_slug}}/*',
            'plugin/*',
            'plugin/{{cookiecutter.plugin_slug}}/*',
            'plugin/{{cookiecutter.plugin_slug}}/plugins/*',
            'project/*',
            'project/{{cookiecutter.project_slug}}/*',
            'project/{{cookiecutter.project_slug}}/{{cookiecutter.source_dir}}/plugins/*']}

install_requires = \
['click>=8.0.0,<9.0.0',
 'colorama>=0.4.3,<0.5.0',
 'cookiecutter>=1.7.2,<2.0.0',
 'httpx>=0.18.0,<1.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'prompt-toolkit>=3.0.19,<4.0.0',
 'pyfiglet>=0.8.post1,<0.9',
 'tomlkit>=0.7.0,<0.8.0',
 'wcwidth>=0.2.5,<0.3.0']

extras_require = \
{'deploy': ['docker-compose>=1.29.2,<1.30.0'],
 'docker': ['docker-compose>=1.29.2,<1.30.0']}

entry_points = \
{'console_scripts': ['nb = nb_cli.__main__:main']}

setup_kwargs = {
    'name': 'nb-cli',
    'version': '0.6.5',
    'description': 'CLI for nonebot2',
    'long_description': '# nb-cli\n\n[English](./README_en.md) | **中文**\n\nNoneBot2 的命令行工具\n\n## 功能\n\n- 创建新的 Nonebot 项目\n- 启动 Nonebot\n- 部署 NoneBot 到 Docker\n- 管理插件\n  - 创建新的插件\n  - 搜索/安装/更新/卸载在官方商店上发布的插件\n- 管理适配器\n  - 创建新的适配器\n  - 搜索/安装/更新/卸载在官方商店上发布的适配器\n\n## 使用\n\n### 安装\n\n```shell\npip install nb-cli\n```\n\n或者，带有可选的 `deploy` 依赖项\n\n```shell\npip install nb-cli[deploy]\n```\n\n### 命令行使用\n\n```shell\nnb --help\n```\n\n- `nb init (create)` 创建新的 Nonebot 项目\n- `nb run` 在当前目录启动 Nonebot\n- `nb driver` 管理驱动器\n  - `nb driver list` 查看驱动器列表\n  - `nb driver search` 搜索驱动器\n  - `nb driver install (add)` 安装驱动器\n- `nb plugin` 管理插件\n  - `nb plugin new (create)` 创建新的插件\n  - `nb plugin list` 列出官方商店的所有插件\n  - `nb plugin search` 在官方商店搜索插件\n  - `nb plugin install (add)` 安装插件\n  - `nb plugin update` 更新插件\n  - `nb plugin uninstall (remove)` 卸载插件\n- `nb adapter` 管理适配器\n  - `nb adapter new (create)` 创建新的适配器\n  - `nb adapter list` 列出官方商店的所有适配器\n  - `nb adapter search` 在官方商店搜索适配器\n  - `nb adapter install (add)` 安装适配器\n  - `nb adapter update` 更新适配器\n  - `nb adapter uninstall (remove)` 卸载适配器\n\n#### 以下功能需要 [deploy] 依赖\n\n- `nb build` 在当前目录构建 Docker 镜像\n- `nb deploy (up)` 在当前目录构建、创建并运行 Docker 容器\n- `nb exit (down)` 在当前目录停止并删除 Docker 容器\n\n### 交互式使用\n\n```shell\nnb\n```\n\n### CookieCutter 使用\n\n#### 安装 cookiecutter\n\n```shell\npip install cookiecutter\n```\n\n#### 创建项目\n\n```shell\ncookiecutter https://github.com/nonebot/nb-cli.git --directory="nb_cli/project"\n```\n\n#### 创建插件\n\n```shell\ncookiecutter https://github.com/nonebot/nb-cli.git --directory="nb_cli/plugin"\n```\n\n#### 创建适配器\n\n```shell\ncookiecutter https://github.com/nonebot/nb-cli.git --directory="nb_cli/adapter"\n```\n',
    'author': 'yanyongyu',
    'author_email': 'yanyongyu_1@126.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://v2.nonebot.dev/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
