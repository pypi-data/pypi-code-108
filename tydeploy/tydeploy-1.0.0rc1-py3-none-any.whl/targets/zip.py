import os
import sys
import time
from zipfile import ZipFile, ZIP_DEFLATED, ZIP_LZMA, ZIP_STORED
from typing import Any, Dict
from ..functions import unixpath, virtual_root

available_algorithms = {
    "ZIP": ZIP_DEFLATED,
    "DEFLATED": ZIP_DEFLATED,
    "LZMA": ZIP_LZMA,
    "STORED": ZIP_STORED,
    "RAW": ZIP_STORED,
}


def deploy(target: Dict[str, Any], force: bool):

    algorithm_name = target["algorithm"].upper()
    source = os.path.abspath(target["source"])
    dest = os.path.abspath(time.strftime(target["archive"]))
    print("ZIP：开始部署")
    print(f"ZIP：部署自 {target['source']}")
    print(f"ZIP：正在创建压缩文件 {dest}")
    if not dest.endswith(".zip"):
        print("警告：ZIP：压缩文件的扩展名应设置为 .zip，否则可能无法在某些操作系统上打开。")
    if algorithm_name not in available_algorithms.keys():
        print(f"错误：ZIP：设置了不兼容的压缩算法 {algorithm_name}。",
              f"算法名称必须是以下之一：{', '.join(available_algorithms.keys())}。", file=sys.stderr)
        sys.exit(-0x2C000002)

    if os.path.exists(dest):
        if (not force) and (input(f"ZIP: 文件 '{dest}' 已存在，是否覆盖？ (y/n) ").lower() != "y"):
            print("错误：ZIP：部署中止。", file=sys.stderr)
            sys.exit(-0x2C000001)
        os.remove(dest)

    print(f"ZIP：使用压缩算法 {algorithm_name} ({available_algorithms[algorithm_name]})")
    print(f"ZIP：使用前缀 '{target['prefix']}'")
    os.makedirs(os.path.dirname(dest), exist_ok=True)

    archive_entries = list()
    for root, directories, files in os.walk(source):
        archive_root = virtual_root(root, source)
        for file in files:
            archive_entries.append({
                "src": os.path.join(root, file),
                "dest": unixpath(target["prefix"], archive_root, file)
            })
    filename_max_length = max([len(x["dest"]) for x in archive_entries]) + 8 + 16

    with ZipFile(dest, "x", available_algorithms[algorithm_name]) as archive:
        for i in range(len(archive_entries)):
            print(" " * filename_max_length, end="\r", flush=True)
            print(f"ZIP：正在压缩 {i}/{len(archive_entries)}：{archive_entries[i]['dest']}", end="\r", flush=True)
            archive.write(archive_entries[i]["src"], archive_entries[i]["dest"])
        print(f"\nZIP：正在写入压缩文件 {dest}")
    print("ZIP：部署完成")
