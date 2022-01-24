import re
from typing import Sequence, Tuple, Union

from nehushtan.httpd.NehushtanHTTPRoute import NehushtanHTTPRoute


class NehushtanHTTPRouteWithRegexArgs(NehushtanHTTPRoute):
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
        self.path_template is expected as '/FIXED/(\\w+)/...'
        Since 0.4.1, the `^` and `$` are not needed; special keyword designed:
            {int} -> r'(\d+)'
            {float} -> r'(\d\.?\d*)'
            {str} -> r'([^/]+)'
        """
        super().__init__()
        # self.regex_for_path = path_template.replace('{int}', r'(\d+)') \
        #     .replace('{float}', r'(\d\.?\d*)') \
        #     .replace('{str}', r'([^/]+)')
        # if self.regex_for_path[0] != '^':
        #     self.regex_for_path = '^' + path_template
        # if self.regex_for_path[-1] != '$':
        #     self.regex_for_path = path_template + '$'
        self.path_template = path_template
        self.method_options = method_options
        self.filter_list = filter_list if filter_list is not None else []
        self.controller_target = controller_target

    def match_request(self, method: str, path: str) -> bool:
        if self.method_options is not None:
            if not self.method_options.__contains__(method):
                return False

        path_components = path.split('/')
        path_template_components = self.path_template.split('/')

        matched_arguments = []

        if len(path_components) < len(path_template_components):
            return False

        for i in range(len(path_components)):
            path_component = path_components[i]

            if i >= len(path_template_components):
                matched_arguments.append(path_component)
                continue

            path_template_component = path_template_components[i]
            if path_component == path_template_component:
                # static
                continue
            elif path_template_component == '{int}' and re.search(r'^\d+$', path_component):
                matched_arguments.append(int(path_component))
            elif path_template_component == '{float}' and re.search(r'^\d+\.?\d*$', path_component):
                matched_arguments.append(float(path_component))
            elif path_template_component == '{str}':
                matched_arguments.append(path_component)
            else:
                return False

        self.matched_arguments = matched_arguments

        # # old
        # result = re.search(self.regex_for_path, path)
        # if result is None:
        #     return False
        #
        # self.matched_arguments = result.groups()

        return True

    def get_filter_list(self) -> Sequence[Union[type, str]]:
        return self.filter_list

    def get_controller_target(self) -> Tuple[Union[type, str], str]:
        return self.controller_target

    def __str__(self):
        method = "|".join(self.method_options) if self.method_options is not None else 'ANY'
        return f'NehushtanHTTPRouteWithRegexArgs [{method}] {self.path_template}'
