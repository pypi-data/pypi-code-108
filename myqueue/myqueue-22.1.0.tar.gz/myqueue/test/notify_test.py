from __future__ import annotations
import getpass
import smtplib


class SMTP:
    def __init__(self):
        self.emails = []

    def __call__(self, host):
        return self

    def login(self, username, password):
        assert username == 'me'
        assert password == '********'

    def sendmail(self, fro, to, data):
        self.emails.append(data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


def test_notify(mq, monkeypatch):
    smtp = SMTP()
    monkeypatch.setattr(smtplib, 'SMTP_SSL', smtp)
    monkeypatch.setattr(getpass, 'getpass', lambda: '********')
    monkeypatch.setattr('builtins.input', lambda _: 'yes')
    mq('submit math@sin+3.13')
    mq('modify . -s q -E rdA')
    mq.wait()
    mq('kick')
    test, notification = smtp.emails
    assert 'Subject: Test email from myqueue' in test
    assert 'Subject: MyQueue: 1 running, 1 done' in notification
