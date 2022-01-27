import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header


# 邮件通知
class Mail:
    def __init__(self, host, user, password):
        self.host = host
        self.username = user
        self.password = password

    def send_mail(self, mail_data, receivers):
        print(f'向{receivers}发送邮件...')
        # 创建一个带附件的实例
        message = MIMEMultipart()
        message['From'] = Header(self.username)
        message['To'] = Header(",".join(receivers))
        message['Subject'] = Header(mail_data.get('title'), 'utf-8')

        # 邮件正文内容
        message.attach(MIMEText(mail_data.get('body'), 'plain', 'utf-8'))
        # 附件
        file_path = mail_data.get('file_path')
        if file_path:
            # 构造附件，传送当前目录下的文件
            att1 = MIMEText(open(file_path, 'r').read(), 'base64', 'utf-8')
            att1["Content-Type"] = 'application/octet-stream'
            # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
            file_name = mail_data.get('file_name')
            att1["Content-Disposition"] = f'attachment; filename="{file_name}"'
            message.attach(att1)

        # 连接
        conn = smtplib.SMTP_SSL(self.host, 465)
        # 登录
        conn.login(self.username, self.password)
        # 发送邮件
        try:
            conn.sendmail(self.username, receivers, message.as_string())
        except Exception as e:
            print(f'发送失败: {str(e)}')
        else:
            print('发送成功')
        # 断开连接
        conn.quit()


# 初始化
mail = Mail('smtphm.qiye.163.com', 'kang.yang@qizhidao.com', 'WzQzd2019')


if __name__ == '__main__':
    # 邮件内容
    mail_data = {
        'title': '测试邮件',
        'body': '测试',
        'file_path': None,
        'file_name': None
    }
    # 收件人
    receiver_list = ['kang.yang@qizhidao.com', 'kang.yang@qizhidao.com']
    mail.send_mail(mail_data, receiver_list)


