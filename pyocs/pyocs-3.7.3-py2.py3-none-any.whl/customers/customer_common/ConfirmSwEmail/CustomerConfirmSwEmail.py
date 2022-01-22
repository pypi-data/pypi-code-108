import datetime
import email
import poplib
import email.policy
import telnetlib
import time
import os
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from pyocs import pyocs_software
confirm_task = pyocs_software.PyocsSoftware()
pop3_server = 'pop.cvte.com'
poplib._MAXLINE=20480
#=============================================================
# 脚本介绍和说明：
# 1、在CVTE企业网页邮箱里设置把收取3个月的邮件改成收取全部
# 2、使用crontab -e 设置一个定时任务，每30分钟执行一次改脚本
# 3、这个脚本第一次运行会生产一个文件counttxt.txt记录目前邮件数
# 4、下次运行会获取最新的邮件的数，然后处理新增的邮件，查找这些邮件里面标题为subject_title的邮件
# 5、标题为subject_title的邮件，采用字符串处理获取ocs 和 软件时间，所以邮件必须包含完整的软件名
# 6、脚本自动调用pyocs接口实现 通过ocs 和软件是时间完成软件和烧录bin确认的功能
# 7、通过LogfileDaily.txt记录每天的确认邮件处理记录
# 8、通过Logfiletotal.txt记录所有的确认邮件处理记录
#==============================================================
# 需要个人配置的地方
# subject_title 是确认软件邮件标题必须包含的特定字符，比如如下"软件确认"
# 则每一封标题带有软件确认的邮件都会进行解析
# email_user 邮件账户
# password 邮件密码
# counttxtpath/LogfileDailypath/Logfiletotalpath 个人pyocs ConfirmSwEmail 目录的绝对路径+XXX.txt
#=============================================================
subject_title="订单软件确认"
email_user = 'xxxxxx@cvte.com'
password = 'xxxxxx'
counttxtpath="/disk2/zhaoxinan/Toolszxn/Confirm_sw_email/pyocs/customers/customer_common/ConfirmSwEmail/counttxt.txt"
LogfileDailypath="/disk2/zhaoxinan/Toolszxn/Confirm_sw_email/pyocs/customers/customer_common/ConfirmSwEmail/LogfileDaily.txt"
Logfiletotalpath="/disk2/zhaoxinan/Toolszxn/Confirm_sw_email/pyocs/customers/customer_common/ConfirmSwEmail/Logfiletotal.txt"
#==============================================================

#==============================================================
# 递归解析出邮件内容
#==============================================================
def get_email_txt(msg):
    if (msg.is_multipart()):
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            #print('part ='+str(n))
            get_email_txt(part)
    else:
        content_type = msg.get_content_type()
        if content_type=='text/plain':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            content = content.decode(charset)
            if len(content) > 15:
                email_confirm_sw_to_ocs(content)
#==============================================================
# 解析有家必要的一些字符转换
#==============================================================
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset

#==============================================================
# 确认软件邮件 ocs号和软件时间提取，并执行确认软件动作
#==============================================================
def email_confirm_sw_to_ocs(textpart):
    ocsFlag=False
    swFlag=False
    #print(len(str(textpart)))
    if len(str(textpart)) < 15:
        return
    for i in range(len(str(textpart))-15):
        if textpart[i] == 'C' and (textpart[i+1] == 'P' or textpart[i+1] == 'S'):
            ocsnum = str(textpart[i+2])+str(textpart[i+3])+str(textpart[i+4])+str(textpart[i+5])+str(textpart[i+6])+str(textpart[i+7])
            print(ocsnum)
            ocsFlag=True
        timerstr = textpart[i]+textpart[i+1]+textpart[i+2]+textpart[i+3]+textpart[i+4]+textpart[i+5]+textpart[i+6]+textpart[i+7]+\
                   textpart[i+9]+textpart[i+10]+textpart[i+11]+textpart[i+12]+textpart[i+13]+textpart[i+14]
        if timerstr.isdigit():
            software_time = textpart[i]+textpart[i+1]+textpart[i+2]+textpart[i+3]+textpart[i+4]+textpart[i+5]+textpart[i+6]+textpart[i+7]+\
                            textpart[i+8]+textpart[i+9]+textpart[i+10]+textpart[i+11]+textpart[i+12]+textpart[i+13]+textpart[i+14]
            print(software_time)
            swFlag = True
        if ocsFlag == True and swFlag == True:
            ocsFlag = False
            swFlag = False

            lock_Status = confirm_task.get_sw_lock_status(ocsnum,software_time)
            if lock_Status == "lock":
                ret_text = "sw lock"
            elif lock_Status == "unlock":
                ret_text = confirm_task.set_enable_software_confirm_for_ocs(ocs_number=ocsnum,sw_name=software_time,confirm_type=4)
            else:
                ret_text = None
            print("lock status ："+ret_text)
            confirm_sw_statistic_data(ocsnum,software_time,ret_text)
        if textpart[i] == '发' and textpart[i+1] == '件' and textpart[i+2] == '人':
            break

