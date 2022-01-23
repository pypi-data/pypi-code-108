# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tep']

package_data = \
{'': ['*']}

install_requires = \
['allure-pytest>=2.8.16,<3.0.0',
 'allure-python-commons>=2.8.16,<3.0.0',
 'faker>=4.1.1,<5.0.0',
 'fastapi>=0.72.0,<0.73.0',
 'httprunner>=3.1.6,<4.0.0',
 'jmespath>=0.9.5,<0.10.0',
 'loguru>=0.4.1,<0.5.0',
 'pydantic>=1.9.0,<2.0.0',
 'pytest-assume>=2.4.2,<3.0.0',
 'pytest>=5.4.2,<6.0.0',
 'pyyaml>=5.4.1,<6.0.0',
 'requests>=2.22.0,<3.0.0',
 'urllib3>=1.25.9,<2.0.0',
 'uvicorn>=0.17.0,<0.18.0']

entry_points = \
{'console_scripts': ['tep = tep.cli:main'],
 'pytest11': ['tep = tep.plugin:Plugin']}

setup_kwargs = {
    'name': 'tep',
    'version': '0.9.6',
    'description': 'tep is a testing tool to help you write pytest more easily. Try Easy Pytest!',
    'long_description': '# tep\n\n`tep`是**T**ry **E**asy **P**ytest的首字母缩写，是一款基于pytest测试框架的测试工具，集成了各种实用的第三方包和优秀的自动化测试设计思想，帮你快速实现自动化项目落地。\n\n# 安装\n\n支持Python3.6以上，推荐Python3.8以上。\n\n标准安装：\n\n```\n$ pip install tep\n```\n\n国内镜像：\n\n```\n$ pip --default-timeout=600 install -i https://pypi.tuna.tsinghua.edu.cn/simple tep\n```\n\n检查安装成功：\n\n```\n$ tep -V  # 或者 tep --version\n0.2.3\n```\n\n# 快速创建项目\n\ntep提供了脚手架，预置了项目结构和代码，打开cmd，使用`startproject`命令快速创建项目：\n\n```\ntep startproject project_name\n```\n\n并且提供了`-venv`参数，在项目初始化时，可以同时创建一个虚拟环境（推荐）：\n\n```\ntep startproject project_name -venv\n```\n\n# 输出测试报告\n\ntep提供了`--tep-reports`参数来生成allure测试报告：\n\n```\npytest  --tep-reports\n```\n\n报告文件存放在根目录的`reports/`中。\n\n# Mock服务\n\ntep自带了一个Flask应用（`utils/flask_mock_api.py`），提供了登录到下单流程的5个接口，启动后即可一键运行示例中的测试用例。\n\n# 三种开发模式\n\ntep兼容三种开发模式：tep（用例数据一体）、mvc（用例数据分离）、HttpRunner。\n\n①tep，示例代码如下所示：\n\n```python\nimport jmespath\nfrom tep.client import request\n\n\ndef test(env_vars, login):\n    # 搜索商品\n    response = request(\n        "get",\n        url=env_vars.domain + "/searchSku",\n        headers={"token": login.token},\n        params={"skuName": "电子书"}\n    )\n    sku_id = jmespath.search("skuId", response.json())\n    sku_price = jmespath.search("price", response.json())\n    assert response.status_code < 400\n\n    # 添加购物车\n    sku_num = 3\n    response = request(\n        "post",\n        url=env_vars.domain + "/addCart",\n        headers={"token": login.token},\n        json={"skuId": sku_id, "skuNum": sku_num}\n    )\n    total_price = jmespath.search("totalPrice", response.json())\n    assert response.status_code < 400\n\n    # 下单\n    response = request(\n        "post",\n        url=env_vars.domain + "/order",\n        headers={"token": login.token},\n        json={"skuId": sku_id, "price": sku_price, "skuNum": sku_num, "totalPrice": total_price}\n    )\n    order_id = jmespath.search("orderId", response.json())\n    assert response.status_code < 400\n\n    # 支付\n    response = request(\n        "post",\n        url=env_vars.domain + "/pay",\n        headers={"token": login.token},\n        json={"orderId": order_id, "payAmount": "6.9"}\n    )\n    assert response.status_code < 400\n    assert response.json()["success"] == "true"\n\n```\n\n更多内容请参考[《如何使用teprunner测试平台编写从登录到下单的大流程接口自动化用例》](https://dongfanger.gitee.io/blog/teprunner/012-%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8teprunner%E6%B5%8B%E8%AF%95%E5%B9%B3%E5%8F%B0%E7%BC%96%E5%86%99%E4%BB%8E%E7%99%BB%E5%BD%95%E5%88%B0%E4%B8%8B%E5%8D%95%E7%9A%84%E5%A4%A7%E6%B5%81%E7%A8%8B%E6%8E%A5%E5%8F%A3%E8%87%AA%E5%8A%A8%E5%8C%96%E7%94%A8%E4%BE%8B.html)\n\n②mvc\n\n```python\nfrom tep.fixture import TepVars\n\nfrom services.AddCart import AddCart\nfrom services.Login import Login\nfrom services.Order import Order\nfrom services.Pay import Pay\nfrom services.SearchSku import SearchSku\n\n\\"\\"\\"\n测试登录到下单流程，需要先运行utils / flask_mock_api.py\n\\"\\"\\"\n\n\nclass Test:\n    case_vars = TepVars()\n    case_vars.vars_ = {\n        "domain": "http://127.0.0.1:5000",\n        "skuNum": "3"\n    }\n\n    def test(self):\n        # 登录\n        Login(Test).post()\n        # 搜索商品\n        SearchSku(Test).get()\n        # 添加购物车\n        AddCart(Test).post()\n        # 下单\n        Order(Test).post()\n        # 支付\n        Pay(Test).post()\n```\n\n③HttpRunner，示例代码如下所示：\n\n```python\nfrom httprunner import HttpRunner, Config, Step, RunRequest\n\n\nclass TestLoginPay(HttpRunner):\n    config = (\n        Config("登录到下单流程")\n            .variables(\n            **{\n                "skuNum": "3"\n            }\n        )\n            .base_url("http://127.0.0.1:5000")\n    )\n\n    teststeps = [\n        Step(\n            RunRequest("登录")\n                .post("/login")\n                .with_headers(**{"Content-Type": "application/json"})\n                .with_json({"username": "dongfanger", "password": "123456"})\n                .extract()\n                .with_jmespath("body.token", "token")\n                .validate()\n                .assert_equal("status_code", 200)\n        ),\n        Step(\n            RunRequest("搜索商品")\n                .get("searchSku?skuName=电子书")\n                .with_headers(**{"token": "$token"})\n                .extract()\n                .with_jmespath("body.skuId", "skuId")\n                .with_jmespath("body.price", "skuPrice")\n                .validate()\n                .assert_equal("status_code", 200)\n        ),\n        Step(\n            RunRequest("添加购物车")\n                .post("/addCart")\n                .with_headers(**{"Content-Type": "application/json",\n                                 "token": "$token"})\n                .with_json({"skuId": "$skuId", "skuNum": "$skuNum"})\n                .extract()\n                .with_jmespath("body.totalPrice", "totalPrice")\n                .validate()\n                .assert_equal("status_code", 200)\n        ),\n        Step(\n            RunRequest("下单")\n                .post("/order")\n                .with_headers(**{"Content-Type": "application/json",\n                                 "token": "$token"})\n                .with_json({"skuId": "$skuId", "price": "$skuPrice", "skuNum": "$skuNum", "totalPrice": "$totalPrice"})\n                .extract()\n                .with_jmespath("body.orderId", "orderId")\n                .validate()\n                .assert_equal("status_code", 200)\n        ),\n        Step(\n            RunRequest("支付")\n                .post("/pay")\n                .with_headers(**{"Content-Type": "application/json",\n                                 "token": "$token"})\n                .with_json({"orderId": "$orderId", "payAmount": "6.9"})\n                .validate()\n                .assert_equal("status_code", 200)\n                .assert_equal("body.success", "true")\n        ),\n    ]\n```\n\n# 猴子补丁扩展request\n\n扩展request，只需要实现`utils/http_client.py`里面的request_monkey_patch猴子补丁即可：\n\n```python\n#!/usr/bin/python\n# encoding=utf-8\n\nimport decimal\nimport json\nimport time\n\nimport allure\nfrom loguru import logger\nfrom tep import client\nfrom tep.client import TepResponse\n\n\ndef request_monkey_patch(req, *args, **kwargs):\n    start = time.process_time()\n    desc = ""\n    if "desc" in kwargs:\n        desc = kwargs.get("desc")\n        kwargs.pop("desc")\n    response = req(*args, **kwargs)\n    end = time.process_time()\n    elapsed = str(decimal.Decimal("%.3f" % float(end - start))) + "s"\n    log4a = "{}\\n{}status:{}\\nresponse:{}\\nelapsed:{}"\n    try:\n        kv = ""\n        for k, v in kwargs.items():\n            # if not json, str()\n            try:\n                v = json.dumps(v, ensure_ascii=False)\n            except TypeError:\n                v = str(v)\n            kv += f"{k}:{v}\\n"\n        if args:\n            method = f\'\\nmethod:"{args[0]}" \'\n        else:\n            method = ""\n        request_response = log4a.format(method, kv, response.status_code, response.text, elapsed)\n        logger.info(request_response)\n        allure.attach(request_response, f\'{desc} request & response\', allure.attachment_type.TEXT)\n    except AttributeError:\n        logger.error("request failed")\n    except TypeError:\n        logger.warning(log4a)\n    return TepResponse(response)\n\n\ndef request(method, url, **kwargs):\n    client.tep_request_monkey_patch = request_monkey_patch\n    return client.request(method, url, **kwargs)\n```\n\n# 可选第三方包安装\n\n```\n# pip install --default-timeout=6000 -i https://pypi.tuna.tsinghua.edu.cn/simple pandas\n\n# mysql\npandas==1.1.0\nSQLAlchemy==1.3.19\nPyMySQL==0.10.0\ntexttable==1.6.2\n\n# more\n```\n\n# 用户手册\n\nhttps://dongfanger.gitee.io/blog/chapters/tep.html\n\n# 联系我\n\nhttps://dongfanger.gitee.io/blog/more.html\n\n',
    'author': 'dongfanger',
    'author_email': 'dongfanger@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dongfanger/tep',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
