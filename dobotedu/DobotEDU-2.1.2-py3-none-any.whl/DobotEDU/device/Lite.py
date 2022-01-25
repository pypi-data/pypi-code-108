from ..pause.pauselab import PauseLab, pause


class LiteApi(PauseLab):
    JOG = 0
    PTP = 1
    CP = 2
    ARC = 3

    def __init__(self, rpc_adapter, port_name=None):
        super().__init__()
        self.__dobotlink = rpc_adapter
        self._port_name = port_name

    def get_portname(func):
        def wrapper(self, *args, **kwargs):
            if self._port_name:
                return func(self, self._port_name, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)

        return wrapper

    def search_dobot(self):
        return self.__dobotlink.MagicianLite.SearchDobot()

    @get_portname
    @pause
    def connect_dobot(self, port_name, queue_start=True, is_queued=False):
        return self.__dobotlink.MagicianLite.ConnectDobot(
            portName=port_name, queueStart=queue_start, isQueued=is_queued)

    @get_portname
    @pause
    def disconnect_dobot(self,
                         port_name,
                         queue_stop=True,
                         queue_clear=True,
                         is_queued=False):
        return self.__dobotlink.MagicianLite.DisconnectDobot(
            portName=port_name,
            queueStop=queue_stop,
            queueClear=queue_clear,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_devicesn(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetDeviceSN(portName=port_name,
                                                         isQueued=is_queued)

    @get_portname
    @pause
    def set_devicename(self, port_name, device_name: str, is_queued=False):
        return self.__dobotlink.MagicianLite.SetDeviceName(
            portName=port_name, deviceName=device_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_devicename(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetDeviceName(portName=port_name,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def get_deviceversion(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetDeviceVersion(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_devicetime(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetDeviceTime(portName=port_name,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def get_deviceid(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetDeviceID(portName=port_name,
                                                         isQueued=is_queued)

    @get_portname
    @pause
    def get_productname(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetProductName(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_start(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.QueuedCmdStart(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_stop(self, port_name, force_stop=False, is_queued=False):
        return self.__dobotlink.MagicianLite.QueuedCmdStop(
            portName=port_name, forceStop=force_stop, isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_clear(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.QueuedCmdClear(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_startdownload(self,
                                port_name,
                                total_loop: int,
                                lineper_loop: int,
                                is_queued=False):
        return self.__dobotlink.MagicianLite.QueuedCmdStartDownload(
            portName=port_name,
            totalLoop=total_loop,
            linePerLoop=lineper_loop,
            isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_stopdownload(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.QueuedCmdStopDownload(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_queuedcmd_currentindex(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetQueuedCmdCurrentIndex(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_queuedcmd_leftspace(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetQueuedCmdLeftSpace(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_armspeed_ratio(self,
                           port_name,
                           set_type: int,
                           set_value: int,
                           is_queued=False):
        return self.__dobotlink.MagicianLite.SetArmSpeedRatio(
            portName=port_name,
            type=set_type,
            value=set_value,
            isQueued=is_queued)

    @get_portname
    @pause
    def set_arm_speed_ratio(self,
                            port_name,
                            mode,
                            speed_ratio,
                            is_queued=False):
        return self.__dobotlink.MagicianLite.SetArmSpeedRatio(
            portName=port_name,
            type=mode,
            value=speed_ratio,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_armspeed_ratio(self, port_name, get_type: int, is_queued=False):
        return self.__dobotlink.MagicianLite.GetArmSpeedRatio(
            portName=port_name, type=get_type, isQueued=is_queued)

    @get_portname
    @pause
    def get_arm_speed_ratio(self, port_name, mode, is_queued=False):
        res = self.__dobotlink.MagicianLite.GetArmSpeedRatio(
            portName=port_name, type=mode, isQueued=is_queued)
        return res["value"]

    @get_portname
    @pause
    def get_pose(self, port_name, is_queued=False):
        a = self.__dobotlink.MagicianLite.GetPose(portName=port_name,
                                                  isQueued=is_queued)
        for k, v in a.items():
            if type(v) == list:
                for i in range(len(v)):
                    a[k][i] = float(format(v[i], ".2f"))
            else:
                a[k] = float(format(v, ".2f"))
        return a

    @get_portname
    @pause
    def reset_pose(self,
                   port_name,
                   manual_enable: bool,
                   rear_armangle=None,
                   front_armangle=None,
                   is_queued=False):
        return self.__dobotlink.MagicianLite.ResetPose(
            portName=port_name,
            manualEnable=manual_enable,
            rearArmAngle=rear_armangle,
            frontArmAngle=front_armangle,
            isQueued=is_queued)

    @get_portname
    @pause
    def check_poselimit(self,
                        port_name,
                        is_joint: bool,
                        x: float,
                        y: float,
                        z: float,
                        r: float,
                        is_queued=False):
        return self.__dobotlink.MagicianLite.CheckPoseLimit(portName=port_name,
                                                            isJoint=is_joint,
                                                            x=x,
                                                            y=y,
                                                            z=z,
                                                            r=r,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def get_alarms_state(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetAlarmsState(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def get_lost_step_result(self, port_name, is_queued=False):
        res = self.__dobotlink.MagicianLite.GetAlarmsState(portName=port_name,
                                                           isQueued=is_queued)
        return res["state"]

    @get_portname
    @pause
    def clear_allalarms_state(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.ClearAllAlarmsState(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def clean_alarm(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.ClearAllAlarmsState(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_homeparams(self,
                       port_name,
                       x: float,
                       y: float,
                       z: float,
                       r: float,
                       is_queued=False):
        return self.__dobotlink.MagicianLite.SetHOMEParams(portName=port_name,
                                                           x=x,
                                                           y=y,
                                                           z=z,
                                                           r=r,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def get_homeparams(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetHOMEParams(portName=port_name,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def set_homecmd(self,
                    port_name,
                    is_wait=True,
                    time_out=86400000,
                    is_queued=True):
        self.__dobotlink.MagicBox.SetHOMECmd(portName=port_name,
                                             isQueued=is_queued,
                                             isWaitForFinish=is_wait,
                                             timeout=time_out)
        return self.__dobotlink.MagicianLite.SetHOMECmd(
            portName=port_name,
            isQueued=is_queued,
            isWaitForFinish=is_wait,
            timeout=time_out)

    @get_portname
    @pause
    def set_endeffector_params(self,
                               port_name,
                               x_offset: float,
                               y_offset: float,
                               z_offset: float,
                               is_queued=False):
        return self.__dobotlink.MagicianLite.SetEndEffectorParams(
            portName=port_name,
            xOffset=x_offset,
            yOffset=y_offset,
            zOffset=z_offset,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetEndEffectorParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_end_effector_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetEndEffectorParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_type(self, port_name, set_type: int, is_queued=False):
        return self.__dobotlink.MagicianLite.SetEndEffectorType(
            portName=port_name, type=set_type, isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_type(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetEndEffectorType(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_end_effector_type(self, port_name, is_queued=False):
        res = self.__dobotlink.MagicianLite.GetEndEffectorType(
            portName=port_name, isQueued=is_queued)
        return res["type"]

    @get_portname
    @pause
    def set_endeffector_suctioncup(self,
                                   port_name,
                                   enable: bool,
                                   on: bool,
                                   is_queued=False):
        return self.__dobotlink.MagicianLite.SetEndEffectorSuctionCup(
            portName=port_name, enable=enable, on=on, isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_suctioncup(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetEndEffectorSuctionCup(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_gripper(self,
                                port_name,
                                enable: bool,
                                on: bool,
                                is_queued=False):
        return self.__dobotlink.MagicianLite.SetEndEffectorGripper(
            portName=port_name, enable=enable, on=on, isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_gripper(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetEndEffectorGripper(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_jogjoint_params(self,
                            port_name,
                            velocity,
                            acceleration,
                            is_queued=False):
        return self.__dobotlink.MagicianLite.SetJOGJointParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogjoint_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetJOGJointParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_jogcoordinate_params(self,
                                 port_name,
                                 velocity,
                                 acceleration,
                                 is_queued=False):
        return self.__dobotlink.MagicianLite.SetJOGCoordinateParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogcoordinate_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetJOGCoordinateParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_jogcommon_params(self,
                             port_name,
                             velocity_ratio: float,
                             acceleration_ratio: float,
                             is_queued=False):
        return self.__dobotlink.MagicianLite.SetJOGCommonParams(
            portName=port_name,
            velocityRatio=velocity_ratio,
            accelerationRatio=acceleration_ratio,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogcommon_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetJOGCommonParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_jogcmd(self, port_name, is_joint: bool, cmd: int, is_queued=True):
        return self.__dobotlink.MagicianLite.SetJOGCmd(portName=port_name,
                                                       isJoint=is_joint,
                                                       cmd=cmd,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpcmd(self,
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
    @pause
    def set_rcmd(self,
                 port_name,
                 r: int,
                 is_queued=True,
                 is_wait=True,
                 time_out=5000):
        return self.__dobotlink.MagicianLite.SetRCmd(portName=port_name,
                                                     r=r,
                                                     isQueued=is_queued,
                                                     isWaitForFinish=is_wait,
                                                     timeout=time_out)

    @get_portname
    @pause
    def set_ptpjoint_param(self,
                           port_name,
                           velocity,
                           acceleration,
                           is_queued=False):
        return self.__dobotlink.MagicianLite.SetPTPJointParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpjoint_param(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetPTPJointParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpcoordinate_params(self,
                                 port_name,
                                 xyz_velocity: float,
                                 r_velocity: float,
                                 xyz_acceleration: float,
                                 r_acceleration: float,
                                 is_queued=False):
        return self.__dobotlink.MagicianLite.SetPTPCoordinateParams(
            portName=port_name,
            xyzVelocity=xyz_velocity,
            rVelocity=r_velocity,
            xyzAcceleration=xyz_acceleration,
            rAcceleration=r_acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpcoordinate_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetPTPCoordinateParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpjump_params(self,
                           port_name,
                           z_limit: float,
                           jump_height: float,
                           is_queued=False):
        return self.__dobotlink.MagicianLite.SetPTPJumpParams(
            portName=port_name,
            zLimit=z_limit,
            jumpHeight=jump_height,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpjump_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetPTPJumpParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpcommon_params(self,
                             port_name,
                             velocity_ratio: float,
                             acceleration_ratio: float,
                             is_queued=False):
        return self.__dobotlink.MagicianLite.SetPTPCommonParams(
            portName=port_name,
            velocityRatio=velocity_ratio,
            accelerationRatio=acceleration_ratio,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpcommon_params(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetPTPCommonParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_loststep_value(self, port_name, value):
        return self.__dobotlink.MagicianLite.SetLostStepValue(
            portName=port_name, value=value)

    @get_portname
    @pause
    def set_lost_step_params(self, port_name, value):
        return self.__dobotlink.MagicianLite.SetLostStepValue(
            portName=port_name, value=value)

    @get_portname
    @pause
    def set_loststep_cmd(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.SetLostStepCmd(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def set_lost_step_cmd(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.SetLostStepCmd(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def set_collision_check(self,
                            port_name,
                            enable: bool,
                            thre_shold: float,
                            is_queued=False):
        return self.__dobotlink.MagicianLite.SetCollisionCheck(
            portName=port_name,
            enable=enable,
            threshold=thre_shold,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_collision_check(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetCollisionCheck(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_cpparams(self,
                     port_name,
                     target_acc: float,
                     junction_vel: float,
                     isreal_timetrack: bool,
                     acc=None,
                     period=None,
                     is_queued=False):
        return self.__dobotlink.MagicianLite.SetCPParams(
            portName=port_name,
            targetAcc=target_acc,
            junctionVel=junction_vel,
            isRealTimeTrack=isreal_timetrack,
            acc=acc,
            period=period,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_cpparams(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetCPParams(portName=port_name,
                                                         isQueued=is_queued)

    @get_portname
    @pause
    def set_cpcmd(self,
                  port_name,
                  cp_mode: int,
                  x: float,
                  y: float,
                  z: float,
                  power: float,
                  is_queued=True,
                  is_wait_for_finish=True):
        return self.__dobotlink.MagicianLite.SetCPCmd(
            portName=port_name,
            cpMode=cp_mode,
            x=x,
            y=y,
            z=z,
            power=power,
            isQueued=is_queued,
            isWaitForFinish=is_wait_for_finish,
            timeout=86400000)

    @get_portname
    @pause
    def set_cplecmd(self,
                    port_name,
                    cp_mode: int,
                    x: float,
                    y: float,
                    z: float,
                    power: float,
                    is_queued=True):
        return self.__dobotlink.MagicianLite.SetCPLECmd(portName=port_name,
                                                        cpMode=cp_mode,
                                                        x=x,
                                                        y=y,
                                                        z=z,
                                                        power=power,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def set_arcparams(self,
                      port_name,
                      xyz_velocity: float,
                      r_velocity: float,
                      xyz_acceleration: float,
                      r_acceleration: float,
                      is_queued=False):
        return self.__dobotlink.MagicianLite.SetARCParams(
            portName=port_name,
            xyzVelocity=xyz_velocity,
            rVelocity=r_velocity,
            xyzAcceleration=xyz_acceleration,
            rAcceleration=r_acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_arcparams(self, port_name, is_queued=False):
        return self.__dobotlink.MagicianLite.GetARCParams(portName=port_name,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_arccmd(self, port_name, cir_point, to_point, is_queued=True):
        return self.__dobotlink.MagicianLite.SetARCCmd(portName=port_name,
                                                       cirPoint=cir_point,
                                                       toPoint=to_point,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def wait(self, port_name, delay):
        return self.__dobotlink.MagicianLite.SetWAITCmd(portName=port_name,
                                                        delay=delay * 1000,
                                                        timeout=604800000)

    @get_portname
    @pause
    def queuedcmd_left_space(self, port_name):
        res = self.__dobotlink.MagicianLite.GetQueuedCmdLeftSpace(
            portName=port_name)
        return res["leftSpace"]
