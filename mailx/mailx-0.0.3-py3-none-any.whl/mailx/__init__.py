#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
from email.mime.text import MIMEText
import smtplib
import showlog
import envx


def send_mail(
        to_addrs: list,  # 收信人
        sub: str = "标题（测试）",  # 标题
        content: str = "内容（测试）",  # 内容
        con_info: dict = None,
):
    from_name = con_info.get('from_name', 'unknown')  # 发信人名称
    smtp_server = con_info.get('smtp_server')  # SMTP服务地址
    smtp_username = con_info.get('smtp_username')  # 发信账号
    smtp_password = con_info.get('smtp_password')  # SMTP密码
    smtp_port = con_info.get('smtp_port')  # SMTP端口
    msg = MIMEText(
        _text=content,
        _subtype='plain'
    )
    msg['Subject'] = sub  # 标题
    msg['From'] = "%s<%s>" % (from_name, smtp_username)  # 发信人信息

    server = smtplib.SMTP()
    server.connect(smtp_server, smtp_port)
    server.login(
        user=smtp_username,
        password=smtp_password
    )
    res = server.sendmail(
        from_addr=smtp_username,
        to_addrs=to_addrs,
        msg=msg.as_string()
    )
    server.close()
    return res


def quick_send_mail(
        sub: str,  # 标题
        content: str,  # 内容
        to_addrs: list = None,  # 收件人列表
        env_file_name: str = 'mail.env',  # 环境文件
):
    inner_env = envx.read(file_name=env_file_name)
    if inner_env is None:
        showlog.warning('未找到配置文件: %s' % env_file_name)
        return
    else:
        if to_addrs is None:
            to_addrs_str = inner_env.get('to_addrs')
            if to_addrs_str is None or len(to_addrs_str) == 0:
                inner_to_addrs = []
            else:
                inner_to_addrs = to_addrs_str.split(',')
        else:
            inner_to_addrs = to_addrs
        con_info = {
            "smtp_server": inner_env['smtp_server'],
            "smtp_username": inner_env['smtp_username'],
            "smtp_password": inner_env['smtp_password'],
            "smtp_port": inner_env['smtp_port'],
            "to_addrs": inner_to_addrs,
            "from_name": inner_env.get('from_name')
        }
        res = send_mail(
            to_addrs=inner_to_addrs,
            sub=sub,
            content=content,
            con_info=con_info
        )
        return res
