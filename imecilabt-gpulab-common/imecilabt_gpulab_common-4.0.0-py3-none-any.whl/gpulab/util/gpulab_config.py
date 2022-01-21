import collections
from abc import ABC, abstractmethod
from typing import Dict, Optional, Callable, List, Any, Union

import yaml


def discard_pem_certs(pem_content: str) -> str:
    res = ''
    include = True
    for line in pem_content.splitlines(keepends=True):
        if line.startswith('-----BEGIN CERTIFICATE-----'):
            include = False
        if include:
            res += line
        if line.startswith('-----END CERTIFICATE-----'):
            include = True
    return res


def discard_pem_privkeys(pem_content: str) -> str:
    res = ''
    include = True
    for line in pem_content.splitlines(keepends=True):
        if line.startswith('-----BEGIN RSA PRIVATE KEY-----') or line.startswith('-----BEGIN PRIVATE KEY-----'):
            include = False
        if include:
            res += line
        if line.startswith('-----END RSA PRIVATE KEY-----') or line.startswith('-----END PRIVATE KEY-----'):
            include = True
    return res


class BaseConfig(ABC):
    @classmethod
    def _read_file_or_none(cls, filename: Optional[str]) -> Optional[str]:
        if filename is None:
            return None
        with open(filename, 'r') as f:
            filecontent = f.read()
        return filecontent

    @classmethod
    def _strip_or_none(cls, arg: Optional[str]) -> Optional[str]:
        if arg is None:
            return None
        return arg.strip()

    @classmethod
    def _split_or_none(cls, arg: Optional[str]) -> List[str]:
        if arg is None:
            return list()
        return arg.split(',')

    @classmethod
    def _parse_list(cls, arg: Any) -> List[str]:
        """
        :param arg: None, a list of str, an empty string, or string, or a string with comma seperated values
        :return: a list of str
        """
        if arg is None:
            return list()
        if isinstance(arg, collections.abc.Sequence) and not isinstance(arg, str):
            return list(arg)
        if isinstance(arg, str) and arg.strip() == '':
            return list()
        return [a.strip() for a in arg.strip().split(',')]

    @classmethod
    def _float_or_none(cls, arg: Optional[Any]) -> Optional[float]:
        if arg is None:
            return None
        return float(arg)

    @classmethod
    def _int_or_none(cls, arg: Optional[Any]) -> Optional[int]:
        if arg is None:
            return None
        return int(arg)

    @classmethod
    def _get_from_dict(cls, cfg: Dict, default: Union[Callable[[List[str]], Any], Any], *keys: str) -> Any:
        cur = cfg
        for key in keys:
            if key in cur:
                cur = cur[key]
            else:
                if callable(default):
                    return default(keys)
                else:
                    return default
        return cur

    @classmethod
    def _get_bool_from_dict(cls, cfg: Dict, default: Union[Callable[[List[str]], Optional[bool]], Optional[bool]], *keys: str) -> Optional[bool]:
        cur = cfg
        for key in keys:
            if key in cur:
                cur = cur[key]
            else:
                if (callable(default)):
                    return default(keys)
                else:
                    return default
        return BaseConfig._str_to_bool(cur)

    @classmethod
    def _to_number_or_str(cls, val: Optional[Any]) -> Optional[Union[int, float, str]]:
        """
        Used to store numbers as numbers in JSON/YAML, and other things as text
        """
        if val is None:
            return None
        try:
            return int(val)
        except ValueError:
            pass
        try:
            return float(val)
        except ValueError:
            pass
        return str(val)

    @classmethod
    def _to_optional_str(cls, val: Optional[Any]) -> Optional[str]:
        if val is None:
            return None
        return str(val)

    @classmethod
    def _to_dict(cls, cfg: Dict, val: Optional[Any], *keys: str) -> None:
        if val is None:
            return
        cur = cfg
        for key in keys[:-1]:
            if not key in cur:
                cur[key] = dict()
            cur = cur[key]
        cur[keys[-1]] = val

    @classmethod
    def _str_to_bool(cls, value: Union[str, int, bool]) -> bool:
        # TODO use utils.any_to_bool
        if isinstance(value, bool):
            return value
        if isinstance(value, int) and 0 <= value <= 1:
            return value == 1
        if value.strip().lower() in ["true", "yes", "1"]:
            return True
        elif value.strip().lower() in ["false", "no", "0"]:
            return False
        else:
            raise ValueError(f'Could not convert {value!r} to bool')

    def __init__(self):
        pass

    @abstractmethod
    def load_from_dict(self, cfg: Dict, *, backward_compatible=False):
        pass

    @abstractmethod
    def save_to_dict(self) -> Dict:
        return dict()

    def load_from_file(self, config_file: str, *, backward_compatible=False):
        with open(config_file, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
            self.load_from_dict(cfg, backward_compatible=backward_compatible)

    def load_from_ymlstr(self, ymlstr: str, *, backward_compatible=False):
        cfg = yaml.safe_load(ymlstr)
        self.load_from_dict(cfg, backward_compatible=backward_compatible)

    def save_to_file(self, filename: str):
        cfg = self.save_to_dict()
        with open(filename, 'w') as outfile:
            yaml.dump(cfg, outfile, default_flow_style=False)

    def __eq__(self, other):
        a = yaml.dump(self.save_to_dict())
        b = yaml.dump(other.save_to_dict())
        return a == b


