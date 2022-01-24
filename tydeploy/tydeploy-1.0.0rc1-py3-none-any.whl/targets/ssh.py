import os
import sys
import paramiko
from queue import Queue
from io import StringIO
from paramiko import SSHClient, SFTPClient
from typing import Any, Dict
from ..thread_pool import ThreadPool
from ..functions import unixpath, virtual_root


def clear_dest(ssh: SSHClient, dest: str, force: bool):
    if (not force) and (input(f"SSH: 是否清空目录 '{dest}'？ (y/n) ").lower() != "y"):
        print("错误：SSH：部署中止。", file=sys.stderr)
        sys.exit(-0x2A000001)
    command = f"rm -rf '{dest}/'*"
    print(f"SSH：执行命令 {command}")
    ssh.exec_command(command)


def connect_ssh(target: Dict[str, Any]):
    private_key = paramiko.RSAKey.from_private_key(StringIO(target["credential"]["private_key"].strip()))
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=target["host"], port=target["port"], username=target["user"], pkey=private_key)
    transport = ssh.get_transport()
    sftp = SFTPClient.from_transport(transport)
    return ssh, sftp


def deploy(target: Dict[str, Any], force: bool):
    print("SSH：开始部署")
    print(f"ZIP：部署自 {target['source']}")
    print(f"SSH：正在连接 {target['user']}@{target['host']}:{target['port']}")
    ssh, sftp = connect_ssh(target)
    if target.get("clear"):
        clear_dest(ssh, target["dest"], force)

    print("SSH：正在建立索引并创建目录")
    source = os.path.abspath(target["source"])
    thread_pool = ThreadPool()
    print(f"SSH：{source} -> {sftp.normalize(target['dest'])}")
    for root, directories, files in os.walk(source):
        remote_root = "/" + unixpath(sftp.normalize(target['dest']), virtual_root(root, source))
        for directory in directories:
            try:
                sftp.mkdir("/" + unixpath(remote_root, directory))
            except IOError:
                pass
        for file in files:
            thread_pool.add_task({"src": os.path.join(root, file), "dest": "/" + unixpath(remote_root, file)})

    def upload_file(queue: Queue):
        task_ssh, task_sftp = connect_ssh(target)
        while True:
            task = queue.get()
            task_sftp.put(task["src"], task["dest"])
            queue.task_done()

    thread_pool.start(worker=upload_file)
    thread_pool.wait_complete("SSH：正在上传 {finished}/{total} {bar} {pct} ({time})", end_text="SSH：上传完成")
    sftp.close()
    ssh.close()
    print("SSH：部署完成")
