# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_htmlrender']

package_data = \
{'': ['*'], 'nonebot_plugin_htmlrender': ['templates/*', 'templates/katex/*']}

install_requires = \
['Pygments>=2.10.0,<3.0.0',
 'aiofiles>=0.8.0,<0.9.0',
 'jinja2>=3.0.3,<4.0.0',
 'markdown>=3.3.6,<4.0.0',
 'nonebot-adapter-cqhttp>=2.0.0-alpha.16,<3.0.0',
 'nonebot2>=2.0.0-alpha.16,<3.0.0',
 'playwright>=1.17.2,<2.0.0',
 'pymdown-extensions>=9.1,<10.0',
 'python-markdown-math>=0.8,<0.9']

setup_kwargs = {
    'name': 'nonebot-plugin-htmlrender',
    'version': '0.0.4.2',
    'description': '通过浏览器渲染图片',
    'long_description': '# nonebot-plugin-htmlrender\n\n* 通过浏览器渲染图片\n* 可通过查看`example`参考使用实例\n\n# ✨ 功能\n\n* 通过html和浏览器生成图片\n* 支持`纯文本` `markdown` 和 `jinja2` 模板输入 \n* 通过 CSS 来控制样式\n\n\n\n# 使用\n\n参考[example/plugins/render/__init__.py](example/plugins/render/__init__.py)\n\n## markdown 转 图片\n\n- 使用 `GitHub-light` 样式\n- 支持绝大部分 md 语法\n- 代码高亮\n- latex 数学公式 （感谢@[MeetWq](https://github.com/MeetWq)）\n    - 使用 `$$...$$` 来输入独立公式\n    - 使用 `$...$` 来输入行内公式\n- 图片需要使用外部连接并使用`html`格式 否则文末会超出截图范围\n- 图片可使用md语法 路径可为 `绝对路径`(建议), 或 `相对于template_path` 的路径\n\n## 模板 转 图片\n\n- 使用jinja2模板引擎\n- 页面参数可自定义\n\n# 🌰 栗子\n\n[example.md](docs/example.md)\n## 文本转图片（同时文本里面可以包括html图片）\n![](docs/text2pic.png)\n\n## markdown转图片（同时文本里面可以包括html图片）\n![](docs/md2pic.png)\n\n## 纯html转图片\n![](docs/html2pic.png)\n\n## jinja2模板转图片\n![](docs/template2pic.png)\n\n\n# 特别感谢\n\n- [MeetWq](https://github.com/MeetWq) 提供数学公式支持代码和代码高亮',
    'author': 'kexue',
    'author_email': 'xana278@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0',
}


setup(**setup_kwargs)
