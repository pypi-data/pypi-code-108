# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rcs_pydantic']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'rcs-pydantic',
    'version': '0.1.14',
    'description': '',
    'long_description': '# RCS-PYDANTIC\n\n<p align="center">\n<a href="https://github.com/xncbf/rcs-pydantic/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/xncbf/rcs-pydantic/workflows/Tests/badge.svg?event=push&branch=main" alt="Test">\n</a>\n<a href="https://codecov.io/gh/xncbf/rcs-pydantic" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/xncbf/rcs-pydantic?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/rcs-pydantic" target="_blank">\n    <img src="https://img.shields.io/pypi/v/rcs-pydantic?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/rcs-pydantic" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/rcs-pydantic.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n- [RCS-PYDANTIC](#rcs-pydantic)\n  - [Introduce](#introduce)\n  - [Installation](#installation)\n  - [Quick start](#quick-start)\n  - [Features](#features)\n  - [Contribution](#contribution)\n\n## Introduce\n\n한국 통신사 rcs 를 위한 pydantic 구조체\n\n## Installation\n\n```sh\npip install rcs-pydantic\n```\n\n## Quick start\n\n```py\nfrom rcs_pydantic import MessageInfo, RcsMessage\n\nmessage_info = {\n    "replyId": "B01RDSFR.KcNNLk67ui.FDSAF432153214",\n    "eventType":"message",\n    "messageBody": "{\\"textMessage\\":\\"안녕하세요?\\"}",\n    "userContact":"01012341234",\n    "chatbotId":"0212351235",\n    "timestamp": "2020-03-03T04:43:55.867+09"\n}\n\nrcs = {\n    "message_base_id": "SCS00000",\n    "service_type": "RCSSMS",\n    "header": "0",\n    "cdr_id": "KT_rcsid",\n    "body": {\n        "title": "타이틀",\n        "description": "일반 RCSSMS 테스트 메시지 입니다."\n    }\n}\n\n\nrcs_message = RcsMessage(message_info=MessageInfo(**message_info), **rcs)\n```\n\n```sh\n>>> print(rcs_message.send_info)\ncommon=CommonInfo(\n    msgId=\'B01RDSFR.KcNNLk67ui.FDSAF432153214\',\n    userContact=\'01012341234\',\n    scheduleType=<ScheduleTypeEnum.IMMEDIATE: 0>,\n    msgGroupId=None,\n    msgServiceType=<MessageServiceTypeEnum.RCS: \'rcs\'>\n)\nrcs=RcsInfo(\n    chatbotId=\'0212351235\',\n    agencyId=\'ktbizrcs\',\n    messagebaseId=\'SCS00000\',\n    serviceType=<ServiceTypeEnum.SMS: \'RCSSMS\'>,\n    expiryOption=<ExpiryOptionEnum.AFTER_SETTING_TIMES: 2>,\n    header=<HeaderEnum.NOT_ADVERTISE: \'0\'>,\n    footer=None,\n    cdrId=\'KT_rcsid\',\n    copyAllowed=True,\n    body=RcsSMSBody(title=\'타이틀\', description=\'일반 RCSSMS 테스트 메시지 입니다.\'),\n    buttons=None,\n    chipLists=None,\n    replyId=None\n)\n>>>\n```\n\n## Features\n\nTODO\n\n## Contribution\n\nTODO\n',
    'author': 'xncbf',
    'author_email': 'xncbf12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/xncbf/rcs-pydantic',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
