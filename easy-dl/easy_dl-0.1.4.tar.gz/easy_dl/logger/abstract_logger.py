class Abstract_Logger:
    '''
    初始化时，设置保存文件夹、实验的名字、是否添加时间后缀、是否为训练模式
    logger 会在目标文件夹下，新建一个实验名字的目录，后续所有的loss，图像，模型参数都会保存在该目录下
    '''
    def __init__(self, base_root, runname=None, time_suffix=True, mode='train') -> None:
        pass


    # log text
    def log(self, msg):
        pass


    # log loss
    def log_metric(self, name, value):
        pass


    def log_state_dict(self, state_dict, save_path):
        pass


    # log tensor image
    def log_image(self, tensor, save_path):
        pass


    # log tensor images
    def log_images(self, tensor, save_path, nrow=4):
        pass


    def log_figure(self, figure, save_path):
        pass