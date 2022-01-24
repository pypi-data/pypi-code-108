from feapder.utils import tools

# 邮件报警
EMAIL_SENDER = "feapder@163.com"  # 发件人
EMAIL_PASSWORD = "YPVZHXFVVDPCJGTH"  # 授权码
EMAIL_RECEIVER = ["897702931@qq.com", "564773807@qq.com"]  # 收件人 支持列表，可指定多个 支持列表，可指定多个

tools.email_warning(
    message="test",
    title="测试",
    email_sender=EMAIL_SENDER,
    email_password=EMAIL_PASSWORD,
    email_receiver=EMAIL_RECEIVER,
    rate_limit=0,
)
