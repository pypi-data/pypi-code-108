from DobotRPC import DobotlinkAdapter, RPCClient


class M1Api(object):
    def __init__(self):
        self.__dobotlink = DobotlinkAdapter(RPCClient(), is_sync=True)

    def search_dobot(self):
        return self.__dobotlink.M1.SearchDobot()

    def connect_dobot(self, port_name, queue_start=True, is_queued=False):
        return self.__dobotlink.M1.ConnectDobot(portName=port_name,
                                                queueStart=queue_start,
                                                isQueued=is_queued)

    def disconnect_dobot(self,
                         port_name,
                         queue_stop=True,
                         queue_clear=True,
                         is_queued=False):
        return self.__dobotlink.M1.DisconnectDobot(portName=port_name,
                                                   queueStop=queue_stop,
                                                   queueClear=queue_clear,
                                                   isQueued=is_queued)

    def get_devicesn(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetDeviceSN(portName=port_name,
                                               isQueued=is_queued)

    def set_devicename(self, port_name, device_name: str, is_queued=False):
        return self.__dobotlink.M1.SetDeviceName(portName=port_name,
                                                 deviceName=device_name,
                                                 isQueued=is_queued)

    def get_devicename(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetDeviceName(portName=port_name,
                                                 isQueued=is_queued)

    def get_deviceversion(self, port_name, get_type: int, is_queued=False):
        return self.__dobotlink.M1.GetDeviceVersion(portName=port_name,
                                                    type=get_type,
                                                    isQueued=is_queued)

    def get_hardware_version(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetHardwareVersion(portName=port_name,
                                                      isQueued=is_queued)

    def queuedcmd_start(self, port_name, is_queued=False):
        return self.__dobotlink.M1.QueuedCmdStart(portName=port_name,
                                                  isQueued=is_queued)

    def queuedcmd_stop(self, port_name, force_stop=False, is_queued=False):
        return self.__dobotlink.M1.QueuedCmdStop(portName=port_name,
                                                 forceStop=force_stop,
                                                 isQueued=is_queued)

    def queuedcmd_clear(self, port_name, is_queued=False):
        return self.__dobotlink.M1.QueuedCmdClear(portName=port_name,
                                                  isQueued=is_queued)

    def queuedcmd_startdownload(self,
                                port_name,
                                total_loop: int,
                                lineper_loop: int,
                                is_queued=False):
        return self.__dobotlink.M1.QueuedCmdStartDownload(
            portName=port_name,
            totalLoop=total_loop,
            linePerLoop=lineper_loop,
            isQueued=is_queued)

    def queuedcmd_stopdownload(self, port_name, is_queued=False):
        return self.__dobotlink.M1.QueuedCmdStopDownload(portName=port_name,
                                                         isQueued=is_queued)

    def get_queuedcmd_currentindex(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetQueuedCmdCurrentIndex(portName=port_name,
                                                            isQueued=is_queued)

    def get_queuedcmd_leftspace(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetQueuedCmdLeftSpace(portName=port_name,
                                                         isQueued=is_queued)

    def get_pose(self, port_name, is_queued=False):
        a = self.__dobotlink.M1.GetPose(portName=port_name, isQueued=is_queued)
        for k, v in a.items():
            if type(v) == list:
                for i in range(len(v)):
                    a[k][i] = float(format(v[i], ".2f"))
            else:
                a[k] = float(format(v, ".2f"))
        return a

    def reset_pose(self,
                   port_name,
                   front_angle1: float,
                   front_angle2: float,
                   is_queued=False):
        return self.__dobotlink.M1.ResetPose(portName=port_name,
                                             frontAngle1=front_angle1,
                                             frontAngle2=front_angle2,
                                             isQueued=is_queued)

    def set_usercoordinate(self,
                           port_name,
                           x: float,
                           y: float,
                           z: float,
                           r: float,
                           is_queued=False):
        return self.__dobotlink.M1.SetUserCoordinate(portName=port_name,
                                                     x=x,
                                                     y=y,
                                                     z=z,
                                                     r=r,
                                                     isQueued=is_queued)

    def get_usercoordinate(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetUserCoordinate(portName=port_name,
                                                     isQueued=is_queued)

    def set_toolcoordinate(self,
                           port_name,
                           x: float,
                           y: float,
                           z: float,
                           r: float,
                           is_queued=False):
        return self.__dobotlink.M1.SetToolCoordinate(portName=port_name,
                                                     x=x,
                                                     y=y,
                                                     z=z,
                                                     r=r,
                                                     isQueued=is_queued)

    def get_toolcoordinate(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetToolCoordinate(portName=port_name,
                                                     isQueued=is_queued)

    def get_alarms_state(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetAlarmsState(portName=port_name,
                                                  isQueued=is_queued)

    def clear_allalarms_state(self, port_name, is_queued=False):
        return self.__dobotlink.M1.ClearAllAlarmsState(portName=port_name,
                                                       isQueued=is_queued)

    def get_run_state(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetRunState(portName=port_name,
                                               isQueued=is_queued)

    def set_homecmd(self,
                    port_name,
                    is_resetpars=False,
                    is_queued=True,
                    is_wait=True,
                    time_out=25000):
        return self.__dobotlink.M1.SetHOMECmd(portName=port_name,
                                              isResetPars=is_resetpars,
                                              isQueued=is_queued,
                                              isWaitForFinish=is_wait,
                                              timeout=time_out)

    def set_home_initialpos(self, port_name, is_queued=False):
        return self.__dobotlink.M1.SetHOMEInitialPos(portName=port_name,
                                                     isQueued=is_queued)

    def set_hhttrig_mode(self, port_name, mode: int, is_queued=False):
        return self.__dobotlink.M1.SetHHTTrigMode(portName=port_name,
                                                  mode=mode,
                                                  isQueued=is_queued)

    def get_hhttrig_mode(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetHHTTrigMode(portName=port_name,
                                                  isQueued=is_queued)

    def set_hhttrig_output_enabled(self,
                                   port_name,
                                   enable: bool,
                                   is_queued=False):
        return self.__dobotlink.M1.SetHHTTrigOutputEnabled(portName=port_name,
                                                           enable=enable,
                                                           isQueued=is_queued)

    def get_hhttrig_output_enabled(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetHHTTrigOutputEnabled(portName=port_name,
                                                           isQueued=is_queued)

    def get_hhttrig_output(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetHHTTrigOutput(portName=port_name,
                                                    isQueued=is_queued)

    def set_servo_power(self, port_name, on: bool, is_queued=False):
        return self.__dobotlink.M1.SetServoPower(portName=port_name,
                                                 on=on,
                                                 isQueued=is_queued)

    def set_endeffector_params(self,
                               port_name,
                               x_offset: float,
                               y_offset: float,
                               z_offset: float,
                               is_queued=False):
        return self.__dobotlink.M1.SetEndEffectorParams(portName=port_name,
                                                        xOffset=x_offset,
                                                        yOffset=y_offset,
                                                        zOffset=z_offset,
                                                        isQueued=is_queued)

    def get_endeffector_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetEndEffectorParams(portName=port_name,
                                                        isQueued=is_queued)

    def set_endeffector_laser(self,
                              port_name,
                              enable: bool,
                              on: bool,
                              is_queued=False):
        return self.__dobotlink.M1.SetEndEffectorLaser(portName=port_name,
                                                       enable=enable,
                                                       on=on,
                                                       isQueued=is_queued)

    def get_endeffector_laser(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetEndEffectorLaser(portName=port_name,
                                                       isQueued=is_queued)

    def set_endeffector_suctioncup(self,
                                   port_name,
                                   enable: bool,
                                   on: bool,
                                   is_queued=False):
        return self.__dobotlink.M1.SetEndEffectorSuctionCup(portName=port_name,
                                                            enable=enable,
                                                            on=on,
                                                            isQueued=is_queued)

    def get_endeffector_suctioncup(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetEndEffectorSuctionCup(portName=port_name,
                                                            isQueued=is_queued)

    def set_endeffector_gripper(self,
                                port_name,
                                enable: bool,
                                on: bool,
                                is_queued=False):
        return self.__dobotlink.M1.SetEndEffectorGripper(portName=port_name,
                                                         enable=enable,
                                                         on=on,
                                                         isQueued=is_queued)

    def get_endeffector_gripper(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetEndEffectorGripper(portName=port_name,
                                                         isQueued=is_queued)

    def set_jogjoint_params(self,
                            port_name,
                            velocity,
                            acceleration,
                            is_queued=False):
        return self.__dobotlink.M1.SetJOGJointParams(portName=port_name,
                                                     velocity=velocity,
                                                     acceleration=acceleration,
                                                     isQueued=is_queued)

    def get_jogjoint_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetJOGJointParams(portName=port_name,
                                                     isQueued=is_queued)

    def set_jogcoordinate_params(self,
                                 port_name,
                                 velocity,
                                 acceleration,
                                 is_queued=False):
        return self.__dobotlink.M1.SetJOGCoordinateParams(
            portName=port_name,
            velocity=velocity,
            acceleration=acceleration,
            isQueued=is_queued)

    def get_jogcoordinate_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetJOGCoordinateParams(portName=port_name,
                                                          isQueued=is_queued)

    def set_jogcommon_params(self,
                             port_name,
                             velocity_ratio: float,
                             acceleration_ratio: float,
                             is_queued=False):
        return self.__dobotlink.M1.SetJOGCommonParams(
            portName=port_name,
            velocityRatio=velocity_ratio,
            accelerationRatio=acceleration_ratio,
            isQueued=is_queued)

    def get_jogcommon_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetJOGCommonParams(portName=port_name,
                                                      isQueued=is_queued)

    def set_jogcmd(self, port_name, is_joint: bool, cmd: int, is_queued=True):
        return self.__dobotlink.M1.SetJOGCmd(portName=port_name,
                                             isJoint=is_joint,
                                             cmd=cmd,
                                             isQueued=is_queued)

    def set_inchmode(self, port_name, mode: int, is_queued=False):
        return self.__dobotlink.M1.SetInchMode(portName=port_name,
                                               mode=mode,
                                               isQueued=is_queued)

    def get_inchmode(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetInchMode(portName=port_name,
                                               isQueued=is_queued)

    def set_inchparam(self,
                      port_name,
                      distance_mm: float,
                      distance_ang: float,
                      is_queued=False):
        return self.__dobotlink.M1.SetInchParam(portName=port_name,
                                                distanceMM=distance_mm,
                                                distanceANG=distance_ang,
                                                isQueued=is_queued)

    def get_inchparam(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetInchParam(portName=port_name,
                                                isQueued=is_queued)

    def set_ptpcmd(self,
                   port_name,
                   ptp_mode: int,
                   x: float,
                   y: float,
                   z: float,
                   r: float,
                   is_queued=True,
                   is_wait=True):
        return self.__dobotlink.M1.SetPTPCmd(portName=port_name,
                                             ptpMode=ptp_mode,
                                             x=x,
                                             y=y,
                                             z=z,
                                             r=r,
                                             isQueued=is_queued,
                                             isWaitForFinish=is_wait,
                                             timeout=86400000)

    def set_ptpjoint_param(self,
                           port_name,
                           velocity,
                           acceleration,
                           is_queued=False):
        return self.__dobotlink.M1.SetPTPJointParams(portName=port_name,
                                                     velocity=velocity,
                                                     acceleration=acceleration,
                                                     isQueued=is_queued)

    def get_ptpjoint_param(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetPTPJointParams(portName=port_name,
                                                     isQueued=is_queued)

    def set_ptpcoordinate_params(self,
                                 port_name,
                                 xyz_velocity: float,
                                 r_velocity: float,
                                 xyz_acceleration: float,
                                 r_acceleration: float,
                                 is_queued=False):
        return self.__dobotlink.M1.SetPTPCoordinateParams(
            portName=port_name,
            xyzVelocity=xyz_velocity,
            rVelocity=r_velocity,
            xyzAcceleration=xyz_acceleration,
            rAcceleration=r_acceleration,
            isQueued=is_queued)

    def get_ptpcoordinate_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetPTPCoordinateParams(portName=port_name,
                                                          isQueued=is_queued)

    def set_ptpjump_params(self,
                           port_name,
                           isusing_zlimit: bool,
                           z_limit: float,
                           jump_height: float,
                           is_queued=False):
        return self.__dobotlink.M1.SetPTPJumpParams(
            portName=port_name,
            isUsingZLimit=isusing_zlimit,
            zLimit=z_limit,
            jumpHeight=jump_height,
            isQueued=is_queued)

    def get_ptpjump_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetPTPJumpParams(portName=port_name,
                                                    isQueued=is_queued)

    def set_ptpcommon_params(self,
                             port_name,
                             velocity_ratio: float,
                             acceleration_ratio: float,
                             is_queued=False):
        return self.__dobotlink.M1.SetPTPCommonParams(
            portName=port_name,
            velocityRatio=velocity_ratio,
            accelerationRatio=acceleration_ratio,
            isQueued=is_queued)

    def get_ptpcommon_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetPTPCommonParams(portName=port_name,
                                                      isQueued=is_queued)

    def set_motivation_mode(self, port_name, mode: int, is_queued=False):
        return self.__dobotlink.M1.SetMotivationMode(portName=port_name,
                                                     mode=mode,
                                                     isQueued=is_queued)

    def get_motivation_mode(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetMotivationMode(portName=port_name,
                                                     isQueued=is_queued)

    def set_motivate_cmd(self,
                         port_name,
                         q1: float,
                         q2: float,
                         dq1: float,
                         dq2: float,
                         ddq1: float,
                         ddq2: float,
                         is_queued=True,
                         is_wait=True,
                         time_out=10000):
        return self.__dobotlink.M1.SetMotivateCmd(portName=port_name,
                                                  q1=q1,
                                                  q2=q2,
                                                  dq1=dq1,
                                                  dq2=dq2,
                                                  ddq1=ddq1,
                                                  ddq2=ddq2,
                                                  isQueued=is_queued,
                                                  isWaitForFinish=is_wait,
                                                  timeout=time_out)

    def set_motivate_zcmd(self,
                          port_name,
                          qz: float,
                          dqz: float,
                          ddqz: float,
                          is_queued=True,
                          is_wait=True):
        return self.__dobotlink.M1.SetMotivateZCmd(portName=port_name,
                                                   qz=qz,
                                                   dqz=dqz,
                                                   ddqz=ddqz,
                                                   isQueued=is_queued,
                                                   isWaitForFinish=is_wait)

    def get_trajectory(self,
                       port_name,
                       count_max: int,
                       index: int,
                       is_queued=False):
        return self.__dobotlink.M1.GetTrajectory(portName=port_name,
                                                 countMax=count_max,
                                                 index=index,
                                                 isQueued=is_queued)

    def set_iodo(self, port_name, port: int, level: int, is_queued=False):
        return self.__dobotlink.M1.SetIODO(portName=port_name,
                                           port=port,
                                           level=level,
                                           isQueued=is_queued)

    def get_iodo(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.M1.GetIODO(portName=port_name,
                                           port=port,
                                           isQueued=is_queued)

    def get_iodi(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.M1.GetIODI(portName=port_name,
                                           port=port,
                                           isQueued=is_queued)

    def get_ioadc(self, port_name, port: int, is_queued=False):
        return self.__dobotlink.M1.GetIOADC(portName=port_name,
                                            port=port,
                                            isQueued=is_queued)

    def set_cpparams(self,
                     port_name,
                     target_acc: float,
                     junction_vel: float,
                     isreal_timetrack: bool,
                     acc=None,
                     period=None,
                     is_queued=False):
        return self.__dobotlink.M1.SetCPParams(
            portName=port_name,
            targetAcc=target_acc,
            junctionVel=junction_vel,
            isRealTimeTrack=isreal_timetrack,
            acc=acc,
            period=period,
            isQueued=is_queued)

    def get_cpparams(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetCPParams(portName=port_name,
                                               isQueued=is_queued)

    def set_cpcmd(self,
                  port_name,
                  cp_mode: int,
                  x: float,
                  y: float,
                  z: float,
                  power: float,
                  is_queued=True):
        return self.__dobotlink.M1.SetCPCmd(portName=port_name,
                                            cpMode=cp_mode,
                                            x=x,
                                            y=y,
                                            z=z,
                                            power=power,
                                            isQueued=is_queued)

    def set_cplecmd(self,
                    port_name,
                    cp_mode: int,
                    x: float,
                    y: float,
                    z: float,
                    power: float,
                    is_queued=True):
        return self.__dobotlink.M1.SetCPLECmd(portName=port_name,
                                              cpMode=cp_mode,
                                              x=x,
                                              y=y,
                                              z=z,
                                              power=power,
                                              isQueued=is_queued)

    def set_arcparams(self,
                      port_name,
                      xyz_velocity: float,
                      r_velocity: float,
                      xyz_acceleration: float,
                      r_acceleration: float,
                      is_queued=False):
        return self.__dobotlink.M1.SetARCParams(
            portName=port_name,
            xyzVelocity=xyz_velocity,
            rVelocity=r_velocity,
            xyzAcceleration=xyz_acceleration,
            rAcceleration=r_acceleration,
            isQueued=is_queued)

    def get_arcparams(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetARCParams(portName=port_name,
                                                isQueued=is_queued)

    def set_arccmd(self, port_name, cir_point, to_point, is_queued=True):
        return self.__dobotlink.M1.SetARCCmd(portName=port_name,
                                             cirPoint=cir_point,
                                             toPoint=to_point,
                                             isQueued=is_queued)

    def set_arcpocmd(self,
                     port_name,
                     cir_point,
                     to_point,
                     arc_po,
                     is_queued=True):
        return self.__dobotlink.M1.SetARCPOCmd(portName=port_name,
                                               cirPoint=cir_point,
                                               toPoint=to_point,
                                               arcPO=arc_po,
                                               isQueued=is_queued)

    def set_circle_cmd(self,
                       port_name,
                       cir_point,
                       to_point,
                       count: int,
                       is_queued=True,
                       is_wait=True,
                       time_out=60000):
        return self.__dobotlink.M1.SetCircleCmd(portName=port_name,
                                                cirPoint=cir_point,
                                                toPoint=to_point,
                                                count=count,
                                                isQueued=is_queued,
                                                isWaitForFinish=is_wait,
                                                timeout=time_out)

    def set_circle_pocmd(self,
                         port_name,
                         cir_point,
                         to_point,
                         count: int,
                         circle_po,
                         is_queued=True):
        return self.__dobotlink.M1.SetCirclePOCmd(portName=port_name,
                                                  cirPoint=cir_point,
                                                  toPoint=to_point,
                                                  count=count,
                                                  circlePO=circle_po,
                                                  isQueued=is_queued)

    def set_arm_orientation(self,
                            port_name,
                            arm_orientation: int,
                            is_queued=False):
        return self.__dobotlink.M1.SetArmOrientation(
            portName=port_name,
            armOrientation=arm_orientation,
            isQueued=is_queued)

    def get_arm_orientation(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetArmOrientation(portName=port_name,
                                                     isQueued=is_queued)

    def set_waitcmd(self, port_name, delay: int, is_queued=True):
        return self.__dobotlink.M1.SetWAITCmd(portName=port_name,
                                              delay=delay,
                                              timeout=delay + 500,
                                              isQueued=is_queued)

    def set_safemode_enabled(self, port_name, enable: bool, is_queued=False):
        return self.__dobotlink.M1.SetSafeModeEnabled(portName=port_name,
                                                      enable=enable,
                                                      isQueued=is_queued)

    def get_safemode_enabled(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetSafeModeEnabled(portName=port_name,
                                                      isQueued=is_queued)

    def set_collision_threshold(self,
                                port_name,
                                tor_diffj1: float,
                                tor_diffj2: float,
                                tor_diffj3: float,
                                tor_diffj4: float,
                                is_queued=False):
        return self.__dobotlink.M1.SetCollisionThreshold(portName=port_name,
                                                         torDiffJ1=tor_diffj1,
                                                         torDiffJ2=tor_diffj2,
                                                         torDiffJ3=tor_diffj3,
                                                         torDiffJ4=tor_diffj4,
                                                         isQueued=is_queued)

    def get_collision_threshold(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetCollisionThreshold(portName=port_name,
                                                         isQueued=is_queued)

    def set_basicdynamic_params(self,
                                port_name,
                                zz1: float,
                                fs1: float,
                                fv1: float,
                                zz2: float,
                                mx2: float,
                                my2: float,
                                ia2: float,
                                fs2: float,
                                fv2: float,
                                is_queued=False):
        return self.__dobotlink.M1.SetBasicDynamicParams(portName=port_name,
                                                         ZZ1=zz1,
                                                         FS1=fs1,
                                                         FV1=fv1,
                                                         ZZ2=zz2,
                                                         MX2=mx2,
                                                         MY2=my2,
                                                         IA2=ia2,
                                                         FS2=fs2,
                                                         FV2=fv2,
                                                         isQueued=is_queued)

    def get_basicdynamic_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetBasicDynamicParams(portName=port_name,
                                                         isQueued=is_queued)

    def set_load_params(self, port_name, load_params: float, is_queued=False):
        return self.__dobotlink.M1.SetLoadParams(portName=port_name,
                                                 loadParams=load_params,
                                                 isQueued=is_queued)

    def get_load_params(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetLoadParams(portName=port_name,
                                                 isQueued=is_queued)

    def set_safestrategy(self, port_name, strategy: int, is_queued=False):
        return self.__dobotlink.M1.SetSafeStrategy(portName=port_name,
                                                   strategy=strategy,
                                                   isQueued=is_queued)

    def get_safestrategy(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetSafeStrategy(portName=port_name,
                                                   isQueued=is_queued)

    def set_safeguard_mode(self, port_name, mode: int, is_queued=False):
        return self.__dobotlink.M1.SetSafeGuardMode(portName=port_name,
                                                    mode=mode,
                                                    isQueued=is_queued)

    def get_safeguard_mode(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetSafeGuardMode(portName=port_name,
                                                    isQueued=is_queued)

    def get_safeguard_status(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetSafeGuardStatus(portName=port_name,
                                                      isQueued=is_queued)

    def set_lanport_config(self,
                           port_name,
                           addr: str,
                           mask: str,
                           gateway: str,
                           dns: str,
                           isdhcp: bool,
                           is_queued=False):
        return self.__dobotlink.M1.SetLanPortConfig(portName=port_name,
                                                    addr=addr,
                                                    mask=mask,
                                                    gateway=gateway,
                                                    dns=dns,
                                                    isdhcp=isdhcp,
                                                    isQueued=is_queued)

    def get_lanport_config(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetLanPortConfig(portName=port_name,
                                                    isQueued=is_queued)

    def set_firmware_reboot(self, port_name, is_queued=False):
        return self.__dobotlink.M1.SetFirmwareReboot(portName=port_name,
                                                     isQueued=is_queued)

    def set_firmware_notifym4mode(self, port_name, mode: int, is_queued=False):
        return self.__dobotlink.M1.SetFirmwareNotifyM4Mode(portName=port_name,
                                                           mode=mode,
                                                           isQueued=is_queued)

    def get_firmware_notifym4mode(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetFirmwareNotifyM4Mode(portName=port_name,
                                                           isQueued=is_queued)

    def set_feed_forward(self, port_name, value: int, is_queued=False):
        return self.__dobotlink.M1.SetFeedforward(portName=port_name,
                                                  value=value,
                                                  isQueued=is_queued)

    def get_feed_forward(self, port_name, is_queued=False):
        return self.__dobotlink.M1.GetFeedforward(portName=port_name,
                                                  isQueued=is_queued)
