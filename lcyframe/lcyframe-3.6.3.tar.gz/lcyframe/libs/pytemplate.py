# -*- coding:utf-8 -*-
from lcyframe.libs import Copyright

def get_handler_init(path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))

""" % (Copyright.file_pre)

    import_str = """
# xxx_handler xx leng must > 1.
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue
    logging.debug("handler [%s] register success!" % hander_file)
    __import__(model_name, globals(), locals(), [model_name], -1)
"""

    return auto_str + import_str


def get_docs_agree():
    """

    :return:
    """
    auto_str = """
## 一、约定说明
### 1.1 参数说明

**请求方式：本框架规定了所有请求参数所配置的方式以及用途：**

|参数位置|Content-Type|编码方式|举个例子|说明|
|---|---|---|---|---|
|path|--|--|/url/{user}/{uid}|拼接在url内|
|query|--|--|/url/user?uid=10|拼接在?后|
|body|application/x-www-form-urlencoded|x-www-form-urlencoded|'uid=100&sex=1'|表单提交，推荐|
|body|application/json|x-www-form-urlencoded|'uid=100&sex=1'|json提交|
|body|multipart/form-data|form-data|{"file": open("../demo.jpg")}|上传文件|

> 1、path：参数被设置在请求url内；如"/url/xxx/yyy"。注意，使用该模式，框架不会自动收集参数，即self.params永远为空

> 2、query：参数被设置在?后面：如"/url?xxx=111&yyy=222"

> 3、body: json提交，参数以json的格式被设置在body内，body设置为x-www-form-urlencoded，Content-Type设置为"application/json"。注意该模式与body-form不能同时设置。

> 4、body：表单提交，参数以kv的格式被设置在body内，body设置为x-www-form-urlencoded，Content-Type设置为"application/x-www-form-urlencoded"。注意该模式与body-json不能同时设置。

> 5、file：上传文件。body设置为form-data，Content-Type设置为"multipart/form-data;boundary=abcefxxx",boundary分解符通常会自动被设置为一个随机字符 
> 
> 注意：以上345模式，由于值都被设置在body内，所以在同一api内，对于不同的参数，不允许混用不同的模式。唯一的例外是，第5（multipart/form-data），既允许同时上传文件，又允许设置其他参数。

**Restful请求示例：**
~~~python
### Send POST request with body as form parameters
POST https://domain.com/post
Content-Type: application/x-www-form-urlencoded

{
  "id": 999,
  "value": "content"
}

### Send POST request with json body
POST https://domain.com/post
Content-Type: application/json

id=999&value=content

### Send a form with the text and file fields
POST https://domain.com/post
Content-Type: multipart/form-data; boundary=WebAppBoundary

--WebAppBoundary
Content-Disposition: form-data; name="element-name"
Content-Type: text/plain

Name
--WebAppBoundary
Content-Disposition: form-data; name="data"; filename="data.json"
Content-Type: application/json

< ./request-form-data.json
--WebAppBoundary--

###
~~~

**参数值类型：在设置schema.yml时，指定type的值允许是以下几种之一**

|类型|说明|
|---|---|
| int | 整形|
| float | 浮点型|
| str | 字符串|
| list | 数组（不推荐)|
| json | json串|
| file | 文件|

### 1.2 headers
API请求时，需要提供请求头

headers：
~~~python
{
    "uid": "10000，注册成功、登录成功后返回",
    "token": "授权码, 注册成功、登录成功后返回",
    "locale": "cn",
    "lang": "",
    "version": "默认 1.0", 
    "bundle": "",
    "platform": 0 IOS, 1 Android,
    "os": "",
    "device_id": ""
}
~~~
### 1.3 API 请求结果
当`HTTP_CODE=200`时，代表本次请求响应成功，响应结构如下所示：
~~~python
{
  "error": 0, 
  "msg": msg, 
  "data": {}
}
~~~

>`error`: 当`error=0`时，代表API处理成功，客户端可以正常处理data；当`error!=0`时，代表API处理失败，error即为对应的异常码
>
>`msg`: 字段为本次请求的提示信息。当`error=0`时，`msg=ok`；当`error!=0`时，`msg=ErrorName`
>
>`data`: 为本次API返回的数据，如{'nickname'：'昵称', 'sex'：1}。在接口文档中，不同的API所返回的结构不同,具体详见《接口说明》

当`HTTP_CODE!=200`时，如`404`、`405`、`500`的错误码，客户端按需处理

### 1.4 双向校验码seq生成
部分防刷接口需要提供参数seq，生成方法如下

salt：写死在客户端
~~~
例如：
params={"nickname": "阿刘", "age": "111", "timestamp": 1473761433}
上述2个参数value 均为 utf-8 编码, 根据key的字典顺序排序 键和值之间用"="连接 键值对之间用"&"连接,
生成待校验的字符串string, string 与 salt 字符串 拼接,计算校验码：
seq = md5(salt + "nickname=阿刘&age=111&timestamp=1473761433")
注：凡需要传seq的接口，必须同时提供请求时间戳参数：timestamp
~~~

