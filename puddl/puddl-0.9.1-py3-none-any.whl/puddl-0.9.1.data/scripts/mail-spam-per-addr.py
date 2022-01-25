#!python
import mailbox
import re
import sys


p = sys.argv[1]
d = mailbox.Maildir(p)

RE_VALID = re.compile(r'([a-z0-9._-]+)@felixhummel.de')

broken_headers = []

for message in d:
    to = message['to']
    if to is None:
        continue
    try:
        m = RE_VALID.search(to)
    except TypeError:
        broken_headers.append(message)
    if m is not None:
        print(m.group(1))
        pass

# one could handle broken_headers here ^^
