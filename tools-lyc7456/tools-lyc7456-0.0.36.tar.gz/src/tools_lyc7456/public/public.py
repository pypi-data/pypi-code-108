#########################################################################################################
import socket

def get_my_ip():
    """[获取本机IP地址]

    Returns:
        [string]: [eth0 IP地址]
    """
    ## 方法一：通过hostname（不推荐）
    # hostname = socket.gethostname()
    # ip = socket.gethostbyname(hostname)
    # return ip

    # 方法二：通过UDP，参考：https://www.cnblogs.com/xxpythonxx/p/11826491.html
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

#########################################################################################################
import os
import zipfile

def zip_file(dir, filename):
    """[打包并压缩目录或文件] 
            如果dir是单个文件，只压缩文件；
            如果是目录，获取目录下的所有文件加入列表再打包压缩

    Args:
        dir ([string]): [要被打包的目录的绝对路径]
        filename ([string]): [打包后的文件名xxx.zip]

    Returns:
        [bool]: True-成功；False-失败
    """
    try:
        filelist = []
        if os.path.isfile(dir):
            filelist.append(dir)
        else:
            for root, dirs, files in os.walk(dir):
                for dir in dirs:
                    filelist.append(os.path.join(root,dir))
                for name in files:
                    filelist.append(os.path.join(root, name))

        zf = zipfile.ZipFile(filename, "w", zipfile.zlib.DEFLATED)
        for tar in filelist:
            # arcname = tar[len(dir):]
            # zf.write(tar,arcname)
            zf.write(tar)

        zf.close()
        return True

    except Exception as err:
        print(err)
        return False


#########################################################################################################
import requests

def download_file(file_url, local_file_name, chunk_size=10240):
    """[通过url下载文件到本地]

    Args:
        file_url ([string]): [文件的URL]
        local_file_name ([string]): [保存到本地的绝对路径]
        chunk_size (int, optional): [指定每次写入的大小，单位 byte] 根据文件大小来配置，从而提高下载效率。默认值 10240 byte = 1M.
                                    参考值：
                                           大文件 10240 byte = 1M（默认值）
                                           小文件 512 byte = 10KB
    Returns:
        [bool]: True-成功；False-失败
    """
    try:
        r = requests.get(file_url, stream=True)
        f = open(local_file_name, "wb")
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)

        return True

    except Exception as err:
        print(err)
        return False

