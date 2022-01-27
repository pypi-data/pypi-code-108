# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['graphql_schema_parse']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.3,<4.0.0', 'graphql-core>=3.2.0,<4.0.0', 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['gql = graphql_schema_parse.cli:app']}

setup_kwargs = {
    'name': 'graphql-schema-parse',
    'version': '0.2.0',
    'description': 'Graphql文档解析工具，提供解析成前端/Postman可用的query语句(.gql)或者RESTFul可使用的(.json)文件能力',
    'long_description': '# graphql_schema_parse\n> 解析GraphQL文档，并提供将其转成**.gql**(前端查询可用得query字符串)，**.json**(requests可用得json关键字参数接收数据)\n\n## [GraphQL](https://graphql.cn/)\n> GraphQL 既是一种用于 API 的查询语言也是一个满足你数据查询的运行时，详细内容点击标题访问官网\n在实际工作种，最常用的是 query(查询), mutation(更改/新增), subscription\n\n当发起一个GraphQL请求之后，通过抓包能够发现，最终和RESTFul发送请求没多大区别，它指定了JSON格式传参数，大致如下\n![](images/发送graphq.png)\n![](images/graphql请求数据.png)\n```json\n{\n  "query": " query users {\\n        users{\\n                  id\\n                  username\\n                 }\\n             \\n        }\\n        ",\n  "variables": {},\n  "operationName": "users"\n}\n```\n```json\n{\n  "query": "mutation addUser($username: String!, $password: String!) {\\n  addUser(username: $username, password: $password) {\\n    id\\n    username\\n  }\\n}\\n",\n  "variables": {\n    "username": "gql",\n    "password": "gql1"\n  },\n  "operationName": "addUser"\n}\n```\n```json\n{\n  "query": "mutation addUserInput($user: AddUserInput!) {\\n  addUserInput(user: $user) {\\n    id\\n    username\\n  }\\n}\\n",\n  "variables": {\n    "user": {\n      "username": "haha",\n      "password": "gg"\n    }\n  },\n  "operationName": "addUserInput"\n}\n```\n\n- query: 其实就是生成的查询部分语句，前端传字段后端定义有返回\n- variables: 使用query语句中的变量名\n- operationName: 则是后端在实现时指定的接口名称(暂时这么理解吧)\n![](images/介绍.png)\n**这里用的Python语言，实际 `_` 会被转换成 `驼峰写法`**\n\n## GraphQL示例应用\n> 提供的GraphQL示例应用源码地址：https://gitee.com/zy7y/starlette-example\n### 源码使用\n1. 克隆\n```shell\ngit clone https://gitee.com/zy7y/starlette-example\n```\n2. 安装依赖\n```shell\npip install -r requirements.txt \npip install strawberry-graphql[debug-server]\n```\n![](images/依赖安装.png)\n3. 启动\n```shell\ncd injection_service\\graphql\nstrawberry server schema \n```\n![](images/微信截图_20220126162625.png)\n**访问：http://127.0.0.1:8000**\n![](images/微信截图_20220126163024.png)\n### 通过url获取接口文档\n``` shell\n# 转JSON\ngql parse http://127.0.0.1:8000 目录地址\n\n# 转GQL\ngql parse http://127.0.0.1:8000 --to gql 目录地址\n\n# 转sqlmap(-r HTTP请求信息.txt)\n# 带json\ngql parse http://127.0.0.1:8000 --headers .\\examples\\headers.json --to sqlmap .\\examples\\sqlmap（json）示例\n# 不带json\ngql parse http://127.0.0.1:8000 --to sqlmap .\\examples\\sqlmap示例\n```\n**需要Token认证**\n```json5\n// 新建headers.json 如下\n{\n"Authorization": "Bearer token"\n}\n```\n```shell\ngql parse http://127.0.0.1:8000 --headers headers.json 目录地址\n```\n![url获取示例](images/urlheaders.png)\n## 使用graphql-schema-parse\n### 安装\n```shell\npip install graphql-schema-parse\n```\n\n### 通过SDL获取接口文档\n1. 前置条件\n```shell\n# 在执行启动服务相同目录下执行, 得到SDL\nstrawberry export-schema schema > schema.graphql\n```\n![](images/sdl.png)\n2. 通过graphql文件转换成gql\n**sdl文件必须是utf-8编码，不是则自行修改**\n```shell\ngql parse examples\\schema.graphql --to gql 目录地址\n```\n![](images/togql.png)\n\n## 测试\n1. gql文件(查询-query)\n**将生成的users.gql 文件内容复制到127.0.0.1:8000当中**\n![](images/query.png)\n2. gql文件(突变-mutation)\n**将生成的addUser.gql 文件内容复制到127.0.0.1:8000当中**\n![](images/add_user.png)\n3. json文件(查询-query)\n**将生成的users.json 文件内容赋值给`data`，使用requests包发送请求，代码如下**\n```python\nfrom requests import post\n\nurl = "http://127.0.0.1:8000/graphql"\ndata = {\n    "query": " query users {\\n        users{\\n                  id\\n                  username\\n                 }\\n             \\n        }\\n        ",\n    "variables": {}, "operationName": "users"}\nprint(post(url, json=data).json())\n```\n![](images/gql-restful.png)\n4. json文件(突变-mutation)\n**将生成的addUsers.json 文件内容赋值给`data`，使用requests包发送请求，代码如下**\n```python\nfrom requests import post\n\nurl = "http://127.0.0.1:8000/graphql"\ndata = {\n    "query": " mutation addUserInput ($user: AddUserInput!){\\n        addUserInput (user: $user){\\n                  id\\n                  username\\n                 }\\n             \\n        }\\n        ",\n    "variables": {"user": {"username": "", "password": ""}}, "operationName": "addUserInput"}\nprint(post(url, json=data).json())\n\n```\n![](images/json-restful.png)\n5. txt文件(sqlmap -r httpinfo.txt， 可用于sqlmap sql注入扫描)\n**addUserInput.txt文件内容**\n```text\nPOST /graphql HTTP/1.1\nHOST: http://127.0.0.1:8000\nAuthorization: Bearer token\nContent-Type: application/json\n\n{"query": " mutation addUserInput ($user: AddUserInput!){\\n        addUserInput (user: $user){\\n                  id\\n                  username\\n                 }\\n             \\n        }\\n        ", "variables": {"user": {"username": "*", "password": "*"}}, "operationName": "addUserInput"}\n```\n```shell\n# 安装sqlmap\npip install sqlmap\n\n# 进行SQL注入扫描， sqlmap详细用法前往sqlmap官网学习\nsqlmap -r addUserInput.txt --level 5 --risk 3\n```\n**扫描过程中**\n![](images/sqlmap执行过程.png)\n![](images/执行时服务被不断请求.png)\n![](images/入库数据.png)\n**扫描结果（获取到了我的数据库为SQLlite）**\n![](images/注入结果.png)\n\n# 参数详情\n```shell\ngql parse --help \n```\noutput:\n```shell\nUsage: cli.py parse [OPTIONS] FROM_PATH TO_DIRECTORY\n\n  将Graphql接口文档转成gql文件/Json文件 :param from_path: 接口文档地址, 本地JSON文件地址(.json) 或者 本地\n  SDL文件(.schema ), 或者 服务器URL填入(服务器的IP:PORT) :param to: 转换之后的文件类型, 可选\n  TO_DIRECTORY  生成文件保存目录，不存在时，自动创建  [required]\n\nOptions:\n  --headers TEXT   url方式获取接口文档时，可选项传入请求头json文件地址\n  --to [json|gql]  [default: ToType.to_json]\n  --depth INTEGER  query语句体中可用查询字段递归深度  [default: 1]\n  --help           Show this message and exit.\n\n```\n',
    'author': '柒意',
    'author_email': '396667207@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zy7y/graphql-schema-parse.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
