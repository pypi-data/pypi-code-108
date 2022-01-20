import datetime
import json
import os
import re
import telnetlib
import xlwt
import numpy as np


class bzCrt:  # 工单处理
    log_lv = 3
    tn = ""
    oltType = ""
    logText = ""  # 执行日志
    oltInfo = {}

    oltData = {

    }
    # script_info = {
    #     "sheet_num": 0,
    #     "app_book": xlwt.Workbook(encoding='utf-8', style_compression=0),
    #     "save_flag": "excl",
    #     "order_content": []
    # }

    def __init__(self, system_info, oltInfo):
        self.script_info = {}
        self.script_info["app_book"] = xlwt.Workbook(encoding='utf-8', style_compression=0)
        self.script_info["sheet_num"] = 0
        self.script_info["order_content"] = []
        self.script_info.setdefault("save_flag", "excl")

        log_lv_data = {
            "ALL": 0,
            "TRACE": 1,
            "DEBUG": 2,
            "INFO": 3,
            "WARN": 4,
            "ERROR": 5,
            "FATAL": 6,
            "OFF": 7,
        }
        self.log_lv = log_lv_data[system_info["log_level"]]
        self.logText = ""  # 执行日志
        print_data = [
            {"text": "正在初始化数据", "color": "33"}
        ]
        self.print_log(print_data, "INFO")
        oltInfo_input = oltInfo["ini"]
        for info in oltInfo_input:
            self.oltData[info["source_key"]] = info["data"]
        self.oltType = oltInfo["type"]
        self.oltInfo = oltInfo

    def print_log(self, log_lv_info, log_lv_num):

        log_lv_data = {
            "ALL": 0,
            "TRACE": 1,
            "DEBUG": 2,
            "INFO": 3,
            "WARN": 4,
            "ERROR": 5,
            "FATAL": 6,
            "OFF": 7,
        }
        log_lv = log_lv_data[log_lv_num.upper()]

        if log_lv >= self.log_lv:
            print("\033[1;%sm%s\033[0m" % ("34", log_lv_num.upper()), end=" - ")
            for info in log_lv_info:
                info.setdefault("end", "\n")
                print("\033[1;%sm%s\033[0m" % (info["color"], info["text"]), end=info["end"])

    def del1(self):

        '''
        with open('C:\\Users\\jiqiren\\Desktop\\1234.txt', "a", encoding='utf-8',
                  errors='ignore') as file:  # 只需要将之前的”w"改为“a"即可，代表追加内容
            file.write(self.logText + "\n")
        '''
        if isinstance(self.tn, telnetlib.Telnet):
            print_data = [
                {"text": "断开连接", "color": "33"}
            ]
            self.print_log(print_data, "INFO")
            self.tn.close()

    def getPon_loid_hw(self, loid_info):

        print_data = [
            {"text": "获取pon信息:", "color": "33", "end": ""},
            {"text": loid_info["desc"], "color": "32"},
        ]
        self.print_log(print_data, "INFO")

        loid = loid_info["input"]["loid"]
        key = loid_info["input"]["key"]
        null_continu = loid_info["input"]["null_continu"]
        input_ini = loid_info["input_ini"]

        # 初始化crt命令
        by_type = ["by-password","by-loid","by-sn"]

        
        # 获取ont pon口
        self.tn.write(b'display ont info by-password ' + loid.encode('ascii') + b" \n")
        res1 = self.tn.expect([b'\)#', b'Press \'Q\' to break'], timeout=10)
        self.logText = self.logText + res1[2].decode('gb2312')
        if res1[0] == 1:
            self.tn.write(b'Q')
            resTmp = self.tn.expect([b'\)#'], timeout=5)
            self.logText = self.logText + resTmp[2].decode('gb2312')
        res1 = res1[2].decode('ascii', 'ignore')
        pattern = re.compile(r'(\d+)/ *(\d+)/ *(\d+) *(?:ONT-ID *: *){0,1}(\d+)')
        PonInfoOlt = pattern.findall(res1)

        if len(PonInfoOlt) == 1:
            self.oltData[key] = PonInfoOlt
            return

        self.tn.write(b'display ont info by-loid ' + loid.encode('ascii') + b" \n")
        res2 = self.tn.expect([b'\)#', b'Press \'Q\' to break'], timeout=10)
        self.logText = self.logText + res2[2].decode('gb2312')
        if res2[0] == 1:
            self.tn.write(b'Q')
            resTmp = self.tn.expect([b'\)#'], timeout=5)
            self.logText = self.logText + resTmp[2].decode('gb2312')
        res2 = res2[2].decode('ascii', 'ignore')
        pattern = re.compile(r'(\d+)/ *(\d+)/ *(\d+) *(?:ONT-ID *: *){0,1}(\d+)')
        PonInfoOlt = pattern.findall(res2)

        # print("olt获取的pon口",PonInfoOlt)
        if len(PonInfoOlt) == 1:
            self.oltData[key] = PonInfoOlt
            return PonInfoOlt

        self.tn.write(b'display ont info by-sn ' + loid.encode('ascii') + b" \n")
        res3 = self.tn.expect([b'\)#', b'Press \'Q\' to break'], timeout=10)
        self.logText = self.logText + res3[2].decode('gb2312')
        if res3[0] == 1:
            self.tn.write(b'Q')
            resTmp = self.tn.expect([b'\)#'], timeout=5)
            self.logText = self.logText + resTmp[2].decode('gb2312')

        res3 = res3[2].decode('ascii', 'ignore')
        pattern = re.compile(r'(\d+)/ *(\d+)/ *(\d+) *(?:ONT-ID *: *){0,1}(\d+)')
        PonInfoOlt = pattern.findall(res3)

        if len(PonInfoOlt) == 1:
            self.oltData[key] = PonInfoOlt
            return PonInfoOlt

        if null_continu == False:
            returnJson = {
                "code": "fatal",
                "msg": "未找到指定pon口",
                "log": ""
            }
            raise Exception(returnJson)

    def en_co_hw(self):
        self.tn.write(b'en\n')
        res = self.tn.read_until(b'#')
        self.logText = self.logText + res.decode('gb2312')
        self.tn.write(b'config\n')
        res = self.tn.read_until(b')#')
        self.logText = self.logText + res.decode('gb2312')

    def loginOlt_hw(self, json_data):
        # print("登录olt_华为")
        res_text = ""
        for userInfo in json_data["userInfo"]:
            Username = userInfo["oltName"].encode('ascii')  # 登录用户名
            Password = userInfo["oltPwd"].encode('ascii')  # 登录密码
            self.tn.read_until(b'name:')
            self.tn.write(Username + b'\n')
            self.tn.read_until(b'password:')
            self.tn.write(Password + b'\n')
            res = self.tn.expect([b'me:', b'>'])
            # .decode('gb2312')
            # print("res",res)
            self.logText = self.logText + res[2].decode('gb2312')
            if res[0] == 1:
                return
            res_text = res_text + res[2].decode('gb2312')
        returnJson = {
            "code": "fatal",
            "msg": "登录失败",
            "log": res_text
        }
        raise Exception(returnJson)

    def regularAss(self, resText, reg_ex, reg_json, right_num, error_num):
        # 正则框选

        pattern = re.compile(reg_ex)
        pattern_text = pattern.findall(resText)
        # print(pattern_text)
        # 检测正则数量
        if int(error_num) < 0:
            pass
        elif int(error_num) == len(pattern_text):
            returnJson = {
                "code": "fatal",
                "msg": "正则匹配数量异常_error_num",
                "log": [pattern_text,reg_ex]
            }
            raise Exception(returnJson)

        if int(right_num) < 0:
            pass
        elif int(right_num) != len(pattern_text):
            returnJson = {
                "code": "fatal",
                "msg": "正则匹配数量异常_right_num",
                "log": pattern_text
            }
            raise Exception(returnJson)

        # 生成数据
        return_tmp_data = []
        for pattern_info in pattern_text:
            return_tmp_json = {}
            for info in reg_json:
                return_tmp_json[info] = pattern_info[int(reg_json[info])]
            return_tmp_data = np.append(return_tmp_data, return_tmp_json)

        return return_tmp_data

    def display_hw(self, display_json):

        print_data = [
            {"text": "获取数据:", "color": "33", "end": ""},
            {"text": display_json["desc"], "color": "32"},
        ]
        self.print_log(print_data, "INFO")

        other_break = display_json["input"]["other_break"]
        inputJson = display_json["input"]
        outputJson = display_json["output"]

        is_show = inputJson.get("is_show",False)
        ord_old = inputJson["ord"]
        crtOrd = ord_old.encode('ascii')
        expectArray = []
        for expectInfo in inputJson["endStr"]:
            expectInfo = expectInfo.replace(")", "\)")
            expectArray = np.append(expectArray, expectInfo.encode('ascii'))

        expectInfo = "\( Press 'Q' to break \)"
        expectArray = np.append(expectArray, expectInfo.encode('ascii'))

        showNum = int(inputJson["showNum"])
        showNum_tmp = 1
        expectArray = expectArray.tolist()
        self.tn.write(crtOrd)
        res = self.tn.expect(expectArray, timeout=20)
        if is_show:
            print(res[2].decode('gb2312'),end="")
        self.logText = self.logText + res[2].decode('gb2312')
        if res[0] == -1:
            returnJson = {
                "code": "fatal",
                "msg": "查看超时",
                "log": res[2].decode('gb2312')
            }
            raise Exception(returnJson)

        # 判断是否结束
        for i in range(len(outputJson)):

            if res[0] == i:
                key = outputJson[i]["key"]
                operate = outputJson[i]["operate"]

                if operate == "break":
                    returnJson = {
                        "code": "fatal",
                        "msg": key,
                        "log": res[2].decode('gb2312')
                    }
                    raise Exception(returnJson)

        # 变量赋值
        resText = res[2].decode('gb2312').replace(
            "---- More ( Press 'Q' to break ) ----[37D                                     [37D", '')
        other_break_flag = False
        while 1:
            if showNum_tmp > showNum:
                print_data = [
                    {"text": "确认退出:", "color": "33", "end": ""},
                    {"text": showNum_tmp, "color": "32", "end": "，"},
                    {"text": showNum, "color": "32"},
                ]
                self.print_log(print_data, "DEBUG")

                res = self.tn.expect(expectArray, timeout=1)
                if is_show:
                    print(res[2].decode('gb2312'),end="")
                self.logText = self.logText + res[2].decode('gb2312')
                if res[0] == len(expectArray) - 1 or res[2].decode('gb2312') == " ----":
                    self.tn.write(b'Q')
                    res = self.tn.expect(expectArray, timeout=5)
                    if is_show:
                        print(res[2].decode('gb2312'), end="")
                    self.logText = self.logText + res[2].decode('gb2312')
                break
            elif res[0] == len(expectArray) - 1:
                print_data = [
                    {"text": "空格继续:", "color": "33"},
                ]
                self.print_log(print_data, "DEBUG")

                self.tn.write(b" ")
                res = self.tn.expect(expectArray, timeout=20)
                if is_show:
                    print(res[2].decode('gb2312'),end="")
                self.logText = self.logText + res[2].decode('gb2312')
                resText = resText + res[2].decode('gb2312').replace(
                    "---- More ( Press 'Q' to break ) ----[37D                                     [37D", '')
            elif "Unknown command, the error locates at" in res[2].decode('gb2312'):
                returnJson = {
                    "code": "fatal",
                    "msg": "命令执行错误",
                    "log": res[2].decode('gb2312')
                }
                raise Exception(returnJson)
            elif other_break_flag:
                print_data = [
                    {"text": "其他跳出:", "color": "33"},
                ]
                self.print_log(print_data, "DEBUG")

                res = self.tn.expect(expectArray, timeout=1)
                if is_show:
                    print(res[2].decode('gb2312'),end="")
                self.logText = self.logText + res[2].decode('gb2312')
                break
            elif res[0] == - 1:
                returnJson = {
                    "code": "fatal",
                    "msg": "遍历时超时",
                    "log": res[2].decode('gb2312')
                }
                raise Exception(returnJson)
            elif res[0] == 0:
                res = self.tn.expect(expectArray, timeout=1)
                if is_show:
                    print(res[2].decode('gb2312'),end="")
                self.logText = self.logText + res[2].decode('gb2312')
                break

            showNum_tmp = showNum_tmp + 1
            # 其他跳出方式
            for info in other_break:
                if info["type"] == "time":

                    # 截取时间
                    pattern = re.compile(info["reg_ex"])
                    pattern_text = pattern.findall(resText)
                    data_tmp = pattern_text
                    for source_data_info in info["reg_data"]:
                        data_tmp = data_tmp[source_data_info]

                    subTime_flag = self.judge_time(info["condition"], data_tmp)

                    if not subTime_flag:
                        '''
                        self.tn.write(b"\n")
                        res = self.tn.expect(expectArray, timeout=20)
                        self.logText = self.logText + res[2].decode('gb2312')
                        '''

                        res = self.tn.expect(expectArray, timeout=2)
                        if is_show:
                            print(res[2].decode('gb2312'), end="")
                        self.logText = self.logText + res[2].decode('gb2312')

                        if res[0] == len(expectArray) - 1 or res[2].decode('gb2312') == " ----":
                            self.tn.write(b'Q')
                            res = self.tn.expect(expectArray, timeout=5)
                            if is_show:
                                print(res[2].decode('gb2312'), end="")

                            self.logText = self.logText + res[2].decode('gb2312')
                        other_break_flag = True
                        break
        # print(123456)

        resText = resText.replace(
            "---- More ( Press 'Q' to break ) ----[37D                                     [37D", '')
        oltData_tmp = ""
        for info in outputJson:
            info.setdefault("right_num", "-1")
            info.setdefault("error_num", "-1")
            key = info["key"]

            if "data_type" not in info:
                continue
            if info["data_type"] == "reg":
                # 判断是否增加
                oltData_tmp = self.regularAss(resText, info["reg_ex"], info["reg_json"], info["right_num"],
                                              info["error_num"])

            # 循环正则
            self.oltData[key] = oltData_tmp

    def input_ini(self, interfaceJson):
        return_json = {}
        for info in interfaceJson:
            data_tmp = self.oltData[info["source_data"]]
            for source_data_info in info["source_num"]:
                data_tmp = data_tmp[source_data_info]
            return_json[info["target_data"]] = data_tmp
        return return_json

    def interface_hw(self, interfaceJson):
        interface_input = interfaceJson["input"]

        crtPon0 = interface_input["pon0"]
        crtPon1 = interface_input["pon1"]
        print_data = [
            {"text": "进pon口:", "color": "33", "end": ""},
            {"text": crtPon0 + "/" + crtPon1, "color": "32"},
        ]
        self.print_log(print_data, "INFO")

        script_info_tmp = {
            "desc": "进pon口",
            "order": str('interface gpon ' + crtPon0 + '/' + crtPon1 + "\n")
        }
        self.script_info["order_content"] = self.script_info["order_content"] + [script_info_tmp]
        
        self.tn.write(b'interface gpon ' + crtPon0.encode('ascii') + b'/' + crtPon1.encode('ascii') + b' \n')
        res = self.tn.expect([crtPon1.encode('ascii') + b'\)#', b'g\)#'], timeout=5)
        self.logText = self.logText + res[2].decode('gb2312')
        if res[0] != 0:
            returnJson = {
                'code': "error",
                'msg': '进pon板错误',
                'log': res[2].decode('gb2312')}
            raise Exception(returnJson)

    def _is_break_doCrtHw(self, errorText, break_filters):

        for break_filters_info in break_filters:
            # print(break_filters_info)
            break_filters_info.setdefault("key", "break")
            break_filters_info.setdefault("condition", "")
            break_filters_info.setdefault("value", "")

            condition = break_filters_info["condition"]

            return_flag = True
            if condition[0] == "!":
                condition = condition[1:]
                return_flag = False

            if break_filters_info["key"] == "continue":
                return_flag = not return_flag

            if condition == "=" and break_filters_info["value"] == errorText:  # 相等
                return return_flag

            if condition == "in" and break_filters_info["value"] in errorText:  # 之内
                return return_flag

        return True

    def generate_script_hw(self, doCrt_info):

        ord_input = doCrt_info["input"]
        input_ini = ord_input["ord_ini"]

        ord_input.setdefault("Failure_config", {"is_break": True})
        Failure_config = ord_input["Failure_config"]

        ord_array = []
        expectArray = []
        expectInfo = "\? \(y/n\)\[n\]"
        expectArray = np.append(expectArray, expectInfo.encode('ascii'))

        for expectInfo in ord_input["endStr"]:
            expectInfo = expectInfo.replace(")", "\)")
            expectArray = np.append(expectArray, expectInfo.encode('ascii'))
        expectArray = expectArray.tolist()

        # 初始化crt命令
        for input_ini_info in input_ini:  # 所有变量赋值
            source_variable = self.oltData[input_ini_info["source_key"]]

            for olt_for_info in source_variable:  #
                # olt_for_info =  {'error_num': '833515', 'error_time': '2021-12-03 17:51:07'}
                ord_tmp = ord_input["ord"]
                for ord_info in input_ini_info["dense"]:
                    ord_tmp = ord_tmp.replace(ord_info["target_data"], str(olt_for_info[ord_info["source_data"]]))
                ord_array = np.append(ord_array, ord_tmp)

        order_tmp = ""
        # 执行crt命令
        for ord_info in ord_array:
            # .encode('ascii')
            crt_ord = ord_info
            # 生成数据
            order_tmp = order_tmp + crt_ord + "\n"

            print_data = [
                {"text": "正在生成脚本:", "color": "33", "end": ""},
                {"text": str(crt_ord), "color": "32"},
            ]
            self.print_log(print_data, "INFO")

        script_info_tmp = {
            "desc": doCrt_info["desc"],
            "order": order_tmp
        }
        self.script_info["order_content"] = self.script_info["order_content"] + [script_info_tmp]

    def save_generate_script(self, save_path,ini_connt = ""):

        order_content = self.script_info["order_content"]
        save_path_array = save_path.split('.')
        suffix = save_path_array[-1]
        # print("保存 日志：",order_content)
        if suffix == "txt":
            # 执行保存
            with open(save_path, "a") as file:
                file.write(ini_connt + "\n")
                for info in order_content:
                    if info["desc"] != '':
                        file.write("#" + info["desc"] + "\n")
                    file.write(info["order"] + "\n")

        elif suffix == "xlsx":
            # 执行保存
            app_book = xlwt.Workbook(encoding='utf-8', style_compression=0)
            add_sheet_num = 1
            for info in order_content:
                if not info["desc"]:
                    info["desc"] = str(add_sheet_num)
                add_sheet_num += 1
                sheet = app_book.add_sheet(info["desc"], cell_overwrite_ok=True)

                order_arry = info["order"].split("\n")
                num = 0
                for write_info in order_arry:
                    sheet.write(num, 0, write_info)
                    num += 1
            app_book.save(save_path)

    def doCrt_hw(self, doCrt_info):

        ord_input = doCrt_info["input"]
        input_ini = ord_input["ord_ini"]

        ord_input.setdefault("Failure_config", {"is_break": True, "break_filters": []})
        Failure_config = ord_input["Failure_config"]

        ord_array = []
        expectArray = []
        expectInfo = "\? \(y/n\)\[n\]"
        expectArray = np.append(expectArray, expectInfo.encode('ascii'))

        for expectInfo in ord_input["endStr"]:
            expectInfo = expectInfo.replace(")", "\)")
            expectArray = np.append(expectArray, expectInfo.encode('ascii'))
        expectArray = expectArray.tolist()

        # 初始化crt命令
        for input_ini_info in input_ini:  # 所有变量赋值
            source_variable = self.oltData[input_ini_info["source_key"]]

            for olt_for_info in source_variable:  #
                # olt_for_info =  {'error_num': '833515', 'error_time': '2021-12-03 17:51:07'}
                ord_tmp = ord_input["ord"]
                for ord_info in input_ini_info["dense"]:
                    ord_tmp = ord_tmp.replace(ord_info["target_data"], str(olt_for_info[ord_info["source_data"]]))
                ord_array = np.append(ord_array, ord_tmp)
        # 执行crt命令
        for ord_info in ord_array:
            crt_ord = ord_info.encode('ascii')
            print_data = [
                {"text": "运行命令:", "color": "33", "end": ""},
                {"text": str(crt_ord), "color": "32"},
            ]
            self.print_log(print_data, "INFO")

            # self.tn.write(b"\n")
            self.tn.write(crt_ord)

            res = self.tn.expect(expectArray, timeout=10)

            self.logText = self.logText + res[2].decode('gb2312')
            if res[0] == 0:  # 输入y
                self.tn.write(b'y\n')
                res = self.tn.expect([b'\)#'], timeout=5)
                self.logText = self.logText + res[2].decode('gb2312')
            elif res[0] == -1:  # 超时退出
                returnJson = {
                    'code': "error",
                    'msg': '执行超时',
                    'log': res}
                raise Exception(returnJson)
            if "Failure" in res[2].decode('gb2312'):
                resText = res[2].decode('gb2312')
                patternIpAd = re.compile(r'(Failure[\s\S]*?\r\n)')
                errorInfo = patternIpAd.findall(resText)
                errorText = ""
                if len(errorInfo) != 0:
                    errorText = errorInfo[0]
                errorText = str(errorText)

                print_data = [
                    {"text": "运行结果:", "color": "31", "end": ""},
                    {"text": errorText, "color": "31"},
                ]
                self.print_log(print_data, "INFO")

                if not Failure_config["is_break"]:  # 跳过所有错误
                    # 赋值继续
                    pass
                elif not self._is_break_doCrtHw(errorText, Failure_config["break_filters"]):
                    pass

                else:
                    returnJson = {
                        'code': "error",
                        'msg': '执行错误\n' + errorText,
                        'log': res}
                    raise Exception(returnJson)
            else:
                print_data = [
                    {"text": "运行结果:", "color": "33", "end": ""},
                    {"text": str(res), "color": "32"},
                ]
                self.print_log(print_data, "INFO")

    def readCrt_hw(self, doCrt_info):

        ord_input = doCrt_info["input"]
        input_ini = ord_input["ord_ini"]

        ord_input.setdefault("Failure_config", {"is_break": True})
        Failure_config = ord_input["Failure_config"]

        ord_array = []
        expectArray = []
        expectInfo = "\? \(y/n\)\[n\]"
        expectArray = np.append(expectArray, expectInfo.encode('ascii'))

        for expectInfo in ord_input["endStr"]:
            expectInfo = expectInfo.replace(")", "\)")
            expectArray = np.append(expectArray, expectInfo.encode('ascii'))
        expectArray = expectArray.tolist()

        # 初始化crt命令
        for input_ini_info in input_ini:  # 所有变量赋值
            source_variable = self.oltData[input_ini_info["source_key"]]

            for olt_for_info in source_variable:  #
                # olt_for_info =  {'error_num': '833515', 'error_time': '2021-12-03 17:51:07'}
                ord_tmp = ord_input["ord"]
                for ord_info in input_ini_info["dense"]:
                    ord_tmp = ord_tmp.replace(ord_info["target_data"], str(olt_for_info[ord_info["source_data"]]))
                ord_array = np.append(ord_array, ord_tmp)
        # 执行crt命令
        for ord_info in ord_array:
            crt_ord = ord_info.encode('ascii')
            print_data = [
                {"text": "将要执行的命令:", "color": "33", "end": ""},
                {"text": str(crt_ord), "color": "32"},
            ]
            self.print_log(print_data, "INFO")

    def judge_time(self, condition, source_time):
        # 判断符号
        condition_tmp = condition.split('：')
        if len(condition_tmp) != 2:
            returnJson = {
                "code": "fatal",
                "msg": "时间格式错误",
                "log": condition
            }
            raise Exception(returnJson)
        start_time = condition_tmp[0][1:]
        start_symbol = condition_tmp[0][0]
        end_time = condition_tmp[1][0:-1]
        end_symbol = condition_tmp[1][-1]

        source_time = datetime.datetime.strptime(source_time, "%Y-%m-%d %H:%M:%S")

        if start_time == "all":
            pass
        elif start_symbol == "[":
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if source_time < start_time:
                return False
        elif start_symbol == "(":
            start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if source_time <= start_time:
                return False

        if end_time == "all":
            pass
        elif end_symbol == "]":
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            if source_time > end_time:
                return False
        elif end_symbol == ")":
            end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            if source_time >= end_time:
                return False
        return True

    def updateOltData(self, updateOltDataInfo):  # 更新全局变量
        interfaceJson = updateOltDataInfo["input_ini"]
        # 初始化
        input_json = updateOltDataInfo["input"]
        for info in interfaceJson:
            data_tmp = self.oltData[info["source_data"]]
            for source_data_info in info["source_num"]:
                data_tmp = data_tmp[source_data_info]
            formatJsonStr = json.dumps(input_json, ensure_ascii=False)  # 转换字符串
            input_json = formatJsonStr.replace(info["target_data"], data_tmp)
            input_json = json.loads(input_json)
        # 循环修改
        for input_info in input_json:
            change_data = self.oltData[input_info["source_key"]]
            change_key = input_info["source_key"]
            change_tmp = []

            if input_info["type"] == "time":
                change_data_len = len(change_data)

                for tmp_i in range(0, change_data_len):
                    tmp_change_data = change_data[tmp_i]
                    condition = input_info["condition"]["semiotic"]
                    source_time = tmp_change_data
                    for source_data_info in input_info["source_num"]:
                        source_time = source_time[source_data_info]
                    del_flag = self.judge_time(condition, source_time)
                    if del_flag:
                        change_tmp = np.append(change_tmp, tmp_change_data)

                self.oltData[change_key] = change_tmp

            elif input_info["type"] == "math":
                change_data_len = len(change_data)
                for tmp_i in range(0, change_data_len):
                    tmp_change_data = self.doMath(input_info["condition"], change_data[tmp_i])
                    change_tmp = np.append(change_tmp, tmp_change_data)

                self.oltData[change_key] = change_tmp
            elif input_info["type"] == "judge_num":
                change_data_len = len(change_data)
                for tmp_i in range(0, change_data_len):
                    save_flag = self.judge_num(input_info["condition"], change_data[tmp_i])
                    if save_flag:
                        change_tmp = np.append(change_tmp, change_data[tmp_i])

                self.oltData[change_key] = change_tmp

            elif input_info["type"] == "crop":
                # change_data_len = len(change_data)
                change_tmp = self.crop_array(input_info["condition"], change_data)
                print(change_tmp)

                self.oltData[change_key] = change_tmp

            # 返回数据
            # self.oltData[change_key] = change_tmp

    # 分割执行数据
    def crop_array(self, condition, source_data):
        start = int(condition.get('start', 0))
        end = int(condition.get('end', len(source_data)))
        step = int(condition.get('step', 1))
        if start == end:
            return_array = [source_data[start]]
        else:
            return_array = source_data[start:end:step]
        return return_array

    def _do_judge_num(self, condition, source_data):
        # print("_do_judge_num",condition,source_data)
        # 判断符号
        condition_tmp = condition.split(',')
        if len(condition_tmp) != 2:
            returnJson = {
                "code": "fatal",
                "msg": "时间格式错误",
                "log": condition
            }
            raise Exception(returnJson)

        source_data = int(source_data)

        start_data = condition_tmp[0][1:]
        start_symbol = condition_tmp[0][0]
        end_data = condition_tmp[1][0:-1]
        end_symbol = condition_tmp[1][-1]

        if start_data == "all" or start_data == "":
            pass
        elif start_symbol == "[":
            start_data = int(start_data)
            if source_data < start_data:
                return False
        elif start_symbol == "(":
            start_data = int(start_data)
            if source_data <= start_data:
                return False

        if end_data == "all" or end_data == "":
            pass
        elif end_symbol == "]":
            end_data = int(end_data)
            if source_data > end_data:
                return False
        elif end_symbol == ")":
            end_data = int(end_data)
            if source_data >= end_data:
                return False

        # print("123:",start_data,start_symbol,end_data,end_symbol)
        return True

    # 判断数字是否符合标准
    def judge_num(self, condition, source_data):
        # print("judge_num",condition,source_data)

        if condition["type"] == "and":
            # 需要所有都符合条件
            return_flag = True
            for info in condition["data"]:
                flag_tmp = self._do_judge_num(info["semiotic"], source_data[info["source_num"]])
                if flag_tmp == False:
                    return_flag = False
                    break

        elif condition["type"] == "or":
            # 有一个真则返回真
            return_flag = False
            for info in condition["data"]:
                flag_tmp = self._do_judge_num(info["semiotic"], source_data[info["source_num"]])
                if flag_tmp == True:
                    return_flag = True
                    break
        else:
            raise Exception("数值判断错误")

        return_flag_all = condition["is_save"]
        if not return_flag:
            return_flag_all = not return_flag_all
        return return_flag_all

        pass

    # 进行数学运算
    def doMath(self, condition, source_data):
        for info in condition:
            if info["semiotic"] == "+":
                source_data[info["source_num"]] = str(int(source_data[info["source_num"]]) + int(info["variable"]))

        return source_data

    def operateFuc(self, operateJson):
        oltInfo = self.oltInfo
        #
        if oltInfo["type"] == "HW":
            pass
            try:
                print_data = [
                    {"text": "正在建立连接:", "color": "33", "end": ""},
                    {"text": oltInfo["oltIp"], "color": "32"},
                ]
                self.print_log(print_data, "INFO")

                self.tn = telnetlib.Telnet(oltInfo["oltIp"], timeout=3)
                # self.tn.set_debuglevel(1)  # 进入调试模式
                self.loginOlt_hw(oltInfo)
            except Exception as e:
                returnJson = {
                    "code": "fatal",
                    "msg": "olt连接失败",
                    "log": e
                }
                raise Exception(returnJson)

        if self.oltType == "HW":

            for info in operateJson:
                info.setdefault("desc", "")
                info.setdefault("input_ini", [])

                # 整体初始化
                info_ini = self.input_ini(info["input_ini"])

                for info_tmp in info_ini:
                    formatJsonStr = json.dumps(info, ensure_ascii=False)  # 转换字符串
                    info = formatJsonStr.replace(info_tmp, str(info_ini[info_tmp]))
                    info = json.loads(info)

                if info["type"] == "en_co":
                    self.en_co_hw()
                elif info["type"] == "display":

                    self.display_hw(info)
                elif info["type"] == "interface":

                    self.interface_hw(info)

                elif info["type"] == "readCrt":
                    print_data = [
                        {"text": "查看要执行的命令:", "color": "33", "end": ""},
                        {"text": info["desc"], "color": "32"},
                    ]
                    self.print_log(print_data, "INFO")

                    self.readCrt_hw(info)
                elif info["type"] == "generate_script":
                    print_data = [
                        {"text": "开始生成脚本:", "color": "33", "end": ""},
                        {"text": info["desc"], "color": "32"},
                    ]
                    self.print_log(print_data, "INFO")
                    self.generate_script_hw(info)

                elif info["type"] == "doCrt":
                    print_data = [
                        {"text": "执行命令:", "color": "33", "end": ""},
                        {"text": info["desc"], "color": "32"},
                    ]
                    self.print_log(print_data, "INFO")

                    self.doCrt_hw(info)
                elif info["type"] == "updateOltData":
                    print_data = [
                        {"text": "更新数据:", "color": "33", "end": ""},
                        {"text": info["desc"], "color": "32"},
                    ]
                    self.print_log(print_data, "INFO")
                    self.updateOltData(info)
                elif info["type"] == "get_poninfo_loid":

                    self.getPon_loid_hw(info)
        else:
            pass
            print("未知olt类型", self.oltType)
