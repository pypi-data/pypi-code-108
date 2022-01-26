import base64
import io

import requests
import yaml

from kikyo import Kikyo, Settings


def configure_by_consul(config_url: str, **kwargs) -> Kikyo:
    """从Consul拉取YAML格式的配置文件

    :param config_url: 获取配置项的URL地址
    """

    resp = requests.get(config_url)
    resp.raise_for_status()

    settings = Settings()
    for data in resp.json():
        v = data['Value']
        if not v:
            continue
        s = base64.b64decode(v)
        conf: dict = yaml.safe_load(io.BytesIO(s))
        if 'kikyo' in conf:
            settings.merge(conf['kikyo'])
            break

    settings.merge(kwargs)
    return Kikyo(settings)
