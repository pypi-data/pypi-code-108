import time
from fzq_scnu import tools
from control import shijue1
import win32

dict = {'fzimage': 'None', 'cam': 'None'}

# 摄像头检测特定物体
def A_contains_Bs(surface_rect, *args):
    rect = surface_rect
    for arg in args:
        if rect.contains(arg):
            return arg
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
        dict['cam'] = 'True'
        print('摄像头开启')

    def close_camera(self):
        # self.cam.release()
        self.cam = None
        dict['cam'] = 'None'
        print('摄像头关闭')

    # get_img 是用来获取单张图片的
    def get_img(self):
        time.sleep(self.time_sleep)
        self.time_sleep = 0.00005
        if dict['cam'] == 'True':
            self.ret, self.img = 1, dict['fzimage']
        else:
            camera_error = '未检测到摄像头，请检测是否开启摄像头'
            raise Exception(camera_error)
