# -*- coding: utf-8 -*-
""" class实例化 延迟 """
import abc
import re
from types import FunctionType, CodeType
from typing import Tuple, Any
from functools import wraps
from inspect import signature, Parameter, getargs, getargspec, getfullargspec


class Box(object):

    def __init__(self):
        self.__payload = None
        # 存放类对应的实例 类 以及 其签名信息
        self.__objs_class_mappings = {}

    def inject(self, *class_args, **class_kwargs):
        _payload = class_kwargs.get('payload', None)
        if _payload is None:
            _payload = {}
        args_payload = class_kwargs.get('args_payload', None)
        kwargs_payload = class_kwargs.get('kwargs_payload', None)

        _dependency = class_kwargs.get('dependency', None)
        __class_args = list(class_args)
        if _dependency is not None:
            __class_args.append(_dependency)

        pattern = "[A-Z]"
        for _c in __class_args:
            # 生成实例化名 根据类的驼峰化转变成 a_b_c 形式
            __c_name = re.sub(pattern, lambda x: "_" + x.group(0).lower(), _c.__name__).strip('_')
            if args_payload and kwargs_payload:
                self.__objs_class_mappings.update({__c_name: dict(_obj=None, _cls=_c, _payload=dict(
                    ___args=args_payload,
                    ___kwargs=kwargs_payload
                ))})
                continue
            if isinstance(_payload, tuple):
                self.__objs_class_mappings.update({__c_name: dict(_obj=None, _cls=_c, _payload=dict(___args=_payload))})
                continue
            if isinstance(_payload, dict):
                self.__objs_class_mappings.update({__c_name: dict(_obj=None, _cls=_c, _payload=dict(___kwargs=_payload))})

    def reset(self, _c_name):
        """ 重置对象 """
        _maybe_ins_obj, is_ins = self.__get_probable_instance_or_class(_c_name)
        if is_ins:
            __get_payload = self.__get_payload(_c_name)
            if len(__get_payload):
                self.__set_val_into_class(__get_payload, _maybe_ins_obj.__init__)
            return _maybe_ins_obj

    def destroy(self, _c_name):
        """ 主动销毁对象 """
        del self.__objs_class_mappings[_c_name]

    def depend(self, *depend_args, **depend_kwargs):

        def decorator(_func):

            self.inject(_func)

            @wraps(_func)
            def _wrap(_self, *wrap_args, **wrap_kwargs):
                print(_self)
                print(wrap_args)
                print(wrap_kwargs)
                return
            return _wrap

        return decorator

    def invoke(self, name,  *payload_args, **payload_kwargs):
        return self.__invoke(name, *payload_args, **payload_kwargs)


    def __get_probable_instance_or_class(self, _c_name):
        """
        返回实例 或者 类
        :param _c_name:
        :return:
        """
        if self.__objs_class_mappings[_c_name]['_obj'] is None:
            return self.__objs_class_mappings[_c_name]['_cls'], False
        return self.__objs_class_mappings[_c_name]['_obj'], True

    def __get_payload(self, _c_name):
        """
            根据实例化名获取类初始化参数
        :param _c_name:
        :return:
        """
        return self.__objs_class_mappings[_c_name]['_payload']

    def __invoke(self, _c_name, *payload_args, **payload_kwargs):
        _maybe_ins_obj, is_ins = self.__get_probable_instance_or_class(_c_name)
        # 判断是否为实例
        if is_ins:
            return _maybe_ins_obj
        else:
            _ins_obj = _maybe_ins_obj(*payload_args, **payload_kwargs)
            self.__set_inst_obj(_c_name, _ins_obj)
            return _ins_obj

    def __set_inst_obj(self, _c_name, _ins_obj):
        """ 存储实例 """
        if self.__objs_class_mappings[_c_name]['_obj'] is None:
            self.__objs_class_mappings[_c_name]['_obj'] = _ins_obj

    def __get_instance_obj(self, _c_name):
        _ins_obj = None
        _maybe_ins_obj, is_ins = self.__get_probable_instance_or_class(_c_name)
        if is_ins:
            return _maybe_ins_obj
        else:
            __get_payload = self.__get_payload(_c_name)
            if len(__get_payload):
                _ins_obj = self.__set_val_into_class(__get_payload, _maybe_ins_obj)
            else:
                _ins_obj = _maybe_ins_obj()
            self.__set_inst_obj(_c_name, _ins_obj)
            return _ins_obj

    def __getattr__(self, _c_name):

        if _c_name in self.__objs_class_mappings:
            return self.__get_instance_obj(_c_name)

    @staticmethod
    def __set_val_into_class(__get_payload: dict, _maybe_ins_obj: Any):
        _ins_obj = None
        if '___args' in __get_payload and '___kwargs' in __get_payload:
            __args = __get_payload['___args']
            __kwargs = __get_payload['___kwargs']
            _ins_obj = _maybe_ins_obj(*__args, **__kwargs)
        elif '___args' in __get_payload:
            __args = __get_payload['___args']
            _ins_obj = _maybe_ins_obj(*__args)
        elif '___kwargs' in __get_payload:
            __kwargs = __get_payload['___kwargs']
            _del_params = []
            _func_sign = signature(_maybe_ins_obj.__init__)
            if __kwargs:
                for p in __kwargs:
                    if p not in _func_sign.parameters:
                        _del_params.append(p)
                    print(_func_sign.parameters)
                for del_k in _del_params:
                    __kwargs.pop(del_k)
            _ins_obj = _maybe_ins_obj(**__kwargs)
        return _ins_obj

    @staticmethod
    def __filter_valid_params(_func: FunctionType, params: dict):

        __full_args = getfullargspec(_func)
        if __full_args.varkw is not None and __full_args.varargs is not None:
            _args = params.pop(__full_args.varkw)
            return 'both', _args, params
        if __full_args.varkw is not None:
            return 'only_has_kw', None, params
        if __full_args.varargs is not None:
            # _args = params.pop(__full_args.varargs)
            return 'only_has_args', params
        _del_params = []
        _func_sign = signature(_func)
        if params:
            for p in params:
                if p not in _func_sign.parameters:
                    _del_params.append(p)
                print(_func_sign.parameters)
            for del_k in _del_params:
                params.pop(del_k)
        return 'normal', params, None


class FactoryInject(metaclass=abc.ABCMeta):

    def construct(self, *args, **kwargs) -> Any:
        raise NotImplementedError


def factory_inject(*factory_args: FactoryInject):

    def decorator(_c):
        @wraps(_c)
        def _wrap(*wrap_args, **wrap_kwargs):
            _cal_map = dict()
            for ins_fd, _cal in _c.__annotations__.items():
                if _cal in _cal_map:
                    _cal_map[_cal].append(ins_fd)
                else:
                    _cal_map[_cal] = [ins_fd, ]
            _c_ins = _c(*wrap_args, **wrap_kwargs)
            for _fac in factory_args:
                fa = _fac.construct.__annotations__
                if fa['return'] in _cal_map:
                    for _fd in _cal_map[fa['return']]:
                        setattr(_c_ins, _fd, _fac().construct())

            return _c_ins
        return _wrap
    return decorator
