from pyocs.pyocs_list import PyocsList
from pyocs.pyocs_software import PyocsSoftware
import json
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import datetime
import sys

#传递2个参数：参数1-是否发送邮件；参数2-保存搜索结果的路径

class DgSoftware:
    Team = []
    SearchID_21D = None
    SearchID_7D_P1 = None
    SearchID_7D_P2 = None
    OutPutList1 = list(range(0, 100))
    OutPutList2 = list(range(0, 100))

    LoadData = ["21天未关闭任务","7天未更新任务","ALL"]
    LoadMember = ["本战队成员","ALL"]

    def __init__(self):
        with open("TeamData.json", 'r', encoding='UTF-8') as f:
            temp = json.loads(f.read())
            self.Team.clear()
            Tmplist = temp.keys()
            for key in Tmplist:
                self.Team.append(key)

    def sendmail(self, Teamvalue,loaddata):
        try:
            self.gen_ocs_list(Teamvalue,loaddata)
            print("启动邮件发送...")

            try:
                with open("TeamData.json", 'r', encoding='UTF-8') as f:
                    temp = json.loads(f.read())
                    sender = temp[Teamvalue]['mail_sender']
                    passwd = temp[Teamvalue]['mail_passwaord']
                    receiver = temp[Teamvalue]['mail_receiver']
                    mailtitle = temp[Teamvalue]['mail_title']
            except:
                print("读取文件邮件配置错误，请确认json文件！")
                exit(0)

            smtpserver='smtp.cvte.com'
            mailsendfrom="订单节点提醒"

            if sender == "" or passwd == "" or receiver == "" or mailtitle == "":
                print("读取文件邮件配置错误，请确认json文件！")
                exit(0)               

            planmsg1 = ""
            
            if len(self.OutPutList1) != 0 or len(self.OutPutList1) != 0:
                for index in range(0,len(self.OutPutList1)):
                    if index == 0:
                        planmsg1 = planmsg1 + "21天未关闭任务：\n"
                    planmsg1=planmsg1 + self.OutPutList1[index] + '\n'

                planmsg1 = planmsg1 + "\n\n"
                for index in range(0,len(self.OutPutList2)):
                    if index == 0:
                        planmsg1 = planmsg1 + "7天未跟进任务：\n"
                    planmsg1=planmsg1 + self.OutPutList2[index] + '\n'

            if planmsg1 == "":
                planmsg1 = "Dear ALL:\n\n    恭喜！没有任何需要预警的订单！\n\n"
            else:
                planmsg1 = "Dear ALL:\n\n    如下订单时间节点即将到来，请及时跟进和备注！\n\n" + planmsg1 + "\n\n"

            msg = MIMEText(planmsg1,'plain','utf-8')
            msg['From']=Header(mailsendfrom,'utf-8')
            msg['To']=Header(receiver)
            msg['Subject']=Header(mailtitle,'utf-8')

            server= smtplib.SMTP(smtpserver,25)
            server.login(sender,passwd)
            server.sendmail(sender,receiver.split(','),msg.as_string())

            server.quit()
            print("邮件发送完成")
        except:
            print("邮件发送失败，请确认原因！")
            exit(0)

    def Get_advanch_filter_21D(self,memberdata):
        advanced_search = {
           "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                 "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_LE", "input1": "已完成", "input2": "null",
                 "offset": "null"},
           "1": {"search_field_name": "Task.sw_user_id", "search_field_id": "555", "search_field_type": "19",
                 "search_field_rel_obj": "Users", "search_opr": "TDD_OPER_INC",
                 "input1": memberdata, "input2": "null", "offset": "null"},
           "2": {"search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status", "search_field_id": "1637",
                 "search_field_type": "19", "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL",
                 "input1": "已代测发放", "input2": "null", "offset": "null"},
           "3": {"search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status", "search_field_id": "1637",
                 "search_field_type": "19", "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL",
                 "input1": "已最终发放", "input2": "null", "offset": "null"},
           "4": {"search_field_name": "Task.plan_end_date", "search_field_id": "548", "search_field_type": "9",
                 "search_field_rel_obj": "null", "search_opr": "TDD_OPER_RECENT", "input1": "19", "input2": "null",
                 "offset": "TDD_OFFSET_DAY"},
           "5": {"search_field_name": "Task.plan_end_date", "search_field_id": "548", "search_field_type": "9",
                 "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": "1000", "input2": "null",
                 "offset": "TDD_OFFSET_DAY"},
           "6": {"search_field_name": "Task.subject", "search_field_id": "554", "search_field_type": "5",
                 "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC", "input1": "虚拟", "input2": "null",
                 "offset": "null"},
           "7": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                 "search_field_rel_obj": "null", "search_opr": "TDD_OPER_RECENT", "input1": "19", "input2": "null",
                 "offset": "TDD_OFFSET_DAY"},
           "8": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                 "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": "1000", "input2": "null",
                 "offset": "TDD_OFFSET_DAY"}
            }

        condition = "1 and 2 and (((3 or 4) and  (not 5 and not 6)) or (7 and  not 8 and not 9))"

        searchid = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def Get_advanch_filter_7D_P1(self,memberdata):
        advanced_search = {
            "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                   "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_LE", "input1": "已完成", "input2": "null",
                   "offset": "null"},
            "1": {"search_field_name": "Task.sw_user_id", "search_field_id": "555", "search_field_type": "19",
                   "search_field_rel_obj": "Users", "search_opr": "TDD_OPER_INC",
                   "input1": memberdata, "input2": "null", "offset": "null"},
            "2": {"search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status", "search_field_id": "1637",
                   "search_field_type": "19", "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL",
                   "input1": "已代测发放", "input2": "null", "offset": "null"},
            "3": {"search_field_name": "Task.rel_obj_id.rel_obj_id.mf_status", "search_field_id": "1637",
                   "search_field_type": "19", "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_EQUAL",
                   "input1": "已最终发放", "input2": "null", "offset": "null"},
            "4": {"search_field_name": "Task.plan_end_date", "search_field_id": "548", "search_field_type": "9",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_RECENT", "input1": "20", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
            "5": {"search_field_name": "Task.plan_end_date", "search_field_id": "548", "search_field_type": "9",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": "1000", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
            "6": {"search_field_name": "Task.update_time", "search_field_id": "586", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_RECENT", "input1": "6", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
            "7": {"search_field_name": "Task.update_time", "search_field_id": "586", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": "1000", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"}
            }

        condition = "(1 and 2 and (((3 or 4) and  (not 5 and not 6))) and (not 7 and not 8))"

        searchid = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid

    def Get_advanch_filter_7D_P2(self,memberdata):
        advanced_search = {
            "0": {"search_field_name": "Task.status", "search_field_id": "584", "search_field_type": "19",
                   "search_field_rel_obj": "Enums", "search_opr": "TDD_OPER_LE", "input1": "已完成", "input2": "null",
                   "offset": "null"},
            "1": {"search_field_name": "Task.sw_user_id", "search_field_id": "555", "search_field_type": "19",
                   "search_field_rel_obj": "Users", "search_opr": "TDD_OPER_INC",
                   "input1": memberdata, "input2": "null", "offset": "null"},
            "2": {"search_field_name": "Task.subject", "search_field_id": "554", "search_field_type": "5",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_INC", "input1": "虚拟", "input2": "null",
                   "offset": "null"},
            "3": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_RECENT", "input1": "20", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
            "4": {"search_field_name": "Task.create_time", "search_field_id": "585", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": "1000", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
            "5": {"search_field_name": "Task.update_time", "search_field_id": "586", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_RECENT", "input1": "6", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"},
            "6": {"search_field_name": "Task.update_time", "search_field_id": "586", "search_field_type": "10",
                   "search_field_rel_obj": "null", "search_opr": "TDD_OPER_FUTURE", "input1": "1000", "input2": "null",
                   "offset": "TDD_OFFSET_DAY"}
            }

        condition = "1 and 2 and  (3 and  not 4 and not 5) and ( not 6 and not 7)"

        searchid = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
        return searchid


    def loaddata(self,Teamvalue):
        try:
            print(Teamvalue)
            with open("TeamData.json", 'r',encoding='UTF-8') as f:
              temp = json.loads(f.read())
              memberlist = str(temp[Teamvalue]['member'])
              if memberlist == "":
                  memberlist = None
                  print("战队成员为空，请到TeamData.json文件中编辑")
                  exit(0)
              else:
                  memberlist = str(memberlist).split(',')

              return memberlist
        except:
              print("读取json文件错误，请确认！")
              exit(0)
        

    def gen_ocs_list(self, Teamvalue,loaddata):
        try:
            MemberList = self.loaddata(Teamvalue)
            LoadDataIndex = self.LoadData.index(loaddata)

            OutPutFile = open(sys.argv[2], "w") 
            memberliststr = ""
            for member in MemberList:
                memberliststr = memberliststr + " " + str(member)


            ocsurl = "http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:all/"

            self.OutPutList1.clear()
            self.OutPutList2.clear()
            print("正在导出数据，请稍后......",file=OutPutFile)

            if LoadDataIndex == 0 or LoadDataIndex == 2:
                searchid_21D = self.Get_advanch_filter_21D(memberliststr)
                print("\n21天未关闭订单数据：(Search_Id: " + searchid_21D + ")",file=OutPutFile)
                (count21D, project21D) = PyocsList().get_ocs_id_list(search_id=str(searchid_21D))
                (count21Dtmp, user21D) = PyocsList().get_ocs_engineer_list(search_id=str(searchid_21D))

                if count21D == 0:
                    print("恭喜，无该类型超期订单",file=OutPutFile)
                else:
                    List1 = list(range(0, count21D))
                    for index in range(0, count21D):
                        List1[index] = user21D[index] + "  :  " + ocsurl + str(project21D[index])

                    self.OutPutList1 = sorted(List1[0:count21D])
                    for index in range(0, count21D):
                        print(self.OutPutList1[index],file=OutPutFile)

            if LoadDataIndex == 1 or LoadDataIndex == 2:
                searchid_7D_P1 = self.Get_advanch_filter_7D_P1(memberliststr)
                searchid_7D_P2 = self.Get_advanch_filter_7D_P2(memberliststr)
                print("\n7天未更新订单数据：(Search_Id: " + searchid_7D_P1 + " " + searchid_7D_P2 + ')',file=OutPutFile)
                (count7D_1, project7D_P1) = PyocsList().get_ocs_id_list(search_id=str(searchid_7D_P1))
                (count7D_1tmp, user7D_1) = PyocsList().get_ocs_engineer_list(search_id=str(searchid_7D_P1))

                (count7D_2, project7D_P2) = PyocsList().get_ocs_id_list(search_id=str(searchid_7D_P2))
                (count7D_2tmp, user7D_2) = PyocsList().get_ocs_engineer_list(search_id=str(searchid_7D_P2))

                count7D = count7D_1 + count7D_2
                project7D = project7D_P1 + project7D_P2
                user7D = user7D_1 + user7D_2

                if count7D == 0:
                    print("恭喜，无该类型超期订单",file=OutPutFile)
                else:
                    List2 = list(range(0, count7D))
                    for index in range(0, count7D):
                        List2[index] = user7D[index] + "  :  " + ocsurl + str(project7D[index])

                    self.OutPutList2 = sorted(List2[0:count7D])
                    for index in range(0, count7D):
                        print(self.OutPutList2[index],file=OutPutFile)

        finally:
            print("\n结束")


if __name__ == '__main__':
    guiSearchSW = DgSoftware()
    try:
        with open("auto_run.json", 'r', encoding='UTF-8') as f:
            temp = json.loads(f.read())
            Teamvalue = temp["SelectTeam"]
            loaddata = temp["SelectData"]

            if Teamvalue != "" and loaddata != "":
                if sys.argv[1] == "1":
                    guiSearchSW.sendmail(Teamvalue, loaddata)
                else:
                    guiSearchSW.gen_ocs_list(Teamvalue,loaddata)
    except:
        print("run error!!")


    #
