'''
    用来转换特殊字符串
'''
import re
import copy
import json
import traceback
from autoTestScheme.common import logger


class Conversion(object):

    def __init__(self, this, json:dict):
        self.this = this
        self.json = json
        self.tmp_variable = {'false': False, 'True': True, 'true': True, 'False': False, 'null': None}
        self.start = r'\$(\d+)'
        self.end = r'\$'
        self.variable_regex = r"([a-zA-z].*)"
        self.function_regex = r"\{(\w+)\((.*?)\)\}"
        self.json_regex = r"JSON((\[.*?\]){1,20})"

    def re_dict(self):
        re_order_list = self.get_re_dict(self.json)
        re_order_list.sort()
        re_order_list = [i[1] for i in re_order_list]
        func_com = re.compile(self.start + self.function_regex)
        var_com = re.compile(self.start + self.variable_regex)
        json_com = re.compile(self.start + self.json_regex)
        for i in re_order_list:
            key = self.json
            for j in i:
                key = key[j]
            new_value = copy.deepcopy(key)
            if len(func_com.findall(key)) > 0:
                new_value = self.re_sub_func(self.start + self.function_regex, new_value, self.replace_function)
            if len(json_com.findall(key)) > 0:
                new_value = self.re_sub_func(self.start + self.json_regex, new_value, self.replace_json)
            if len(var_com.findall(key)) > 0:
                new_value = self.re_sub_func(self.start + self.variable_regex, new_value, self.replace_variable)
            _json = self.json
            for jj in i[:-1]:
                _json = _json[jj]
            _json[i[-1]] = new_value
        return self.json

    def re_sub_func(self, regex, value, func):
        func_com = re.compile(regex)
        new_value = copy.deepcopy(value)

        _list = []
        if isinstance(value, str) is True:
            _find_list = [k for k in func_com.finditer(value)]
            for k in _find_list[::-1]:
                pos = k.span()
                try:
                    if (k.start() == 0 and len(value) == k.end()):
                        new_value = json.loads(func(k))
                    else:
                        _str = list(new_value)
                        _str[pos[0]:pos[1]] = new_v = str(json.loads(func(k)))
                        new_value = ''.join(_str)
                except Exception as e:
                    logger.error('{} 替换异常:{}'.format(value, traceback.format_exc()))
                    raise e
            logger.debug('替换特殊字符串：{}，替换结果:{}'.format(value, new_value))
        return new_value

    def get_re_str(self, _str, loc):
        re_order_list = []
        re_func_result = re.compile(self.start + self.function_regex).findall(_str)
        re_val_result = re.compile(self.start + self.variable_regex).findall(_str)
        if len(re_func_result) > 0:
            pos = re_func_result[0][0]
            re_order_list.append([int(pos), loc])
        elif len(re_val_result) > 0:
            pos = re_val_result[0][0]
            re_order_list.append([int(pos), loc])
        return re_order_list

    def get_re_list(self, _list, loc):
        re_order_list = []
        for i in range(len(_list)):
            v = _list[i]
            _loc = loc + [i]
            if type(v) == dict:
                re_order_list += self.get_re_dict(v, _loc)
            if type(v) == list:
                re_order_list += self.get_re_list(v, _loc)
            elif type(v) == str:
                re_order_list += self.get_re_str(v, _loc)
        return re_order_list

    def get_re_dict(self, _dict, loc=[]):
        re_order_list = []
        for k, v in _dict.items():
            _loc = loc + [k]
            if type(v) == dict:
                re_order_list += self.get_re_dict(v, _loc)
            if type(v) == list:
                re_order_list += self.get_re_list(v, _loc)
            elif type(v) == str:
                re_order_list += self.get_re_str(v, _loc)
        return re_order_list

    def replace_function(self, value):
        if len(value.groups()) > 1:
            _find_list = value.groups()[1:]
        else:
            _find_list = value.groups()
        func = _find_list[0]
        _arg_list = []
        kwargs = {}
        if _find_list[1] == '':
            obj = self.this.get_func(func)
            if obj is not False:
                try:
                    from inspect import isgeneratorfunction
                    if isgeneratorfunction(obj) is False:
                        return json.dumps(obj())
                    else:
                        return json.dumps(next(obj()))
                except:
                    logger.error('replace value:{},error:{}'.format(value, traceback.format_exc()))
            return json.dumps(value.group())
        for arg in _find_list[1].split(','):
            if arg.find('=') != -1:
                _tmp = arg.split('=')
                if _tmp[1] in list(self.tmp_variable.keys()):
                    kwargs[_tmp[0]] = self.tmp_variable[_tmp[1]]
                else:
                    func_com = re.compile(self.end + self.function_regex)
                    var_com = re.compile(self.end + self.variable_regex)
                    _value = _tmp[1]
                    if len(func_com.findall(_tmp[1])) > 0:
                        _value = self.re_sub_func(self.end + self.function_regex, _value, self.replace_function)
                    elif len(var_com.findall(_tmp[1])) > 0:
                        _value = self.re_sub_func(self.end + self.variable_regex, _value, self.replace_variable)
                    kwargs[_tmp[0]] = _value
            else:
                if arg in list(self.tmp_variable.keys()):
                    _arg_list.append(self.tmp_variable[arg])
                else:
                    tmp = copy.deepcopy(arg)
                    func_com = re.compile(self.end + self.function_regex)
                    var_com = re.compile(self.end + self.variable_regex)
                    if len(func_com.findall(arg)) > 0:
                        tmp = self.re_sub_func(self.end + self.function_regex, tmp, self.replace_function)
                    elif len(var_com.findall(arg)) > 0:
                        tmp = self.re_sub_func(self.end + self.variable_regex, tmp, self.replace_variable)
                    try:
                        _arg_list.append(tmp)
                    except Exception:
                        _arg_list.append(tmp)
        arg = tuple(_arg_list)

        obj = self.this.get_func(func)
        if obj is not False:
            result = obj(*arg, **kwargs)
            result = json.dumps(result)
        else:
            result = json.dumps(value.group(0))
        return result

    def replace_json(self, value):
        if len(value.groups()) > 1:
            _find_list = value.groups()[1:]
        else:
            _find_list = value.groups()
        _find_list = _find_list[0]
        tmp = copy.deepcopy(self.json)
        for i in re.compile(r'\[(.*?)\]').findall(_find_list):
            if type(tmp) == list:
                tmp = tmp[int(i)]
            elif type(tmp) == str:
                if i.find(':') != -1:
                    tmp = tmp[int(i.split(':')[0]):int(i.split(':')[1])]
                else:
                    tmp = tmp[int(i)]
            else:
                tmp = tmp[i]
        return json.dumps(tmp)

    def replace_variable(self, value):
        if len(value.groups()) > 1:
            _find_list = value.groups()[1:]
        else:
            _find_list = value.groups()
        variable = _find_list[0]
        if variable.startswith('JSON') is True:
            tmp = copy.deepcopy(self.json)
            for i in re.compile(r'\[(.*?)\]').findall(variable):
                if type(tmp) == list:
                    tmp = tmp[int(i)]
                elif type(tmp) == str:
                    if i.find(':') != -1:
                        tmp = tmp[int(i.split(':')[0]):int(i.split(':')[1])]
                    else:
                        tmp = tmp[int(i)]
                else:
                    tmp = tmp[i]
            return json.dumps(tmp)
        obj = self.this.get_func(variable)
        if obj is not False:
            return json.dumps(obj)
        return json.dumps(variable)


