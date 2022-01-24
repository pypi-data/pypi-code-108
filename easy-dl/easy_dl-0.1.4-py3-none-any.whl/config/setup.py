import re
import json

'''
解析配置参数，接受三种参数:
1. 类对象
2. json 文件
3. dict 参数字典
返回包含参数属性的对象
'''
class Config:
    config_name = 'default'
    pass

def get_attrs(obj):
    attr_dict = {}
    for name in dir(obj):
        if callable(getattr(obj, name)): continue
        if re.match('__.*__', name): continue
        if re.match('__.*', name): continue
        if re.match('.*__', name): continue
        attr_dict[name] = getattr(obj, name)
    return attr_dict

def from_dict(dic:dict):
    config = Config()
    for name, value in dic.items():
        setattr(config, name, value)
    return config

def from_json(path):
    with open(path,'r') as f:
        param_dict = json.load(f)
        return from_dict(param_dict)

def config_setup(config):
    if isinstance(config,str):
        return from_json(config)
    elif isinstance(config,dict):
        return from_dict(config)
    else:
        return config
    
def strconfig(config):
    attr_dict = get_attrs(config)

    s = '\n# ----------------------------parameters table--------------------------- #\n'
    for name,value in attr_dict.items():
        s += f'{name}: {value}\n'
    s += '# ------------------------------------------------------------------------ #'
    return s