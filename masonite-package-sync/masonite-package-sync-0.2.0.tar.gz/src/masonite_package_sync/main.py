#!/usr/bin/env python
from cleo import Application

from .commands import PullCommand

application = Application()
application.add(PullCommand())

if __name__ == "__main__":
    application.run()
