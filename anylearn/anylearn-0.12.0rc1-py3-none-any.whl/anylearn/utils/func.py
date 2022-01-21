from datetime import datetime, timedelta
from typing import Dict, List
import uuid

def utc_plus_8():
    return datetime.utcnow() + timedelta(hours=8)


def generate_primary_key(type_name):
    """用于生成ID，给一个四个字符的类别返回一个32位长的ID

    :param type_name: 4位类别名
    :returns: 32位ID

    """
    return type_name + ''.join(uuid.uuid1().__str__().split('-'))[4:]


def logs_beautify(logs: List[Dict], debug: bool=False):
    tz = datetime.now().astimezone().tzinfo
    logs = [
        f"[{str(datetime.fromtimestamp(int(l['offset']) / 1000, tz=tz))}] {l['text']}"
        for l in logs
        if not l['text'].startswith("[Anylearn]") or debug
    ]
    return logs
