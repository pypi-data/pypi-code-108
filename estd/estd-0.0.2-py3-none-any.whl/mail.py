import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


class Mail:
    def __init__(self, email: str, password: str, host: str = "smtp.qq.com", port: int = 465):
        self.email = email
        self.password = password
        self.host = host
        self.port = port

    def send(self, sender: str, receivers: list, subject: str, body: str, files: list = None):
        if files:
            files = files.split(",")
        smtp = smtplib.SMTP_SSL(self.host, self.port)
        smtp.login(self.email, self.password)
        mm = MIMEMultipart()
        mm["From"] = sender
        mm["Subject"] = Header(subject, "utf-8")
        body = body.replace("\\n", "<br />")
        body = body.replace("\n", "<br />")
        mm.attach(MIMEText(body, "html", "utf-8"))
        if files:
            for filename in files:
                p = Path(filename).absolute()
                with p.open("rb") as f:
                    attachment = MIMEText(f.read(), "base64", "utf-8")
                    attachment.add_header("Content-Disposition", "attachment", filename=p.name)
                    mm.attach(attachment)
        sender += f"<{sender}>"
        smtp.sendmail(sender, receivers, mm.as_string())
        smtp.close()
