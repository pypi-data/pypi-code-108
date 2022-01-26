# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_guild_patch']

package_data = \
{'': ['*']}

install_requires = \
['nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0', 'nonebot2>=2.0.0-beta.1,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-guild-patch',
    'version': '0.1.1',
    'description': 'Patch plugin for NoneBot2 QQ guild (go-cqhttp) support.',
    'long_description': '# nonebot-plugin-guild-patch\n\n*Patch plugin for NoneBot2 QQ guild (go-cqhttp) support.*\n\n*NoneBot2 QQ 频道 (go-cqhttp) 支持适配补丁插件.*\n\n![PyPI](https://img.shields.io/pypi/v/nonebot-plugin-guild-patch?style=for-the-badge)\n\n[![GitHub issues](https://img.shields.io/github/issues/mnixry/nonebot-plugin-guild-patch)](https://github.com/mnixry/nonebot-plugin-guild-patch/issues)\n[![GitHub forks](https://img.shields.io/github/forks/mnixry/nonebot-plugin-guild-patch)](https://github.com/mnixry/nonebot-plugin-guild-patch/network)\n[![GitHub stars](https://img.shields.io/github/stars/mnixry/nonebot-plugin-guild-patch)](https://github.com/mnixry/nonebot-plugin-guild-patch/stargazers)\n[![GitHub license](https://img.shields.io/github/license/mnixry/nonebot-plugin-guild-patch)](https://github.com/mnixry/nonebot-plugin-guild-patch/blob/main/LICENSE)\n\n> **注: 本补丁没有经过充分测试, 不建议在生产环境使用, 如果发现任何问题请[Issue反馈](https://github.com/mnixry/nonebot-plugin-guild-patch/issues/new/choose)**\n\n## 适用版本\n\n- [`go-cqhttp` >= `1.0.0-beta8`](https://github.com/Mrs4s/go-cqhttp/releases/tag/v1.0.0-beta8)\n  - 已支持[`1.0.0-beta8-fix1`](https://github.com/Mrs4s/go-cqhttp/releases/tag/v1.0.0-beta8-fix1)新加入的事件\n- `NoneBot2` >= `2.0.0b1`\n\n## 支持功能\n\n- [x] 正常接收并处理频道消息事件\n  - [x] 支持字符串形式消息上报\n  - [x] 支持数组形式消息上报\n- [x] 支持`bot.send`和`matcher.send`直接向频道发送消息\n- [ ] 支持`event.to_me`以支持`to_me`规则\n- [ ] 可选的事件转换器, 将频道消息事件转换为群消息\n\n## 安装\n\n使用`nb-cli`或者其他什么你喜欢的方式安装并加载该插件即可\n\n如果它被成功加载, 你在调试模式下应该看到这样的日志:\n\n```diff\n11-13 09:14:52 [DEBUG] nonebot | Succeeded to load adapter "cqhttp"\n11-13 09:14:52 [SUCCESS] nonebot | Succeeded to import "nonebot.plugins.echo"\n+ 11-13 09:14:52 [SUCCESS] nonebot | Succeeded to import "nonebot_plugin_guild_patch"\n11-13 09:14:52 [SUCCESS] nonebot | Running NoneBot...\n11-13 09:14:52 [DEBUG] nonebot | Loaded adapters: cqhttp\n11-13 09:14:52 [INFO] uvicorn | Started server process [114514]\n11-13 09:14:52 [INFO] uvicorn | Waiting for application startup.\n11-13 09:14:52 [INFO] uvicorn | Application startup complete.\n```\n\n## 使用\n\n这里有一个示例插件, 它只会接收来自频道的消息\n\n```python\nfrom nonebot.plugin import on_command\nfrom nonebot.adapters.cqhttp import Bot, MessageSegment\n\nfrom nonebot_plugin_guild_patch import GuildMessageEvent\n\nmatcher = on_command(\'image\')\n\n\n@matcher.handle()\nasync def _(bot: Bot, event: GuildMessageEvent):\n    await matcher.send(\n        MessageSegment.image(\n            file=\'https://1mg.obfs.dev/\',\n            cache=False,\n        ))\n```\n\n## 开源许可\n\n本项目使用[MIT](./LICENSE)许可证开源\n\n    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n    SOFTWARE.\n',
    'author': 'Mix',
    'author_email': 'mnixry@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mnixry/nonebot-plugin-guild-patch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