#
ins = {
		"title":"网商-企业-已开户在线账户-修改手机号",
		"ins":{
            "customerAccountNo": "$1{get_customer_account(2,3,antb,1)}",
            "userId": "$2{get_user_id_by_customer_account_no($JSON[ins][customerAccountNo])}",
            "institutionCode": "ANTB",
            "name": "熊润",
            "nowMobile": "$2{get_update_moblie_by_customer_account_no($JSON[ins][customerAccountNo])}",
            "nowCode": "888888",
            "nowAuthNo": "$2{get_auth_no_by_update($JSON[ins][customerAccountNo])}",
            "originalCode": "888888",
            "a":{
                "a_son1": "$2{get_moblie_by_customer_account_no($JSON[ins][customerAccountNo])}",
                "a_son2": [
                    {
                        "a_son2_son": "$2JSON[ins][name]"
                    },
                    "$2JSON[ins][name]"
                ]
            },
            "originalMobile": "$2{get_moblie_by_customer_account_no($JSON[ins][customerAccountNo])}",
            "originalAuthNo": "$2{get_auth_no_by_original($JSON[ins][customerAccountNo])}",
            "tradeNo": "test_$2{current_subtle_unix()}"
        },
		"outs":{
            "status": 200,
            "errorCode": None,
            "message": None,
            "data": {
                "failReason": None,
                "result": None
            },
            "success": True
        }
	}


class Test(object):
    def __init__(self):
        self.current_subtle_unix_str = 123
        con = Conversion(self, ins)
        con.re_dict()
        print(con.json)

    def get_cash_sweep(self, v, k):
        return 123

    def get_user_id_by_customer_account_no(self, _str):
        return '---get_user_id_by_customer_account_no--{}'.format(_str)

    def get_customer_account(self, *args):
        return '560286448494204'

    def get_update_moblie_by_customer_account_no(self, _str):
        return '---get_update_moblie_by_customer_account_no--{}'.format(_str)

    def get_auth_no_by_update(self, _str):
        return '---get_auth_no_by_update--{}'.format(_str)

    def get_moblie_by_customer_account_no(self, _str):
        return '---get_moblie_by_customer_account_no--{}'.format(_str)

    def get_auth_no_by_original(self, _str):
        return '---get_auth_no_by_original--{}'.format(_str)

    def get_account_no_by_origin_cash_sweep_no(self,k):
        return 'ddddddddddddddddddddddd'

if __name__ == '__main__':
    Test()


