from dataclasses import dataclass
from typing import List, Dict, Union


@dataclass
class Javar:
    """
    Represent java command line with its arguments.
    """

    bin: str = '/bin/java'

    class_path: str = ''
    class_path_items: List[str] = ()
    module_path: str = ''
    module_path_items: List[str] = ()

    sys_properties: Dict = None
    sys_args: Union[List[str], Dict[str, str]] = ()

    main_class: str = ''
    main_jar: str = ''
    main_args: Union[List[str], Dict[str, str]] = ()

    def cmd_class_path(self) -> list:
        items = list(self.class_path_items)
        if self.class_path:
            items.append(self.class_path)
        if items:
            return ['-cp', ':'.join(items)]

        return []

    def cmd_module_path(self) -> list:
        items = list(self.module_path_items)
        if self.module_path:
            items.append(self.module_path)
        if items:
            return ['--module-path', ':'.join(items)]

        return []

    def cmd_sys_properties(self) -> list:
        if self.sys_properties:
            return ['-D{}={}'.format(*i) for i in self.sys_properties.items()]

        return []

    def cmd_sys_args(self) -> list:
        return _args_as_list(self.sys_args)

    # noinspection PyMethodMayBeStatic
    def cmd_extra_params(self):
        return []

    def cmd_main(self) -> list:
        if self.main_jar:
            return ['-jar', self.main_jar]
        else:
            return [self.main_class, ]

    def cmd_main_args(self) -> list:
        return _args_as_list(self.main_args)

    def as_list(self) -> list:
        cmd = [self.bin]
        cmd += self.cmd_class_path()
        cmd += self.cmd_module_path()
        cmd += self.cmd_sys_properties()
        cmd += self.cmd_sys_args()
        cmd += self.cmd_extra_params()
        cmd += self.cmd_main()
        cmd += self.cmd_main_args()

        return cmd

    def as_str(self) -> str:
        return ' '.join(self.as_list())


def _args_as_list(args) -> list:
    if isinstance(args, dict):
        return ['='.join(i) for i in args.items()]
    else:
        return list(args)
