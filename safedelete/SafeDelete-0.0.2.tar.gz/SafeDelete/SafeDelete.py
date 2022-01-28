'''
Author: Cheryl Li
Date: 2022-01-28 13:29:12
LastEditTime: 2022-01-28 14:57:17
FilePath: /undefined/Users/licheryl/Desktop/test/SafeDelete/SafeDelete.py
'''
import os
import shutil
import time
from datetime import datetime
##############删除的文件会先进入到回收站################
def delete(path, info=False): #默认安全模式
    os.makedirs('./deleted', exist_ok=True)
    if not os.path.exists(path):
        print("No such file {}".format(path))
        return
    if os.path.isfile(path):
        file_name = path.split('/')[-1]
        if os.path.exists(os.path.join('./deleted', file_name)):
            file_name = path+'_'+(datetime.now()).strftime("%m.%d_%H.%M.%S")
        if info: print("Now deleteing a file {}".format(file_name))
        shutil.move(path, os.path.join('./deleted', file_name))
    elif os.path.isdir(path):
        dir_name = path.split('/')[-1]
        if os.path.exists(os.path.join('./deleted', dir_name)):
            dir_name = dir_name+'_'+(datetime.now()).strftime("%m.%d_%H.%M.%S")
        aim_dir = os.path.join('./deleted', dir_name)
        os.mkdir(aim_dir)
        filelist = os.listdir(path)
        if info: print("Now deleting a dir {}".format(path))
        for file in filelist:
            src = os.path.join(path, file)
            dst = os.path.join(aim_dir, file)
            shutil.move(src, dst)
        if not os.listdir(path):  # 如果文件夹为空
            os.rmdir(path)
    else:
        print("{} is a special file (socket,FIFO,device file)".format(path))
def thre2int(t):
    if 'd' in t:
        d_idx = t.find('d')
        try: d = int(t[:d_idx])
        except: print("Unrecognized threshold {}".format(t))
        return d*3600*24
    if 'h' in t:
        h_idx = t.find('h')
        try: h = int(t[:h_idx])
        except: print("Unrecognized threshold {}".format(t))
        return h*3600
    if 'm' in t:
        m_idx = t.find('m')
        try: m = int(t[:m_idx])
        except: print("Unrecognized threshold {}".format(t))
        return m*60
    if 's' in t:
        s_idx = t.find('s')
        try: s = int(t[:s_idx])
        except: print("Unrecognized threshold {}".format(t))
        return s

def clean(threshold='3d', date=True): #date==True时只删除访问时间超过阈值的文件
    if not os.path.exists('./deleted'):
        print("No recycle bin")
        return
    for file in os.listdir('./deleted'):
        unix = os.path.getatime(os.path.join('./deleted', file))
        diff = time.time()-unix
        thre = thre2int(threshold)
        if (date and diff>thre) or (not date):
            ans = input('Do you want to delete {} forever? '.format(file))
            if ans.lower() == 'yes' or ans.lower() == 'y':
                aim_file = os.path.join('./deleted', file)
                if os.path.isfile(aim_file): os.remove(aim_file)
                else: shutil.rmtree(aim_file)
    
