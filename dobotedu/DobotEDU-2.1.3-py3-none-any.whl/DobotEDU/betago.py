import time

# ********出入库涉及到的全局变量******
# 智能仓库库外点与库内点
P1_out = [250, 48]
P1_in = [203, 50]  # 智能仓库库内点
# 超市库外点与库内点
P2_out = [100, 48]
P2_in = [53, 50]  # 超市库内点
# **********************************

# *************************抓取涉及到的全局变量*******************************************
# 小车置物盒上方固定检测点
p_x0 = 0
p_y0 = -223
p_z0 = 110
p_R0 = -45

p_R0_grap = -110  # 从小车置物盒抓取角度，防控制盒干涉
p_R0_throw = p_R0

# 地面上方固定检测点
p_x1 = 223
p_y1 = 0
p_z1 = 110
p_R1 = -75

# 小车置物盒固定放置物品点参数
p_x2 = -60
p_y2 = -233
p_z2 = 25
p_R2 = -75
thetaX = 0  # 放置偏移
catch_num = 1  # 物品计数

# 机械臂目标坐标
p_x = 0
p_y = 0
p_R = 0

# 仓库固定放置点
X1 = 250
Y1 = 60
Z1 = 33

X2 = 250
Y2 = -60
Z2 = 33

# 目标id索引
object_id = 0
'''
 OBJECT_INDEX = {"orange":0,"cabbage":1,"water":2,"Beijin":3,"ShangHai":4,
 "ShenZhen":5}
 *************************************************************************************
'''

# 新增二维码接口
Atag_list = {}  # 保存用户创建的二维码信息
BOX_MZ = -15  # 吸嘴到达置物盒平面的机械臂z轴坐标


