import re
from typing import Sequence, Tuple, Union

from nehushtan.helper.CommonHelper import CommonHelper
from nehushtan.httpd.NehushtanHTTPRoute import NehushtanHTTPRoute


class NehushtanHTTPRouteWithRestFul(NehushtanHTTPRoute):
    """
    Since 0.4.0
    """

    def __init__(
            self,
            path_template: str,
            process_chain_base_package: str,
            filter_list: Sequence[Union[type, str]] = None,
            method_options: Sequence[str] = None
    ):
        """
        `path_template` is expected as '/PRE../..FIX',
            would be mapped to URL '/PRE../..FIX/PACKAGE...S/CLASS/METHOD'
            or '/PRE../..FIX/PACKAGE...S/CLASS/METHOD/ARGS[0]/ARGS[1]/...'
        `process_chain_base_package` should be a package namespace naem, e.g. 'a.b.c',
            (thus, the target class-method pair for '/d/e/f' would be (`a.b.c.d.e`,`f`)
        """
        super().__init__()
        self.path_template = path_template
        self.process_chain_base_package = process_chain_base_package
        self.sub_class_path = ''
        self.class_method_name = ''
        self.filter_list = filter_list if filter_list is not None else []
        self.method_options = method_options

    def match_request(self, method: str, path: str) -> bool:
        if self.method_options is not None:
            if not self.method_options.__contains__(method):
                return False

        # print(self.path_template)

        regex = r'^(' + self.path_template + ')/(.+)$'
        result = re.search(regex, path)
        if result is None:
            return False
        # print(regex)
        # print(result)
        components = result.group(2).split('/')
        # print(components)

        class_full_path = self.process_chain_base_package
        for i in range(len(components)):
            # print(f'components[{i}]')
            component = components[i]
            class_full_path += '.' + component
            try:
                CommonHelper.class_with_class_path(class_full_path)
            except ModuleNotFoundError:
                continue
            if len(components) - 1 == i:
                # do not have enough path components
                return False
            self.sub_class_path = ".".join(components[:i + 1])
            self.class_method_name = components[i + 1]
            self.matched_arguments = components[i + 2:]
            # print({
            #     'self.sub_class_path':self.sub_class_path,
            #     'self.class_method_name':self.class_method_name,
            #     'self.matched_arguments':self.matched_arguments,
            # })
            return True

        # anyway not match
        return False

        # self.class_method_name = result.group(2)
        #
        # if len(result.groups()) > 2:
        #     x = result.group(2)[1:].split('/')
        #     self.matched_arguments = x
        # return True

    def get_filter_list(self) -> Sequence[Union[type, str]]:
        return self.filter_list

    def get_controller_target(self) -> Tuple[Union[type, str], str]:
        return self.process_chain_base_package + "." + self.sub_class_path, self.class_method_name

    def __str__(self):
        method = "|".join(self.method_options) if self.method_options is not None else 'ANY'
        return f'NehushtanHTTPRouteWithRestFul [{method}] {self.path_template}'
