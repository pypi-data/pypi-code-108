import os
import sys
import hashlib
from queue import Queue
from qcloud_cos import CosConfig, CosS3Client
from multiprocessing import Pool as ProcessPool
from typing import Any, Dict, Tuple, List, Optional
from ..thread_pool import ThreadPool
from ..functions import unixpath, virtual_root


available_hashes = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}


def py310_fix():
    if sys.version_info >= (3, 10):
        import collections.abc, collections
        collections.Iterable = collections.abc.Iterable


def connect_client(target: Dict[str, Any]) -> Tuple[CosS3Client, CosS3Client]:
    client = CosS3Client(CosConfig(
        Region=target["region"],
        SecretId=target["credential"]["secret_id"],
        SecretKey=target["credential"]["secret_key"]
    ))
    if not target.get("accelerate"):
        return client, client
    print("COS：正在连接到全球加速网络")
    uploader = CosS3Client(CosConfig(
        Region="accelerate",
        SecretId=target["credential"]["secret_id"],
        SecretKey=target["credential"]["secret_key"]
    ))
    return client, uploader


def list_files(cos_client: CosS3Client, bucket: str, prefix: str, include_dir: Optional[bool] = False) -> List[Dict]:
    marker = ""
    files = list()
    while True:
        response = cos_client.list_objects(Bucket=bucket, Prefix=prefix, Marker=marker, MaxKeys=500)
        if "Contents" in response:
            files += response["Contents"]
        if response["IsTruncated"] == "false":
            break
        marker = response["NextMarker"]
    if include_dir:
        return files
    return list(filter(lambda file: not file["Key"].endswith("/"), files))


def clear_prefix(cos_client: CosS3Client, bucket: str, prefix: str, remote_files: List[Dict]):
    delete_objects = [{"Key": file["Key"]} for file in remote_files]
    clear_task = cos_client.delete_objects(Bucket=bucket, Delete={"Object": delete_objects})
    deleted = len(clear_task.get("Deleted", []))
    errored = len(clear_task.get("Error", []))
    print(f"COS：删除了 {deleted} 个文件")
    if errored != 0:
        print(f"错误：COS：无法全部删除文件。{errored} 个文件在删除时遇到了错误。", file=sys.stderr)
        sys.exit(-0x2D000002)


def hash_worker(task: Dict[str, Any], hash_names: List[str]):
    buf_size = 16 * 1024 * 1024
    filename = task["filename"]
    hash_instances = [(x, available_hashes[x]()) for x in hash_names]
    with open(filename, "rb") as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            for hash_name, hash_algo in hash_instances:
                hash_algo.update(data)
    task["hash"] = dict()
    for hash_name, hash_algo in hash_instances:
        task["hash"][hash_name] = hash_algo.hexdigest()
    return task


def deploy(target: Dict[str, Any], force: bool):
    py310_fix()
    print("COS：开始部署")
    print(f"COS：部署自 {target['source']}")
    print(f"COS：正在连接 {target['region']}:{target['bucket']}/{target['prefix']}")
    client, uploader = connect_client(target)

    hash_names = [name.lower() for name in set(target.get("hash", []))]
    for hash_name in hash_names:
        if hash_name not in available_hashes.keys():
            print(f"错误：COS：不支持的哈希算法 {hash_name}",
                  f"算法名称必须是以下之一：{', '.join(available_hashes.keys())}", file=sys.stderr)
            sys.exit(-0x2D000003)
    print(f"COS：启用了哈希算法 {', '.join(hash_names)}")

    remote_files = list_files(client, target["bucket"], target["prefix"], include_dir=True)
    if target.get("clear") and (len(remote_files) > 0):
        if (not force) and (input(f"COS: 是否清空前缀 '{target['prefix']}'？ (y/n) ").lower() != "y"):
            print("错误：COS：部署中止。", file=sys.stderr)
            sys.exit(-0x2D000001)
        clear_prefix(client, target["bucket"], target["prefix"], remote_files)

    tasks = list()
    source = os.path.abspath(target["source"])
    for root, dirs, files in os.walk(source):
        remote_root = unixpath(target["prefix"], virtual_root(root, source))
        for file in files:
            tasks.append({"filename": os.path.join(root, file), "remote": unixpath(remote_root, file)})
    print(f"COS：本地文件扫描完成，共 {len(tasks)} 个文件。")

    print("COS：正在计算哈希...", end="", flush=True)
    with ProcessPool(processes=16) as pool:
        results = list()
        for task in tasks:
            results.append(pool.apply_async(hash_worker, args=(task, hash_names,)))
        pool.close()
        pool.join()
    tasks = [result.get() for result in results]
    print("完成")

    def upload_worker(queue: Queue):
        while True:
            work_args = queue.get()
            metadata = {"x-cos-meta-" + k: v for k, v in work_args["hash"].items()}
            uploader.upload_file(Bucket=target["bucket"], LocalFilePath=work_args["filename"], Key=work_args["remote"],
                                 EnableMD5=True, Metadata=metadata)
            queue.task_done()

    upload_pool = ThreadPool(8)
    for task in tasks:
        upload_pool.add_task(task)
    upload_pool.start(worker=upload_worker)
    upload_pool.wait_complete("COS：正在上传 {finished}/{total} {bar} {pct} ({time})", end_text="COS：上传完成")
    print("SSH：部署完成")
