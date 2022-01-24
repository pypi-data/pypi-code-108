import argparse
import re

'''
使用argparse对参数进行解析，方便通过命令行与程序进行交互
'''
def get_attrs(obj):
    attr_dict = {}
    for name in dir(obj):
        if callable(getattr(obj, name)): continue
        if re.match('__.*__', name): continue
        if re.match('__.*', name): continue
        if re.match('.*__', name): continue
        attr_dict[name] = getattr(obj, name)
    return attr_dict

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def config_parse(config):
    attr_dict=get_attrs(config)

    parser = argparse.ArgumentParser()
    # start to parse
    for name,value in attr_dict.items():
        if isinstance(value, list):
            parser.add_argument(f'--{name}', type=type(value[0]), nargs='*', default=value)
        elif isinstance(value, bool):
            parser.add_argument(f'--{name}', type=str2bool, default=value)
        else:
            parser.add_argument(f'--{name}', type=type(value), default=value)

    args = parser.parse_args()

    # update config
    for name, value in vars(args).items():
        setattr(config, name, value)

    return config