### 1.5 翻页码规则：仅支持查看下一页，不支持跳页
参数名：last_id，由服务器返回。客户端可以在请求列表时，回传给服务端，
~~~
    1、当不提供该参数时，代表查看第一页
    2、当服务端返回last_id=-1时，代表没有下一页了
~~~

### 1.6 域名配置
**本地环境：**
> 1、api：http://192.168.2.50:6700  
> 2、docs文档：http://192.168.2.50:6779

**测试环境：**
> 1、api：http://192.168.2.140:6700  
> 2、docs文档：http://192.168.2.140:6779
"""
    return auto_str


def get_mq_work_init():
    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
    """ % Copyright.file_pre

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_worker\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    logging.debug("register mq workers [%s.py] success!" % model_name)
    __import__(model_name, globals(), locals(), [model_name], -1)
    """

    return auto_str + import_str


def get_nsq_producer_init(root_path, produce_path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
from importlib import import_module
from lcyframe.libs.singleton import NsqCon
nsq = NsqCon.get_connection()

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
produce_path = "%s"
""" % (Copyright.file_pre, produce_path)

    import_str = """
# xxx_handler xx leng must > 1.
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue

    model_name = produce_path.strip("/").replace("/", ".") + "." + model_name
    objs = __import__(model_name, fromlist=["*"])
    for p in dir(objs):
        if p.startswith("__"):
            continue
            
        # if not p.lower().startswith("publish"):
            #logging.debug("nsq producer [%s] load fail. it must been start with 'publish'" % p)
        #    continue
        
        if not hasattr(getattr(objs, p), "topic"):
            continue
        
        logging.debug("nsq producer [%s] register success!" % p)
        setattr(nsq, p, getattr(objs, p)())
"""

    return auto_str + import_str


def get_nsq_work_init():
    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
    """ % Copyright.file_pre

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_worker\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    logging.debug("register nsq workers [%s.py] success!" % model_name)
    __import__(model_name, globals(), locals(), [model_name], -1)

    """
    return auto_str + import_str


def get_mqtt_producer_init(root_path, produce_path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
from importlib import import_module
from lcyframe.libs.singleton import MqttCon
mqtt = MqttCon.get_connection()

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
produce_path = "%s"
""" % (Copyright.file_pre, produce_path)

    import_str = """
# xxx_handler xx leng must > 1.
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue

    model_name = produce_path.strip("/").replace("/", ".") + "." + model_name
    objs = __import__(model_name, fromlist=["*"])
    # objs = import_module(model_name)  # 重名py文件会被覆盖
    for p in dir(objs):
        if p.startswith("__"):
            continue
            
        # if not p.lower().startswith("publish"):
            #logging.debug("mqtt producer [%s] load fail. it must been start with 'publish'" % p)
        #    continue
        
        if not hasattr(getattr(objs, p), "topic"):
            continue
            
        logging.debug("mqtt producer [%s] register success!" % p)
        setattr(mqtt, p, getattr(objs, p)())
"""

    return auto_str + import_str


def get_mqtt_work_init():
    auto_str = """%s
import os
import re
import logging
dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
    """ % Copyright.file_pre

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+_worker\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    logging.debug("register mqtt workers [%s.py] success!" % model_name)
    __import__(model_name, globals(), locals(), [model_name], -1)

    """
    return auto_str + import_str

def get_celery_works_init(root_path, workers_path):
    """

    :param path:
    :return:
    """

    auto_str = """%s
import os
import re
import logging
from lcyframe.libs.singleton import CeleryCon
from lcyframe.libs.celery_route import Events
app = CeleryCon._app

dir_path = os.listdir(os.path.abspath(os.path.dirname(__file__)))
workers_path = "%s"
""" % (Copyright.file_pre, workers_path)

    import_str = """
hander_files = [x for x in dir_path if re.findall('[A-Za-z]\w+\.py$', x)]

for hander_file in hander_files:
    model_name = hander_file[:-3]
    if model_name == "__init__":
        continue

    model_name = workers_path.strip("/").replace("/", ".") + "." + model_name
    objs = __import__(model_name, fromlist=["*"])
    module_name = objs.__name__.split(".")[-1]

    setattr(Events, module_name, objs)

    for p in dir(objs):
        if p.startswith("__"):
            continue

        if type(getattr(objs, p)) == type:
            if not hasattr(getattr(objs, p), "queue"):
                continue

            if hasattr(app, p) and p != 'BaseEvent':
                raise Exception("exists same attribute：%s" % p)

        # logging.debug("celery task [%s] register success!" % p)
        setattr(Events, p, getattr(objs, p))

    setattr(app, Events.__name__, Events)

"""

    return auto_str + import_str