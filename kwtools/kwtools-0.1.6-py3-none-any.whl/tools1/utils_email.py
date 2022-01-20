## exchange邮件发送相关的库包
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3
import smtplib
from email.mime.text import MIMEText
urllib3.disable_warnings() # 可以避免老是报错...



class kEmailSenderExchange():
    "使用outlook邮箱的那种模式发邮件"

    def __init__(self):
        #此句用来消除ssl证书错误，exchange使用自签证书需加上
        BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

        # 配置基本用户信息
        # self.user_name = "lvzc1"
        # self.password = "Lzc15168201914*"

        # self.user_name = "chenb"
        # self.password = "Zz00000000."

        self.user_name = "yangjj4"
        self.password = "Yangjiajing131#"
        self.email_domain = "ziroom.com"
        self.server_address = "zr-casc.ziroom.com"

        # 登录
        self.login()


    def login(self, user_name=None, password=None, email_domain=None, server_address=None):
        """后续应该建立异常捕获机制"""
        user_name = user_name if user_name else self.user_name
        password = password if password else self.password
        email_domain = email_domain if email_domain else self.email_domain
        server_address = server_address if server_address else self.server_address

        # 连接/登录 我的邮箱
        my_email_address = "{}@{}".format(user_name, email_domain)
        cred = Credentials(r'{}\{}'.format(email_domain, user_name), password)
        config = Configuration(server=server_address, credentials=cred, auth_type=NTLM)
        self.account = Account(
            primary_smtp_address=my_email_address, config=config, autodiscover=False, access_type=DELEGATE
        )
        print('我的邮箱已连接/登录...\n')


    def python_str_2_html_tag(self, message, **kwargs):
        # print(kwargs)
        message = message.replace("\n", "<br>")
        message = message.replace(" ", "&nbsp;")
        message = message.replace("font:", "font ")
        message = message.replace("div:", "div ")
        message = message.replace("table:", "table ")
        message = message.replace("th:", "th ")
        # message = message.replace('<tr>', '<tr align="center">')
        # message = message.replace('&lt;', '<')
        # message = message.replace('&gt;', '>')
        message = message
        return message


    def k_send_msg(self, message, subject_="无主题", receiver_lst=['15168201914@163.com'], need_to_conver_html=False, **kwargs):
        # 1. 把message先转换成能在浏览器正常显示的 html类型 的文本
        if need_to_conver_html:
            message = self.python_str_2_html_tag(message)

        # 2. 编辑邮件内容
        email_obj = Message(
            account=self.account,
            subject=subject_,
            body=HTMLBody(message),
            # to_recipients=[Mailbox(email_address=['365079025@qq.com'])]
            to_recipients = [Mailbox(email_address=receiver_address) for receiver_address in receiver_lst]
        )

        # 3. 发送邮件
            ### 随机睡眠: 防止被封
        random_time = random.random()*2
        print("发送邮件前，睡眠 {}  中。。。".format(random_time))
        time.sleep(random_time)
            ### 异常捕获
        try:
            x = email_obj.send()
            print("邮件发送成功！")
            return True
        except Exception as e:
            print(e)
            print("邮件发送失败！")
            return False



class kEmailSenderSmtp():
    "**使用中转模式发邮件"

    def __init__(self):
        # 发邮件相关参数
        self.sender='365079025@qq.com'
        # qq邮箱授权码
        self.password="rrtvphpkphylbgja"
        # 服务提供商的邮箱后缀??
        self.smtpsever='smtp.qq.com'
        # 端口号
        self.port=465
        # 链接服务器发送 (是个发送邮件的实例对象)
        self.smtp = smtplib.SMTP_SSL(self.smtpsever,self.port)
        # 登录
        self.login()


    def login(self):
        #登录
            ### 登录时候容易连接错误报错,应该捕获异常,并重新执行!
        try:
            for count in range(1, 4): # 尝试3次连续登录
                try:
                    print("正在 login 邮箱..")
                    self.smtp.quit() #1. 先退出连接
                    self.smtp.connect(self.smtpsever, self.port) #2. 再连接
                    self.smtp.login(self.sender, self.password)
                    print("邮箱 login 成功..")
                    break # 如果能正常登录, 则退出循环
                except Exception as e:
                    print("尝试第 {} 次login 邮箱..".format(count))
                    time.sleep(1)
                    print(e)
        except Exception as e:
            print(e)
            raise Exception("邮箱连续登录3次, 依旧出错...")


    def python_str_2_html_tag(self, message, **kwargs):
        # print(kwargs)
        message_html = message.replace("\n", "<br>")
        message_html = message_html.replace(" ", "&nbsp;")
        return message_html


    def k_send_msg(self, message, subject_="无主题", receiver_lst=['15168201914@163.com'], **kwargs):
        """
        in: 1. receiver_lst 接受者的邮箱
            2. message为需要发生邮件的正文内容
            3. subject 邮件显示中的第一栏（主题）

        notes:
            1. 这里传送进来的message中的\n换行是python语法中的，而如果要在前端html中展示换行，
                需要使用<br>,或者<div>等html标签

        tips:
            1. 字体大小
                最小： <font size="1">a</font>
                最大： <font size="6">a</font>
            2. 字体颜色
                字体红色： <font color="#ff0000"> a </font>
            3. 背景颜色
                背景颜色黄色：<span style="background-color: rgb(255, 255, 0);"> a </span>

        todo:
            想用**kwargs的关键词传参，来自动使某些需要的元素格式化（字体大小、颜色等）
        """

        # 1. 把msg先转换成能在浏览器正常显示的 html类型 的文本
        message_html = self.python_str_2_html_tag(message)

        # 2. 编辑邮件内容
        body = message_html # 正文内容
        msg=MIMEText(body,'html','utf-8') ## 使用html格式解析器
        msg['from'] = self.sender # 不加这行也可以发送，但是邮箱列表中没有发件人的头像和名称。
        msg['subject'] = subject_

        # 3. 发送邮件
            ### 随机睡眠: 防止被封
        random_time = random.random()*3
        print("发送邮件前，睡眠 {}  中。。。".format(random_time))
        time.sleep(random_time)
            ### 异常捕获
        for try_time in range(3):
            try:
                self.smtp.sendmail(self.sender, receiver_lst, msg.as_string())  #发送
                print("邮件发送成功！")
                return True
            except Exception as e:
                print(e)
                print("邮件发送失败！尝试重新login....")
                self.login()
        return False


    def quit(self):
        #关闭
        self.smtp.quit()



def txt_2_html(txt):
    txt = txt.replace("\n", "<br>")
    txt = txt.replace(" ", "&nbsp;")
    txt = txt.replace("font:", "font ")
    txt = txt.replace("div:", "div ")
    txt = txt.replace("table:", "table ")
    txt = txt.replace("th:", "th ")
    txt_html = txt
    return txt_html




if __name__ == '__main__':
    sender1 = kEmailSenderExchange()
    sender1.k_send_msg("tt: exchange")
    sender2 = kEmailSenderSmtp()
    sender2.k_send_msg("tt: smtp")
