import os
def check_dir(dirs):
    """
    @description  : 判断文件夹是否存在，不存在的话就新建一个
    @param        :
    @Returns      :
    """
    if not os.path.exists(dirs):
        os.makedirs(dirs)

def check_file(filename):
    """
    @description  : 判断文件是否存在，不存在的话就新建一个
    @param        :
    @Returns      :
    """
    if not os.path.exists(filename):
        os.system(r"touch {}".format(filename))#调用系统命令行来创建文件