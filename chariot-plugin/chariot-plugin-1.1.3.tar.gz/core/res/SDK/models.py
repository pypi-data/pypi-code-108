from typing import Optional, List
from pydantic import BaseModel, ValidationError

"""
入参出参数据格式验证，除　PluginStdin外，需自行编写对应类
"""

# json测试文件
class PluginStdin(BaseModel):
    version: str
    type: str
    body: dict











