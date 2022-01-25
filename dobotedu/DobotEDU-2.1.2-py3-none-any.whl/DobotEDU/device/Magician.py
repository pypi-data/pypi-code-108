from ..pause.pauselab import PauseLab, pause


class MagicianApi(PauseLab):
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
            self.on_pause()
            if self._port_name:
                return func(self, self._port_name, *args, **kwargs)
            else:
                return func(self, *args, **kwargs)

        return wrapper

    def search_dobot(self):
        return self.__dobotlink.Magician.SearchDobot()

    @get_portname
    @pause
    def connect_dobot(self, port_name, queue_start=True, is_queued=False):
        return self.__dobotlink.Magician.ConnectDobot(portName=port_name,
                                                      queueStart=queue_start,
                                                      isQueued=is_queued)

    @get_portname
    @pause
    def disconnect_dobot(self,
                         port_name,
                         queue_stop=True,
                         queue_clear=True,
                         is_queued=False):
        return self.__dobotlink.Magician.DisconnectDobot(
            portName=port_name,
            queueStop=queue_stop,
            queueClear=queue_clear,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_devicesn(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetDeviceSN(portName=port_name,
                                                     isQueued=is_queued)

    @get_portname
    @pause
    def set_devicename(self, port_name, device_name: str, is_queued=False):
        return self.__dobotlink.Magician.SetDeviceName(portName=port_name,
                                                       deviceName=device_name,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def get_devicename(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetDeviceName(portName=port_name,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def get_deviceversion(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetDeviceVersion(portName=port_name,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_device_withl(self,
                         port_name,
                         enable=True,
                         version=1,
                         is_queued=False):
        return self.__dobotlink.Magician.SetDeviceWithL(portName=port_name,
                                                        enable=enable,
                                                        version=version,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_device_withl(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetDeviceWithL(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_devicetime(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetDeviceTime(portName=port_name,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def get_deviceid(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetDeviceID(portName=port_name,
                                                     isQueued=is_queued)

    @get_portname
    @pause
    def get_productname(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetProductName(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_start(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.QueuedCmdStart(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_stop(self, port_name, force_stop=False, is_queued=False):
        return self.__dobotlink.Magician.QueuedCmdStop(portName=port_name,
                                                       forceStop=force_stop,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_clear(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.QueuedCmdClear(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_startdownload(self,
                                port_name,
                                total_loop: int,
                                lineper_loop: int,
                                is_queued=False):
        return self.__dobotlink.Magician.QueuedCmdStartDownload(
            portName=port_name,
            totalLoop=total_loop,
            linePerLoop=lineper_loop,
            isQueued=is_queued)

    @get_portname
    @pause
    def queuedcmd_stopdownload(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.QueuedCmdStopDownload(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_queuedcmd_currentindex(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetQueuedCmdCurrentIndex(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_queuedcmd_leftspace(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetQueuedCmdLeftSpace(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_armspeed_ratio(self,
                           port_name,
                           set_type: int,
                           set_value: int,
                           is_queued=False):
        return self.__dobotlink.Magician.SetArmSpeedRatio(portName=port_name,
                                                          type=set_type,
                                                          value=set_value,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def get_armspeed_ratio(self, port_name, get_type: int, is_queued=False):
        return self.__dobotlink.Magician.GetArmSpeedRatio(portName=port_name,
                                                          type=get_type,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_arm_speed_ratio(self,
                            port_name,
                            set_type: int,
                            set_value: int,
                            is_queued=False):
        return self.__dobotlink.Magician.SetArmSpeedRatio(portName=port_name,
                                                          type=set_type,
                                                          value=set_value,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def get_arm_speed_ratio(self, port_name, mode, is_queued=False):
        res = self.__dobotlink.Magician.GetArmSpeedRatio(portName=port_name,
                                                         type=mode,
                                                         isQueued=is_queued)
        return res["value"]

    @get_portname
    @pause
    def set_servoangle(self,
                       port_name,
                       index: int,
                       set_value: float,
                       is_queued=False):
        return self.__dobotlink.Magician.SetServoAngle(portName=port_name,
                                                       index=index,
                                                       value=set_value,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def get_servoangle(self, port_name, index: int, is_queued=False):
        return self.__dobotlink.Magician.GetServoAngle(portName=port_name,
                                                       index=index,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def set_lspeed_ratio(self,
                         port_name,
                         set_type: int,
                         set_value: int,
                         is_queued=False):
        return self.__dobotlink.Magician.SetLSpeedRatio(portName=port_name,
                                                        type=set_type,
                                                        value=set_value,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_lspeed_ratio(self, port_name, get_type: int, is_queued=False):
        return self.__dobotlink.Magician.GetLSpeedRatio(portName=port_name,
                                                        type=get_type,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_pose(self, port_name, is_queued=False):
        a = self.__dobotlink.Magician.GetPose(portName=port_name,
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
        return self.__dobotlink.Magician.ResetPose(
            portName=port_name,
            manualEnable=manual_enable,
            rearArmAngle=rear_armangle,
            frontArmAngle=front_armangle,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_posel(self, port_name, is_queued=False):
        res = self.__dobotlink.Magician.GetPoseL(portName=port_name,
                                                 isQueued=is_queued)
        return {"positionL": float(format(res["positionL"], ".2f"))}

    @get_portname
    @pause
    def get_alarms_state(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetAlarmsState(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_lost_step_result(self, port_name, is_queued=False):
        res = self.__dobotlink.Magician.GetAlarmsState(portName=port_name,
                                                       isQueued=is_queued)
        return res["state"]

    @get_portname
    @pause
    def clear_allalarms_state(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.ClearAllAlarmsState(
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
        return self.__dobotlink.Magician.SetHOMEParams(portName=port_name,
                                                       x=x,
                                                       y=y,
                                                       z=z,
                                                       r=r,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def get_homeparams(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetHOMEParams(portName=port_name,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def set_homecmd(self,
                    port_name,
                    is_queued=True,
                    is_wait=True,
                    time_out=86400000):
        return self.__dobotlink.Magician.SetHOMECmd(portName=port_name,
                                                    isQueued=is_queued,
                                                    isWaitForFinish=is_wait,
                                                    timeout=time_out)

    @get_portname
    @pause
    def set_autoleveling(self,
                         port_name,
                         enable: bool,
                         precision: float,
                         is_queued=False):
        return self.__dobotlink.Magician.SetAutoLeveling(portName=port_name,
                                                         enable=enable,
                                                         precision=precision,
                                                         isQueued=is_queued)

    @get_portname
    @pause
    def get_autoleveling(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetAutoLeveling(portName=port_name,
                                                         isQueued=is_queued)

    @get_portname
    @pause
    def set_hhttrig_mode(self, port_name, mode: int, is_queued=False):
        return self.__dobotlink.Magician.SetHHTTrigMode(portName=port_name,
                                                        mode=mode,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_hhttrig_mode(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetHHTTrigMode(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def set_hhttrig_output_enabled(self,
                                   port_name,
                                   enable: bool,
                                   is_queued=False):
        return self.__dobotlink.Magician.SetHHTTrigOutputEnabled(
            portName=port_name, enable=enable, isQueued=is_queued)

    @get_portname
    @pause
    def get_hhttrig_output_enabled(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetHHTTrigOutputEnabled(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def get_hhttrig_output(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetHHTTrigOutput(portName=port_name,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_params(self,
                               port_name,
                               x_offset: float,
                               y_offset: float,
                               z_offset: float,
                               is_queued=False):
        return self.__dobotlink.Magician.SetEndEffectorParams(
            portName=port_name,
            xOffset=x_offset,
            yOffset=y_offset,
            zOffset=z_offset,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetEndEffectorParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_type(self, port_name, set_type: int, is_queued=False):
        return self.__dobotlink.Magician.SetEndEffectorType(portName=port_name,
                                                            type=set_type,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_type(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetEndEffectorType(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_laser(self,
                              port_name,
                              enable: bool,
                              on: bool,
                              is_queued=False):
        return self.__dobotlink.Magician.SetEndEffectorLaser(
            portName=port_name, enable=enable, on=on, isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_laser(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetEndEffectorLaser(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_suctioncup(self,
                                   port_name,
                                   enable: bool,
                                   on: bool,
                                   is_queued=False):
        return self.__dobotlink.Magician.SetEndEffectorSuctionCup(
            portName=port_name, enable=enable, on=on, isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_suctioncup(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetEndEffectorSuctionCup(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_endeffector_gripper(self,
                                port_name,
                                enable: bool,
                                on: bool,
                                is_queued=False):
        return self.__dobotlink.Magician.SetEndEffectorGripper(
            portName=port_name, enable=enable, on=on, isQueued=is_queued)

    @get_portname
    @pause
    def get_endeffector_gripper(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetEndEffectorGripper(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_jogjoint_params(self,
                            port_name,
                            velocity,
                            acceleration,
                            is_queued=False):
        return self.__dobotlink.Magician.SetJOGJointParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogjoint_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetJOGJointParams(portName=port_name,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def set_jogcoordinate_params(self,
                                 port_name,
                                 velocity,
                                 acceleration,
                                 is_queued=False):
        return self.__dobotlink.Magician.SetJOGCoordinateParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogcoordinate_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetJOGCoordinateParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_jogcommon_params(self,
                             port_name,
                             velocity_ratio: float,
                             acceleration_ratio: float,
                             is_queued=False):
        return self.__dobotlink.Magician.SetJOGCommonParams(
            portName=port_name,
            velocityRatio=velocity_ratio,
            accelerationRatio=acceleration_ratio,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogcommon_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetJOGCommonParams(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def set_jogl_params(self,
                        port_name,
                        velocity,
                        acceleration,
                        is_queued=False):
        return self.__dobotlink.Magician.SetJOGLParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_jogl_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetJOGLParams(portName=port_name,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def set_jogcmd(self, port_name, is_joint: bool, cmd: int, is_queued):
        return self.__dobotlink.Magician.SetJOGCmd(portName=port_name,
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
        return self.__dobotlink.Magician.SetPTPCmd(portName=port_name,
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
    def set_ptppocmd(self,
                     port_name,
                     ptp_cmd,
                     po_cmd,
                     is_queued=True,
                     is_wait=True):
        return self.__dobotlink.Magician.SetPTPPOCmd(portName=port_name,
                                                     ptpCmd=ptp_cmd,
                                                     poCmd=po_cmd,
                                                     isQueued=is_queued,
                                                     isWaitForFinish=is_wait,
                                                     timeout=86400000)

    @get_portname
    @pause
    def set_ptppo_withlcmd(self,
                           port_name,
                           ptp_cmd,
                           po_cmd,
                           is_queued=True,
                           is_wait=True):
        return self.__dobotlink.Magician.SetPTPPOWithLCmd(
            portName=port_name,
            ptpCmd=ptp_cmd,
            poCmd=po_cmd,
            isQueued=is_queued,
            isWaitForFinish=is_wait,
            timeout=86400000)

    @get_portname
    @pause
    def set_rcmd(self,
                 port_name,
                 r,
                 is_queued=True,
                 is_wait=True,
                 time_out=86400000):
        return self.__dobotlink.Magician.SetRCmd(portName=port_name,
                                                 r=r,
                                                 isQueued=is_queued,
                                                 isWaitForFinish=is_wait,
                                                 timeout=time_out)

    @get_portname
    @pause
    def set_ptpwithl_cmd(self,
                         port_name,
                         mode: int,
                         x: float,
                         y: float,
                         z: float,
                         r: float,
                         set_l: float,
                         is_queued=True,
                         is_wait=True):
        return self.__dobotlink.Magician.SetPTPWithLCmd(
            portName=port_name,
            ptpMode=mode,
            x=x,
            y=y,
            z=z,
            r=r,
            l=set_l,
            isQueued=is_queued,
            isWaitForFinish=is_wait,
            timeout=86400000)

    @get_portname
    @pause
    def set_ptpjoint_param(self,
                           port_name,
                           velocity,
                           acceleration,
                           is_queued=False):
        return self.__dobotlink.Magician.SetPTPJointParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpjoint_param(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetPTPJointParams(portName=port_name,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpcoordinate_params(self,
                                 port_name,
                                 xyz_velocity: float,
                                 r_velocity: float,
                                 xyz_acceleration: float,
                                 r_acceleration: float,
                                 is_queued=False):
        return self.__dobotlink.Magician.SetPTPCoordinateParams(
            portName=port_name,
            xyzVelocity=xyz_velocity,
            rVelocity=r_velocity,
            xyzAcceleration=xyz_acceleration,
            rAcceleration=r_acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpcoordinate_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetPTPCoordinateParams(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpjump_params(self,
                           port_name,
                           z_limit: float,
                           jump_height: float,
                           is_queued=False):
        return self.__dobotlink.Magician.SetPTPJumpParams(
            portName=port_name,
            zLimit=z_limit,
            jumpHeight=jump_height,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpjump_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetPTPJumpParams(portName=port_name,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpcommon_params(self,
                             port_name,
                             vel: float,
                             acc: float,
                             is_queued=False):
        return self.__dobotlink.Magician.SetPTPCommonParams(
            portName=port_name,
            velocityRatio=vel,
            accelerationRatio=acc,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpcommon_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetPTPCommonParams(portName=port_name,
                                                            isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpl_params(self,
                        port_name,
                        velocity,
                        acceleration,
                        is_queued=False):
        return self.__dobotlink.Magician.SetPTPLParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpl_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetPTPLParams(portName=port_name,
                                                       isQueued=is_queued)

    @get_portname
    @pause
    def set_ptpjump2_params(self,
                            port_name,
                            z_limit,
                            start_jump_height,
                            end_jump_height,
                            is_queued=False):
        return self.__dobotlink.Magician.SetPTPJump2Params(
            portName=port_name,
            zLimit=z_limit,
            startJumpHeight=start_jump_height,
            endJumpHeight=end_jump_height,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_ptpjump2_params(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetPTPJump2Params(portName=port_name,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def set_iomultiplexing(self,
                           port_name,
                           port: int,
                           multiplex: int,
                           is_queued=False):
        return self.__dobotlink.Magician.SetIOMultiplexing(portName=port_name,
                                                           port=port,
                                                           multiplex=multiplex,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def get_iomultiplexing(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.Magician.GetIOMultiplexing(portName=port_name,
                                                           port=port,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def set_iodo(self, port_name, port: int, level: int, is_queued=False):
        return self.__dobotlink.Magician.SetIODO(portName=port_name,
                                                 port=port,
                                                 level=level,
                                                 isQueued=is_queued)

    @get_portname
    @pause
    def get_iodo(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.Magician.GetIODO(portName=port_name,
                                                 port=port,
                                                 isQueued=is_queued)

    @get_portname
    @pause
    def set_iopwm(self,
                  port_name,
                  port: int,
                  frequency: float,
                  duty_cycle: float,
                  is_queued=False):
        return self.__dobotlink.Magician.SetIOPWM(portName=port_name,
                                                  port=port,
                                                  frequency=frequency,
                                                  dutyCycle=duty_cycle,
                                                  isQueued=is_queued)

    @get_portname
    @pause
    def get_iopwm(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.Magician.GetIOPWM(portName=port_name,
                                                  port=port,
                                                  isQueued=is_queued)

    @get_portname
    @pause
    def get_iodi(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.Magician.GetIODI(portName=port_name,
                                                 port=port,
                                                 isQueued=is_queued)

    @get_portname
    @pause
    def get_ioadc(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.Magician.GetIOADC(portName=port_name,
                                                  port=port,
                                                  isQueued=is_queued)

    @get_portname
    @pause
    def set_emotor(self,
                   port_name,
                   index: int,
                   enable: bool,
                   speed,
                   is_queued=False):
        return self.__dobotlink.Magician.SetEMotor(portName=port_name,
                                                   index=index,
                                                   enable=enable,
                                                   speed=speed,
                                                   isQueued=is_queued)

    @get_portname
    @pause
    def set_emotors(self,
                    port_name,
                    index: int,
                    enable: bool,
                    speed,
                    distance,
                    is_queued=False):
        return self.__dobotlink.Magician.SetEMotorS(portName=port_name,
                                                    index=index,
                                                    enable=enable,
                                                    speed=speed,
                                                    distance=distance,
                                                    isQueued=is_queued)

    @get_portname
    @pause
    def set_color_sensor(self,
                         port_name,
                         port: int,
                         enable: bool,
                         version: int,
                         is_queued=False):
        return self.__dobotlink.Magician.SetColorSensor(portName=port_name,
                                                        port=port - 1,
                                                        enable=enable,
                                                        version=version,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def get_color_sensor(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetColorSensor(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def set_infrared_sensor(self,
                            port_name,
                            port: int,
                            enable: bool,
                            version: int,
                            is_queued=False):
        return self.__dobotlink.Magician.SetInfraredSensor(portName=port_name,
                                                           port=port - 1,
                                                           enable=enable,
                                                           version=version,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def get_infrared_sensor(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.Magician.GetInfraredSensor(portName=port_name,
                                                           port=port - 1,
                                                           isQueued=is_queued)

    @get_portname
    @pause
    def set_loststep_value(self, port_name, value, is_queued=False):
        return self.__dobotlink.Magician.SetLostStepValue(portName=port_name,
                                                          value=value,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_lost_step_params(self, port_name, value, is_queued=False):
        return self.__dobotlink.Magician.SetLostStepValue(portName=port_name,
                                                          value=value,
                                                          isQueued=is_queued)

    @get_portname
    @pause
    def set_loststep_cmd(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.SetLostStepCmd(portName=port_name,
                                                        isQueued=is_queued)

    @get_portname
    @pause
    def set_lost_step_cmd(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.SetLostStepCmd(portName=port_name,
                                                        isQueued=is_queued)

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
        return self.__dobotlink.Magician.SetCPParams(
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
        return self.__dobotlink.Magician.GetCPParams(portName=port_name,
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
        return self.__dobotlink.Magician.SetCPCmd(
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
                    is_queued=False,
                    is_wait_for_finish=True):
        return self.__dobotlink.Magician.SetCPLECmd(
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
    def set_arcparams(self,
                      port_name,
                      xyz_velocity: float,
                      r_velocity: float,
                      xyz_acceleration: float,
                      r_acceleration: float,
                      is_queued=False):
        return self.__dobotlink.Magician.SetARCParams(
            portName=port_name,
            xyzVelocity=xyz_velocity,
            rVelocity=r_velocity,
            xyzAcceleration=xyz_acceleration,
            rAcceleration=r_acceleration,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_arcparams(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetARCParams(portName=port_name,
                                                      isQueued=is_queued)

    @get_portname
    @pause
    def set_arccmd(self, port_name, cir_point, to_point, is_queued=False):
        return self.__dobotlink.Magician.SetARCCmd(portName=port_name,
                                                   cirPoint=cir_point,
                                                   toPoint=to_point,
                                                   isQueued=is_queued,
                                                   timeout=86400000)

    @get_portname
    @pause
    def set_anglesensorstatic_error(self,
                                    port_name,
                                    rear_armangle_error,
                                    front_armangle_error,
                                    is_queued=False):
        return self.__dobotlink.Magician.SetAngleSensorStaticError(
            portName=port_name,
            rearArmAngleError=rear_armangle_error,
            frontArmAngleError=front_armangle_error,
            isQueued=is_queued)

    @get_portname
    @pause
    def get_anglesensorstatic_error(self, port_name, is_queued=False):
        return self.__dobotlink.Magician.GetAngleSensorStaticError(
            portName=port_name, isQueued=is_queued)

    @get_portname
    @pause
    def set_waitcmd(self, port_name, delay):
        return self.__dobotlink.Magician.SetWAITCmd(portName=port_name,
                                                    delay=delay,
                                                    timeout=delay + 500)

    @get_portname
    @pause
    def set_rccmd(self, port_name, r):
        return self.__dobotlink.Magician.SetRCmd(portName=port_name,
                                                 r=r,
                                                 timeout=86400000)

    @get_portname
    @pause
    def queuedcmd_left_space(self, port_name):
        res = self.__dobotlink.Magician.GetQueuedCmdLeftSpace(
            portName=port_name)
        return res["leftSpace"]
