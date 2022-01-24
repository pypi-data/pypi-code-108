import os
import sys
import time
import logging

import torch
from torchvision.utils import save_image

'''
自定义一个logger类
能够生成一个目录(可以指定目录名,也可以自动根据时间来生成目录), 保存日志信息，生成图片，模型参数等
能够在终端输出日志信息，同时保存到txt文件
'''

def loadLogger(work_dir='./', save_name='log.txt', logToFile=True):
    # setup logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # set prefix information
    formatter = logging.Formatter(fmt="[ %(asctime)s ] %(message)s", datefmt="%a %b %d %H:%M:%S %Y")
    sHandler = logging.StreamHandler()
    sHandler.setFormatter(formatter)
    logger.addHandler(sHandler)
    # save to file
    if logToFile:
        fHandler = logging.FileHandler(os.path.join(work_dir,save_name), mode='w')
        fHandler.setLevel(logging.DEBUG)
        fHandler.setFormatter(formatter)
        logger.addHandler(fHandler)
        # sys.stdout = fHandler.stream # 设置 print 打印到logger 日志中。
    return logger


class Logger():
    def __init__(self, base_root, runname=None, time_suffix=True, mode='train'):
        # create the dir of results
        self.base_root = base_root
        time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        if runname is None:
            self.runname = time_stamp
        else:
            self.runname = f'{runname}_{time_stamp}'if time_suffix else runname
        self.res_dir=os.path.join(self.base_root,self.runname)
        if not os.path.exists(self.res_dir):
            os.makedirs(self.res_dir)

        # setup logger
        self.logger = loadLogger(self.res_dir, save_name=f'log_{mode}.txt')

    
    # log text
    def log(self,msg):
        self.logger.info(msg)

    
    # log tensor images
    def log_images(self, tensor, save_path, nrow=4):
        save_image(tensor, os.path.join(self.res_dir,save_path), nrow=nrow)


    def log_state_dict(self,state_dict,save_path):
        torch.save(state_dict, os.path.join(self.res_dir,save_path))
        self.log('save weight successfully!')


    # log tensor image
    def log_image(self,tensor,save_path):
        pass

    def log_figure(self,figure,save_path):
        pass

    def log_metric(self, name, value, global_step):
        pass

    def log_metrics(self, loss_dict):
        pass
