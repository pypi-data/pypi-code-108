# coding=<encoding name> ： # coding=utf-8
# 项目名称：华光人工智能教育硬件仿真器
# 前项目组成员：lmq,hjh,wpz,czj,sjw
# 文件名：仿真器运行文件
# 作者：lmq(1代),hjh(2代)
# 版本：2代
# --------------------------------------------------------------------------------------------------------
import os
import threading
import sys
import logging
import traceback
import math
import pygame
from pgzero import loaders
from pgzero.screen import Screen
from pgzero.actor import Actor
from pgzero.rect import Rect
from fzq_scnu import fzgpio, fzshijue1, tools, Input
# --------------------------------------------------------------------------------------------------------
# 控制运行的标志，空字符为不运行，非空字符为运行
run = ''
# 换页，code线程结束控制
pagechange = {'left': 1, 'right': 1}
code_threading_is_over = {'over': 0}


# --------------------------------------------------------------------------------------------------------
# 主控
class Update(fzgpio.Mecanum_wheel):
    def __init__(self):
        super(Update, self).__init__()
        self.py_image = 'None'
        self.actor = Actor(LEVEL.actor[0])
        self.actor.pos = (LEVEL.actor[1])
        self.actor_small_rect = Rect((self.actor.left + 10, self.actor.top + 10),
                                     (self.actor.width - 20, self.actor.height - 20))
        self.actor_big_rect = Rect((self.actor.left - 10, self.actor.top - 10),
                                   (self.actor.width + 20, self.actor.height + 20))
        # 积分
        self.score = 0
        self.stars = []
        # 加载level里面的stars为actor类
        if len(LEVEL.level[3]) >= 1:
            for i in range(len(LEVEL.level[3][1])):
                self.stars.append(Actor(LEVEL.level[3][0]))  # 用于存放所有星星对象的列表
            self.stars_pos = [p for p in LEVEL.level[3][1]]
            for num, ac in enumerate(self.stars):
                ac.pos = self.stars_pos[num]  # 给每个对象配置中心坐标
        else:
            self.stars = []
        # 加载level里面的markers为actor类
        if len(LEVEL.level[4]) >= 1:
            self.markers = [Actor(a[0]) for a in LEVEL.level[4]]  # 用于存放所有标志物对象的列表
            self.markers_pos = [(a[1]) for a in LEVEL.level[4]]
            self.markers_front_view = [a[2] for a in LEVEL.level[4]]
            for num, ac in enumerate(self.markers):
                ac.pos = self.markers_pos[num]  # 给每个对象配置中心坐标
        else:
            self.markers = []

    # 定义绘制文本的方法
    @staticmethod
    def draw_t(text, pos, color='black', fontname='fangsong.ttf', fontsize=17):
        screen.draw.text(text, center=pos, color=color, fontname=fontname, fontsize=fontsize)

    # 背景清空
    @staticmethod
    def draw_clear():
        screen.clear()
        screen.fill((244, 244, 244))

    # 背景绘制
    def draw_background(self):
        # 先画场景，再画界面
        screen.blit(LEVEL.level[0], LEVEL.level[1])
        screen.blit(LEVEL.racetrack[0], LEVEL.racetrack[1])
        screen.blit(LEVEL.interface[0], LEVEL.interface[1])
        # 绘制所有星星对象，用于积分
        if self.stars:
            for st in self.stars:
                st.draw()
        # 绘制所有标志物对象，用于视觉
        if self.markers:
            for ma in self.markers:
                ma.draw()
        # 翻页按钮
        self.draw_t('上一页', (pageback_rect.x+pageback_rect.w/2, pageback_rect.y+pageback_rect.h/2))
        self.draw_t('下一页', (pageforward_rect.x+pageforward_rect.w/2, pageforward_rect.y+pageforward_rect.h/2))
        # 文本框
        self.draw_t('文本框', fzgpio.texts_pos_sitting['文本框'])
        self.draw_t('场景长宽约: 3m*2m', fzgpio.texts_pos_sitting['场景长宽约: 3m*2m'])
        self.draw_t('前进速度(mm/s): '+str(round(math.sqrt(fzgpio.msg_dict['actor'][1]['contr_fb']**2 +
                                       fzgpio.msg_dict['actor'][1]['contr_lr']**2), 1)),
                    fzgpio.texts_pos_sitting['前进速度(mm/s): '])
        # 积分
        self.draw_t('分数：' + str(self.score), (1050, 678))

    # 硬件图像刷新
    def draw_sensors(self):
        # 查看小车初始位置的像素点颜色
        # print(pygame.Surface.get_at(screen.surface, [360, 400]))
        # 实现翻页展示传感器画面
        if fzgpio.transmit_right:
            for key, value in list(fzgpio.transmit_right.items()):
                if key <= 5 and value[8] == 1 and pagechange['right'] == 1:  # 第一页的传感器绘制
                    img = Actor('sensors/' + value[0])
                    img.pos = value[1]
                    img.draw()  # 绘制传感器
                    self.draw_t(value[2], value[3])  # 绘制接口类型和接口位号
                    fzgpio.servo.servo_angle_control(value[2], value[1], value[6][1])  # 舵机旋转角度图像绘制
                    for i in range(2):  # 绘制两个文本
                        self.draw_t(value[4][i], value[5][i])
                        self.draw_t(value[6][i], value[7][i])
                elif (5 <= key <= 10) and value[8] == 2 and pagechange['right'] == 2:  # 第二页的传感器绘制
                    img = Actor('sensors/' + value[0])
                    img.pos = value[1]
                    img.draw()
                    self.draw_t(value[2], value[3])
                    fzgpio.servo.servo_angle_control(value[2], value[1], value[6][1])
                    for i in range(2):
                        self.draw_t(value[4][i], value[5][i])
                        self.draw_t(value[6][i], value[7][i])
                elif (10 <= key <= 15) and value[8] == 3 and pagechange['right'] == 3:  # 第三页的传感器绘制
                    img = Actor('sensors/' + value[0])
                    img.pos = value[1]
                    img.draw()
                    self.draw_t(value[2], value[3])
                    fzgpio.servo.servo_angle_control(value[2], value[1], value[6][1])
                    for i in range(2):
                        self.draw_t(value[4][i], value[5][i])
                        self.draw_t(value[6][i], value[7][i])

        # # 小车左红外绘制
        # screen.draw.circle((int(fzgpio.msg_dict['Hongwai_pos']['hongwai_left_x']),
        #                            int(fzgpio.msg_dict['Hongwai_pos']['hongwai_left_y'])), 20, color=(0, 0, 0))
        # # 小车右红外绘制
        # screen.draw.circle((int(fzgpio.msg_dict['Hongwai_pos']['hongwai_right_x']),
        #                            int(fzgpio.msg_dict['Hongwai_pos']['hongwai_right_y'])), 20, color=(0, 0, 0))
        # IO输入碰撞检测框绘制
        # io_in_x = self.actor.center[0] - (self.actor.width / 2 + 13) * math.sin(math.radians(self.actor.angle))
        # io_in_y = self.actor.center[1] - (self.actor.height / 2 + 13) * math.cos(math.radians(self.actor.angle))
        # io_input_rect = Rect((io_in_x, io_in_y), (10, 10))  # IO输入模式下的碰撞检测矩形
        # screen.draw.rect(io_input_rect, color=(0, 0, 0))
        # # 截取的图像绘制
        # def cramer_draw(self):
        #     if self.py_image != 'None':
        #         screen.blit(self.py_image, (self.image_rect.x + 50, self.image_rect.y + 500))
        #         screen.blit('shijue//cramer_fill', (self.image_rect.x + 50, self.image_rect.y + 500))

    # 温湿度文本显示与输入
    def draw_tmp_hum(self):
        # 温湿度手动设置
        if fzgpio.transmit_right:
            for key, value in list(fzgpio.transmit_right.items()):
                result = fzgpio.tmp_hum.tmp_hum_input(value[2])
                if result:
                    InpurBox_temp.draw()
                    InpurBox_humi.draw()
                    if Input.input_text['设置温度'] != '':
                        fzgpio.tmp_hum_data['temp'] = Input.input_text['设置温度']
                    if Input.input_text['设置湿度'] != '':
                        fzgpio.tmp_hum_data['humi'] = Input.input_text['设置湿度']
        # 绘制当前温湿度并绘制
        if fzgpio.texts_pos_sitting:
            if fzgpio.tmp_hum_data['temp'] and fzgpio.tmp_hum_data['humi']:
                self.draw_t(('当前温度(℃): ' + str(fzgpio.tmp_hum_data['temp'])),
                            constants.texts_pos_sitting['当前温度(℃): '])
                self.draw_t(('当前湿度(%): ' + str(fzgpio.tmp_hum_data['humi'])),
                            constants.texts_pos_sitting['当前湿度(%): '])
            elif fzgpio.tmp_hum_data['temp']:
                self.draw_t(('当前温度(℃): ' + str(fzgpio.tmp_hum_data['temp'])),
                            constants.texts_pos_sitting['当前温度(℃): '])
            elif fzgpio.tmp_hum_data['humi']:
                self.draw_t(('当前湿度(%): ' + str(fzgpio.tmp_hum_data['humi'])),
                            constants.texts_pos_sitting['当前湿度(%): '])

    # 小车图像刷新
    def draw_car(self):
        if fzgpio.msg_dict['actor'][0] == 1:
            self.actor.draw()
            # self.xunxian_run()

    # 获取红外像素点颜色
    def hongwai_position(self):
        # 计算小车左右红外的位置
        self.car_hongwai()
        # 获取小车左红外坐标处的像素颜色（RGBA）
        fzgpio.msg_dict['car_pos_color_alpha']['left'] = \
            screen.surface.get_at((int(fzgpio.msg_dict['Hongwai_pos']['hongwai_left_x']),
                                   int(fzgpio.msg_dict['Hongwai_pos']['hongwai_left_y'])))
        # 获取小车右红外坐标处的像素颜色（RGBA）
        fzgpio.msg_dict['car_pos_color_alpha']['right'] = \
            screen.surface.get_at((int(fzgpio.msg_dict['Hongwai_pos']['hongwai_right_x']),
                                   int(fzgpio.msg_dict['Hongwai_pos']['hongwai_right_y'])))
    # ---------------------------------------------------------------------------------

    # 摄像头获取仿真界面图像
    def cramer_update(self):
        # 图像矩形位置
        # if self.actor.x > (200 + 130) and self.actor.y > (6 + 130):
        cr_x = self.actor.center[0] - (self.actor.width / 2 + 55) * math.sin(math.radians(self.actor.angle))
        cr_y = self.actor.center[1] - (self.actor.height / 2 + 55) * math.cos(math.radians(self.actor.angle))
        screen_rect = screen.surface.get_rect()  # 屏幕矩形
        shijue_clip = screen_rect.clip((cr_x - 50, cr_y - 50), (100, 100))  # 裁剪矩形
        py_image, image_rect = tools.clip_image(shijue_clip)
        fzimage = tools.change_image(py_image, size=(200, 200))  # cv2类型的图像
        if self.markers:
            for key, ot in enumerate(self.markers):
                ot_rect = Rect((ot.left, ot.top), (ot.width, ot.height))
                b_rect = fzshijue1.acontainsbs(shijue_clip, ot_rect)
                if b_rect:
                    other_front_view = loaders.images.load(self.markers_front_view[key])
                    fzimage = tools.change_image(other_front_view, size=(200, 200))  # cv2类型的图像
        fzshijue1.fzcamera_dict['fzimage'] = fzimage

    # 小车运动刷新
    def car_update(self):
        if fzgpio.msg_dict['actor'][0] == 1:
            self.actor_small_rect = Rect((self.actor.left + 10, self.actor.top + 10),
                                         (self.actor.width - 20, self.actor.height - 20))
            # IO输入模式下的提前碰撞检测框
            io_in_x = self.actor.center[0] - (self.actor.width / 2 + 13) * math.sin(math.radians(self.actor.angle))
            io_in_y = self.actor.center[1] - (self.actor.height / 2 + 13) * math.cos(math.radians(self.actor.angle))
            io_input_rect = Rect((io_in_x, io_in_y), (1, 1))  # IO输入模式下的碰撞检测矩形
            # ---------------------------------------------------------------------------------
            # 中间画面的大小，小车和物体的放置和运动不能超过此界限
            background_rect = Rect(constants.background_rect[0], constants.background_rect[1])
            hongwai_rect = Rect((int(fzgpio.msg_dict['Hongwai_pos']['hongwai_right_x']),
                                 int(fzgpio.msg_dict['Hongwai_pos']['hongwai_right_y'])), (1, 1))
            # ---------------------------------------------------------------------------------
            # 超声波利用与rect的碰撞来计算距离
            # 超声波刷新
            if fzgpio.msg_dict['csbs'][0] == 1:
                fzgpio.msg_dict['csbs'][1].append(fzgpio.CsbProducing(Update, Rect))  # 制造超声波
                for obj in fzgpio.msg_dict['csbs'][1]:
                    obj.update()
                    # if len(LEVEL.level[2]) > 0:
                    #     for csb_collide in [Rect(i) for i in LEVEL.level[2]]:
                    #         csb_collide, csb_obj_rect = tools.A_colliderect_Bs(obj.csb_rect, csb_collide)
                    #         if csb_collide == True
            # ---------------------------------------------------------------------------------
            # 检测小车与物体或者边界的碰撞，若碰撞则停止行驶
            if len(LEVEL.level[2]) > 0:
                for collide_detection in [Rect(i) for i in LEVEL.level[2]]:
                    # 小车扩展矩形与各个指定矩形的碰撞检测
                    fzgpio.msg_dict['car_expansion_collide'], expansion_obj_rect = \
                        tools.a_collide_rect_bs(io_input_rect, collide_detection)
                    # 小车本身与各个指定矩形的碰撞检测
                    fzgpio.msg_dict['car_collide'], car_obj_rect = tools.a_collide_rect_bs(self.actor_small_rect,
                                                                                           collide_detection)
                    # 超声波操作
                    if fzgpio.msg_dict['csbs'][0] == 1:
                        for key, obj in enumerate(fzgpio.msg_dict['csbs'][1]):
                            # 超声波与各个矩形的碰撞检测
                            csb_collide, csb_obj_rect = tools.a_collide_rect_bs(obj.csb_rect, collide_detection)
                            if not background_rect.contains(obj.csb_rect):
                                del obj, fzgpio.msg_dict['csbs'][1][key]  # 销毁碰撞后的超声波对象，并把其从list中移除
                                fzgpio.msg_dict['csbs'][2] = None
                            elif csb_collide:  # 超声波如果碰撞
                                # 计算碰撞点与小车的距离
                                fzgpio.msg_dict['csbs'][2] = tools.distance_ab(self.actor.pos,
                                                                               (obj.csb_rect.x, obj.csb_rect.y))
                                del obj, fzgpio.msg_dict['csbs'][1][key]  # 销毁碰撞后的超声波对象，并把其从list中移除
                    if fzgpio.msg_dict['car_collide'] or fzgpio.msg_dict['car_expansion_collide']:  # 小车如果碰撞
                        break
            else:
                fzgpio.msg_dict['car_collide'] = False
            if background_rect.contains(self.actor_small_rect) and \
                    background_rect.contains(hongwai_rect) and \
                    (not fzgpio.msg_dict['car_collide']):
                self.car_contr_run()  # 小车运动，若碰撞则无法执行
            # ---------------------------------------------------------------------------------
            # 尝试定位红外
            try:
                self.hongwai_position()
            except Exception as result:
                # 获取报错内容（获取后会导致报错内容不输出）
                msg = traceback.format_exc()
                logging.error(str(msg))
                # 打印出报错内容
                print(result)
                sys.exit(0)

    def score_update(self):
        if fzgpio.msg_dict['actor'][0] == 1:
            self.actor_big_rect = Rect((self.actor.left - 10, self.actor.top - 10),
                                       (self.actor.width + 20, self.actor.height + 20))
            csb_collide = False
            if self.stars:
                for num, star in enumerate(self.stars):
                    star_rect = Rect((star.x, star.y), (star.width, star.height))
                    collide_or_not, collided_star_rect = tools.a_collide_rect_bs(self.actor_big_rect, star_rect)
                    # 此判断用于超声波虚拟场景时的超声波碰撞星星后积分
                    if fzgpio.msg_dict['csbs'][0] == 1 and LEVEL.level[3][3] == '超声波':
                        for key, obj in enumerate(fzgpio.msg_dict['csbs'][1]):
                            csb_collide, csb_obj_rect = tools.a_collide_rect_bs(obj.csb_rect, star_rect)
                            if csb_collide:
                                del star, self.stars[num]
                                self.score += round(100 / len(LEVEL.level[3][1]))
                    # 小车碰撞星星后积分
                    elif collide_or_not:
                        del star, self.stars[num]
                        self.score += round(100/len(LEVEL.level[3][1]))

    # 运行监听
    @staticmethod
    def fzq_over():
        if fzgpio.msg_dict['exit']:
            sys.exit(0)

    @staticmethod
    # 子线程，这里写入新代码，子线程为仿真器画面展示的控制者
    def code():
        try:
            pass
        except Exception as result:
            msg = traceback.format_exc()
            logging.error(str(msg))
            print(msg)
            sys.exit(0)

    # 子线程控制，控制code线程
    def fzgo(self):
        # daemon参数为True，将子线程设置为守护线程，主线程结束，子线程跟着结束，进而使得进程立即结束
        # 设置daemon参数，最终目的是为了，在点击仿真界面右上角的叉叉关闭仿真器的时候，立即结束进程，避免主线程仍在等待子线程结束
        code_threading = threading.Thread(target=self.code, daemon=True)
        code_threading.start()


