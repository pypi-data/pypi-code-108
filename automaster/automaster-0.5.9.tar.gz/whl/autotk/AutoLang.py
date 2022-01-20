# 定义语言切换函数
def lolang(lang="EN"):
    languages = dict(EN=ENLang, CN=CNLang)
    return languages[lang]()

def lang_append(key,english=None,chinese=None,*args):
    if(english):
        ENLang().appendkey(key,english)
    if(chinese):
        CNLang().appendkey(key,chinese)

class CNLang:
    # 中文语言字典
    def __init__(self):
        # 定义外部字典，有外部字典优先外部字典
        self.dictfile = './Chinese'
        try:
            with open(self.dictfile, 'r', encoding='utf-8') as f:
                self.trans = eval(f.read())
        except IOError:
            # 内置字典文件，重新生成字典文件
            self.trans = dict(Export='导出..', Copy='复制', Clean='清空', Autoscrolling='自动滚屏', Editable='允许编辑',
                              Error=u"错误", NotFound=u"找不到", Configuration='选项配置',Reset='重置',OK='确定',Cancel='取消',
                              Desktop_Shortcut='桌面快捷方式',IPERF_24='2.4G吞吐量',IPERF_5='5G吞吐量',
                              HDMI_AUDIO="HDMI音频", HDMI_VIDEO="HDMI视频", FTP="上传FTP",
                              VISION_DETECT="视觉检测", LEDS_DETECT="LED灯条检测",Item="项",
                              AV_AUDIO="AV音频", AV_VIDEO="AV视频", SETTING="全局设定", WaitDUT="等待设备接入..", WaitScan="请扫码->",
                              ADB_IPERF="OTT吞吐量", RESOLUTION="分辨率", USB_TEST="USB测试", SD_TEST="SD卡测试", BT_TEST="蓝牙测试",
                              AGING_TEST='老化测试', BURN_KEY="Keys写入", HDMI_VOLT='HDMI电压测试', DVB_VOLT='DVB电压测试',
                              WIFI_COUPLE="WIFI耦合测试", ROUTER_COUPLE="路由耦合测试", ROUTER_TELNET="路由连接", ADB_CLOSE="关闭ADB",
                              READ_KEY="读Key", TestItems="测试项目", Click2First="点击切到全局首页", CHECK_KEYS="Keys校验",
                              RESET="恢复出厂", DVB="DVB测试", BASIC_TEST="基本信息检测", WIFI_24="2.4G WIFI测试", WIFI_5="5G WIFI测试",
                              SPDIF_AUDIO="光纤音频", Item_Total="测试项数量", Thread_Total="并行线程总数", Device_Total="设备总数",
                              Device_Overflow="溢出异常设备", ETH_TEST="网口测试", IR_TEST="红外测试", SIM_TEST="SIM模块测试",
                              LED_TEST="LED检测", BUTTON_TEST="按键检测", BURN_TEST="写SN&MAC", SCANNER="条码校验", MES="上传MES",
                              Name="名称", Value="值", Adb_Devices_Overflow="ADB设备溢出", Total="总数", Elapsed="耗时")
            with open(self.dictfile, 'w', encoding='utf-8') as f:
                f.write(str(self.trans))
        except Exception as e:
            raise (e)

    def get(self, msgid):
        try:
            return self.trans[msgid]
        except Exception as e:
            print('LanguageDictNotFound "%s"' % msgid)
            return str(msgid)
    def appendkey(self,key,value):
        if(key in self.trans):
            print("[Lang]",self.trans[key],"-->",value)
        self.trans[key]=value
        with open(self.dictfile, 'w', encoding='utf-8') as f:
            f.write(str(self.trans))

class ENLang:
    #  英文处理字段空格和标点符号
    def __init__(self):
        # 定义外部字典，有外部字典优先外部字典
        self.dictfile = './English'
        try:
            with open(self.dictfile, 'r', encoding='utf-8') as f:
                self.trans = eval(f.read())
        except IOError:
            # 内置字典文件，重新生成字典文件
            self.trans = dict(Export='Export', Copy='Copy', Clean='Clean', Autoscrolling='Autoscrolling',
                              Editable='Editable',Configuration='Configuration',Reset='Reset',OK='OK',Cancel='Cancel',
                              Desktop_Shortcut='Desktop Shortcut',Item="Item"
                              , Error=u"Error", NotFound=u"Not Found", HDMI_AUDIO="HDMI Audio", HDMI_VIDEO="HDMI Video",
                              CHECK_KEYS="Check Keys", WIFI_COUPLE="WIFI Couple", ROUTER_COUPLE="Router Couple",
                              AV_AUDIO="AV Audio", AV_VIDEO="AV Video", TestItems="Test Items",
                              VISION_DETECT="Vision Detect",IPERF_24='2.4G Throughput',IPERF_5='5G Throughput',
                              Click2First="Click->SETTING", ROUTER_TELNET="Telnet Connect", ADB_CLOSE="Close ADB",
                              ADB_IPERF="OTT Throughput", RESOLUTION="Resolution", USB_TEST="USB Test",
                              WaitDUT="Wait for DUT..", WaitScan="Wait Scan Station->", LEDS_DETECT="LED Vision Detect",
                              AGING_TEST='Aging Test', BURN_KEY="Write Keys", HDMI_VOLT='HDMI Voltage Test',
                              DVB_VOLT='DVB Voltage Test', BT_TEST="Bluetooth Test", READ_KEY="Read Key",
                              RESET="Reset Factory", DVB="DVB Test", BASIC_TEST="Basic Hardware Test", FTP="FTP Upload",
                              SD_TEST="SD Test", IR_TEST="IR Test", SIM_TEST="SIM Test", SCANNER="Barcode Check",
                              LED_TEST="LED Test", BUTTON_TEST="Button Test", BURN_TEST="Burn SN&MAC", MES="Upload MES",
                              SPDIF_AUDIO="SPDIF Audio", Item_Total="Item Total", Thread_Total="Thread Total",
                              ETH_TEST="Ethernet Test", WIFI_24="2.4G WIFI Test", WIFI_5="5G WIFI Test",
                              Device_Total="Device Total", Device_Overflow="Device Overflow",
                              Adb_Devices_Overflow="Adb Devices Overflow")
            with open(self.dictfile, 'w', encoding='utf-8') as f:
                f.write(str(self.trans))
        except Exception as e:
            raise (e)

    def get(self, msgid):
        try:
            return self.trans[msgid]
        except Exception as e:
            return str(msgid)
    def appendkey(self,key,value):
        if(key in self.trans):
            print("[Lang]",self.trans[key],"-->",value)
        self.trans[key]=value
        with open(self.dictfile, 'w', encoding='utf-8') as f:
            f.write(str(self.trans))