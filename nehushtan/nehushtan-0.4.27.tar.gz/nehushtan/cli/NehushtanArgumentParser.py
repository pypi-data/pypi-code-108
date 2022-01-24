import re
import sys


class NehushtanArgumentParser:
    """
    Since 0.2.19 Add Flag Support
    Support
    <python xxx.py> [-a B] [--bb C] [--dd-ee F --dd-gg H] [-i] [--jj] [--kk-ll --kk-mm]
    Suppose key is as argument name, the above would be parsed as
    {
        "a":"B"
        "bb":"C",
        "dd":{
            "ee":"F",
            "gg":"H",
        },
        "i":True,
        "jj":True,
        "kk":{
            "ll":True,
            "mm":True,
        }
    }
    """

    def __init__(self, sys_arg_list: list = None):
        """
        Since 0.2.19 sys_arg_list become optional
        :param sys_arg_list: a list of arguments, if omitted use `sys.argv[1:]`
        """
        if sys_arg_list is None:
            sys_arg_list = sys.argv[1:]

        self._sys_arg_list = sys_arg_list
        self._argument_dict = {}

        self._options_short = {}
        self._options_long = {}
        self._options_prefix = {}

        self._flags_short = {}
        self._flags_long = {}
        self._flags_prefix = {}

        self._result_dict = {}
        self._usage_dict = {}

    def set_arg_list(self, arg_list: list):
        """
        :param arg_list: Commonly `sys.argv[1:]`
        """
        self._sys_arg_list = arg_list
        return self

    def add_option(
            self,
            key: str, desc: str = '',
            short: str = '',
            long: str = '',
            prefix: str = '',
            is_flag=False
    ):
        """

        :param desc:
        :param key: Any Name
        :param short: a -> `-a`
        :param long: alpha -> `--alpha`
        :param prefix: alef -> `--alef-`
        :param is_flag: if its value follows existence only as boolean
        :return:
        """
        if short == '' and long == '' and prefix == '':
            return self

        usage = {
            'key': key,
            'desc': desc,
        }

        if short != '':
            argument_key = f'-{short}'
            self.__assert_key_unique(argument_key, 'short')
            if is_flag:
                self._flags_short[argument_key] = key
                usage['short'] = f'[-{short}]'
            else:
                self._options_short[argument_key] = key
                usage['short'] = f'-{short} [VALUE]'
        if long != '':
            argument_key = f'--{long}'
            self.__assert_key_unique(argument_key, 'long')
            if is_flag:
                self._flags_long[argument_key] = key
                usage['long'] = f'[--{long}]'
            else:
                self._options_long[argument_key] = key
                usage['long'] = f'--{long} [VALUE]'
        if prefix != '':
            argument_key = f'--{prefix}-'
            self.__assert_key_unique(argument_key, 'prefix')
            if is_flag:
                self._flags_prefix[argument_key] = key
                usage['prefix'] = f'[--{prefix}-[KEY]]'
            else:
                self._options_prefix[argument_key] = key
                usage['prefix'] = f'--{prefix}-[KEY] [VALUE]'

        self._usage_dict[key] = usage

        return self

    def __assert_key_unique(self, argument_key: str, key_type: str):
        if key_type == 'short':
            if self._flags_short.get(argument_key) is not None or self._options_short.get(argument_key) is not None:
                raise RuntimeError(f'Short Key [{argument_key}] Already Existed')
        elif key_type == 'long':
            if self._flags_long.get(argument_key) is not None or self._options_long.get(argument_key) is not None:
                raise RuntimeError(f'Long Key [{argument_key}] Already Existed')
        elif key_type == 'prefix':
            if self._flags_prefix.get(argument_key) is not None or self._options_prefix.get(argument_key) is not None:
                raise RuntimeError(f'Prefix Key [{argument_key}] Already Existed')

    def parse(self):
        self._result_dict = {}

        current_key = None
        self._argument_dict = {}
        for item in self._sys_arg_list:
            if current_key is None:
                # check if current item is a flag key
                if self.__parse_flag_key(item) is True:
                    self._argument_dict[item] = True
                    continue

                current_key = item
            else:
                self._argument_dict[current_key] = item
                current_key = None

        for (key, value) in self._argument_dict.items():
            self.__parse_option_pair(key, value)

        return self

    def __parse_flag_key(self, key):
        if self._flags_short.get(key) is not None:
            self._result_dict[self._flags_short[key]] = True
            return True
        elif self._flags_long.get(key) is not None:
            self._result_dict[self._flags_long[key]] = True
            return True
        else:
            for prefix, mapping_key in self._flags_prefix.items():
                matches = re.match(f'^{prefix}([A-Za-z0-9._-]+)$', key)
                if matches is not None:
                    if self._result_dict.get(mapping_key) is None:
                        self._result_dict[mapping_key] = {}
                    self._result_dict[mapping_key][matches[1]] = True
                    return True
        # not matched any
        return False

    def __parse_option_pair(self, key: str, value):
        if self._options_short.get(key) is not None:
            self._result_dict[self._options_short[key]] = value
        elif self._options_long.get(key) is not None:
            self._result_dict[self._options_long[key]] = value
        else:
            for prefix, mapping_key in self._options_prefix.items():
                matches = re.match(f'^{prefix}([A-Za-z0-9._-]+)$', key)
                if matches is not None:
                    if self._result_dict.get(mapping_key) is None:
                        self._result_dict[mapping_key] = {}
                    self._result_dict[mapping_key][matches[1]] = value
                    break

    def get_raw_option_dict(self):
        return self._argument_dict

    def get_parsed_option_dict(self):
        return self._result_dict

    def get_usage_text(self):
        usage_text = ""
        for key, value in self._usage_dict.items():
            options = []
            if len(value.get('short', '')) > 0:
                options.append(value.get('short'))
            if len(value.get('long', '')) > 0:
                options.append(value.get('long'))
            if len(value.get('prefix', '')) > 0:
                options.append(value.get('prefix'))

            usage_text += f"{value['key']}" + "\t\t"
            usage_text += ", ".join(options)
            if len(value.get('desc', '')) > 0:
                usage_text += f"\n{value['desc']}"
            usage_text += "\n"

        return usage_text
