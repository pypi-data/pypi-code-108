import os, json, sys, time, logging, configparser
import threading
import pickle
import tkinter as tk
from tkinter import ttk
from tkinter.ttk import *
from tkinter import PhotoImage
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import asksaveasfilename
import tkinter.messagebox as mbox
import queue
from ftplib import FTP

from autotk.AutoCoreLite import runmain, license_name, logger, getnewdir, atom, config_auto
from autotk.AutoCore import UIForm, Box
from autotk.AutoMES import Mes
from autotk.AutoDB import log2db
from autotk.AutoLang import lolang,lang_append

from PIL import Image, ImageDraw, ImageFont, ImageTk
from ttkwidgets import CheckboxTreeview
import win32event
import win32api
import win32com.client

try:
    import cv2
except:
    pass


class BoxFrame(tk.Toplevel):
    def __init__(self, master=None, cnf={}, setting={}, result={}, **kw):
        self.setting = setting
        self.result = result
        super().__init__(master, cnf, **kw)
        if ("geometry" in self.setting):
            # self.geometry(self.setting["geometry"])  # 自动尺寸
            pass
        if ("title" in self.setting):
            self.title(self.setting["title"])
        self.resizeframe = setting.get("resize", None)
        self.frame= setting.get("frame", None)
        # self.iconbitmap("./ico.ico")      # iconphoto(True 继承图标
        self.transient(master)  # 调用这个函数就会将Toplevel注册成master的临时窗口,临时窗口简化最大最小按钮
        self.resizable(height=False, width=False)  # 禁止调整大小
        self.grab_set()  # 将此应用程序的所有事件路由到此窗口小部件
        self.init_ui()
        self.bind("<Escape>", self.destroy)
        self.focus_force()  #

    def destroy(self, *args) -> None:
        super().destroy()

    def init_ui(self):
        try:
            panel = Label(self)
            panel.pack()
            if (self.resizeframe):
                img_h, img_w, _ = self.frame.shape
                self.frame = cv2.resize(self.frame, (int(img_w * 0.5), int(img_h * 0.5)))
            cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
            current_image = Image.fromarray(cv2image)  # 将图像转换成Image对象
            imgtk = ImageTk.PhotoImage(image=current_image)
            panel.imgtk = imgtk
            panel.config(image=imgtk)
        except Exception as e:
            print(e)


class Func_Loop_Box(tk.Toplevel):
    def __init__(self, master=None, cnf={}, setting={}, result={}, **kw):
        self.setting = setting
        self.result = result
        super().__init__(master, cnf, **kw)
        if ("func" in self.setting):
            self.func = self.setting["func"]
        if ("keycodes" in self.setting):
            self.tags = self.setting["keycodes"]
        if ("geometry" in self.setting):
            self.geometry(self.setting["geometry"])
        if ("title" in self.setting):
            self.showname = self.setting["title"]
            self.title(self.showname)
        self.dute = 200
        self.timeout = 100
        if ("dute" in self.setting):
            self.dute = self.setting["dute"]
        self.dute_count = self.dute / 1000
        if ("timeout" in self.setting):
            self.timeout = self.setting["timeout"]
        self.count = self.timeout if self.timeout > 0 else 0
        # self.iconbitmap("./ico.ico")      # iconphoto(True 继承图标
        self.transient(master)  # 调用这个函数就会将Toplevel注册成master的临时窗口,临时窗口简化最大最小按钮
        self.resizable(height=False, width=False)  # 禁止调整大小
        self.grab_set()  # 将此应用程序的所有事件路由到此窗口小部件
        self.init_ui()
        self.refresh_data()

    def loop(self, *args, **kwargs):
        ret, data = self.func()
        self.result['Data'] = data
        if (ret):
            allpass = True
            for k in self.tags.split(','):
                if (not k in data):
                    allpass = False
                    break
            if (allpass):
                self.result['Result'] = True
                self.destroy()

    def refresh_data(self, *args, **kwargs):
        if (self.timeout > 0):
            self.count -= self.dute_count
            self.title("{} {}".format(self.showname, int(self.count)))
        else:
            self.title("{}".format(self.showname))
        try:
            self.loop()
        except Exception as e:
            logger.critical(e)
            self.destroy()
        if (self.count < 0):
            self.destroy()
        else:
            self.after(self.dute, self.refresh_data)

    def destroy(self, *args, **kwargs):
        super().destroy()

    def init_ui(self):
        self.msgtip = Label(self, text="请按键：", anchor='w', font=('宋体', 18), background="yellow")
        self.msgtip.place(relx=0.02, rely=0.04, relwidth=0.97, relheight=0.4)
        self.b_fail = Button(self, text='FAIL [故障]', command=self.destroy, style='TButton')
        self.b_fail.place(relx=0.02, rely=0.5, relwidth=0.97, relheight=0.4)


