import time
from control import shijue1

fzcamera_dict = {'fzimage': 'None', 'cam': 'None'}


# 摄像头检测特定物体
def acontainsbs(surface_rect, *args):
    rect = surface_rect
    for arg in args:
        if rect.contains(arg):
            return arg
        else:
            return 0
# -------------------------------------------------------------------------
# Img继承+修改
class Img(shijue1.Img):
    def __init__(self):
        shijue1.Img.__init__(self)
        self.img = None
        self.cam = None
        self.time_sleep = 0.5

    def camera(self, num=0):
        # self.cam = shijue1.cv2.VideoCapture(num)
        self.cam = True
        fzcamera_dict['cam'] = 'True'
        print('摄像头开启')

    def close_camera(self):
        # self.cam.release()
        self.cam = None
        fzcamera_dict['cam'] = 'None'
        print('摄像头关闭')

    # get_img 是用来获取单张图片的
    def get_img(self):
        time.sleep(self.time_sleep)
        self.time_sleep = 0.00005
        if fzcamera_dict['cam'] == 'True':
            self.ret, self.img = 1, fzcamera_dict['fzimage']
        else:
            camera_error = '未检测到摄像头，请检测是否开启摄像头'
            raise Exception(camera_error)