class BetaGoApi(object):
    def __init__(self, rpc_adapter, port_name=None):
        self.__dobotlink = rpc_adapter
        self._port_name = port_name
        self.rgb_number = {
            "LED_1": 1,
            "LED_2": 2,
            "LED_3": 3,
            "LED_4": 4,
            "LED_ALL": 5
        }

        self.camera_h = 159  # 摄像头距离标定平面高度
        self.theta_h = 0  # 物体平面相对标定平面高度

        self.indicator_id = {
            "lors": 0,
            "l": 1,
            "p": 2,
            "apt": 3,
            "rors": 4,
            "r": 5,
            "stop": 6,
            "spm": 7,
            "t": 8,
            "u": 9,
            "wh": 10,
            "z": 11
        }

    def get_portname(func):
        def wrapper(self, *args, **kwargs):
            if self._port_name:
                return func(self, self._port_name, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)

        return wrapper

    @get_portname
    def set_running_mode(self, port_name, mode):
        return self.__dobotlink.MagicianGO.SetRunningMode(portName=port_name,
                                                          runningMode=mode)

    @get_portname
    def set_move_speed_direct(self, port_name, direction, speed):
        return self.__dobotlink.MagicianGO.SetMoveSpeedDirect(
            portName=port_name, dir=direction, speed=speed)

    @get_portname
    def set_move_speed(self, port_name, x, y, r):
        return self.__dobotlink.MagicianGO.SetMoveSpeed(portName=port_name,
                                                        x=x,
                                                        y=y,
                                                        r=r)

    @get_portname
    def set_rotate(self, port_name, r, Vr):
        return self.__dobotlink.MagicianGO.SetRotate(portName=port_name,
                                                     r=r,
                                                     Vr=Vr,
                                                     isQueued=True,
                                                     isWaitForFinish=True,
                                                     timeout=604800000)

    @get_portname
    def set_move_dist(self, port_name, x, y, Vx, Vy):
        return self.__dobotlink.MagicianGO.SetMoveDist(portName=port_name,
                                                       x=x,
                                                       y=y,
                                                       Vx=Vx,
                                                       Vy=Vy,
                                                       isQueued=True,
                                                       isWaitForFinish=True,
                                                       timeout=604800000)

    @get_portname
    def set_move_pos(self, port_name, x, y, s):
        speed_res = self.__dobotlink.MagicianGO.GetSpeedometer(
            portName=port_name)
        self.__dobotlink.MagicianGO.SetRotate(portName=port_name,
                                              r=-(speed_res["yaw"]),
                                              Vr=s,
                                              isQueued=True,
                                              isWaitForFinish=True,
                                              timeout=604800000)
        return self.__dobotlink.MagicianGO.SetMovePos(portName=port_name,
                                                      x=x,
                                                      y=y,
                                                      s=s,
                                                      isQueued=True,
                                                      isWaitForFinish=True,
                                                      timeout=604800000)

    @get_portname
    def set_arc_rad(self, port_name, velocity, radius, angle, mode):
        return self.__dobotlink.MagicianGO.SetArcRad(portName=port_name,
                                                     velocity=velocity,
                                                     radius=radius,
                                                     angle=angle,
                                                     mode=mode,
                                                     isQueued=True,
                                                     isWaitForFinish=True,
                                                     timeout=604800000)

    @get_portname
    def set_arc_cent(self, port_name, velocity, x, y, angle, mode):
        return self.__dobotlink.MagicianGO.SetArcCent(portName=port_name,
                                                      velocity=velocity,
                                                      x=x,
                                                      y=y,
                                                      angle=angle,
                                                      mode=mode,
                                                      isQueued=True,
                                                      isWaitForFinish=True,
                                                      timeout=604800000)

    @get_portname
    def set_coord_closed_loop(self, port_name, isEnable, angle):
        return self.__dobotlink.MagicianGO.SetCoordClosedLoop(
            portName=port_name, isEnable=isEnable, angle=angle)

    @get_portname
    def set_increment_closed_loop(self, port_name, x, y, angle):
        return self.__dobotlink.MagicianGO.SetIncrementClosedLoop(
            portName=port_name,
            x=x,
            y=y,
            angle=angle,
            isQueued=True,
            isWaitForFinish=True,
            timeout=604800000)

    @get_portname
    def set_rgb_light(self, port_name, number, effect, r, g, b, cycle, counts):
        if type(number) == "str":
            return self.__dobotlink.MagicianGO.SetLightRGB(
                portName=port_name,
                number=self.rgb_number[number],
                effect=effect,
                r=r,
                g=g,
                b=b,
                cycle=cycle,
                counts=counts)
        else:
            return self.__dobotlink.MagicianGO.SetLightRGB(portName=port_name,
                                                           number=number,
                                                           effect=effect,
                                                           r=r,
                                                           g=g,
                                                           b=b,
                                                           cycle=cycle,
                                                           counts=counts)

    @get_portname
    def set_buzzer_sound(self, port_name, index, tone, beat):
        return self.__dobotlink.MagicianGO.SetBuzzerSound(portName=port_name,
                                                          index=index,
                                                          tone=tone,
                                                          beat=beat)

    @get_portname
    def get_ultrasonic_data(self, port_name):
        u_data = self.__dobotlink.MagicianGO.GetUltrasoundData(
            portName=port_name)
        u_res = {
            "front": float(format(u_data["front"], ".2f")),
            "back": float(format(u_data["back"], ".2f")),
            "left": float(format(u_data["left"], ".2f")),
            "right": float(format(u_data["right"], ".2f"))
        }
        return u_res

    @get_portname
    def set_odometer_data(self, port_name, x, y, yaw):
        return self.__dobotlink.MagicianGO.SetSpeedometer(portName=port_name,
                                                          x=x,
                                                          y=y,
                                                          yaw=yaw)

    @get_portname
    def get_odometer_data(self, port_name):
        o_data = self.__dobotlink.MagicianGO.GetSpeedometer(portName=port_name)
        o_res = {
            "x": float(format(o_data["x"], ".2f")),
            "y": float(format(o_data["y"], ".2f")),
            "yaw": float(format(o_data["yaw"], ".2f"))
        }
        return o_res

    @get_portname
    def get_power_voltage(self, port_name):
        v_data = self.__dobotlink.MagicianGO.GetBatteryVoltage(
            portName=port_name)
        v_res = {
            "powerVoltage": float(format(v_data["powerVoltage"], ".2f")),
            "powerPercentage": float(format(v_data["powerPercentage"], ".2f"))
        }
        return v_res

    @get_portname
    def get_imu_angle(self, port_name):
        a_data = self.__dobotlink.MagicianGO.GetImuAngle(portName=port_name)
        a_res = {
            "yaw": float(format(a_data["yaw"], ".2f")),
            "roll": float(format(a_data["roll"], ".2f")),
            "pitch": float(format(a_data["pitch"], ".2f"))
        }
        return a_res

    @get_portname
    def set_auto_trace(self, port_name, trace):
        if trace:
            self.__dobotlink.MagicianGO.SetTraceLoop(portName=port_name,
                                                     enable=True)
        else:
            self.__dobotlink.MagicianGO.SetTraceLoop(portName=port_name,
                                                     enable=False)
        return self.__dobotlink.MagicianGO.SetTraceAuto(portName=port_name,
                                                        isTrace=trace)

    @get_portname
    def set_trace_speed(self, port_name, speed):
        return self.__dobotlink.MagicianGO.SetTraceSpeed(portName=port_name,
                                                         speed=speed)

    @get_portname
    def set_trace_pid(self, port_name, p, i, d):
        return self.__dobotlink.MagicianGO.SetTracePid(portName=port_name,
                                                       p=p,
                                                       i=i,
                                                       d=d)

    @get_portname
    def get_trace_angle(self, port_name):
        an_data = self.__dobotlink.MagicianGO.GetCarCameraAngle(
            portName=port_name)
        an_res = {"angle": float(format(an_data["angle"], ".2f"))}
        return an_res

    @get_portname
    def get_arm_camera_obj(self, port_name):
        return self.__dobotlink.MagicianGO.GetArmCameraObj(portName=port_name)

    @get_portname
    def get_car_camera_obj(self, port_name):
        return self.__dobotlink.MagicianGO.GetCarCameraObj(portName=port_name)

    @get_portname
    def get_arm_camera_tag(self, port_name):
        return self.__dobotlink.MagicianGO.GetArmCameraTag(portName=port_name)

    @get_portname
    def set_stop_point_server(self, port_name, x, y):
        return self.__dobotlink.MagicBox.SetStopPointServer(portName=port_name,
                                                            PointX=x,
                                                            PointY=y)

    @get_portname
    def set_stop_point_param(self, port_name, scope_err, stop_err):
        return self.__dobotlink.MagicBox.SetStopPointParam(portName=port_name,
                                                           scopeErr=scope_err,
                                                           stopErr=stop_err)

    @get_portname
    def get_stop_point_state(self, port_name):
        return self.__dobotlink.MagicBox.GetStopPointState(portName=port_name)

    # 进入仓库
    def into_park_space(self, garage_class=0):
        '''小车入库,garage_class=0为进入仓库，1为进入超市'''
        if garage_class == 0:
            point = P1_in  # 智能仓库库内点
        else:
            point = P2_in  # 超市库内点
        self.set_stop_point_server(x=point[0] + 64, y=point[1])  # 设置后退停车点
        self.set_stop_point_param(scope_err=40, stop_err=2)
        # time.sleep(0.3)
        # self.set_auto_trace(trace=0)
        self.set_move_speed_direct(direction=0, speed=-20)  # 后退
        self.wait_stop_point()  # 等待完成停车动作
        self.set_stop_point_server(x=point[0] + 23, y=point[1])  # 设置巡线停车点
        # time.sleep(0.3)
        self.set_trace_pid(p=0.5, i=0, d=0.5)
        self.set_trace_speed(speed=20)  # 入库必该速度巡线进入比较稳定
        self.set_auto_trace(trace=1)  # 打开巡线
        self.wait_stop_point()  # 等待完成停车动作
        self.set_stop_point_server(x=point[0], y=point[1])  # 设置巡线停车点
        # time.sleep(0.3)
        self.set_move_speed_direct(direction=0, speed=10)
        self.wait_stop_point()  # 等待完成停车动作

    # 出仓
    def out_park_space(self, garage_class=0):
        '''小车出库,garage_class=0为退出仓库，1为退出超市'''
        if garage_class == 0:
            point = P1_out  # 智能仓库库外点
        else:
            point = P2_out  # 超市库外点
        self.set_stop_point_param(scope_err=40, stop_err=2)
        self.set_stop_point_server(x=point[0], y=point[1])  # 设置后退停车点
        # time.sleep(0.2)
        self.set_move_speed_direct(direction=0, speed=-10)
        self.wait_stop_point()  # 等待完成停车

    def stop_point(self, point, scope=40, err=2):
        ''' 设置指定点停车,scope为小车四周范围误差，err为小车前进方向误差'''
        self.set_stop_point_param(scope_err=scope, stop_err=err)
        self.set_stop_point_server(x=point[0], y=point[1])
        # time.sleep(0.1)
        self.wait_stop_point()  # 等待完成停车

    # 等待完成停车服务
    def wait_stop_point(self):
        '''等待指定点停车完成'''
        while True:
            stop_flag = self.get_stop_point_state()
            value = self.get_odometer_data()
            print("x:" + str('%.2f' % value['x']) + " y:" +
                  str('%.2f' % value['y']) + " angle:" +
                  str('%.2f' % value['yaw']))
            time.sleep(0.001)
            if stop_flag['result']:
                break

    @get_portname
    def imgxy_to_armxy(self,
                       port_name,
                       px,
                       py,
                       need_tranxy,
                       suck_apriltag=0,
                       apriltag_h=5):
        '''图像坐标转机器坐标'''
        res = self.__dobotlink.MagicBox.GetImgToArmXY(
            portName=port_name,
            imgX=px,
            imgY=py,
            needTranxy=need_tranxy,
            suckApriltag=suck_apriltag,
            apriltagHeight=apriltag_h)
        Mx = res["armX"]
        My = res["armY"]
        return Mx, My

    # 由于下面两个函数调用到lite的api，所以在此处封装两个lite接口
    @get_portname
    def _set_ptpcmd(self,
                    port_name,
                    ptp_mode: int,
                    x: float,
                    y: float,
                    z: float,
                    r: float,
                    is_queued=True,
                    is_wait=True):
        return self.__dobotlink.MagicianLite.SetPTPCmd(portName=port_name,
                                                       ptpMode=ptp_mode,
                                                       x=x,
                                                       y=y,
                                                       z=z,
                                                       r=r,
                                                       isQueued=is_queued,
                                                       isWaitForFinish=is_wait,
                                                       timeout=86400000)

    @get_portname
    def _set_endeffector_gripper(self,
                                 port_name,
                                 enable: bool,
                                 on: bool,
                                 is_queued=False):
        return self.__dobotlink.MagicianLite.SetEndEffectorGripper(
            portName=port_name, enable=enable, on=on, isQueued=is_queued)

    def grab_obj_cartofloor(self, object_class=0):
        '''从小车上抓取生鲜/快递到地面置物盒,object_class=0、1、2,分别代表生鲜快递、生鲜、快递'''
        global p_x0, p_x1, p_x2, p_x, p_y, p_y0, p_y1, p_y2, p_z0, p_z1, p_z2
        global p_R, p_R0, p_R1, p_R2, p_R0_grap
        global X1, X2, X3, Y1, Y2, Y3, Z1, Z2, Z3
        global object_id
        detect_flag = True
        need_trans = 0
        NoObj_time = 0
        cannotReach_time = 0
        move_x0 = 0
        move_y0 = 0
        move_time = 0
        if object_class == 0:  # 0代表生鲜和快递
            index_1 = -1
            index_2 = 6
        elif object_class == 1:  # 1代表生鲜
            index_1 = -1
            index_2 = 3
        else:  # object_class == 2:代表快递
            index_1 = 2
            index_2 = 6
        self._set_endeffector_gripper(enable=True, on=True)  # 闭合
        time.sleep(0.5)

        while detect_flag:
            self._set_ptpcmd(ptp_mode=1,
                             x=p_x0 + move_x0,
                             y=p_y0 + move_y0,
                             z=p_z0,
                             r=p_R0)
            time.sleep(0.8)
            datalist = self.get_arm_camera_obj()  # 检测物品
            NoObj_time = 0
            while datalist[
                    'count'] == 0 and NoObj_time < 5:  # 防止某一瞬间没检测到物品导致认为没有物品
                datalist = self.get_arm_camera_obj()
                NoObj_time += 1
            if datalist['count']:  # 是否有物体
                for i in range(datalist['count']):
                    if datalist['dl_obj'][i]['id'] > index_1 and datalist[
                            'dl_obj'][i]['id'] < index_2:  # 取快递/生鲜进行抓取
                        cx = datalist['dl_obj'][i]['x']
                        cy = datalist['dl_obj'][i]['y']
                        p_x, p_y = self.imgxy_to_armxy(cx, cy, need_trans)
                        p_x = p_x + move_x0
                        p_y = p_y + move_y0
                        object_id = datalist['dl_obj'][i]['id']

                        if -100 < p_x < 90 and -260 < p_y < -195:
                            cannotReach_time = 0
                        else:
                            print("Can't reach!")
                            # 防止误检测盒子外部物体时，一直while循环
                            # 处理方式：连续3次检测到无法到达抓取位置的物体，则结束while循环
                            cannotReach_time += 1
                            if cannotReach_time > 3:
                                detect_flag = False
                            continue  # 无法到达抓取位置，则抓取下一个物体

                        if object_id == 2:  # 水瓶特殊抓取策略
                            w = datalist['dl_obj'][i]['w']
                            h = datalist['dl_obj'][i]['h']
                            if w < h:  # 水瓶偏向“竖”放在小车置物盒上
                                p_R = p_R1
                            else:  # 水瓶偏向“横”放在小车置物盒上
                                p_R = p_R0_grap

                        self._set_endeffector_gripper(enable=False,
                                                      on=True)  # 常态
                        self._set_ptpcmd(1, p_x, p_y, 35, p_R)  # 物体上方过度点
                        self._set_endeffector_gripper(enable=True,
                                                      on=False)  # 张开
                        time.sleep(0.5)  # 延迟一会
                        self._set_ptpcmd(1, p_x, p_y, 17, p_R)  # 抓取位置
                        self._set_endeffector_gripper(enable=True,
                                                      on=True)  # 闭合
                        time.sleep(0.5)  # 延迟一会抓稳
                        self._set_ptpcmd(1, p_x, p_y, 9, p_R)  # 下压抓稳位置
                        self._set_ptpcmd(1, p_x0, p_y0, p_z0,
                                         p_R)  # 先回归位，作为中转点
                        self._set_ptpcmd(1, p_x1, p_y1, p_z1, p_R0)  # 仓库上方点

                        if (object_id == 0) or (object_id == 1) or (
                                object_id == 3) or (object_id == 4):  # 橙子\白菜
                            self._set_ptpcmd(1, X1, Y1, Z1, p_R0)  # 丢到固定位置1
                            self._set_endeffector_gripper(enable=True,
                                                          on=False)  # 张开
                        else:  # 水瓶
                            self._set_ptpcmd(1, X2, Y2, Z2, p_R0)  # 丢到固定位置2
                            self._set_endeffector_gripper(enable=True,
                                                          on=False)  # 张开
                        time.sleep(0.5)
                        self._set_ptpcmd(1, p_x1, p_y1, p_z1, p_R0)  # 仓库上方点
                        self._set_endeffector_gripper(enable=True,
                                                      on=True)  # 闭合
                        break  # 抓取检测到的第一个目标成功，则结束for循环

                    elif i == datalist[
                            'count'] - 1:  # 循环到最后一个检测到的物体不是目标物体，移动机械臂一下，防止漏检
                        move_time += 1
                        if move_time == 1:  # 第一次没检测到物体，机械臂往里面走10mm
                            move_x0 = 0
                            move_y0 = 10
                            continue
                        elif move_time == 2:  # 第二次没检测到物体，机械臂往外面走10mm
                            move_x0 = 0
                            move_y0 = -10
                            continue
                        else:
                            print("No target object!")
                            detect_flag = False
            else:
                move_time += 1
                if move_time == 1:  # 第一次没检测到物体，机械臂往里面走10mm
                    move_x0 = 0
                    move_y0 = 10
                    continue
                elif move_time == 2:  # 第二次没检测到物体，机械臂往外面走10mm
                    move_x0 = 0
                    move_y0 = -10
                    continue
                else:
                    print("No object!")
                    detect_flag = False
        self._set_ptpcmd(ptp_mode=1, x=0, y=-200, z=50, r=0)
        self._set_endeffector_gripper(enable=False, on=True)

    def grab_obj_floortocar(self, object_class=0):
        '''从地面置物盒抓取生鲜快递到小车上,object_class=0、1、2,分别代表生鲜快递、生鲜、快递'''
        global p_x0, p_x1, p_x2, p_x, p_y, p_y0, p_y1, p_y2, p_z0, p_z1, p_z2
        global p_R, p_R0, p_R1, p_R2, p_R0_throw
        global object_id
        thetaX = 0  # 放置置物盒位置增量
        catch_num = 0  # 物品计数
        detect_flag = True
        need_trans = 1
        NoObj_time = 0
        cannotReach_time = 0
        move_x0 = 0
        move_y0 = 0
        move_time = 0
        if object_class == 0:  # 代表生鲜和快递
            index_1 = -1
            index_2 = 6
        elif object_class == 1:  # 1代表生鲜
            index_1 = -1
            index_2 = 3
        else:  # object_class == 2:代表快递
            index_1 = 2
            index_2 = 6
        self._set_endeffector_gripper(enable=True, on=True)  # 闭合
        time.sleep(0.5)

        while detect_flag and catch_num < 3:  # 有物体且已抓取的数量小于3个
            self._set_ptpcmd(1, p_x1 + move_x0, p_y1 + move_y0, p_z1, p_R1)
            time.sleep(0.8)
            # 检测物品
            datalist = self.get_arm_camera_obj()
            NoObj_time = 0
            while datalist['count'] == 0 and NoObj_time < 5:
                datalist = self.get_arm_camera_obj()
                NoObj_time += 1
            if datalist['count']:  # 有物体且已抓取的数量小于3个
                for i in range(datalist['count']):  # 取第一个目标物体进行抓取
                    if datalist['dl_obj'][i]['id'] > index_1 and datalist[
                            'dl_obj'][i]['id'] < index_2:  # 取目标物体进行抓取
                        catch_num += 1  # 已抓取物品数量+1
                        cx = datalist['dl_obj'][i]['x']
                        cy = datalist['dl_obj'][i]['y']
                        p_x, p_y = self.imgxy_to_armxy(cx, cy, need_trans)
                        p_x = p_x + move_x0
                        p_y = p_y + move_y0
                        object_id = datalist['dl_obj'][i]['id']
                        if 180 < p_x < 317 and -284 < p_y < 160:
                            cannotReach_time = 0
                        else:
                            print("Can't reach!")
                            # 防止误检测盒子外部物体时，一直while循环
                            # 处理方式：连续3次检测到无法到达抓取位置的物体，则结束while循环
                            cannotReach_time += 1
                            if cannotReach_time > 3:
                                detect_flag = False
                            continue  # 无法到达抓取位置，则抓取下一个物体
                        if object_id == 2:  # 水瓶特殊抓取策略
                            w = datalist['dl_obj'][i]['w']
                            h = datalist['dl_obj'][i]['h']
                            if w < h:  # 水瓶偏向“竖”放在地面置物盒上
                                p_R = p_R0
                                p_R0_throw = p_R0
                            else:
                                p_R = p_R1
                                p_R0_throw = -170
                        self._set_endeffector_gripper(enable=False,
                                                      on=True)  # 常态
                        self._set_ptpcmd(1, p_x, p_y, 35, p_R)  # 物体上放过度点
                        self._set_endeffector_gripper(enable=True,
                                                      on=False)  # 张开
                        time.sleep(0.5)  # 延迟一会抓稳
                        self._set_ptpcmd(1, p_x, p_y, 17, p_R)  # 抓取位置
                        self._set_endeffector_gripper(enable=True,
                                                      on=True)  # 闭合
                        time.sleep(0.5)  # 延迟一会抓稳
                        self._set_ptpcmd(1, p_x, p_y, 9, p_R)  # 下压抓稳位置
                        self._set_ptpcmd(1, p_x1, p_y1, p_z1,
                                         p_R1)  # 先回归位，作为中转点
                        self._set_ptpcmd(1, p_x0, p_y0, p_z0,
                                         p_R)  # 小车置物盒上方零位点
                        self._set_ptpcmd(
                            1, p_x2 + thetaX, p_y2, p_z2,
                            p_R0_throw)  # 抓取到的物品按从左到右，从上到下顺序放置在置物盒
                        self._set_endeffector_gripper(enable=True,
                                                      on=False)  # 张开
                        time.sleep(0.5)
                        self._set_ptpcmd(1, p_x0, p_y0, p_z0,
                                         p_R0)  # 回到小车置物盒上方零位点
                        self._set_endeffector_gripper(enable=True,
                                                      on=True)  # 闭合
                        time.sleep(1)  # 这里需要等待1s秒钟等待机械臂末端完全闭合
                        # 检测物品数量，判断是否抓取成功并放置置物盒
                        datalist = self.get_arm_camera_obj()
                        NoObj_time = 0
                        while datalist['count'] == 0 and NoObj_time < 5:
                            datalist = self.get_arm_camera_obj()
                            NoObj_time += 1
                        if datalist['count'] >= catch_num:  # 目前置物盒物体数量是否等于已抓取数量
                            thetaX += 60  # 设置下次放置点
                        else:  # 如果数量和小于抓取数量（可能未成功抓取，或者漏检测物体），则机械臂往里面走10mm再次检测
                            self._set_ptpcmd(1, p_x0 + 0, p_y0 + 10, p_z0,
                                             p_R0)  # 小车置物盒上方零位点
                            time.sleep(0.5)
                            datalist = self.get_arm_camera_obj()
                            NoObj_time = 0
                            while datalist['count'] == 0 and NoObj_time < 5:
                                datalist = self.get_arm_camera_obj()
                                NoObj_time += 1
                            if datalist['count'] == catch_num:
                                thetaX += 60  # 设置下次放置点
                            else:
                                catch_num -= 1
                        break  # 抓取检测到的第一个目标成功，则结束for循环

                    elif i == datalist[
                            'count'] - 1:  # 循环到最后一个检测到的物体不是目标物体，移动机械臂一下，防止漏检
                        move_time += 1
                        if move_time == 1:  # 第一次没检测到物体，机械臂往里面走10mm
                            move_x0 = -10
                            move_y0 = 0
                            continue
                        elif move_time == 2:  # 第二次没检测到物体，机械臂往外面走10mm
                            move_x0 = 10
                            move_y0 = 0
                            continue
                        else:
                            print("No target object!")
                            detect_flag = False
            else:
                move_time += 1
                if move_time == 1:  # 第一次没检测到物体，机械臂往里面走10mm
                    move_x0 = -10
                    move_y0 = 0
                    continue
                elif move_time == 2:  # 第二次没检测到物体，机械臂往外面走10mm
                    move_x0 = 10
                    move_y0 = 0
                    continue
                else:
                    print("No object!")
                    detect_flag = False
        print("There is no target object or the number has exceeded 3!")
        self._set_ptpcmd(ptp_mode=1, x=0, y=-200, z=50, r=0)
        self._set_endeffector_gripper(enable=False, on=True)

    # 到置物盒检测位置
    def set_ptp_car(self):
        self._set_ptpcmd(1, p_x0, p_y0, p_z0, p_R0)

    # 到地面上方检测位置
    def set_ptp_floor(self):
        self._set_ptpcmd(1, p_x1, p_y1, p_z1, p_R1)

    def creat_apriltag_obj(self, id, height):
        # '''创建二维码物体信息，输入参数：id-二维码的id，height-二维码物体高度'''
        Atag_list['%d' % (id)] = height
        return True

    def get_apriltag_obj_height(self, id):
        # '''获取已创建的目标id二维码物体高度'''
        if '%d' % (id) in Atag_list:  # 判断是否在用户创建的二维码字典中
            height = Atag_list['%d' % (id)]
            return height
        else:
            print("AprilTag:" + str(id) + " has not been created")  # 该二维码未创建"

    def get_apriltag_obj_z(self, id):
        # '''获取已创建的目标id二维码物体的机器坐标z'''
        if '%d' % (id) in Atag_list:  # 判断是否在用户创建的二维码字典中
            height = Atag_list['%d' % (id)]
            suck_z = BOX_MZ + height - 2.5
            return suck_z
        else:
            print("AprilTag:" + str(id) + " has not been created")  # 该二维码未创建"

    # 2021-2-19新增末端摄像头运行模型
    @get_portname
    def set_car_camera_model(self, port_name, index):
        return self.__dobotlink.MagicianGO.SetCarCameraRunModel(
            portName=port_name, runModelIndex=index)

    @get_portname
    def get_car_camera_model(self, port_name):
        return self.__dobotlink.MagicianGO.GetCarCameraRunModel(
            portName=port_name)

    @get_portname
    def set_arm_camera_model(self, port_name, index):
        return self.__dobotlink.MagicianGO.SetArmCameraRunModel(
            portName=port_name, runModelIndex=index)

    @get_portname
    def get_arm_camera_model(self, port_name):
        return self.__dobotlink.MagicianGO.GetArmCameraRunModel(
            portName=port_name)

    # 2021-03-04新增识别目标判断的接口
    # 函数输入是路标名字，返回值是bool
    def car_camera_is_detected(self, sign_name):
        # 路标的名字缩写列表
        all_signs = [
            "lors", "l", "p", "apt", "rors", "r", "stop", "spm", "t", "u",
            "wh", "z"
        ]
        # 路标名字检查
        if sign_name in all_signs:
            dl_objs = self.get_car_camera_obj()
            if dl_objs["count"]:
                for one_obj in dl_objs["dl_obj"]:
                    _id = one_obj["id"]
                    if all_signs[_id] == sign_name:
                        return True
        else:
            # 输入路标名字拼写错误或者不存在这个名字的路标
            print("***Err: Wrong sign, please check your spelling!!!***")
        return False

    # 函数输入是被检测物品的名字，返回值是bool
    def arm_camera_is_detected(self, obj_name):
        all_objs = [["red", "yellow", "blue", "green"], ["apriltag"],
                    ["orange", "cabbage", "water", "dexp", "iexp", "cexp"]]
        # 是否检测到id号码为***的apriltag码
        r_model = self.get_arm_camera_model()["runModelIndex"]
        if r_model == 2:
            # print("***Input <<< an integer between 0~586 ***")
            try:
                int(obj_name)
            except Exception:
                print("***Apriltag id err: ID should be an integer !!!***")
                return False
            if 0 <= int(obj_name) <= 586:
                tag_all = self.get_arm_camera_tag()
                if tag_all["count"]:
                    for one_tag in tag_all["aptag_obj"]:
                        _id = one_tag["id"]
                        if _id == int(obj_name):
                            return True
                        else:
                            return False
                else:
                    return False
            else:
                print(
                    "***Apriltag id err: ID should be an integer bwtween 0~586 !!!***"
                )
                return False

        # 是否检测到某个物体
        _objs = all_objs[r_model - 1]
        # print("***Input should be a string in list --->"+str(_objs))
        if obj_name in _objs:
            dl_objs = self.get_arm_camera_obj()
            if dl_objs["count"]:
                for one_obj in dl_objs["dl_obj"]:
                    _id = one_obj["id"]
                    if _objs[_id] == obj_name:
                        return True
        else:
            print(
                "***Err: Wrong sign, please check your spelling and the running model!!!***"
            )
        return False
