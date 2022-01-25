from ..pause.pauselab import PauseLab, pause


class MagicianGoApi(PauseLab):
    def __init__(self, rpc_adapter, port_name=None):
        super().__init__()
        self.__dobotlink = rpc_adapter
        self._port_name = port_name
        self.rgb_number = {
            "LED_1": 1,
            "LED_2": 2,
            "LED_3": 3,
            "LED_4": 4,
            "LED_ALL": 5
        }

    def get_portname(func):
        def wrapper(self, *args, **kwargs):
            self.on_pause()
            if self._port_name:
                return func(self, self._port_name, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)

        return wrapper

    @get_portname
    @pause
    def set_running_mode(self, port_name, mode):
        return self.__dobotlink.MagicianGO.SetRunningMode(portName=port_name,
                                                          runningMode=mode)

    @get_portname
    @pause
    def set_move_speed_direct(self, port_name, direction, speed):
        return self.__dobotlink.MagicianGO.SetMoveSpeedDirect(
            portName=port_name, dir=direction, speed=speed)

    @get_portname
    @pause
    def set_move_speed(self, port_name, x, y, r):
        return self.__dobotlink.MagicianGO.SetMoveSpeed(portName=port_name,
                                                        x=x,
                                                        y=y,
                                                        r=r)

    @get_portname
    @pause
    def set_rotate(self, port_name, r, Vr):
        return self.__dobotlink.MagicianGO.SetRotate(portName=port_name,
                                                     r=r,
                                                     Vr=Vr,
                                                     isQueued=True,
                                                     isWaitForFinish=True,
                                                     timeout=604800000)

    @get_portname
    @pause
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
    @pause
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
    @pause
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
    @pause
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
    @pause
    def set_coord_closed_loop(self, port_name, isEnable, angle):
        return self.__dobotlink.MagicianGO.SetCoordClosedLoop(
            portName=port_name, isEnable=isEnable, angle=angle)

    @get_portname
    @pause
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
    @pause
    def set_rgb_light(self, port_name, number, effect, r, g, b, cycle, counts):
        if type(number) == str:
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
    @pause
    def set_buzzer_sound(self, port_name, index, tone, beat):
        return self.__dobotlink.MagicianGO.SetBuzzerSound(portName=port_name,
                                                          index=index,
                                                          tone=tone,
                                                          beat=beat)

    @get_portname
    @pause
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
    @pause
    def set_odometer_data(self, port_name, x, y, yaw):
        return self.__dobotlink.MagicianGO.SetSpeedometer(portName=port_name,
                                                          x=x,
                                                          y=y,
                                                          yaw=yaw)

    @get_portname
    @pause
    def get_odometer_data(self, port_name):
        o_data = self.__dobotlink.MagicianGO.GetSpeedometer(portName=port_name)
        o_res = {
            "x": float(format(o_data["x"], ".2f")),
            "y": float(format(o_data["y"], ".2f")),
            "yaw": float(format(o_data["yaw"], ".2f"))
        }
        return o_res

    @get_portname
    @pause
    def get_power_voltage(self, port_name):
        v_data = self.__dobotlink.MagicianGO.GetBatteryVoltage(
            portName=port_name)
        v_res = {
            "powerVoltage": float(format(v_data["powerVoltage"], ".2f")),
            "powerPercentage": float(format(v_data["powerPercentage"], ".2f"))
        }
        return v_res

    @get_portname
    @pause
    def get_imu_angle(self, port_name):
        a_data = self.__dobotlink.MagicianGO.GetImuAngle(portName=port_name)
        a_res = {
            "yaw": float(format(a_data["yaw"], ".2f")),
            "roll": float(format(a_data["roll"], ".2f")),
            "pitch": float(format(a_data["pitch"], ".2f"))
        }
        return a_res

    @get_portname
    @pause
    def get_imu_speed(self, port_name):
        s_data = self.__dobotlink.MagicianGO.GetImuSpeed(portName=port_name)
        s_res = {
            "ax": float(format(s_data["ax"], ".2f")),
            "ay": float(format(s_data["ay"], ".2f")),
            "az": float(format(s_data["az"], ".2f")),
            "gx": float(format(s_data["gx"], ".2f")),
            "gy": float(format(s_data["gy"], ".2f")),
            "gz": float(format(s_data["gz"], ".2f"))
        }
        return s_res

    @get_portname
    @pause
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
    @pause
    def set_trace_speed(self, port_name, speed):
        return self.__dobotlink.MagicianGO.SetTraceSpeed(portName=port_name,
                                                         speed=speed)

    @get_portname
    @pause
    def set_trace_pid(self, port_name, p, i, d):
        return self.__dobotlink.MagicianGO.SetTracePid(portName=port_name,
                                                       p=p,
                                                       i=i,
                                                       d=d)

    @get_portname
    @pause
    def get_trace_angle(self, port_name):
        an_data = self.__dobotlink.MagicianGO.GetCarCameraAngle(
            portName=port_name)
        an_res = {"angle": float(format(an_data["angle"], ".2f"))}
        return an_res

    @get_portname
    @pause
    def get_arm_camera_obj(self, port_name):
        return self.__dobotlink.MagicianGO.GetArmCameraObj(portName=port_name)

    @get_portname
    @pause
    def get_car_camera_obj(self, port_name):
        return self.__dobotlink.MagicianGO.GetCarCameraObj(portName=port_name)

    @get_portname
    @pause
    def get_arm_camera_tag(self, port_name):
        return self.__dobotlink.MagicianGO.GetArmCameraTag(portName=port_name)
