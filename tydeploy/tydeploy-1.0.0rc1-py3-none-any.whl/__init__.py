import os
import sys
import toml
import argparse
from typing import List, Dict, Any

from .targets.ssh import deploy as ssh_deploy
from .targets.zip import deploy as zip_deploy
from .targets.cos import deploy as cos_deploy
from .targets.fs import deploy as fs_deploy

handlers = {
    "ssh": {"function": ssh_deploy, "credential": True},
    "zip": {"function": zip_deploy, "credential": False},
    "cos": {"function": cos_deploy, "credential": True},
    "filesystem": {"function": fs_deploy, "credential": False},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="tianyi's deploy tool")
    parser.add_argument("profile", metavar="<profile>", type=str, help="部署配置的名称")
    parser.add_argument("-f", "--force", action="store_true", help="不进行确认，强制部署")
    return parser.parse_args()


def find_targets(target_names: List[str], config) -> List[Dict[str, Any]]:
    targets = list()
    for name in target_names:
        target = next(filter(lambda x: x["name"] == name, config["target"]), None)
        targets.append(target)

        if target is None:
            print(f"错误：找不到名为 {name} 的部署目标。", file=sys.stderr)
            sys.exit(-0x10000011)

        if target["type"] not in handlers.keys():
            print(f"错误：部署目标 {name} 配置了不支持的部署类型 {target['type']}。", file=sys.stderr)
            sys.exit(-0x10000012)

        if handlers[target["type"]]["credential"]:
            if not target.get("credential"):
                print(f"错误：部署目标 {name} 的类型 {target['type']} 需要设置凭据，但没有设置。", file=sys.stderr)
                sys.exit(-0x10000013)
            target["credential"] = next(filter(lambda x: x["name"] == target["credential"], config["credential"]), None)
            if target["credential"] is None:
                print(f"错误：找不到部署目标 {name} 所需求的凭据。", file=sys.stderr)
                sys.exit(-0x10000014)
    return targets


def main():
    arguments = parse_args()
    config = toml.load(os.path.join(os.getcwd(), ".tydeploy.toml"))
    profile = next(filter(lambda x: x["name"] == arguments.profile, config["profile"]), None)
    if profile is None:
        print(f"错误：找不到名为 {arguments.profile} 的配置。", file=sys.stderr)
        sys.exit(-0x10000001)
    print(f"配置名称：{profile['name']}")
    print(f"配置描述：{profile['description']}")
    print(f"部署目标：{', '.join(profile['targets'])}")

    targets = find_targets(profile["targets"], config)
    for target in targets:
        print(f"开始部署到 {target['name']}")
        target_handler = handlers[target["type"]]
        target_handler["function"](target, force=arguments.force)
    print("已完成全部部署任务。")