class MForm(UIForm):

    def show_view(self, pane_id, img, resize=None):
        try:
            LabelView = self.pane_all[pane_id]["LabelView"]
            if (resize):
                img_h, img_w, _ = img.shape
                img = cv2.resize(img, (img_w * resize, img_h * resize))
            cv2image = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
            current_image = Image.fromarray(cv2image)  # 将图像转换成Image对象
            imgtk = ImageTk.PhotoImage(image=current_image)
            LabelView.imgtk = imgtk
            LabelView.config(image=imgtk)
        except:
            pass

    def isRemove(self, pane_id):
        return self.pane_all[pane_id]["Tid"] == ""

    def babort_click(self, item, pane_id):
        try:
            self.pane_all[pane_id]["Abort"] = True
        except:
            pass

    def blist_click(self, item, pane_id):
        super().blist_click(item, pane_id)
        try:
            data = self.pane_item_dict[pane_id][item]["Data"]
            if (self.plan[item] in self.planClickFrame):
                if (isinstance(data, str)):
                    mbox.showinfo(self.pane_sn[pane_id].get(), data)
                else:
                    frame, msg = data
                    show_title = "%s %s" % (self.pane_sn[pane_id].get(), msg)
                    self.show_box_class(BoxFrame, setting={'title': show_title, "frame": frame, "resize": 0.5})
                return
            if (self.plan[item] in self.planClickPlot):
                if (isinstance(data, str)):
                    mbox.showinfo(self.pane_sn[pane_id].get(), data)
                else:
                    moddal = Modal_PSD(self, self.pane_sn[pane_id].get(), data)  # 待处理
                return
            if (self.plan[item] in self.planClickInfo):
                if (data):
                    mbox.showinfo(self.pane_sn[pane_id].get(), data)
                else:
                    print("No Data..", data)
                return
            print("blist_click[planClickFrame/planClickPlot/planClickInfo] Undefined",self.plan[item])
            # 重测执行代码段
            # logger.info("Retest {}".format(self.plan[item]))
            # name = self.pane_sn[pane_id].get()
            # self.plan_todo[self.plan[item]](name, pane_id)
        except:
            pass

    def loadconfig(self):
        super().loadconfig()
        # 标志adb模式,mode为双数使用usb模式,mode为单数使用exe模式,mode=0为默认usb模式
        self.adb_is_exe=bool(int(self.conf_dict["SETTING"].get("mode","0"))%2)
        # 颜色 默认初始值为 黑：-16777216
        self.color_dict = {"indx": ["红", "绿", "蓝", "白", "黄", "紫", "青", "灰", "黑", ], "红": -65536, "绿": -16711936,
                           "蓝": -16776961, "白": -1, "黑": -16777216, "灰": -7829368, "黄": -256, "紫": -65281,
                           "青": -16711681}
        self.show_log_heigth = 8  # 重置LOG的显示高度
        # 注册执行线程                                                                                 Plan注册>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.plan_todo = {"HDMI_VIDEO": self.todo_HDMI_VIDEO, "HDMI_AUDIO": self.todo_HDMI_AUDIO,
                          "WIFI_COUPLE": self.todo_WIFI_COUPLE, "ROUTER_COUPLE": self.todo_ROUTER_COUPLE,
                          'BURN_KEY': self.todo_BURN_KEY, 'HDMI_VOLT': self.todo_HDMI_VOLT,
                          "ADB_CLOSE": self.todo_ADB_CLOSE,
                          'CHECK_KEYS': self.todo_CHECK_KEYS, 'ROUTER_TELNET': self.todo_ROUTER_TELNET,
                          'DVB_VOLT': self.todo_DVB_VOLT, 'BT_TEST': self.todo_BT_TEST, 'READ_KEY': self.todo_READ_KEY,
                          "ETH_TEST": self.todo_ETH_TEST, "MES": self.todo_MES, "DVB": self.todo_DVB,
                          'WIFI_24': self.todo_WIFI_24, 'WIFI_5': self.todo_WIFI_5, 'FTP': self.todo_FTP,
                          "RESET": self.todo_RESET, "BASIC_TEST": self.todo_BASIC_TEST, "SCANNER": self.todo_SCANNER,
                          'BUTTON_TEST': self.todo_BUTTON_TEST, 'AGING_TEST': self.todo_AGING_TEST,
                          "RESOLUTION": self.todo_RESOLUTION, "USB_TEST": self.todo_USB_TEST,
                          "VISION_DETECT": self.todo_VISION_DETECT, "LEDS_DETECT": self.todo_LEDS_DETECT,
                          "SD_TEST": self.todo_SD_TEST, "IR_TEST": self.todo_IR_TEST, 'LED_TEST': self.todo_LED_TEST,
                          "SPDIF_AUDIO": self.todo_SPDIF_AUDIO, "ADB_IPERF": self.todo_ADB_IPERF}
        self.planAllowAbort = ["VISION_DETECT", "LEDS_DETECT"]
        self.planClickFrame = ["HDMI_VIDEO", "DVB", "LED_TEST"]
        self.planClickPlot = ["HDMI_AUDIO", "SPDIF_AUDIO"]
        self.planClickInfo = ["RESOLUTION", "USB_TEST", "SD_TEST", "ETH_TEST", "IR_TEST", "BASIC_TEST", "MES",
                              "SCANNER", "BURN_KEY", "READ_KEY", "CHECK_KEYS", "WIFI_COUPLE", "ROUTER_COUPLE",
                              "BUTTON_TEST", "HDMI_VOLT", "DVB_VOLT", "AGING_TEST", "WIFI_5", "WIFI_24",
                              "ROUTER_TELNET", "ADB_CLOSE", "LEDS_DETECT", "IPERF_24", "IPERF_5",
                              "BT_TEST"]
        self.scanlock = threading.Semaphore(1)  # 资源锁

    def initdata(self):
        super().initdata()
        for i, p in enumerate(self.pane_sn):
            self.pane_all[i] = {"Ready": True, "Run": False, "HDMI": 0, "Boxid": "", "BoxidVstr": p, "Tid": "",
                                "Class": "", "Abort": False,
                                }
        # 参数定义最多有几个线程可以同时使用资源
        self.pane_all["DeviceNum"] = 0  # 记录ADB的搜索数量
        self.pane_all["Overflow"] = []  # 超出治具数量的设备记录
        self.pane_all["Abort"] = {}  # 中断的设备记录,中断的判断为Fail
        if ("HDMI_VIDEO" in self.plan):
            if (os.path.isfile("./hdmi.jpg")):
                img = cv2.imread("./hdmi.jpg")
                self.samplehash = self.aHash(img)  # 1111100010100100100111101111011001100000000001000101010100011110
            else:
                logger.info("Read the Default hdmi sample ahash value")
                self.samplehash = "1111100010100100100111101111011001100000000001000101010100011110"
        # MES
        try:
            logger.debug("MES Connnetting..")
            mes_id = int(self.conf_dict["MES"]["id"])
            mes_wsdl = self.conf_dict["MES"]["wsdl"]
            mes_station = self.conf_dict["MES"]["station"]
            mes_scanner = self.conf_dict["MES"]["scanner"]
            self.mes = Mes(mes_wsdl, mes_station, mes_scanner, not mes_id, self.conf_dict["MES"])
        except:
            logger.debug("MES Connect Error")
        #
        self.pane_dict_report = {"PASSCount": 0, "FAILCount": 0, "ItemFailCount": {i: 0 for i in self.plan}}
        #
        self.pane_port = {}

    def t_plan(self, name, sn_ctl, pane_id):
        try:
            btime = time.time()
            self.pane_dict_report[pane_id] = {"SN": name}
            for i, p in enumerate(self.plan):
                if (not self.main_run): return
                _btime = time.time()
                self.pane_item_dict[pane_id][i]["Data"] = None  # 清空数据
                self.pane_item_dict[pane_id][i]["running"]()
                self.pane_dict_report[pane_id]["TestItem"] = i + 1
                try:
                    self.pane_dict_report[pane_id][p] = {}
                    self.log_db.plan(name, p)
                    result, show_tips = self.plan_todo[p](name, pane_id, i, p, self.pane_dict_report[pane_id][p])
                except Exception as e:
                    result = False
                    show_tips = ""
                    logger.critical("[Error]t_plan %s pane %s" % (name, pane_id))
                    logger.critical(str(e))
                finally:
                    elpstime = round(time.time() - _btime, 3)
                    self.pane_dict_report[pane_id][p]['elpstime'] = elpstime
                    self.pane_dict_report[pane_id][p]['result'] = result
                    if (result):
                        logger.warning("%s %s %s PASS" % (name, self.lo(p), show_tips))
                    else:
                        logger.error("%s %s %s FAIL" % (name, self.lo(p), show_tips))
                    logger.info("Elapsed Time: %.3f s" % (elpstime))  # 统一计算耗时
                self.log_db.add_report(name, p, elpstime, result, self.pane_dict_report[pane_id][p])
                if (pane_id in self.pane_all["Abort"]):
                    pass
                    # self.pane_all["Abort"].pop(pane_id)
                    # break
                if (self.isRemove(pane_id)):  # 设备已移除
                    break
                if (not result):
                    self.pane_item_dict[pane_id][i]["fail"]()
                    break
                self.pane_item_dict[pane_id][i]["pass"]()
            self.log_db.plan(name, report=result)
            # adb = self.pane_all[pane_id]["Class"]
            # if (not adb.error):   #20210715 adb错误 更换成移除与执行关闭 更新界面
            # print(self.main_run,self.pane_all)
            if (self.main_run and not self.isRemove(pane_id)):
                self.update_report(pane_id)
            # 由执行中 转存 到 完成
            self.pane_all[pane_id]["Abort"] = False
            self.pane_all[pane_id]["Run"] = False
            logger.info("Test Device {} Finish (Elapsed: {:.1f} s)".format(name, time.time() - btime))
            if (not 'FTP' in self.plan):  # 去重
                self.save_report(pane_id, result)
            if ("a" in self.conf_dict["SETTING"]["debug"]):
                self.pane_all[pane_id]["Class"].adb_close()  # DUT 自动关闭adb
            elif ("l" in self.conf_dict["SETTING"]["debug"]):
                if ("e" in self.conf_dict["SETTING"]["debug"]):
                    if (result):
                        self.debug_remove(pane_id)
                else:
                    self.debug_remove(pane_id)
            # adb.dev_finish()  # DUT 完成
        except Exception as e:
            print(e)
            logger.critical("[t_plan]Error: %s" % e)

    def update_report(self, pane_id):
        try:
            dict_report = self.pane_dict_report[pane_id]
            if (dict_report):
                result = False
                usetime = 0
                for i in self.plan:
                    if ("result" in dict_report[i].keys()):
                        result = dict_report[i]["result"]
                        usetime += dict_report[i]["elpstime"]
                        if (not result):
                            self.pane_dict_report["ItemFailCount"][i] += 1  # 统计错误Item
                            break
                    else:
                        self.pane_dict_report["ItemFailCount"][i] += 1  # 统计错误Item
                        break  # 未执行完 result没有
                self.pane_dict_report[pane_id]["elpstime"] = usetime
                if (result):
                    self.pane_dict_report["PASSCount"] += 1
                    self.pane_result[pane_id]["text"] = "PASS"
                    self.pane_result[pane_id]["background"] = "green"
                else:
                    self.pane_dict_report["FAILCount"] += 1
                    self.pane_result[pane_id]["text"] = "FAIL"
                    self.pane_result[pane_id]["background"] = "red"
            else:
                self.pane_result[pane_id]["text"] = "Result"
                self.pane_result[pane_id]["background"] = "gray"
            self.refresh_info()
        except Exception as e:
            logger.warning("[Warn] update_report")
            logger.warning(e)

    def save_report(self, pane_id, result):
        loadsn = self.pane_all[pane_id]["BoxidVstr"].get()
        reportjson = self.pane_dict_report[pane_id]
        reportjson['Boxid'] = reportjson['SN']
        reportjson['SN'] = ''  # 修正SN>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        app_json = json.dumps(reportjson, indent=4, sort_keys=True)
        self.mes.SaveJson(loadsn, result, reportjson)
        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        filename = "./report/%s_%s_%s.json" % (loadsn, timestr, "PASS" if result else "FAIL")
        with open(filename, "w+") as jsonf:
            jsonf.write(app_json)
        if ("csv" in self.conf_dict["SETTING"]["debug"]):  # 保存结果汇总到本地csv
            with open("ReportCollect.csv", 'a+') as f:
                content = "%s,%s\n" % (loadsn, reportjson)
                f.write(content)
        return filename

    def todo_ADB_CLOSE(self, name, pane_id, item, tagid, report_dict, msg=[], *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            mode = self.conf_dict[tagid]["mode"]
            dhcp = int(self.conf_dict[tagid]["dhcp"])
            if "door" in self.conf_dict[tagid]:
                open_door = int(self.conf_dict[tagid]["door"])
            else:
                open_door = True  # 兼容旧版本,无该配置
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        # 临时ADB指令
        '''
        cmd0 = pm install /storage/%s/Nes_SetNetHdcp_v1.0.apk
        delay0 = 2
        match0 = Success
        cmd1 = am start -n com.nes.sethdcp/com.nes.sethdcp.MainActivity
        delay1 = 2
        match1 = cmp=com.nes.sethdcp/.MainActivity
        cmd2 = dumpsys activity com.nes.sethdcp/com.nes.sethdcp.MainActivity getHdcpState
        delay2 = 3
        match2 = getHdcpState_SUCCESS
        '''
        result = True
        try:
            for i in range(10):
                if (not "cmd%d" % i in self.conf_dict[tagid]): break
                cmd = self.conf_dict[tagid]["cmd%d" % i]
                if ("%" in cmd):
                    # if("storage/%s" in cmd):
                    cmd = cmd % (adb.sendshell("ls /storage ")[:9])  # 变量变换
                logger.debug("[CMD%d] %s" % (i, cmd))
                if (cmd):
                    ret = adb.sendshell(cmd)
                    logger.debug("[RECV%d] %s" % (i, ret.strip()))
                    delay = self.conf_dict[tagid]["delay%d" % i]
                    if (delay):
                        time.sleep(int(delay))
                    match = self.conf_dict[tagid]["match%d" % i]
                    if (match):
                        if (not match in ret):
                            logger.error("[CMD%s]Match:%s Fail" % (i, match))
                            msg.append("[RECV%d] %s" % (i, ret.strip()))
                            result = False
                            break
        except Exception as e:
            logger.critical(e)
            result = False
        if (result and dhcp):
            result = adb.setDhcp()
            msg.append("[HDCP]%s" % result)
            logger.debug("%s %s [DHCP]%s" % (name, self.lo(tagid), result))
        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
        # 临时增加治具门打开
        if (result):
            if (mode == "0"):
                adb.adb_close_next()
            else:
                adb.adb_close()
                # 临时增加治具门打开
                if (result and open_door):
                    try:
                        auto = int(self.conf_dict["BUTTON_TEST"]["auto"])
                    except:
                        logger.critical("Config BUTTON_TEST temp Para %s" % self.lo("Error"))
                        # self.pane_dict_report[pane_id][tagid] = {"result": False}
                        return False
                    if (auto == 1):
                        try:
                            # 控制自动按键,波特率9600打开串口，发送“BUTTON_ON” 按键开启 ，串口返回“OK”；发送“BUTTON_OF”F 按键关闭，串口返回“OK
                            ports = self.conf_dict["BUTTON_TEST"]["ports"].split(',')
                            ctl_m = control_com(ports[pane_id])
                            ctl_m.open()
                            ctl_m.open_door()
                            logger.debug("Open the Door")
                        except:
                            logger.critical("Temp Control COM Error")
                        finally:
                            ctl_m.close()
        return result, ""

    def todo_MES(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            id = int(self.conf_dict[tagid]["id"])
            keywords = self.conf_dict[tagid]["keyword"].split(',')
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if ("SCANNER" in self.pane_dict_report[pane_id] and "scan" in self.pane_dict_report[pane_id]["SCANNER"]):
            sn = self.pane_dict_report[pane_id]["SCANNER"]["scan"]
        else:
            sn = self.pane_dict_report[pane_id]["SN"]
        msg = []
        result = True
        for k, v in self.pane_dict_report[pane_id].items():
            if (k == tagid): break
            if (k == "SN"):
                k = "Boxid"  # 当前工具使用的主键名称为Boxid AutoHDMI需要替换Report中的SN为对应的Boxid>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            result = self.mes.Uploaditem(sn, k, v)
            msg.append("%s>> %s" % (k, v))
            if (keywords != [""] and isinstance(v, dict)):
                for w in keywords:
                    if (w in v and bool(v[w])):
                        result = self.mes.Uploaditem(sn, w, v[w])  # 特殊上传
                        msg.append("%s+> %s" % (w, v[w]))
            if (not result): break
        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
        result = self.mes.Result(sn, True)
        # if (result):
        #     logger.warning("%s Upload PASS" % (name))
        # else:
        #     logger.error("%s FAIL" % (name))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime}
        return result, ''

    def todo_AV_AUDIO(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        if (not adb.palystate): adb.hdmiPlay(self.hdmi_sour, self.hdmi_delay)
        # tagid = "AV_AUDIO"
        # btime = time.time()
        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        wavename = './report/%s %s %s.wav' % (tagid, name, timestr)
        report = {"result": False, "elpstime": 0}
        try:
            vmax_limit = self.conf_dict[tagid]["vmax_limit"]
            loudness_limit = self.conf_dict[tagid]["loudness_limit"]
            len = float(self.conf_dict[tagid]["len"])
            psd_enable = int(self.conf_dict[tagid]["psd_enable"])
            p_limit1 = float(self.conf_dict[tagid]["p_limit1"])
            judge1 = list(map(float, [i for i in self.conf_dict[tagid]["judge1"].split(',')]))
            p_limit2 = float(self.conf_dict[tagid]["p_limit2"])
            judge2 = list(map(float, [i for i in self.conf_dict[tagid]["judge1"].split(',')]))
            judge_offset = float(self.conf_dict[tagid]["offset"])
            savewave = self.conf.getboolean(tagid, "save")
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        try:
            ret_name, rec_dev = self.dev_class.get_av_rec(pane_id)  # Record Device Name = S1~Sn
            if (not ret_name):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, ''
            self.reclock.acquire()
            time.sleep(0.2)
            rate, data, buffer = self.sound_rec(rec_dev, len, wavename)
            self.reclock.release()
            # if(os.path.exists(wavename)):
            # rate, data = wavfile.read(wavename)
            msg = []
            if (rate):
                # 最大值判断
                result = True
                if (vmax_limit):
                    vmax_limit_f = float(vmax_limit)
                    vmax = round(np.max(data), 4)
                    # vmax = round(np.max(data[:, 0]), 4)  # 多通道,需同步更新sound_rec
                    result = bool(vmax >= vmax_limit_f)
                    if (result):
                        msg.append("Vmax:%.3f" % (vmax))
                    else:
                        msg.append("Vmax:%.3f[%s]" % (vmax, vmax_limit))
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                    report["Vmax"] = "%.3f" % (vmax)
                if (result and loudness_limit):
                    loudness_limit_f = float(loudness_limit)
                    meter = pyln.Meter(rate)
                    loudness = meter.integrated_loudness(data)
                    result = bool(loudness >= loudness_limit_f)
                    if (result):
                        msg.append("Loudness:%.2f" % (loudness))
                    else:
                        msg.append("Loudness:%.2f[%s]" % (loudness, loudness_limit))
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                    report["Loudness"] = "%.2f" % (loudness)
                if (result):
                    if (psd_enable):
                        result, *showdata = self.check_wave(rate, data, p_limit1, judge1, p_limit2, judge2,
                                                            judge_offset)
                        self.pane_item_dict[pane_id][item]["Data"] = tuple(showdata)
                    else:
                        msg.append("PSD:Off")
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                if (savewave):
                    wavfile.write(wavename, rate, data)
            else:
                # logger.error("Not Found Record File %s" % wavename)
                result = False
            return result, "[%s] %s" % (ret_name, " ".join(msg))

        except Exception as e:
            logger.critical(e)
            logger.critical("%s %s" % (self.lo(tagid), self.lo("Error")))
            return False, ''

    def todo_USB_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            num_limit = self.conf_dict[tagid]["limit"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        ret, count = adb.getUsbNum()
        result = int(count) >= int(num_limit)
        logger.debug("%s Detect Count %s" % (name, count))
        self.pane_item_dict[pane_id][item]["Data"] = "Detect Count: %s [Limit:%s]" % (count, num_limit)
        report_dict['count'] = count
        return result, '%s[%s]' % (count, num_limit)

    def todo_AV_VIDEO(self, name, pane_id, item, tagid, report_dict, *args):
        # tagid = "AV_VIDEO"
        # btime = time.time()
        adb = self.pane_all[pane_id]["Class"]
        if (not adb.palystate): adb.hdmiPlay(self.hdmi_sour, self.hdmi_delay)
        try:
            limit = float(self.conf_dict[tagid]["limit"])
            capnum = self.conf_dict[tagid]["len"]  # 复用于match算法的匹配时长
            quality = float(self.conf_dict[tagid]["quality"])
            savejpg = int(self.conf.getboolean(tagid, "save"))
            sour_num = int(self.conf_dict["SETTING"]["hdmi_source"])
            samplefile = "SampleAV%d.pkl" % (sour_num)
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not os.path.exists(samplefile)):
            logger.critical("Config Sample Not Found %s" % self.lo("Error"))
            return False, ''
        self.hdmilock.acquire()
        ret, frame, result, resultmsg = self.cap_ahash_match_av(pane_id, samplefile, limit, float(capnum), quality)
        self.hdmilock.release()
        if (savejpg):
            timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            cv2.imwrite('./report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr), frame)
        self.pane_item_dict[pane_id][item]["Data"] = [frame, resultmsg]
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s limit[%s] FAIL" % (name, self.lo(tagid), limit))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime}
        return result, "" if result else "limit[%s]" % limit

    def todo_HDMI_AUDIO(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        if (not adb.palystate): adb.hdmiPlay(self.hdmi_sour, self.hdmi_delay)
        # tagid = "HDMI_AUDIO"
        # btime = time.time()
        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        wavename = './report/%s %s %s.wav' % (tagid, name, timestr)
        # report = {"result": False, "elpstime": 0}
        try:
            vmax_limit = self.conf_dict[tagid]["vmax_limit"]
            loudness_limit = self.conf_dict[tagid]["loudness_limit"]
            len = float(self.conf_dict[tagid]["len"])
            psd_enable = int(self.conf_dict[tagid]["psd_enable"])
            p_limit1 = float(self.conf_dict[tagid]["p_limit1"])
            judge1 = list(map(float, [i for i in self.conf_dict[tagid]["judge1"].split(',')]))
            p_limit2 = float(self.conf_dict[tagid]["p_limit2"])
            judge2 = list(map(float, [i for i in self.conf_dict[tagid]["judge1"].split(',')]))
            judge_offset = float(self.conf_dict[tagid]["offset"])
            savewave = self.conf.getboolean(tagid, "save")
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        try:
            ret_name, rec_dev = self.dev_class.get_hdmi_rec(pane_id)  # A1~An
            if (not ret_name):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, ''
            self.reclock.acquire()
            time.sleep(0.2)
            logger.debug("HDMI Reclock Lock.")
            rate, data, buffer = self.sound_rec(rec_dev, len, wavename)
            # self.hdmilock.release()
            self.reclock.release()
            logger.debug("HDMI Reclock Release.")
            # if(os.path.exists(wavename)):
            # rate, data = wavfile.read(wavename)
            msg = []

            if (rate):
                # 最大值判断
                result = True
                if (vmax_limit):
                    vmax_limit_f = float(vmax_limit)
                    vmax = round(np.max(data), 4)
                    # vmax = round(np.max(data[:, 0]), 4)  # 多通道,需同步更新sound_rec
                    result = bool(vmax >= vmax_limit_f)
                    if (result):
                        msg.append("Vmax:%.3f" % (vmax))
                    else:
                        msg.append("Vmax:%.3f[%s]" % (vmax, vmax_limit))
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                    report_dict["Vmax"] = "%.3f" % (vmax)
                if (result and loudness_limit):
                    loudness_limit_f = float(loudness_limit)
                    meter = pyln.Meter(rate)
                    loudness = meter.integrated_loudness(data)
                    result = bool(loudness >= loudness_limit_f)
                    if (result):
                        msg.append("Loudness:%.2f" % (loudness))
                    else:
                        msg.append("Loudness:%.2f[%s]" % (loudness, loudness_limit))
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                    report_dict["Loudness"] = "%.2f" % (loudness)
                if (result):
                    if (psd_enable):
                        result, *showdata = self.check_wave(rate, data, p_limit1, judge1, p_limit2, judge2,
                                                            judge_offset)
                        self.pane_item_dict[pane_id][item]["Data"] = tuple(showdata)
                    else:
                        msg.append("PSD:Off")
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                if (savewave):
                    wavfile.write(wavename, rate, data)
            else:
                logger.error("Not Found Record File %s" % wavename)
                result = False
            # result = True
            # if (result):
            #     logger.warning("%s [%s] %s %s PASS" % (name, ret_name, self.lo(tagid), " ".join(msg)))
            # else:
            #     logger.error("%s [%s] %s %s FAIL" % (name, ret_name, self.lo(tagid), " ".join(msg)))
            return result, "[%s] %s" % (ret_name, " ".join(msg))
        except Exception as e:
            logger.critical(e)
            logger.critical("%s %s" % (self.lo(tagid), self.lo("Error")))
            return False, ''
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # report["result"] = result
        # report["elpstime"] = elpstime
        # self.pane_dict_report[pane_id][tagid] = report
        # return result

    def todo_DECODE_H264(self, name, pane_id, item, tagid, report_dict, *args):
        # tagid = "DECODE_H264"
        # btime = time.time()
        resultmsg = ""
        adb = self.pane_all[pane_id]["Class"]
        try:
            # mode = int(self.conf_dict[tagid]["mode"])
            limit = float(self.conf_dict[tagid]["limit"])
            hitlimit = int(self.conf_dict[tagid]["hit_limit"])
            capnum = self.conf_dict[tagid]["len"]  # 复用于match算法的匹配时长
            quality = float(self.conf_dict[tagid]["quality"])
            set2k = self.conf.getboolean(tagid, "set2k")
            loudness_limit = self.conf_dict[tagid]["loudness_limit"]
            savejpg = int(self.conf.getboolean(tagid, "save"))
            sour_num = int(self.conf_dict[tagid]["source_id"])
            samplefile = "Sample%d.pkl" % sour_num  # DECODE_H264 播放指定的视频源(带杜比)
            wavename = './report/%s %s %s.wav' % (
            tagid, name, time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not os.path.exists(samplefile)):
            logger.critical("Config Sample Not Found %s" % self.lo("Error"))
            return False, "SampleNotFound"
        self.hdmilock.acquire()
        # 增加的视频解码测试
        adb.hdmiPlay(sour_num, self.hdmi_delay)  # DECODE_H264 播放指定的视频源(带杜比)
        ret, frame, result, resultmsg = self.cap_ahash_match(pane_id, samplefile, limit, float(capnum), quality,
                                                             hitlimit,
                                                             set2k)
        if (loudness_limit):
            ret_name, rec_dev = self.dev_class.get_hdmi_rec(pane_id)  # A1~An
            if (not ret_name):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, "RecNotFound"
            self.reclock.acquire()
            logger.debug("HDMI Reclock Lock.")
            rate, data, buffer = self.sound_rec(rec_dev, float(capnum), wavename)
            # self.hdmilock.release()
            self.reclock.release()
            logger.debug("HDMI Reclock Release.")
        adb.hdmiStop()
        self.hdmilock.release()
        # result = True
        # self.pane_dict_report[pane_id][tagid] = {"result": result}
        if (result and loudness_limit):
            loudness_limit_f = float(loudness_limit)
            meter = pyln.Meter(rate)
            loudness = meter.integrated_loudness(data)
            result = bool(loudness >= loudness_limit_f)
            if (result):
                resultmsg += " Loudness:%.2f" % (loudness)
                logger.info("%s %s Loudness:%.2f" % (name, self.lo(tagid), loudness))
            else:
                resultmsg += " Loudness:%.2f[%s]" % (loudness, loudness_limit)
                logger.error("%s %s Loudness:%.2f[%s]" % (name, self.lo(tagid), loudness, loudness_limit))
        if (savejpg):
            timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            cv2.imwrite('./report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr), frame)
        self.pane_item_dict[pane_id][item]["Data"] = [frame, resultmsg]
        report_dict['Message'] = resultmsg
        return result, "" if result else "limit[%s]" % limit

    def todo_DECODE_AV1(self, name, pane_id, item, tagid, report_dict, *args):
        # tagid = "DECODE_AV1"
        # btime = time.time()
        resultmsg = ""
        adb = self.pane_all[pane_id]["Class"]
        try:
            # mode = int(self.conf_dict[tagid]["mode"])
            limit = float(self.conf_dict[tagid]["limit"])
            hitlimit = int(self.conf_dict[tagid]["hit_limit"])
            capnum = self.conf_dict[tagid]["len"]  # 复用于match算法的匹配时长
            quality = float(self.conf_dict[tagid]["quality"])
            set2k = self.conf.getboolean(tagid, "set2k")
            loudness_limit = self.conf_dict[tagid]["loudness_limit"]
            savejpg = int(self.conf.getboolean(tagid, "save"))
            sour_num = int(self.conf_dict[tagid]["source_id"])
            samplefile = "Sample%d.pkl" % sour_num  # DECODE_AV1 播放指定的视频源(带杜比)
            wavename = './report/%s %s %s.wav' % (
            tagid, name, time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not os.path.exists(samplefile)):
            logger.critical("Config Sample Not Found %s" % self.lo("Error"))
            return False, "SampleNotFound"
        self.hdmilock.acquire()
        # 增加的视频解码测试
        adb.hdmiPlay(sour_num, self.hdmi_delay)  # DECODE_AV1 播放指定的视频源(带杜比)
        ret, frame, result, resultmsg = self.cap_ahash_match(pane_id, samplefile, limit, float(capnum), quality,
                                                             hitlimit,
                                                             set2k)
        if (loudness_limit):
            ret_name, rec_dev = self.dev_class.get_hdmi_rec(pane_id)  # A1~An
            if (not ret_name):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, "RecNotFound"
            self.reclock.acquire()
            logger.debug("HDMI Reclock Lock.")
            rate, data, buffer = self.sound_rec(rec_dev, float(capnum), wavename)
            # self.hdmilock.release()
            self.reclock.release()
            logger.debug("HDMI Reclock Release.")
        adb.hdmiStop()
        self.hdmilock.release()
        # result = True
        # self.pane_dict_report[pane_id][tagid] = {"result": result}
        if (result and loudness_limit):
            loudness_limit_f = float(loudness_limit)
            meter = pyln.Meter(rate)
            loudness = meter.integrated_loudness(data)
            result = bool(loudness >= loudness_limit_f)
            if (result):
                resultmsg += " Loudness:%.2f" % (loudness)
                logger.info("%s %s Loudness:%.2f" % (name, self.lo(tagid), loudness))
            else:
                resultmsg += " Loudness:%.2f[%s]" % (loudness, loudness_limit)
                logger.error("%s %s Loudness:%.2f[%s]" % (name, self.lo(tagid), loudness, loudness_limit))
        if (savejpg):
            timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            cv2.imwrite('./report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr), frame)
        self.pane_item_dict[pane_id][item]["Data"] = [frame, resultmsg]
        report_dict['Message'] = resultmsg
        return result, "" if result else "limit[%s]" % limit

    def todo_DECODE_WEBM(self, name, pane_id, item, tagid, report_dict, *args):
        # tagid = "DECODE_WEBM"
        # btime = time.time()
        resultmsg = ""
        adb = self.pane_all[pane_id]["Class"]
        try:
            # mode = int(self.conf_dict[tagid]["mode"])
            limit = float(self.conf_dict[tagid]["limit"])
            hitlimit = int(self.conf_dict[tagid]["hit_limit"])
            capnum = self.conf_dict[tagid]["len"]  # 复用于match算法的匹配时长
            quality = float(self.conf_dict[tagid]["quality"])
            set2k = self.conf.getboolean(tagid, "set2k")
            loudness_limit = self.conf_dict[tagid]["loudness_limit"]
            savejpg = int(self.conf.getboolean(tagid, "save"))
            sour_num = int(self.conf_dict[tagid]["source_id"])
            samplefile = "Sample%d.pkl" % sour_num  # DECODE_H264 播放指定的视频源(带杜比)
            wavename = './report/%s %s %s.wav' % (
                tagid, name, time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not os.path.exists(samplefile)):
            logger.critical("Config Sample Not Found %s" % self.lo("Error"))
            return False, "SampleNotFound"
        self.hdmilock.acquire()
        # 增加的视频解码测试
        adb.hdmiPlay(sour_num, self.hdmi_delay)  # DECODE_H264 播放指定的视频源(带杜比)
        ret, frame, result, resultmsg = self.cap_ahash_match(pane_id, samplefile, limit, float(capnum), quality,
                                                             hitlimit,
                                                             set2k)
        if (loudness_limit):
            ret_name, rec_dev = self.dev_class.get_hdmi_rec(pane_id)  # A1~An
            if (not ret_name):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, "RecNotFound"
            self.reclock.acquire()
            logger.debug("HDMI Reclock Lock.")
            rate, data, buffer = self.sound_rec(rec_dev, float(capnum), wavename)
            # self.hdmilock.release()
            self.reclock.release()
            logger.debug("HDMI Reclock Release.")
        adb.hdmiStop()
        self.hdmilock.release()
        # result = True
        # self.pane_dict_report[pane_id][tagid] = {"result": result}
        if (result and loudness_limit):
            loudness_limit_f = float(loudness_limit)
            meter = pyln.Meter(rate)
            loudness = meter.integrated_loudness(data)
            result = bool(loudness >= loudness_limit_f)
            if (result):
                resultmsg += " Loudness:%.2f" % (loudness)
                logger.info("%s %s Loudness:%.2f" % (name, self.lo(tagid), loudness))
            else:
                resultmsg += " Loudness:%.2f[%s]" % (loudness, loudness_limit)
                logger.error("%s %s Loudness:%.2f[%s]" % (name, self.lo(tagid), loudness, loudness_limit))
        if (savejpg):
            timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            cv2.imwrite('./report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr), frame)
        self.pane_item_dict[pane_id][item]["Data"] = [frame, resultmsg]
        report_dict['Message'] = resultmsg
        return result, "" if result else "limit[%s]" % limit

    def todo_HDMI_VIDEO(self, name, pane_id, item, tagid, report_dict, *args):
        # tagid = "HDMI_VIDEO"
        # btime = time.time()
        resultmsg = ""
        adb = self.pane_all[pane_id]["Class"]
        if (not adb.palystate): adb.hdmiPlay(self.hdmi_sour, self.hdmi_delay)
        try:
            mode = int(self.conf_dict[tagid]["mode"])
            limit = float(self.conf_dict[tagid]["limit"])
            hitlimit = int(self.conf_dict[tagid]["hit_limit"])
            capnum = self.conf_dict[tagid]["len"]  # 复用于match算法的匹配时长
            quality = float(self.conf_dict[tagid]["quality"])
            set2k = self.conf.getboolean(tagid, "set2k")
            savejpg = int(self.conf.getboolean(tagid, "save"))
            sour_num = int(self.conf_dict["SETTING"]["hdmi_source"])
            samplefile = "Sample%d.pkl" % (sour_num)
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not os.path.exists(samplefile)):
            logger.critical("Config Sample Not Found %s" % self.lo("Error"))
            return False, ''
        self.hdmilock.acquire()
        # 增加的视频算法通过mode切换
        if (mode == 0):
            ret, frame, result = self.cap_ahash(pane_id, self.samplehash, limit, int(capnum), 30, set2k)
        else:
            ret, frame, result, resultmsg = self.cap_ahash_match(pane_id, samplefile, limit, float(capnum), quality,
                                                                 hitlimit,
                                                                 set2k)
        self.hdmilock.release()
        # result = True
        # self.pane_dict_report[pane_id][tagid] = {"result": result}
        if (savejpg):
            timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            cv2.imwrite('./report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr), frame)
        self.pane_item_dict[pane_id][item]["Data"] = [frame, resultmsg]
        report_dict['Message'] = resultmsg
        # self.pane_item_dict[pane_id][item]["msg"](item,pane_id,"xxx")
        # logger.info("Elapsed Time: %.3f s" % (time.time() - btime))
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s limit[%s] FAIL" % (name, self.lo(tagid), limit))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, "msg": resultmsg}
        return result, "" if result else "limit[%s]" % limit

    def todo_RESOLUTION(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            num_limit = self.conf_dict[tagid]["limit"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        ret, ls = adb.getResolution()
        result = len(ls) >= int(num_limit)
        logger.debug("%s %s" % (name, ls))
        # logger.info("%s %s %s[%s]"%(name,self.lo(tagid),len(ls),num_limit))
        self.pane_item_dict[pane_id][item]["Data"] = "%s\r\n\r\nSUM:%d [Limit:%s]" % (ls, len(ls), num_limit)
        report_dict['resolution'] = ";".join(ls)
        # if (result):
        #     logger.warning("%s %s %s[%s] PASS" % (name, self.lo(tagid), len(ls), num_limit))
        # else:
        #     logger.error("%s %s %s[%s] FAIL" % (name, self.lo(tagid), len(ls), num_limit))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'resolution': ";".join(ls)}
        return result, '%s[%s]' % (len(ls), num_limit)

    def todo_LED_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "LED_TEST"
        # btime = time.time()
        try:
            auto = int(self.conf_dict[tagid]["auto"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            dute_time = float(self.conf_dict[tagid]["dute_time"])
            exposures = self.conf_dict[tagid]["exposure"].split(",")
            values = self.conf_dict[tagid]["values"].split(",")
            tags = self.conf_dict[tagid]["colors"].split(",")
            savejpg = int(self.conf.getboolean(tagid, "save"))
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (auto == 1):
            # 读取识别结果并比较
            result = True
            cap = self.led_cap_open(pane_id)
            if (cap.isOpened()):
                for i, t in enumerate(values):
                    cap.set(15, int(exposures[i]))
                    adb.ledtest(t)
                    time.sleep(dute_time)
                    ret, frame, tagframe, tagdata, = self.led_circle_roi(cap, True, circle_para=(200, 40, 30, 70, 100))
                    if (ret):
                        get, color = self.get_color_name(tagframe)
                    else:
                        get, color = "灭", 'off'
                    judge = get == tags[i]
                    result = result and judge
                    if (judge):
                        logger.debug("%s %s %s(%s):%s" % (name, self.lo(tagid), tags[i], t, judge))
                    else:
                        logger.debug("%s %s %s(%s):%s [%s]" % (name, self.lo(tagid), tags[i], t, judge, get))
                        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                        cv2.imwrite("./log/Err[%d] %s[%s] %s.jpg" % (pane_id + 1, t, i, timestr), frame)
                        break
                show_msg = "%s %s %s(%s):%s" % (name, self.lo(tagid), tags[i], t, judge)
                self.pane_item_dict[pane_id][item]["Data"] = [frame, show_msg]
                if (savejpg):
                    timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                    cv2.imwrite('./report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr),
                                frame)
            else:
                result = False
                logger.critical("Capture Open Error")
        else:
            askret = {"PASS": False, 'FAIL': False}
            self.blist_ask(item, pane_id, askret)
            while self.main_run and not adb.error and not (askret["PASS"] or askret['FAIL']):
                for v in values:
                    adb.ledtest(v)
                    time.sleep(dute_time)
            result = askret["PASS"]
        # self.pane_item_dict[pane_id][item]["Data"] = "Detect :%s\r\n Require :%s"%(data,keycodes)
        adb.ledfinish()
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s FAIL" % (name, self.lo(tagid)))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime}
        return result, ''

    def todo_BUTTON_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "BUTTON_TEST"
        btime = time.time()
        try:
            auto = int(self.conf_dict[tagid]["auto"])
            dute = float(self.conf_dict[tagid]["dute"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            keycodes = self.conf_dict[tagid]["keycodes"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (auto == 1):
            try:
                # 控制自动按键,波特率9600打开串口，发送“BUTTON_ON” 按键开启 ，串口返回“OK”；发送“BUTTON_OF”F 按键关闭，串口返回“OK
                ports = self.conf_dict[tagid]["ports"].split(',')
                ctl_m = control_com(ports[pane_id])
                ctl_m.open()
                time.sleep(dute)
                ctl_m.click()
            except:
                logger.critical("Button Control COM Error")
            finally:
                ctl_m.close()
            result, data = adb.buttontest()  # buttonResult_SUCCESS_19,20,21,22,8,9,10,11
            if (result):
                for k in keycodes.split(','):  # 有一个要求的按键不存在即FAIL
                    if not k in data:
                        result = False
                        break
        elif (auto == 2):
            result, data = adb.buttontest()  # buttonResult_SUCCESS_19,20,21,22,8,9,10,11
            if (result):
                for k in keycodes.split(','):  # 有一个要求的按键不存在即FAIL
                    if not k in data:
                        result = False
                        break
            if (not result):
                # screenwidth = self.master.winfo_screenwidth()
                # screenheight = self.master.winfo_screenheight()
                # width = 300
                # height = 100
                # size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
                # _set = {"title":name,"geometry": size,"func":adb.buttontest,"keycodes":keycodes,"timeout":timeout}
                _set = {"title": name, "func": adb.buttontest, "keycodes": keycodes, "timeout": timeout}
                boxresult = {"Result": False, "Data": ""}
                result, data = self.show_box_class(Func_Loop_Box, setting=_set, result=boxresult)
                # wait_box=Func_Loop_Box(self.master,setting=_set, result=boxresult)
                # self.master.wait_window(wait_box)  # 停止执行 阻塞 该行代码
                # result = boxresult["Result"]
                # data = boxresult["Data"]
        else:
            elpstime = round(time.time() - btime, 3)
            while self.main_run and elpstime < timeout:
                result, data = adb.buttontest()  # buttonResult_SUCCESS_19,20,21,22,8,9,10,11
                if (result):
                    for k in keycodes.split(','):  # 有一个要求的按键不存在即FAIL
                        if not k in data:
                            result = False
                            break
                if (result):
                    break
                else:
                    time.sleep(0.5)
                    # elpstime = round(time.time() - btime, 3)
                    # self.blist_msg(item,pane_id,"等待按钮%d"%(timeout-elpstime))  # 动态显示
            # self.blist_msg(item,pane_id,self.lo(tagid))  # 动态显示
        self.pane_item_dict[pane_id][item]["Data"] = "Keycode Detect :%s\r\n Require :%s" % (data, keycodes)
        # if (result):
        #     logger.warning("%s %s %s PASS" % (name, self.lo(tagid), data))
        # else:
        #     logger.error("%s %s %s[%s] FAIL" % (name, self.lo(tagid), data, keycodes))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime}
        return result, '%s' % data if result else '%s[%s]' % (data, keycodes)

    def todo_BASIC_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "BASIC_TEST"
        # btime = time.time()
        try:
            cpu_type_match = self.conf_dict[tagid]["cpu_type_match"]
            cpu_temp_min = self.conf_dict[tagid]["cpu_temp_min"]
            cpu_temp_max = self.conf_dict[tagid]["cpu_temp_max"]
            ddr_size_limit = self.conf_dict[tagid]["ddr_size_limit"]
            emmc_size_limit = self.conf_dict[tagid]["emmc_size_limit"]
            hw_id_match = self.conf_dict[tagid]["hw_id_match"]
            hw_ver_match = self.conf_dict[tagid]["ver_match"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        msg = []
        err = []
        result = True
        if cpu_type_match:
            ret, data = adb.getCpuType()
            report_dict["CPU"] = data
            if ret and cpu_type_match in data:
                msg.append("CPU:%s" % data)
            else:
                result = False
                msg.append("CPU:%s[%s]" % (data, cpu_type_match))
                err.append("CPU:%s[%s]" % (data, cpu_type_match))
        if cpu_temp_min and cpu_temp_max:
            ret, data = adb.getCpuTemp()
            report_dict["Temp"] = data
            if ret and float(cpu_temp_max) >= float(data) >= float(cpu_temp_min):
                msg.append("Temp:%s" % data)
            else:
                result = False
                msg.append("Temp:%s[%s,%s]" % (data, cpu_temp_min, cpu_temp_max))
                err.append("Temp:%s[%s,%s]" % (data, cpu_temp_min, cpu_temp_max))
        if ddr_size_limit:
            ret, data = adb.getDDR()
            report_dict["DDR"] = data
            if ret and int(data) >= int(ddr_size_limit):
                msg.append("DDR:%s" % data)
            else:
                result = False
                msg.append("DDR:%s[%s]" % (data, ddr_size_limit))
                err.append("DDR:%s[%s]" % (data, ddr_size_limit))
        if emmc_size_limit:
            ret, data = adb.getEMMC()
            report_dict["EMMC"] = data
            if ret and int(data) >= int(emmc_size_limit):
                msg.append("EMMC:%s" % data)
            else:
                result = False
                msg.append("EMMC:%s[%s]" % (data, emmc_size_limit))
                err.append("EMMC:%s[%s]" % (data, emmc_size_limit))
        if hw_id_match:
            ret, data = adb.gethwid()
            report_dict["ID"] = data
            if ret and hw_id_match in data:
                msg.append("ID:%s" % data)
            else:
                result = False
                msg.append("ID:%s[%s]" % (data, hw_id_match))
                err.append("ID:%s[%s]" % (data, hw_id_match))
        if hw_ver_match:
            ret, data = adb.gethwver()
            report_dict["VER"] = data
            if ret and hw_ver_match in data:
                msg.append("VER:%s" % data)
            else:
                result = False
                msg.append("VER:%s[%s]" % (data, hw_ver_match))
                err.append("VER:%s[%s]" % (data, hw_ver_match))

        logger.debug("%s %s" % (name, " ".join(msg)))

        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s %s FAIL" % (name, self.lo(tagid), " ".join(err)))

        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # report["result"] = result
        # report["elpstime"] = elpstime
        # self.pane_dict_report[pane_id][tagid] = report
        return result, "" if result else " ".join(err)

    def todo_SCANNER(self, name, pane_id, item, tagid, report_dict, *args):
        showsn = self.pane_all[pane_id]["BoxidVstr"]
        adb = self.pane_all[pane_id]["Class"]
        scan_now = ''
        try:
            mode = self.conf_dict["SCANNER"]["mode"]
            getkeys = self.conf_dict["SCANNER"]["getkeys"].upper()
            retry = int(self.conf_dict["SCANNER"]["retry"])
            len_limit = int(self.conf_dict["SCANNER"]["len"])
            match = self.conf_dict[tagid]["match"]
            sn_match = self.conf_dict[tagid]["sn_match"]
            boxid_match = self.conf_dict[tagid]["boxid_match"]
            emac_match = self.conf_dict[tagid]["emac_match"]
            wmac_match = self.conf_dict[tagid]["wmac_match"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not mode.isdigit()):  # 非数字模式,读取Key值,usid(sn),mac,wmac,fbxserial,oem
            judge, scan_now = adb.sendcmd_recv2("readKeyValue", mode)
            logger.debug("Read %s=%s %s" % (mode, scan_now, judge))
        elif (mode == "0"):  # 模式0 读取界面控件当前显示
            scan_now = name
        elif (mode == '00'):  # 模式00 读取临时SN.txt
            scan_now = adb.getTempSN()
        elif (mode == '1'):  # 模式1 扫码Box
            # scan_now = self.pane_all[pane_id]["ScanIn"]
            tip = "%s USB_%s" % (self.lo(tagid), self.pane_all[pane_id]["Tid"])
            self.scanlock.acquire()
            try:
                self.set_guide("WaitScan", "%s [%s]" % (tip, name))
                scan_now = self.show_box(name, tip)
                self.set_guide()
            except:
                scan_now = self.show_box(name, tip)
            self.scanlock.release()
        elif (mode == '11'):  # 模式11 扫码Box
            tip = "%s Camera_%s" % (self.lo(tagid), self.pane_all[pane_id]["Tid"])
            self.scanlock.acquire()
            try:
                self.set_guide("WaitScan", "%s [%s]" % (tip, name))
                scan_now = self.show_box(name, tip)
                self.set_guide()
            except:
                scan_now = self.show_box(name, tip)
            self.scanlock.release()
        elif (mode == '111'):  # 模式1 扫码Box 扫描并写入boxid
            # scan_now = self.pane_all[pane_id]["ScanIn"]
            tip = "%s USB_%s" % (self.lo(tagid), self.pane_all[pane_id]["Tid"])
            self.scanlock.acquire()
            try:
                self.set_guide("WaitScan", "%s [%s]" % (tip, name))
                scan_now = self.show_box(name, tip)
                if (scan_now):
                    adb.setBoxid(scan_now)
                self.set_guide()
            except:
                scan_now = self.show_box(name, tip)
            self.scanlock.release()
        elif (mode == "2"):  # 模式2 流程需要重新扫码 串口接收 AutoBurnKey使用
            self.scanlock.acquire()
            if (self.isRemove(pane_id) or not self.main_run):  # 强制中断
                logger.debug("[Abort]SCANNER %s" % name)
                self.scanlock.release()
                return False, ''
            try:
                portname = self.pane_all[pane_id]["Tid"]
                self.set_guide("WaitScan", "USB_%s [%s]" % (portname, name))
                port = self.conf_dict["SCANNER"]["port"]
                scanner = scan_com(port)
                if (scanner.open()):
                    ret = False
                    while not ret:
                        ret, value = scanner.scan(3)
                        if (ret):
                            break
                        if (self.isRemove(pane_id) or not self.main_run):  # 强制中断
                            value = b""
                            logger.debug("[Abort]Scanning %s" % name)
                            break
                    scan_now = value.decode().strip()
                    scanner.close()
                else:
                    logger.critical("Scanner Open Error 扫码设备错误")
                    scan_now = None
            except Exception as e:
                pass
                print(e)
            finally:
                self.set_guide()
                self.scanlock.release()
        elif (mode == "22"):  # 模式2 流程需要重新扫码  AutoBurnKey调试1个DUT时自动扫码
            judge, scan_now = adb.sendcmd_recv2("readKeyValue", 'usid')
            if (scan_now and len(scan_now) < 13):
                judge, scan_now = adb.sendcmd_recv2("readKeyValue", 'fbxserial')
            logger.debug("[DUT]%s %s %s" % (
                scan_now, adb.sendcmd_recv2("readKeyValue", 'mac'), adb.sendcmd_recv2("readKeyValue", 'wmac')))
            # time.sleep(2)
        elif (mode == "3"):  # 模式3 支持在流程前扫码 如没有记录需重新扫码(RouterControl暂不支持)是否测A扫B防呆？
            value = self.pane_all[pane_id]["ScanIn"]
            if (not value):
                scanner = self.pane_all[pane_id]["Scanner"]
                value = scanner.scan(-1)
            scan_now = value.decode().strip()
        elif (mode == "4"):  # 模式4 流程需要重新扫码:自动扫码
            ret, port = self.dev_class.get_scan_name(pane_id)  # COM scan
            if (not ret):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, ''
            scanner = scan_com(port)
            if (scanner.open()):
                for i in range(retry):
                    value = scanner.trig_recv()
                    if (len(value) >= len_limit):
                        if (match):
                            if (match in value):
                                break
                        else:
                            break
                scan_now = value
                scanner.close()
            else:
                logger.critical("Scanner Open Error 扫码设备错误")
                scan_now = None
        elif (mode == "6"):  # 模式6 流程需要重新扫码  AutoRouterCouple从路由板子读取SN
            for i in range(retry):
                scan_now = adb.telnet_gpon140_cmd("prolinecmd xponsn display")
                logger.debug("[Router]xponsn:%s" % scan_now)
                judge = bool(scan_now)
                if (judge): break
        elif (mode == "77"):  # freebox通过boxid获取emac,然后仍然使用emac过站
            scan_now = self.mes.GetByboxid(name)
        elif (mode == "7"):  # 模式7 使用GetKeys切换过站SN
            scan_now = self.mes.GetKeys(name, 1)  # freebox 使用emac过站
        else:  # 其他模式=模式0
            scan_now = name
        showsn.set(scan_now)
        # 按模式读取扫码记录,对比sn,mac
        mesjudge = self.mes.CheckSN(scan_now)
        if (getkeys == "EMAC"):
            _sn, _emac, _wmac = self.mes.GetMac(scan_now, 1)
            report_dict["EMAC"] = _emac
        elif (getkeys == "WMAC"):
            _sn, _emac, _wmac = self.mes.GetMac(scan_now, 2)
            report_dict["WMAC"] = _wmac
        elif (getkeys == "EMAC,WMAC"):
            _sn, _emac, _wmac = self.mes.GetMac(scan_now, 3)
            report_dict["EMAC"] = _emac
            report_dict["WMAC"] = _wmac
        _msg = []
        loadsn = name
        sn = scan_now
        result = bool(scan_now) and mesjudge
        _msg.append("Scanner: %s" % scan_now)
        _msg.append("Load : %s " % loadsn)
        _msg.append("MES: %s" % mesjudge)
        if (result):
            result = loadsn == name
            _msg.append("Boxid: %s [%s]" % (loadsn, name))
        else:
            logger.error("%s %s Boxid:%s[%s] Not Match" % (name, self.lo(tagid), loadsn, name))
        if (result and "EMAC" in report_dict):
            if (emac_match):
                result = emac_match in report_dict["EMAC"]
                _msg.append("eMAC:%s [%s]" % (report_dict["EMAC"], emac_match))
                if (not result):
                    logger.error(
                        "%s %s eMAC:%s[%s] Not Match" % (name, self.lo(tagid), report_dict["EMAC"], emac_match))
            else:
                _msg.append("eMAC:%s " % (report_dict["EMAC"]))
        if (result and "WMAC" in report_dict):
            if (wmac_match):
                result = wmac_match in report_dict["WMAC"]
                _msg.append("wMAC: %s [%s]" % (report_dict["WMAC"], wmac_match))
                if (not result):
                    logger.error(
                        "%s %s wMAC:%s[%s] Not Match" % (name, self.lo(tagid), report_dict["WMAC"], wmac_match))
            else:
                _msg.append("wMAC: %s " % (report_dict["WMAC"]))
        logger.debug("%s Input %s [%s]" % (name, scan_now, loadsn))
        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(_msg)
        report_dict['scan'] = scan_now
        report_dict['BOXID'] = loadsn
        report_dict['SN'] = sn
        # 提前自动执行预触发,混合产测APK的多线程
        for p in self.plan:
            if (p == "BT_TEST"):
                try:
                    btname = self.conf_dict["BT_TEST"]["name"]
                    if (" " in btname):
                        btname = "'%s'" % btname
                    connect = int(self.conf_dict["BT_TEST"]["connect"])
                    ret = adb.bt_begin(btname, connect)
                    logger.debug("%s %s Begin..%s" % (name, self.lo("BT_TEST"), ret))
                except Exception as e:
                    print(e)
            if (p == "WIFI_5"):
                try:
                    ssid = self.conf_dict["WIFI_5"]["ssid"]
                    key = self.conf_dict["WIFI_5"]["key"]
                    type = self.conf_dict["WIFI_5"]["type"]
                    connect = int(self.conf_dict["WIFI_5"]["connect"])
                    ret = adb.wifi_begin(ssid, key, type, connect)
                    logger.debug("%s %s Begin..%s" % (name, self.lo("WIFI_5"), ret))
                except Exception as e:
                    print(e)
            if (p == "WIFI_24"):
                try:
                    ssid = self.conf_dict["WIFI_24"]["ssid"]
                    key = self.conf_dict["WIFI_24"]["key"]
                    type = self.conf_dict["WIFI_24"]["type"]
                    connect = int(self.conf_dict["WIFI_24"]["connect"])
                    ret = adb.wifi_begin(ssid, key, type, connect)
                    logger.debug("%s %s Begin..%s" % (name, self.lo("WIFI_24"), ret))
                except Exception as e:
                    print(e)
        return result, '%s[%s]' % (scan_now, loadsn)

    def todo_FTP(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "FTP"
        # btime = time.time()
        try:
            host = self.conf_dict[tagid]["host"]
            port = int(self.conf_dict[tagid]["port"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            user = self.conf_dict[tagid]["user"]
            key = self.conf_dict[tagid]["key"]
            sub_dir = self.conf_dict[tagid]["sub_dir"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        try:
            local_path = self.save_report(pane_id, True)  # 在测试序列中,FAIL的流程无法跑到FTP测试项
            ftp = FTP()
            # ftp.encoding="utf-8"
            ftp.connect(host, port, timeout=timeout)  # 第一个参数可以是ftp服务器的ip或者域名，第二个参数为ftp服务器的连接端口，默认为21
            ftp.login(user, key)  # 匿名登录直接使用ftp.login()
            # ftp.set_pasv(False)
            ftp.cwd("./%s" % sub_dir)  # 切换目录
            _path, filename = os.path.split(local_path)
            logger.debug("%s %s Ready for upload.." % (name, self.lo(tagid)))
            try:
                with open(local_path, "rb") as fp:
                    ftp.storbinary("STOR {}".format(filename), fp)
                result = True
            except Exception as e:
                logger.critical("Upload Files Error")
                logger.critical(e)
                result = False
            logger.debug("%s %s Upload Finish" % (name, self.lo(tagid)))
            ftp.quit()
        except Exception as e:
            logger.critical(e)
            result = False
        # self.pane_item_dict[pane_id][item]["Data"] = " SN: %s\r\nMAC: %s" % (getsn, getmac)
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s FAIL" % (name, self.lo(tagid)))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime}
        return result, ''

    def todo_HDMI_VOLT(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "HDMI_VOLT"
        # btime = time.time()
        try:
            # portlist = self.conf_dict[tagid]["portlist"]
            # port = portlist.split(',')[pane_id]
            volt_min = float(self.conf_dict[tagid]["volt_min"])
            volt_max = float(self.conf_dict[tagid]["volt_max"])
            cec_retry = int(self.conf_dict[tagid]["cec_retry"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        try:
            # 检测电压
            ret, port = self.dev_class.get_com_name(pane_id)  # COM
            if (not ret):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, ''
            volt_m = volt_com(port)
            volt_m.open()
            time.sleep(0.2)
            value = volt_m.getVolt_H()
            if (value == None):
                pass
            else:
                time.sleep(0.2)
                value = volt_m.getVolt_H()
            # CEC信号测试
            cec_judge = False
            for r in range(cec_retry):
                adb.cecTest()  # 底层有2秒延时后发出信号,产测APK5.0.34.2以后更新1.5秒
                time.sleep(1)
                volt_m.ser.write("C".encode())
                time.sleep(1)
                ret = volt_m.ser.readline().strip()
                if (b"" == ret):
                    time.sleep(1)
                    ret = volt_m.ser.readline().strip()
                out = ret.decode()
                logger.debug(out.strip())
                if ("CEC" in out):
                    cec_judge = "_P" in out
                    if (cec_judge):
                        break
            volt_m.close()
            result = cec_judge and volt_min <= value <= volt_max
            logger.info("%s %s Voltage:%s[%s,%s] CEC:%s" % (name, self.lo(tagid), value, volt_min, volt_max, cec_judge))
        except Exception as e:
            value = None
            result = False
            logger.critical(e)
        self.pane_item_dict[pane_id][item]["Data"] = "Voltage:%s[%s,%s]\r\nCEC:%s" % (
            value, volt_min, volt_max, cec_judge)
        report_dict['voltage'] = value
        report_dict['cec'] = cec_judge
        # if (result):
        #     logger.warning("%s %s Voltage:%s CEC:%s PASS" % (name, self.lo(tagid), value, cec_judge))
        # else:
        #     logger.error(
        #         "%s %s Voltage:%s[%s,%s] CEC:%s FAIL" % (name, self.lo(tagid), value, volt_min, volt_max, cec_judge))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'voltage': value,
        #                                          "cec": cec_judge}
        return result, 'Voltage:%s CEC:%s' % (value, cec_judge) if result else "Voltage:%s[%s,%s] CEC:%s" % (
            value, volt_min, volt_max, cec_judge)

    def todo_DVB_VOLT(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "DVB_VOLT"
        # btime = time.time()
        try:
            # portlist = self.conf_dict[tagid]["portlist"]
            # port = portlist.split(',')[pane_id]
            cmd_list = self.conf_dict[tagid]["cmd_list"].split(',')
            volt_retry = int(self.conf_dict[tagid]["volt_retry"])
            dute_delay = float(self.conf_dict[tagid]["dute_delay"])
            enable_22k = int(self.conf_dict[tagid]["enable_22k"])
            volt_min_list = self.conf_dict[tagid]["volt_min_list"].split(',')
            volt_max_list = self.conf_dict[tagid]["volt_max_list"].split(',')
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        msg = []
        result = True
        try:
            self.dvblock.acquire()  # dvb电压加资源锁,优化效果好像不明显
            if (cmd_list and len(cmd_list) > 1):
                ret, port = self.dev_class.get_com_name(pane_id)  # COM dvb
                if (not ret):
                    logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                    return False, ''
                volt_m = volt_com(port)
                volt_m.open()
                time.sleep(0.2)
                for i, cmd in enumerate(cmd_list):
                    # 输出电压
                    adb.dvb_volt(cmd)
                    # 检测电压
                    volt_min = float(volt_min_list[i])
                    volt_max = float(volt_max_list[i])
                    for j in range(volt_retry):
                        time.sleep(dute_delay)
                        value = volt_m.getVolt_D()
                        if (value == None):
                            pass
                        else:
                            judge = volt_min <= value <= volt_max
                            if (judge):
                                break
                    msg.append("%s[%s,%s]" % (value, volt_min, volt_max))
                    result = result and judge
                    logger.info(
                        "%s %s CMD:%s Voltage:%s[%s,%s]" % (name, self.lo(tagid), cmd, value, volt_min, volt_max))
                    if (enable_22k and 12 <= value <= 14):  # DVB输出13v的时候同时检测22k
                        check22k = volt_m.getK()
                        result = result and check22k
                        logger.info("%s %s 22K:%s" % (name, self.lo(tagid), check22k))
                        msg.append("22K[%s]" % check22k)
                volt_m.close()
            else:
                result = False
                logger.critical("DVB_VOLT Config cmd_list Not Match")
        except Exception as e:
            result = False
            logger.critical(e)
        finally:
            pass
            self.dvblock.release()
        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
        report_dict['Message'] = ",".join(msg)
        # if (result):
        #     logger.warning("%s %s Voltage:%s PASS" % (name, self.lo(tagid), ",".join(msg)))
        # else:
        #     logger.error("%s %s Voltage:%s FAIL" % (name, self.lo(tagid), ",".join(msg)))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'msg': ",".join(msg)}
        return result, "Voltage:%s" % (",".join(msg))

    def todo_DVB(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "DVB"
        # btime = time.time()
        resultmsg = ""
        try:
            playlist = self.conf_dict[tagid]["playlist"].split(",")
            sampletag = self.conf_dict[tagid]["sampletag"]
            samplefile = "SampleDVB%s.pkl" % sampletag
            cap_delay = float(self.conf_dict[tagid]["cap_delay"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            timelen = float(self.conf_dict[tagid]["len"])
            limit = float(self.conf_dict[tagid]["limit"])
            hitlimit = int(self.conf_dict[tagid]["hit_limit"])
            quality = float(self.conf_dict[tagid]["quality"])
            savejpg = int(self.conf.getboolean(tagid, "save"))
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (not os.path.exists(samplefile)):
            logger.critical("Config Sample Not Found %s" % self.lo("Error"))
            return False, ''
        # 检测视频播放
        try:
            if (adb.dvb_open()):
                time.sleep(1)
                for i in playlist:
                    logger.debug("%s %s DVB[%s] Play.." % (name, self.lo(tagid), i))
                    if (adb.dvb_play(i)):
                        time.sleep(cap_delay)
                        logger.debug("%s %s DVB[%s] Start Capture.." % (name, self.lo(tagid), i))
                        self.hdmilock.acquire()
                        ret, frame, result, resultmsg = self.cap_ahash_match(pane_id, samplefile, limit, timelen,
                                                                             quality,
                                                                             hitlimit)
                        self.hdmilock.release()
                        if (savejpg):
                            timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
                            cv2.imwrite(
                                './report/%s %s %s %s.jpg' % ("PASS" if result else "FAIL", tagid, name, timestr),
                                frame)
                        self.pane_item_dict[pane_id][item]["Data"] = [frame, resultmsg]
                        if (result):
                            for j in range(timeout):
                                result = adb.dvb_result(i)
                                if (result):
                                    logger.debug("%s %s DVB[%s] Return PASS" % (name, self.lo(tagid), i))
                                    break
                                else:
                                    time.sleep(1)
                            if (not result):
                                logger.critical("%s %s DVB[%s] Return FAIL" % (name, self.lo(tagid), i))
                        else:
                            break
            else:
                result = False
                logger.critical("%s %s DVB Open Error" % (name, self.lo(tagid)))
            adb.dvb_close()
        except Exception as e:
            logger.critical(e)
            result = False
        finally:
            adb.dvb_close()
        report_dict["Message"] = resultmsg
        # self.pane_item_dict[pane_id][item]["Data"] = " SN: %s\r\nMAC: %s" % (getsn, getmac)
        # result = False
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s FAIL" % (name, self.lo(tagid)))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, "msg": resultmsg}
        return result, ''

    def todo_SPDIF_AUDIO(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        if (not adb.palystate): adb.hdmiPlay(self.hdmi_sour, self.hdmi_delay)
        # tagid = "SPDIF_AUDIO"
        # btime = time.time()
        timestr = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        wavename = './report/%s %s %s.wav' % (tagid, name, timestr)
        # report = {"result": False, "elpstime": 0}
        try:
            vmax_limit = self.conf_dict[tagid]["vmax_limit"]
            loudness_limit = self.conf_dict[tagid]["loudness_limit"]
            len = float(self.conf_dict[tagid]["len"])
            psd_enable = int(self.conf_dict[tagid]["psd_enable"])
            p_limit1 = float(self.conf_dict[tagid]["p_limit1"])
            judge1 = list(map(float, [i for i in self.conf_dict[tagid]["judge1"].split(',')]))
            p_limit2 = float(self.conf_dict[tagid]["p_limit2"])
            judge2 = list(map(float, [i for i in self.conf_dict[tagid]["judge1"].split(',')]))
            judge_offset = float(self.conf_dict[tagid]["offset"])
            savewave = self.conf.getboolean(tagid, "save")
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        try:
            ret_name, rec_dev = self.dev_class.get_spdif_rec(pane_id)  # Record Device Name = S1~Sn
            if (not ret_name):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, ''
            self.reclock.acquire()
            time.sleep(0.2)
            logger.debug("SPDIF Rec Lock.")
            rate, data, buffer = self.sound_rec(rec_dev, len, wavename)
            self.reclock.release()
            logger.debug("SPDIF Rec Release.")
            # if(os.path.exists(wavename)):
            # rate, data = wavfile.read(wavename)
            msg = []
            if (rate):
                # 最大值判断
                result = True
                if (vmax_limit):
                    vmax_limit_f = float(vmax_limit)
                    vmax = round(np.max(data), 4)
                    # vmax = round(np.max(data[:, 0]), 4)  # 多通道,需同步更新sound_rec
                    result = bool(vmax >= vmax_limit_f)
                    if (result):
                        msg.append("Vmax:%.3f" % (vmax))
                    else:
                        msg.append("Vmax:%.3f[%s]" % (vmax, vmax_limit))
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                    report_dict["Vmax"] = "%.3f" % (vmax)
                if (result and loudness_limit):
                    loudness_limit_f = float(loudness_limit)
                    meter = pyln.Meter(rate)
                    loudness = meter.integrated_loudness(data)
                    result = bool(loudness >= loudness_limit_f)
                    if (result):
                        msg.append("Loudness:%.2f" % (loudness))
                    else:
                        msg.append("Loudness:%.2f[%s]" % (loudness, loudness_limit))
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                    report_dict["Loudness"] = "%.2f" % (loudness)
                if (result):
                    if (psd_enable):
                        result, *showdata = self.check_wave(rate, data, p_limit1, judge1, p_limit2, judge2,
                                                            judge_offset)
                        self.pane_item_dict[pane_id][item]["Data"] = tuple(showdata)
                    else:
                        msg.append("PSD:Off")
                        self.pane_item_dict[pane_id][item]["Data"] = "\r\n".join(msg)
                if (savewave):
                    wavfile.write(wavename, rate, data)
            else:
                # logger.error("Not Found Record File %s" % wavename)
                result = False
            # result = True
            return result, "[%s]%s" % (ret_name, " ".join(msg))
            # if (result):
            #     logger.warning("%s [%s] %s %s PASS" % (name, ret_name, self.lo(tagid), " ".join(msg)))
            # else:
            #     logger.error("%s [%s] %s %s FAIL" % (name, ret_name, self.lo(tagid), " ".join(msg)))

        except Exception as e:
            logger.critical(e)
            logger.critical("%s %s" % (self.lo(tagid), self.lo("Error")))
            return False, ''
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # report["result"] = result
        # report["elpstime"] = elpstime
        # self.pane_dict_report[pane_id][tagid] = report
        # return result

    def todo_IR_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "IR_TEST"
        # btime = time.time()
        try:
            # portlist = self.conf_dict[tagid]["portlist"]
            retry = int(self.conf_dict[tagid]["retry"])
            # if (portlist):
            #     port = portlist.split(',')[pane_id]
            timeout = self.conf_dict[tagid]["timeout"]
            match = self.conf_dict[tagid]["match"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        # if (portlist):  # 启用外部模块
        try:
            ret, port = self.dev_class.get_ir_name(pane_id)  # COM ir
            if (not ret):
                logger.critical("%s %s Deploy[%d] Read Error" % (name, self.lo(tagid), pane_id))
                return False, ''
            ir = ir_com(port)
            ir.open()
            logger.debug("IR Module %s Send:%s" % (port, match))
            for i in range(retry):
                ir.sendkey(match)
                time.sleep(0.2)
                ret, code = adb.getIrKeyEvent(timeout=int(timeout))
                result = match in code
                if (result):
                    break
                else:
                    logger.debug("IR Module %s Send:%s Again[%d]" % (port, match, i + 2))
                    time.sleep(0.5)
            ir.close()
        except Exception as e:
            logger.critical(e)
        ret, code = adb.getIrKeyEvent(timeout=int(timeout))
        result = match in code
        logger.debug("%s KeyCode %s [%s]" % (name, code, match))
        # logger.info("%s %s %s[%s]"%(name,self.lo(tagid),len(ls),num_limit))
        self.pane_item_dict[pane_id][item]["Data"] = "KeyCode: %s        \r\n Match : %s" % (code, match)
        report_dict['keycode'] = code
        # if (result):
        #     logger.warning("%s %s %s[%s] PASS" % (name, self.lo(tagid), code, match))
        # else:
        #     logger.error("%s %s %s[%s] FAIL" % (name, self.lo(tagid), code, match))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'keycode': code}
        return result, '%s[%s]' % (code, match)

    def todo_BT_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "BT_TEST"
        # btime = time.time()
        try:
            btname = self.conf_dict[tagid]["name"]
            if (" " in btname):
                btname = "'%s'" % btname
            retry = int(self.conf_dict[tagid]["retry"])
            rssi_min = float(self.conf_dict[tagid]["rssi_min"])
            rssi_max = float(self.conf_dict[tagid]["rssi_max"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            connect = int(self.conf_dict[tagid]["connect"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        rssi = ''
        if (connect):
            logger.debug("%s Buletooth:%s Connect.." % (name, btname))
            ret = adb.bttest(btname)
            if (ret):
                ret, rssi = adb.getbttestres(timeout)
                if (ret):
                    logger.debug("%s Name:%s RSSI:%s[%s,%s]" % (name, btname, rssi, rssi_min, rssi_max))
                    result = rssi_min <= float(rssi) <= rssi_max
                    if (not result):
                        ret, rssi = adb.getwifirssi()
                        logger.debug("%s Name:%s RSSI:%s[%s,%s] Again" % (name, btname, rssi, rssi_min, rssi_max))
                        result = rssi_min <= float(rssi) <= rssi_max
                else:
                    logger.error("%s Get %s RSSI Error" % (name, btname))
                    result = False
                self.pane_item_dict[pane_id][item]["Data"] = "Name: %s \r\n RSSI : %s [%s,%s]" % (
                    btname, rssi, rssi_min, rssi_max)
            else:
                logger.error("%s Get IP[%s] Timeout" % (name, btname))
                result = False
        else:
            logger.debug("%s Scan:%s .." % (name, btname))
            for r in range(retry):
                ret, rssi = adb.btscan(btname, timeout)
                if (ret):
                    logger.debug("%s Scan %s RSSI:%s[%s,%s]" % (name, btname, rssi, rssi_min, rssi_max))
                    result = rssi_min <= float(rssi) <= rssi_max
                    if (result):
                        break
                else:
                    result = False
            self.pane_item_dict[pane_id][item]["Data"] = " Name: %s \r\n RSSI : %s [%s,%s]" % (
                btname, rssi, rssi_min, rssi_max)
        report_dict['rssi'] = rssi
        # if (result):
        #     logger.warning("%s %s RSSI:%s PASS" % (name, self.lo(tagid), rssi))
        # else:
        #     logger.error("%s %s RSSI:%s[%s,%s] FAIL" % (name, self.lo(tagid), rssi, rssi_min, rssi_max))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'rssi': rssi}
        return result, "RSSI:%s" % rssi if result else "RSSI:%s[%s,%s]" % (rssi, rssi_min, rssi_max)

    def todo_WIFI_5(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "WIFI_5"
        # btime = time.time()
        try:
            ssid = self.conf_dict[tagid]["ssid"]
            key = self.conf_dict[tagid]["key"]
            type = self.conf_dict[tagid]["type"]
            retry = int(self.conf_dict[tagid]["retry"])
            rssi_min = float(self.conf_dict[tagid]["rssi_min"])
            rssi_max = float(self.conf_dict[tagid]["rssi_max"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            connect = int(self.conf_dict[tagid]["connect"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        rssi = ''
        if (connect):
            ret = adb.conwifi(ssid, key, type)
            if (ret):
                ret, ip = adb.again(adb.getwifiip, retry, timeout)
                if (ret):
                    ret, rssi = adb.getwifirssi()
                    if (ret):
                        logger.debug("%s IP:%s RSSI:%s[%s,%s]" % (name, ip, rssi, rssi_min, rssi_max))
                        result = rssi_min <= float(rssi) <= rssi_max
                        if (not result):
                            ret, rssi = adb.getwifirssi()
                            logger.debug("%s IP:%s RSSI:%s[%s,%s] Again" % (name, ip, rssi, rssi_min, rssi_max))
                            result = rssi_min <= float(rssi) <= rssi_max
                    else:
                        logger.error("%s Get %s[%s] RSSI Error" % (name, ssid, ip))
                        result = False
                    self.pane_item_dict[pane_id][item]["Data"] = "IP: %s \r\n RSSI : %s [%s,%s]" % (
                        ip, rssi, rssi_min, rssi_max)
                else:
                    logger.error("%s Get IP[%s] Timeout" % (name, ssid))
                    result = False

            else:
                logger.error("%s Connect Error [%s]%s" % (name, ssid, key))
                result = False
        else:
            for r in range(retry):
                ret, rssi = adb.wifiscan(ssid, timeout)
                if (ret):
                    logger.debug("%s Scan %s RSSI:%s[%s,%s]" % (name, ssid, rssi, rssi_min, rssi_max))
                    result = rssi_min <= float(rssi) <= rssi_max
                    if (result):
                        break
                else:
                    result = False
            self.pane_item_dict[pane_id][item]["Data"] = " SSID: %s \r\n RSSI : %s [%s,%s]" % (
                ssid, rssi, rssi_min, rssi_max)
        report_dict['rssi'] = rssi
        # if (result):
        #     logger.warning("%s %s RSSI:%s PASS" % (name, self.lo(tagid), rssi))
        # else:
        #     logger.error("%s %s RSSI:%s[%s,%s] FAIL" % (name, self.lo(tagid), rssi, rssi_min, rssi_max))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'rssi': rssi}
        return result, 'RSSI:%s' % rssi if result else "RSSI:%s[%s,%s]" % (rssi, rssi_min, rssi_max)

    def todo_WIFI_24(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "WIFI_24"
        # btime = time.time()
        try:
            ssid = self.conf_dict[tagid]["ssid"]
            key = self.conf_dict[tagid]["key"]
            type = self.conf_dict[tagid]["type"]
            retry = int(self.conf_dict[tagid]["retry"])
            rssi_min = float(self.conf_dict[tagid]["rssi_min"])
            rssi_max = float(self.conf_dict[tagid]["rssi_max"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            connect = int(self.conf_dict[tagid]["connect"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        rssi = ''
        if (connect):
            ret = adb.conwifi(ssid, key, type)
            if (ret):
                ret, ip = adb.again(adb.getwifiip, retry, timeout)
                if (ret):
                    ret, rssi = adb.getwifirssi()
                    if (ret):
                        logger.debug("%s IP:%s RSSI:%s[%s,%s]" % (name, ip, rssi, rssi_min, rssi_max))
                        result = rssi_min <= float(rssi) <= rssi_max
                        if (not result):
                            ret, rssi = adb.getwifirssi()
                            logger.debug("%s IP:%s RSSI:%s[%s,%s] Again" % (name, ip, rssi, rssi_min, rssi_max))
                            result = rssi_min <= float(rssi) <= rssi_max
                    else:
                        logger.error("%s Get %s[%s] RSSI Error" % (name, ssid, ip))
                        result = False
                    self.pane_item_dict[pane_id][item]["Data"] = "IP: %s \r\n RSSI : %s [%s,%s]" % (
                        ip, rssi, rssi_min, rssi_max)
                else:
                    logger.error("%s Get IP[%s] Timeout" % (name, ssid))
                    result = False

            else:
                logger.error("%s Connect Error [%s]%s" % (name, ssid, key))
                result = False
        else:
            for r in range(retry):
                ret, rssi = adb.wifiscan(ssid, timeout)
                if (ret):
                    logger.debug("%s Scan %s RSSI:%s[%s,%s]" % (name, ssid, rssi, rssi_min, rssi_max))
                    result = rssi_min <= float(rssi) <= rssi_max
                    if (result):
                        break
                else:
                    result = False
            self.pane_item_dict[pane_id][item]["Data"] = " SSID: %s \r\n RSSI : %s [%s,%s]" % (
                ssid, rssi, rssi_min, rssi_max)
        report_dict['rssi'] = rssi
        # if (result):
        #     logger.warning("%s %s RSSI:%s PASS" % (name, self.lo(tagid), rssi))
        # else:
        #     logger.error("%s %s RSSI:%s[%s,%s] FAIL" % (name, self.lo(tagid), rssi, rssi_min, rssi_max))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'rssi': rssi}
        return result, 'RSSI:%s' % rssi if result else "RSSI:%s[%s,%s]" % (rssi, rssi_min, rssi_max)

    def todo_CHECK_KEYS(self, name, pane_id, item, tagid, report_dict, *args):  # AutoBurnKey 读KEY校验
        adb = self.pane_all[pane_id]["Class"]
        msg = ""
        try:
            retry = int(self.conf_dict[tagid]["retry"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        for r in range(retry):
            result, msg = adb.keys_read()
            if (result): break
        if (not result):
            logger.error("%s %s %s" % (name, self.lo(tagid), msg))
        self.pane_item_dict[pane_id][item]["Data"] = "Check Keys: %s" % (msg)
        report_dict["Message"] = msg
        return result, ''

    def todo_READ_KEY(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "READ_KEY"
        # btime = time.time()
        msg = ""
        try:
            timeout = int(self.conf_dict[tagid]["timeout"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        result = adb.readKey()
        if (result):
            time.sleep(0.5)
            ret, msg = adb.readKeyResult()
            for i in range(timeout):
                if (ret):
                    result = "PCPASS" in msg
                    break
                else:
                    time.sleep(1)
                    result = False
                ret, msg = adb.readKeyResult()
                logger.debug("%s %s %s" % (name, self.lo(tagid), msg))
        else:
            logger.debug("Error Start ReadKey!")
        self.pane_item_dict[pane_id][item]["Data"] = "Message: %s" % (msg)
        report_dict["Message"] = msg
        # if (result):
        #     logger.warning("%s %s PASS" % (name, self.lo(tagid)))
        # else:
        #     logger.error("%s %s FAIL" % (name, self.lo(tagid)))
        # # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, "msg": msg}
        return result, ''

    def todo_BURN_KEY(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "BURN_KEY"
        msg = ""
        # btime = time.time()
        try:
            mode = int(self.conf_dict[tagid]["mode"])
            sn_match = self.conf_dict[tagid]["sn_match"]
            emac_match = self.conf_dict[tagid]["emac_match"]
            wmac_match = self.conf_dict[tagid]["wmac_match"]
            timeout = int(self.conf_dict[tagid]["timeout"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        # 通过MES获取sn,emac,wmac
        # scan_now = name  # 临时sn
        if (4 > mode > 0):
            scan_now = self.pane_sn[pane_id].get()  # 使用显示条码从MES读取emac和wmac
            sn, emac, wmac = self.mes.GetMac(scan_now, mode)
            logger.debug("%s %s SN:%s EMAC:%s WMAC:%s " % (name, self.lo(tagid), sn, emac, wmac))
        else:
            # 使用扫码校验的测试项的记录结果作为sn
            if ("SCANNER" in self.pane_dict_report[pane_id] and "SN" in self.pane_dict_report[pane_id]["SCANNER"]):
                sn = self.pane_dict_report[pane_id]["SCANNER"]["SN"]
                if ("EMAC" in self.pane_dict_report[pane_id]["SCANNER"]):
                    emac = self.pane_dict_report[pane_id]["SCANNER"]["EMAC"]
                    logger.debug("%s %s eMAC:%s" % (name, self.lo(tagid), emac))
                else:
                    emac = "null"
                if ("WMAC" in self.pane_dict_report[pane_id]["SCANNER"]):
                    wmac = self.pane_dict_report[pane_id]["SCANNER"]["WMAC"]
                    logger.debug("%s %s wMAC:%s" % (name, self.lo(tagid), wmac))
                else:
                    wmac = "null"
            else:  # 使用显示条码作为SN
                sn = self.pane_dict_report[pane_id]["SN"]
                emac = "null"
                wmac = "null"
            logger.debug("%s %s SN:%s" % (name, self.lo(tagid), sn))
        result = True
        if (result and sn_match):
            result = sn_match in sn
            if (not result): logger.error("%s %s SN:%s[%s] Not Match" % (name, self.lo(tagid), sn, sn_match))
        if (result and emac_match):
            result = emac_match in emac
            if (not result): logger.error("%s %s eMAC:%s[%s] Not Match" % (name, self.lo(tagid), emac, emac_match))
        if (result and wmac_match):
            result = wmac_match in wmac
            if (not result): logger.error("%s %s wMAC:%s[%s] Not Match" % (name, self.lo(tagid), wmac, wmac_match))
        if (result):
            if (mode == 4):  # 定义为PC烧录模式
                try:
                    result, msg = adb.keys_burn(sn, emac, wmac)  # AutoBurnKey 使用
                    if (result):
                        adb.sendcmd_recv1("casePass", "WRITE_KEY")  # 回传结果
                    else:
                        logger.error("%s %s %s" % (name, self.lo(tagid), msg))
                        adb.sendcmd_recv1("caseFail", "WRITE_KEY")  # 回传结果
                except Exception as e:
                    result = False
                    logger.critical("%s" % e)
            else:
                result = adb.burnKey(sn, emac, wmac)
                if (result):
                    time.sleep(1)
                    logger.debug("burnKey..")
                    ret, msg = adb.burnKeyResult()
                    for i in range(timeout):
                        if (ret or adb.error):
                            result = "PCPASS" in msg
                            break
                        else:
                            time.sleep(1)
                            result = False
                        ret, msg = adb.burnKeyResult()
                        logger.debug("%s %s %s" % (name, self.lo(tagid), msg))
        self.pane_item_dict[pane_id][item]["Data"] = "SN: %s \r\neMAC: %s \r\nwMAC : %s \r\nMessage: %s" % (
            sn, emac, wmac, msg)
        report_dict['sn'] = sn
        report_dict['emac'] = emac
        report_dict['wmac'] = wmac
        report_dict['Message'] = msg
        # if (result):
        #     logger.warning("%s %s [%s,%s,%s] PASS" % (name, self.lo(tagid), sn, emac, wmac))
        # else:
        #     logger.error("%s %s [%s,%s,%s] %s FAIL" % (name, self.lo(tagid), sn, emac, wmac, msg))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, "sn": sn, "emac": emac,
        #                                          "wmac": wmac, "Message": msg}
        return result, "[%s,%s,%s]" % (sn, emac, wmac)

    def todo_AGING_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            # set_time = self.conf_dict[tagid]["set_time"]    # 使用厂测配置模板的设定值set_time暂未使用
            limit = self.conf_dict[tagid]["limit"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (limit):
            ret, value = adb.agingResult()  # 单位秒
            if (value == ''):  # 未开始状态
                logger.info("%s unaged.." % name)
                value = "0"
            logger.info("Aging Judge %s[%s]" % (value, limit))
            self.pane_item_dict[pane_id][item]["Data"] = "设备[%d]\r\nAging Time(秒): %s [limit: %s]" % (
                pane_id + 1, value, limit)
            result = ret and int(value) >= int(limit)
        else:  # limit为空的时候为进入老化
            logger.info("Aging Start")
            result = adb.agingTest() # 使用厂测配置模板的设定老化时长
        return result,""

    def todo_ETH_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "ETH_TEST"
        # btime = time.time()
        try:
            timeout = self.conf_dict[tagid]["timeout"]
            match = self.conf_dict[tagid]["match"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        ret, ip = adb.getEthIp(timeout=int(timeout))
        result = match in ip
        logger.debug("%s IP %s [%s]" % (name, ip, match))
        # logger.info("%s %s %s[%s]"%(name,self.lo(tagid),len(ls),num_limit))
        self.pane_item_dict[pane_id][item]["Data"] = "Ether IP: %s \r\n Match : %s" % (ip, match)
        report_dict['ip'] = ip
        # if (result):
        #     logger.warning("%s %s %s[%s] PASS" % (name, self.lo(tagid), ip, match))
        # else:
        #     logger.error("%s %s %s[%s] FAIL" % (name, self.lo(tagid), ip, match))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'ip': ip}
        return result, '%s[%s]' % (ip, match)

    def todo_VISION_DETECT(self, name, pane_id, item, tagid, report_dict, *args):
        cap = self.pane_all[pane_id]["Camera"]
        try:
            tagfile = self.conf_dict[tagid]["tagfile"]
            limit = int(self.conf_dict[tagid]["limit"])
            timeout = int(self.conf_dict[tagid]["timeout"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        factoryfile = "./factory.pkl"
        if (os.path.exists(factoryfile)):
            with open(factoryfile, 'rb') as l:
                factorydict = pickle.load(l)
        if (os.path.exists(tagfile)):
            with open(tagfile, 'rb') as l:
                sampledict = pickle.load(l)
        else:
            return False, 'NotFound tagfile(%s)' % tagfile
        btime = time.time()
        result = False
        msg = ""
        # print(sampledict)
        hashFun = cv2.img_hash.PHash_create()
        while self.main_run and cap.isOpened():
            try:
                if (time.time() - btime) > timeout:
                    msg = "TimeOut"
                    break
                if (self.pane_all[pane_id]["Abort"]):
                    msg = "Abort Clicked"
                    break
                ret, frame = cap.read()
                hashA = hashFun.compute(frame)
                minvalue = 99999
                for name, hashB in sampledict.items():
                    cmpValue = hashFun.compare(hashA, hashB)
                    if cmpValue < minvalue:
                        minvalue = cmpValue
                    result = minvalue <= limit
                    if result: break
                showtext = str(minvalue)
                cv2.putText(frame, showtext, (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                # result = self.compute_taghash(frame, sampledict, limit)
                if (os.path.exists(factoryfile)):
                    err = self.compute_taghash(frame, factorydict)
                    if (err):
                        result = False
                        msg = "Detect Factory"
                        break
                self.show_view(pane_id, frame)
                if (result):
                    break
                else:
                    cv2.waitKey(200)
            except Exception as e:
                logger.warning("Detect Error:%s" % e)
        # self.pane_item_dict[pane_id][item]["Data"] = msg
        # report_dict['Message'] = msg.replace('\n', '')
        return result, msg

    def todo_LEDS_DETECT(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            camid_list = [int(i) for i in self.conf_dict[tagid]["id"].split(",")]
            if (not len(camid_list) == 3):
                return False, "Camera config not enough"
            tagfile = self.conf_dict[tagid]["tagfile"]
            htag = cv2.imread("./%s" % tagfile, 0)
            htagvalue = cv2.calcHist([htag], [0], None, [64], [1, 255])
            len_limit = int(self.conf_dict[tagid]["len_limit"])
            hist_limit = float(self.conf_dict[tagid]["hist_limit"])
            timeout = int(self.conf_dict[tagid]["timeout"])
            delaytime = int(self.conf_dict[tagid]["delay"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'

        btime = time.time()
        result = False
        msg = ""
        ROI_led_h = 30
        try:
            logger.debug("Delay %s sec and Start..." % delaytime)
            cap_list = []
            adb.leds_change(1)
            time.sleep(delaytime)
            btime = time.time()
            for id in camid_list:
                cap = cv2.VideoCapture(id, cv2.CAP_DSHOW)
                cap.set(cv2.CAP_PROP_EXPOSURE, -7)
                if (not cap.grab()):
                    msg = "Open Camera %s Error" % id
                else:
                    cap_list.append(cap)
        except:
            pass
        if (not len(cap_list) == 3):
            return False, "Camera init not enough"
        while self.main_run:
            try:
                if (time.time() - btime) > timeout:
                    break
                if (self.pane_all[pane_id]["Abort"]):
                    msg = "Abort Clicked"
                    break
                adb.leds_change(1)
                if (time.time() - btime > 5):  # debug
                    adb.leds_change(4)
                for cap in cap_list:
                    cap.set(cv2.CAP_PROP_EXPOSURE, -7)
                cv2.waitKey(50)
                cap_list_result = []
                ispass = 0
                for i, cap in enumerate(cap_list):
                    for a in range(3):
                        ret, frame = cap.read()
                        ret, frame = cap.read()
                        if (ret):
                            _result, _msg, _frame, _rect = self.detect_ledbox(frame, lenlimit=len_limit, ROIw=ROI_led_h,
                                                                              debug=True)
                            cap_list_result.append((cap, _frame, _rect))
                            if (_result):
                                ispass += 1
                            else:
                                logger.debug("[%s]%s" % (i, _msg))
                                msg = "[%s]%s" % (i, _msg)
                            break
                        # cv2.waitKey(50)
                if (ispass >= len(cap_list)):
                    adb.leds_change(3)
                    hist_list = {}
                    for cap, oldframe, rect in cap_list_result:
                        cap.set(cv2.CAP_PROP_EXPOSURE, -5)
                        cv2.waitKey(50)
                        ret, frame = cap.read()
                        ret, frame = cap.read()
                        d_hist, frame = self.detect_ledflag(frame, htagvalue, rect, oldframe, debug=False)
                        hist_list[d_hist] = (frame, oldframe)
                    judge_hist = min(hist_list.keys())
                    if (judge_hist <= hist_limit):
                        result = True
                    msg = "Hist:%.2f(%s)" % (judge_hist, hist_limit)
                    centre_show = hist_list.pop(judge_hist)[0]
                    if (result):
                        cv2.putText(centre_show, msg, (5, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)
                    else:
                        logger.debug(msg)
                        cv2.putText(centre_show, msg, (5, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
                    h2, w = centre_show.shape[:2]
                    show_make = np.zeros((ROI_led_h * 4 + h2, w, 3), dtype="uint8")
                    show_make[0:h2, :] = centre_show
                    _key, (_new, old) = hist_list.popitem()
                    show_make[h2:h2 + ROI_led_h * 2, :] = old
                    _key, (_new, old) = hist_list.popitem()
                    show_make[h2 + ROI_led_h * 2:h2 + ROI_led_h * 4, :] = old
                else:
                    h2, w = frame.shape[:2]
                    show_make = np.zeros((ROI_led_h * 6, w, 3), dtype="uint8")
                    _cap, old, _rect = cap_list_result.pop(0)
                    show_make[0:ROI_led_h * 2] = old
                    _cap, old, _rect = cap_list_result.pop(0)
                    show_make[ROI_led_h * 2:ROI_led_h * 4] = old
                    _cap, old, _rect = cap_list_result.pop(0)
                    show_make[ROI_led_h * 4:ROI_led_h * 6] = old
                self.show_view(pane_id, show_make)
                if (result):
                    break
                else:
                    cv2.waitKey(200)
            except Exception as e:
                logger.warning("Detect Error:%s" % e)
        self.pane_item_dict[pane_id][item]["Data"] = msg.replace(";", "\n").replace(":", ": ")
        report_dict['Message'] = msg
        return result, msg

    def todo_WIFI_COUPLE(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "WIFI_COUPLE"
        # btime = time.time()
        try:
            _txchain = self.conf_dict[tagid]["txchain"].split(',')
            _minlist = [float(i) for i in self.conf_dict[tagid]["min"].split(',')]
            _maxlist = [float(i) for i in self.conf_dict[tagid]["max"].split(',')]
            dute = float(self.conf_dict[tagid]["dute"])
            num = int(self.conf_dict[tagid]["num"])
            fw_file = self.conf_dict[tagid]["fw_file"]
            nvram = self.conf_dict[tagid]["nvram"]
            num_limit = float(self.conf_dict[tagid]["limit"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        _channel = 1
        data = []
        msg = "Couple: %s Min: %s Max: %s Limit: %s Num: %s" % (_channel, _minlist, _maxlist, num_limit, num)
        result = adb.push_fw(fw_file, nvram)
        if (result):
            for i, c in enumerate(_txchain):
                if (i < len(_minlist)):
                    _min = _minlist[i]
                    _max = _maxlist[i]
                else:
                    _min = _minlist[-1]
                    _max = _maxlist[-1]
                logger.debug("%s Start WIFI txchain %s" % (name, c))
                result = adb.wifi_fw_start(c)
                if (result):
                    RF = RFmode()
                    logger.debug("%s Begin Couple [%s]2412 MHz" % (name, _channel))
                    data = RF.get_power_list(_channel, 2412, num, dute)
                    _pass = 0
                    for d in data:
                        if (_min <= d <= _max):
                            _pass += 1
                    result = _pass / num >= num_limit
                    logger.debug("%s TxChain[%s] Powers %s Pass:%s" % (name, c, data, _pass))
                    msg += "\n[%s]Pass %s Powers:\n%s" % (c, _pass, data)
                    if (not result):
                        break
        self.pane_item_dict[pane_id][item]["Data"] = msg
        report_dict['Message'] = msg.replace('\n', '')
        # if (result):
        #     logger.warning("%s %s %s[%s] PASS" % (name, self.lo(tagid), data, num_limit))
        # else:
        #     logger.error("%s %s %s[%s] FAIL" % (name, self.lo(tagid), data, num_limit))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'msg': msg.replace('\n', '')}
        return result, '%s[%s]' % (data, num_limit)

    def todo_ROUTER_TELNET(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            _ip = self.conf_dict[tagid]["ip"]
            _static = self.conf_dict[tagid]["static"]
            static_ip = ".".join(_ip.split(".")[:-1] + [_static])  # 生成同网段静态IP
            _user = self.conf_dict[tagid]["user"]
            _password = self.conf_dict[tagid]["password"]
            _wait = int(self.conf_dict[tagid]["wait"])
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        if (_static):
            ret = adb.setEthIp(static_ip, _ip)  # 设置静态IP
        result, value = adb.sendcmd_recv2("getEthIp")
        for a in range(_wait):
            if (result): break
            time.sleep(1)
            if (_static and not ret):
                ret = adb.setEthIp(static_ip, _ip)  # 设置静态IP
            result, value = adb.sendcmd_recv2("getEthIp")
            if (adb.has_error()):
                logger.critical("[ADB_ERROR]%s %s" % (name, adb.errormsg[adb.error]))
                # break
        if (not result):
            return False, 'Wait(%s) Ethernet' % (a)
        logger.debug("[Wait %s]%s" % (a, value))
        result = adb.telnet_router(_ip, _user, _password)
        self.pane_item_dict[pane_id][item]["Data"] = "Host:%s (%s/%s) \nLocal:%s\nWait:%s" % (
            _ip, _user, _password, value, a)
        return result, ''

    def todo_ROUTER_COUPLE(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        try:
            with open("./CoupleCmd", "r", encoding='utf-8') as f:
                cmd_dict = eval(f.read())
            _txchain = cmd_dict.keys()
            if (not _txchain):
                return False, "CoupleCmd"
            _freqlist = [int(i) for i in self.conf_dict[tagid]["freq"].split(',')]
            _minlist = [float(i) for i in self.conf_dict[tagid]["min"].split(',')]
            _maxlist = [float(i) for i in self.conf_dict[tagid]["max"].split(',')]
            dute = float(self.conf_dict[tagid]["dute"])
            num = int(self.conf_dict[tagid]["num"])
            num_limit = float(self.conf_dict[tagid]["limit"])
            _channel = None
            for i in range(8):
                usb_tid = self.conf_dict[tagid]['bind%d' % (i + 1)]
                if (usb_tid == self.pane_all[pane_id]["Tid"]):
                    _channel = i + 1
                    bind_offset = self.conf_dict[tagid]['bind%d_offset' % (i + 1)]
                    if (bind_offset):
                        _offset_list = [float(i) for i in bind_offset.split(',')]
                    else:
                        _offset_list = [0]
                    break
            if (_channel == None):
                logger.critical("Bind Couple Channel %s" % self.lo("Error"))
                report_dict["result"] = False
                return False, 'Config'
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        data = []
        max_data = []
        msg = "Couple: %s FREQ:%s Min: %s Max: %s Limit: %s Num: %s Offset: %s" % (
            _channel, _freqlist, _minlist, _maxlist, num_limit, num, _offset_list)
        result = adb.telnet_state
        if (result):
            for i, c in enumerate(_txchain):
                _min = self.get_one_value(_minlist, i)
                _max = self.get_one_value(_maxlist, i)
                _freq = self.get_one_value(_freqlist, i)
                _offset = self.get_one_value(_offset_list, i)
                logger.debug("%s Start Router TxChain(%s)" % (name, c))
                result = adb.telnet_cmdlist(cmd_dict[c])
                if (result):
                    RF = RFmode()
                    logger.debug("%s Begin Couple(%s)%s MHz" % (name, _channel, _freq))
                    data = RF.get_power_list(_channel, _freq, num, dute, _offset)
                    max_data.append(max(data))
                    _pass = 0
                    for d in data:
                        if (_min <= d <= _max):
                            _pass += 1
                    result = _pass / num >= num_limit
                    logger.debug("%s Powers(%s)Pass(%s)%s" % (name, c, _pass, data))
                    msg += "\nPowers(%s)Pass(%s)\n%s" % (c, _pass, data)
                    if (not result):
                        break
                else:
                    logger.error("Couple(%s) Control TxChain(%s) Fail" % (_channel, c))
        self.pane_item_dict[pane_id][item]["Data"] = msg
        report_dict['Message'] = msg.replace('\n', '')
        report_dict['Data'] = "%s" % (max_data)
        return result, "%s" % (max_data)

    def todo_SD_TEST(self, name, pane_id, item, tagid, report_dict, *args):
        adb = self.pane_all[pane_id]["Class"]
        # tagid = "SD_TEST"
        # btime = time.time()
        try:
            num_limit = self.conf_dict[tagid]["limit"]
        except:
            logger.critical("Config Para %s" % self.lo("Error"))
            report_dict["result"] = False
            return False, 'Config'
        ret, count = adb.getSdNum()
        result = int(count) >= int(num_limit)
        logger.debug("%s Detect Count %s" % (name, count))
        # logger.info("%s %s %s[%s]"%(name,self.lo(tagid),len(ls),num_limit))
        self.pane_item_dict[pane_id][item]["Data"] = "Detect Count: %s [Limit:%s]" % (count, num_limit)
        report_dict['count'] = count
        # if (result):
        #     logger.warning("%s %s %s[%s] PASS" % (name, self.lo(tagid), count, num_limit))
        # else:
        #     logger.error("%s %s %s[%s] FAIL" % (name, self.lo(tagid), count, num_limit))
        # elpstime = round(time.time() - btime, 3)
        # logger.info("Elapsed Time: %.3f s" % (elpstime))
        # self.pane_dict_report[pane_id][tagid] = {"result": result, "elpstime": elpstime, 'count': count}
        return result, '%s[%s]' % (count, num_limit)

    def todo_RESET(self, name, pane_id, item, tagid, report_dict, *args):
        pass  # 清除厂测数据?

    def todo_ADB_IPERF(self, name, pane_id, item, tagid, report_dict, *args):
        pass  # iperf 吞吐量测试


def init_logo(text1="LED视觉检测", pos1=(52, 3), text2="LED Vision Detect", pos2=(56, 19)):
    image = Image.open("./SEI.png")
    draw = ImageDraw.Draw(image)
    setFont1 = ImageFont.truetype('C:/windows/fonts/simhei.ttf', 15)
    # setFont1 = ImageFont.truetype('C:/windows/fonts/STXINWEI.ttf', 15)
    setFont2 = ImageFont.truetype('C:/windows/fonts/STXINWEI.ttf', 10)
    draw.text(pos1, text1, font=setFont1, fill="#000000", direction=None)
    draw.text(pos2, text2, font=setFont2, fill="#000000", direction=None)
    image.show()
    image.save("./SEI_logo.png")


if __name__ == '__main__':
    # init_logo()
    os.remove('./English')
    os.remove('./Chinese')
    os.remove('./Config.ini')