#==============================================================
# 确认软件邮件 统计模块
#==============================================================
def confirm_sw_statistic_data(ocsnum, sw_name, ret_text):
    if ret_text == "sw lock":
        newlog = "订单：http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/" + str(ocsnum) + "   软件版本：" + str(sw_name) + "  软件被禁用,请确认是否需要更新软件!\n"
    else:
        if ret_text == None:
            newlog = "订单：http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/"+str(ocsnum)+"   软件版本："+str(sw_name)+"  确认失败!\n"
        elif int(ret_text) > 0:
            newlog = "订单：http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/"+str(ocsnum)+"   软件版本："+str(sw_name)+"  确认成功!\n"
        else:
            newlog = "订单：http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:my/"+str(ocsnum)+"   软件版本："+str(sw_name)+"  确认失败!\n"
    #统计当天的数据
    fd = open(LogfileDailypath, 'a+',encoding='utf-8',errors='ignore')
    fd.write(newlog)
    fd.close()
    #统计总的数据
    ft = open(Logfiletotalpath, 'a+',encoding='utf-8',errors='ignore')
    ft.write(newlog)
    ft.close()

#==============================================================
# 主程序
# 登录邮箱。获取邮件个数，对比处理新增邮件个数
# 将名称含有subject_title 特殊字符的邮件才进行解析处理。
#==============================================================
if __name__ == '__main__':
    # 连接到POP3服务器,有些邮箱服务器需要ssl加密，可以使用poplib.POP3_SSL
    try:
        telnetlib.Telnet('pop.cvte.com', 995)
        server = poplib.POP3_SSL(pop3_server, 995, timeout=10)
    except:
        time.sleep(5)
        server = poplib.POP3(pop3_server, 110, timeout=10)

    # 可以打开或关闭调试信息
    # server.set_debuglevel(1)
    # 打印POP3服务器的欢迎文字:
    print(server.getwelcome().decode('utf-8'))

    # 身份认证:
    server.user(email_user)
    server.pass_(password)
    # 返回邮件数量和占用空间
    print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    new_email_num = len(mails)
    print("当前邮件个数 ="+str(new_email_num))

    if os.path.exists(counttxtpath):
        #记录文件存在
        fr =open(counttxtpath)
        old_email_num = fr.read()

        if (str(old_email_num) == str(new_email_num)):
            #没有新邮件
            print("没有新邮件")
            fr.close()
        else:
            #有新邮件，得到邮件个数差值
            dif_value = int(new_email_num) - int(old_email_num)
            fr.close()
            #记录新的邮件个数
            fw = open(counttxtpath, 'w',encoding='utf-8',errors='ignore')
            fw.write(str(new_email_num))
            fw.close()

            #print(int(old_email_num))
            #print(int(new_email_num))
            for index in range(int(old_email_num)+1, int(new_email_num)+1):
                resp, lines, octets = server.retr(index)
                # lines存储了邮件的原始文本的每一行
                # 邮件的原始文本:
                msg_content = b'\r\n'.join(lines).decode('utf-8','ignore')

                msg = Parser().parsestr(msg_content)
                subject_str = decode_str(msg.get('Subject',''))
                if subject_title in str(subject_str):
                    print(subject_str)
                    get_email_txt(msg)
                    print("\n\n-------------------------------一封邮件处理完毕-------------------------------\n\n")
            #关闭连接
            server.quit()
    else:
        #记录文件不存在
        #第一次运行,创建并写入文件
        f = open(counttxtpath, 'w',encoding='utf-8',errors='ignore')
        f.write(str(new_email_num))
        f.close()
