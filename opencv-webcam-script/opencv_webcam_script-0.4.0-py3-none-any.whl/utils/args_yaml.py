# 脚本参数管理
# 创建人：曾逸夫
# 创建时间：2022-01-16


import yaml
import sys

ROOT_PATH = sys.path[0]  # 项目根目录


# 脚本参数
def argsYaml(args):
    with open(f'{ROOT_PATH}/args.yaml', 'w') as f:
        yaml.safe_dump(vars(args), f, sort_keys=False)  # 脚本参数yaml保存
