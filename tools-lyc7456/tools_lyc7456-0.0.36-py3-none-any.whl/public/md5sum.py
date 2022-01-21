import os
import hashlib

# Write by lyc at 2019-8-9
# Modify by lyc at 2020-3-2
# 文件 md5 值操作

def get_smallfile_md5(filename):
    '''获取小文件md5值'''
    try:
        with open(filename,'rb') as f_read:
            md5_obj = hashlib.md5()
            md5_obj.update(f_read.read())
            hash_code = md5_obj.hexdigest()
            md5 = str(hash_code).lower()

        return md5
    
    except Exception as err:
        print(err)


def get_largefile_md5(filename):
    '''获取大文件md5值'''
    try:
        bufsize = 1024 * 8        # 大文件增大读入缓冲区块，按块读取数据
        with open(filename, 'rb') as f_read:
            md5_obj = hashlib.md5()
            while True:
                d = f_read.read(bufsize)
                if not d:
                    break
                md5_obj.update(d)
            hash_code = md5_obj.hexdigest()
            md5 = str(hash_code).lower()

        return md5
    
    except Exception as err:
        print(err)


def get_file_md5(filename):
    """[获取文件md5值（接口方法）]

    Args:
        filename ([string]): [文件的绝对路径]

    Returns:
        [string]: [文件的md5值]
    """
    # 根据文件大小简单判断：
    chunk = 1024 * 1024 * 50        # 50Mb
    if os.path.getsize(filename) <= chunk: 
        filename_md5 = get_smallfile_md5(filename)
    else: 
        filename_md5 = get_largefile_md5(filename)

    return filename_md5

############################################################################################
import requests

def get_remotefile_md5(filename):
    """[获取远端服务上某个指定文件的md5值]

    Args:
        filename ([string]): [文件的绝对路径]

    Returns:
        [string]: [远端文件的md5值]
    """
    url = 'http://checkmd5.tdtech.gao7.com/fileinfo.php?path={}&action=1'.format(filename)
    try:
        response = requests.get(url)
        remotefile_md5 = response.content.decode('utf-8').lower().split(' ')[0]
        return remotefile_md5

    except Exception as err:
        print(err)

