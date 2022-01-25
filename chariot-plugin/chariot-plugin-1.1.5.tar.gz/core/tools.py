import tarfile
import yaml
import jinja2
from typing import List, Optional, Any
import os


from .config import *


class Tools(object):

    def tarExtract(self, tar_path, target_path):
        """
        .tar.gz　提取
        """

        try:
            tar = tarfile.open(tar_path, "r:gz")
            file_names = tar.getnames()
            for file_name in file_names:
                if not os.path.exists(os.path.join(target_path, file_name)):
                    tar.extract(file_name, target_path)
                    logging.info(f"generated {file_name} ok")
            tar.close()
        except Exception as e:
            logging.error(f"SDK生成失败 - {tar_path} - {str(e)}")

    def readYaml(self, yaml_path: str) -> dict:
        # 以json格式读取yaml

        with open(yaml_path, "r", encoding="utf-8") as f:
            yaml_data = yaml.load(f.read(), Loader=yaml.FullLoader)

        return yaml_data

    def renderStrTemplate(self, data, temp: str) -> str:
        #　字符串渲染

        template = jinja2.Template(temp)
        res = template.render(data)

        return res

    def typeTrans(self, t: str, rq: str, dft: Any, enm: Optional[List]):
        # 类型转换

        strMark = lambda x: f'"{x}"' if isinstance(x, str) else x

        argType = ""

        typeMap = {
            "string": "str",
            "bytes": "str",
            "boolean": "bool",
            "float": "float",
            "date": "str",
            "object": "dict",
            "password": "str",
            "integer": "int",
            "file": "dict"
        }

        if isinstance(enm, list):
            argType = f"Literal{enm}"
        else:
            argType = typeMap.get(t)

        if not argType:

            if t.startswith("[]"):
                argType = f"Optional[List[{typeMap.get(t[2:], self.getModelName(t[2:]))}]]"
            else:
                argType = self.getModelName(t)

        if not rq and not dft:
            argType += " = None"
        else:
            if dft:
                argType += f' = {strMark(dft)}'

        return argType

    def ymlTransPy(self, data: dict) -> List:
        # yml　转 py　类型, 返回列表，以便直接渲染

        py_list = []

        if data:
            for name,v in data.items():
                # 默认　type: string, required: false
                tp = v.get("type", "string")
                rq = v.get("required", False)
                dft = v.get("default", None)
                enm = v.get("enum", None)

                assert not (isinstance(enm, list) and dft and dft not in enm), "valid fail, default value not in enum value."

                tp = self.typeTrans(tp, rq, dft, enm)

                py_list.append([name, tp])

        return py_list

    def getModelName(self, tit: str, t="") -> str:
        # 生成校验类型名字

        return (tit + t).upper()

    def writeFile(self, data: str, filepath: str):
        # 写入文件,　生成初始化文件

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(data)

    def readFile(self, filepath: str):
        # 读取文件

        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()

        return data

