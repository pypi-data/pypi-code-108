from __future__ import annotations
import smtplib
import stat
from collections import defaultdict
from email.mime.text import MIMEText
import getpass
from pathlib import Path

from myqueue.config import Configuration
from myqueue.task import Task
from myqueue.utils import mqhome


def send_notification(tasks: list[Task],
                      email: str,
                      host: str,
                      username: str = None) -> list[tuple[Task, str]]:
    """Compose and send email."""
    notifications = []
    for task in tasks:
        character = task.state.value
        if character in 'dMTFC' and 'r' in task.notifications:
            task.notifications = task.notifications.replace('r', '')
            notifications.append((task, 'running'))
        if character in task.notifications:
            task.notifications = task.notifications.replace(character, '')
            notifications.append((task, task.state.name))
    if notifications:
        count: dict[str, int] = defaultdict(int)
        lines = []
        for task, name in notifications:
            count[name] += 1
            lines.append(f'{name}: {task}')
        subject = 'MyQueue: ' + ', '.join(f'{c} {name}'
                                          for name, c in count.items())
        body = '\n'.join(lines)
        password_file = mqhome() / f'.myqueue/{host}'
        password = read_password(password_file)
        send_mail(subject, body,
                  to=email,
                  fro=email,
                  host=host,
                  username=username or email,
                  password=password)
    return notifications


def send_mail(subject: str,
              body: str,
              to: str,
              fro: str,
              host: str,
              username: str,
              password: str) -> None:
    """Send an email.

    >>> send_mail('MyQueue: bla-bla',
    ...          'Hi!\\nHow are you?\\n',
    ...          'you@myqueue.org',
    ...          'me@myqueue.org',
    ...          'test.smtp.org',
    ...          'me',
    ...          '********')
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = fro
    msg['To'] = to
    data = msg.as_string()
    if host != 'test.smtp.org':
        with smtplib.SMTP_SSL(host) as s:
            s.login(username, password)
            s.sendmail(msg['From'], [to], data)


def read_password(password_file: Path) -> str:
    """Read password from password file."""
    assert password_file.stat().st_mode & (stat.S_IRGRP | stat.S_IROTH) == 0
    password = password_file.read_text().splitlines()[0]
    return password


def configure_email(config: Configuration) -> None:
    """Check configuration and ask for password if it's not already known."""
    ndct = config.notifications
    if 'email' not in ndct or 'host' not in ndct:
        raise ValueError(
            "Please add 'notifications': "
            "{'email': ..., 'host': ..., 'username': ...} "
            'to your ~/.myqueue/config.py '
            '(username can be left out if it is the same as email).')

    host = ndct['host']
    password_file = mqhome() / f'.myqueue/{host}'
    if password_file.is_file():
        password = read_password(password_file)
    else:
        password = getpass.getpass()
        padding = (len(password) % 80) * '.'
        password_file.write_text(f'{password}\n{padding}\n')
        password_file.chmod(0o600)
        if input('Would you like to send a test email? [yes] ') in {'', 'yes'}:
            send_mail('Test email from myqueue',
                      'Testing ...\n',
                      ndct['email'],
                      ndct['email'],
                      host,
                      ndct.get('username', ndct['email']),
                      password)
            print('Sent!')
