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
    'version': '0.1.10',
    'description': '',
    'long_description': '<p align="center">\n    <em>한국 통신사 rcs 를 위한 pydantic 구조체</em>\n</p>\n<p align="center">\n<a href="https://github.com/xncbf/rcs-pydantic/actions?query=workflow%3ATests+event%3Apush+branch%3Amain" target="_blank">\n    <img src="https://github.com/xncbf/rcs-pydantic/workflows/Tests/badge.svg?event=push&branch=main" alt="Test">\n</a>\n<a href="https://codecov.io/gh/xncbf/rcs-pydantic" target="_blank">\n    <img src="https://img.shields.io/codecov/c/github/xncbf/rcs-pydantic?color=%2334D058" alt="Coverage">\n</a>\n<a href="https://pypi.org/project/rcs-pydantic" target="_blank">\n    <img src="https://img.shields.io/pypi/v/rcs-pydantic?color=%2334D058&label=pypi%20package" alt="Package version">\n</a>\n<a href="https://pypi.org/project/rcs-pydantic" target="_blank">\n    <img src="https://img.shields.io/pypi/pyversions/rcs-pydantic.svg?color=%2334D058" alt="Supported Python versions">\n</a>\n</p>\n\n- [Installation](#installation)\n- [Quick start](#quick-start)\n- [Features](#features)\n- [Contribution](#contribution)\n\n## Installation\n\n```sh\npip install rcs-pydantic\n```\n\n## Quick start\n\n```py\nimport httpx\nfrom fastapi import Body, FastAPI\nfrom rcs_pydantic import scheme\n\napp = FastAPI()\n\n\ndef get_card(message_info):\n    rcs_message = RcsMessage(\n        message_info,\n        agency_id="ktbizrcs",\n        message_base_id="STANDALONE_1",\n        service_type="RCSSMS",\n        expiry_option=2,\n        header="0",\n        footer="080-0000-0000",\n        cdr_id="ktrcs02",\n        copy_allowed=True,\n        body=scheme.RcsSMSBody(\n            description=textwrap.dedent(\n                """\\\n                안녕하세요.\n                메세지입니다.\n                """\n            )\n        ),\n        buttons=[\n            scheme.ButtonInfo(\n                suggestions=[\n                    scheme.SuggestionInfo(\n                        action=scheme.ActionInfo(\n                            urlAction=scheme.UrlActionInfo(\n                                openUrl=scheme.OpenUrlInfo(url="https://www.kt.com")\n                            ),\n                            displayText="kt 홈페이지 들어가기",\n                            postback=scheme.PostbackInfo(data="postback_kt"),\n                        )\n                    )\n                ]\n            )\n        ],\n    )\n    return rcs_message\n\n@app.post("/corp/{version}/momsg")\nasync def recieve_message(version: str, message_info: scheme.MessageInfo = Body(...)):\n    """\n    메세지 받는 웹훅\n    """\n    body = get_card(message_info)\n    response = httpx.post(url=f"{config.RCS_URL}/message", json=body.json())\n    return {"status": response.status_code, "content": response.json()}\n\n```\n\n## Features\n\nTODO\n\n## Contribution\n\nTODO\n',
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
