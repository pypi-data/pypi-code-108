import re
from typing import Sequence, Tuple, Union

from nehushtan.httpd.NehushtanHTTPRoute import NehushtanHTTPRoute


class NehushtanHTTPRouteWithRegexKwargs(NehushtanHTTPRoute):
    """
    Since 0.4.0
    """

    def __init__(
            self,
            path_template: str,
            controller_target: Tuple[Union[type, str], str],
            filter_list: Sequence[Union[type, str]] = None,
            method_options: Sequence[str] = None
    ):
        """
        self.path_template is expected as /FIXED/{NAMED}/...
        Since 0.4.1 `{NAMED}` could be extended as `{NAMED:int|float|str}`
        """

        super().__init__()
        self.filter_list = filter_list if filter_list is not None else []
        self.controller_target = controller_target
        self.method_options = method_options

        pairs = re.findall(r'{([A-Za-z0-9_]+):?([a-z]+)?}', path_template)
        self.kwargs_type_dict = {}
        for kwargs_name, kwargs_type in pairs:
            self.kwargs_type_dict[kwargs_name] = kwargs_type

        # print(path_template)
        x = re.sub(r'{([A-Za-z0-9_]+):int}', r'(?P<\1>\\d+)', path_template)
        x = re.sub(r'{([A-Za-z0-9_]+):float}', r'(?P<\1>\\d+\.?\\d+)', x)
        x = re.sub(r'{([A-Za-z0-9_]+)(:str)?}', r'(?P<\1>[^/]+)', x)
        # print(x)

        self.named_path_template = f'^{x}$'

    def match_request(self, method: str, path: str) -> bool:
        if self.method_options is not None:
            if not self.method_options.__contains__(method):
                return False

        result = re.search(self.named_path_template, path)
        if result is None:
            return False

        # self.matched_arguments = result.groups()
        # self.matched_keyed_arguments = result.groupdict()

        self.matched_keyed_arguments = {}
        for k, v in result.groupdict().items():
            t = self.kwargs_type_dict.get(k, 'str')
            if t == 'int':
                self.matched_keyed_arguments[k] = int(v)
            elif t == 'float':
                self.matched_keyed_arguments[k] = float(v)
            else:
                self.matched_keyed_arguments[k] = v

        return True

    def get_filter_list(self) -> Sequence[Union[type, str]]:
        return self.filter_list

    def get_controller_target(self) -> Tuple[Union[type, str], str]:
        return self.controller_target

    def __str__(self):
        method = "|".join(self.method_options) if self.method_options is not None else 'ANY'
        return f'NehushtanHTTPRouteWithRegexKwargs [{method}] {self.named_path_template}'
