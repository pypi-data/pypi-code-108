import os
import sys
import stat
import shutil
from typing import Any, Dict


def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def deploy(target: Dict[str, Any], force: bool):
    source = os.path.abspath(target["source"])
    dest = os.path.abspath(target["dest"])
    print("FS：开始部署")
    print(f"FS：部署自 {source}")
    print(f"FS：部署至 {dest}")

    if target.get("clear") and os.path.exists(dest):
        if (not force) and (input(f"FS: 是否清空目录 '{dest}'？ (y/n) ").lower() != "y"):
            print("错误：FS：部署中止。", file=sys.stderr)
            sys.exit(-0x2B000001)
        shutil.rmtree(dest, onerror=remove_readonly)

    os.makedirs(dest, exist_ok=True)
    print("FS：正在复制文件，请稍等")
    shutil.copytree(source, dest, dirs_exist_ok=True)
    print("FS：部署完成")