# --------------------------------------------------------------------------------------------------------
def on_mouse_down(pos, button):
    print(pos)
    # 点击鼠标右键给右边的硬件展示画面翻页
    if button == 1:
        if pageback_rect.collidepoint(pos[0], pos[1]):
            if pagechange['right'] > 1:
                pagechange['right'] -= 1
            else:
                pagechange['right'] = 3
        elif pageforward_rect.collidepoint(pos[0], pos[1]):
            if pagechange['right'] <= 2:
                pagechange['right'] += 1
            else:
                pagechange['right'] = 1
    # 鼠标点击输入框
    if InpurBox_temp_rect.collidepoint(pos[0], pos[1]):
        InpurBox_temp.active = True
    else:
        InpurBox_temp.active = False
    if InpurBox_humi_rect.collidepoint(pos[0], pos[1]):
        InpurBox_humi.active = True
    else:
        InpurBox_humi.active = False


def on_key_up():
    InpurBox_temp.count_time = 0
    InpurBox_humi.count_time = 0


# --------------------------------------------------------------------------------------------------------
# 仿真器运行
if run != '':
    import pgzrun

    # 必须'def draw()'和'def update()',原设定就是如此,即无限循环执行draw()和update()
    # 当然，也可以在game.py里的PGZeroGame.mainloop()设置无限循环
    # 这里利用return返回调用的对象Update里面的draw(),update(),这样可以实现无限循环执行类中的方法
    # 最终目的是实现面向对象开发
    def draw():
        Update.draw_clear()
        Update.draw_background()
        Update.draw_sensors()
        Update.draw_car()
        Update.draw_tmp_hum()

    def update():
        Update.car_update()
        Update.cramer_update()
        Update.score_update()
        Update.fzq_over()
    # --------------------------------------------------------------------------------------------------------
    # 设置根路径（也就是仿真所需要的图像路径，此处由change.py写入）
    # files_path = 'C:\\Users\\86137\\Documents\\python_code\\fzq_test\\emulator_files\\'
    files_path = ''
    loaders.set_root(files_path)
    # 获取constants.py文件的位置，并导入
    sys.path.append(files_path)
    import constants
    # 关卡设置：
    LEVEL = constants.Level()
    # 获取储存日志的位置，记录报错内容
    # files_path_logger = tools.path_processing(files_path, -2, 'txt\\')
    tools.Logging(files_path)
    # --------------------------------------------------------------------------------------------------------
    # 窗口设置
    # screen : Screen
    screen = Screen(pygame.image.load(files_path + 'images\\interfaces\\interface_none.png'))
    WIDTH, HEIGHT = constants.WIDTH, constants.HEIGHT
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    TITLE = constants.TITLE
    icon_path = tools.path_processing(files_path, -1, 'data\\')
    ICON = icon_path + constants.ICON
    # --------------------------------------------------------------------------------------------------------
    # 输入框
    InpurBox_temp_rect = Rect(constants.input_pos['设置温度'][0], constants.input_pos['设置温度'][1])
    InpurBox_temp = Input.InputBox(screen,
                                   rect=InpurBox_temp_rect,
                                   boxname='设置温度',
                                   rectcolor='black',
                                   fontname='fangsong.ttf',
                                   fontsize=18)
    InpurBox_humi_rect = Rect(constants.input_pos['设置湿度'][0], constants.input_pos['设置湿度'][1])
    InpurBox_humi = Input.InputBox(screen,
                                   rect=InpurBox_humi_rect,
                                   boxname='设置湿度',
                                   rectcolor='black',
                                   fontname='fangsong.ttf',
                                   fontsize=18)
    # --------------------------------------------------------------------------------------------------------
    # 翻页框
    pageback_rect = Rect(constants.pageback_rect[0], constants.pageback_rect[1])
    pageforward_rect = Rect(constants.pageforward_rect[0], constants.pageforward_rect[1])
    # --------------------------------------------------------------------------------------------------------
    # 事件刷新
    Update = Update()
    # 启动子线程code（目的：利用子线程控制主线程的仿真画面）
    Update.fzgo()
    # --------------------------------------------------------------------------------------------------------
    # 开始运行
    # pgzrun.go()为死循环,也就是game.py里的PGZeroGame.mainloop()所设置的无限循环。
    pgzrun.go()
    # 以下语句只能在仿真器结束后执行。
    print('仿真器运行结束')
else:
    pass
