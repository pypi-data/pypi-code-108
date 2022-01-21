import os
import time

# 功能：目录与文件操作

def scanDir(targetDir):
    """[扫描目标目录] Write by lyc 2021-5-19

    Args:
        targetDir ([str]): [目标目录]

    Yields:
        [dic]: [返回文件的相对路径和绝对路径] 
                file_info = {
                'abs_file_path': ,      # 文件的绝对路径
                'rel_file_path': ,      # 文件的相对路径
                }
    """
    relativePath = targetDir.rsplit(os.sep, 1)[0] + os.sep  # 目标的相对路径
    relativeDir = targetDir.rsplit(os.sep, 1)[-1]  # 目标的相对路径下的第一级目录

    for (dirpath, dirnames, filenames) in os.walk(targetDir):
        for fn in filenames:
            # 把 dirpath 和 每个文件名拼接起来 就是全路径
            abs_file_path = os.path.join(dirpath, fn)  # 文件的绝对路径
            rel_file_path = abs_file_path.replace(relativePath, '')  # 文件的相对路径
            file_info = {
                'abs_file_path': abs_file_path,
                'rel_file_path': rel_file_path,
            }
            yield file_info



def is_expire(file_timestamp, expire_day):
    """[判断一个文件的是否过期]
    
    Args:
        file_timestamp ([string]): [文件的最后修改时间]
        expire_day ([int]): [过期时间，单位day]

    Returns:
        [bool]: [True-文件过期，False-文件未过期]
    """
    now_timestamp = time.time()
    diff_timestamp = now_timestamp - file_timestamp     # 时间差的时间戳
    diff_structtime = time.localtime(diff_timestamp)    # 时间差的结构化时间
    diff_days = (diff_structtime.tm_year - 1970)*365 + \
               (diff_structtime.tm_mon - 1)*30 + \
               (diff_structtime.tm_mday - 1)*1          # 时间差转换成天
    
    return True if diff_days > expire_day else False    # 比较时间差的天数与过期时间


def clean_dir(dir, save_day):
    """[清除目录下过期的文件；生成器函数，每删除成功一个文件返回一条 dict 状态码]
    
    :return: ret_code=1 删除文件成功
    Args:
        dir ([string]): [要清理的目录，绝对路径]
        save_day ([int]): [保存时间]

    Yields:
        [string]: [description]
    """
    try:
        if os.path.exists(dir):
            os.chdir(dir)
            for item in os.listdir(dir):        # 遍历该目录下的所有文件存进列表
                if is_expire(os.path.getmtime(item), int(save_day)):     # 调用比较时间的函数，返回值为True表示已过期
                    os.remove(item)             # 过期则删除
                    filename = dir + os.sep + item
                    yield filename
    
    except Exception as err:
        print(err)

