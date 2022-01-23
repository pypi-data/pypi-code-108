#!/usr/bin/env python2.7
from moke import * #@UnusedWildImport

@task
def sayhello(name = "stranger"):
    log("executing hello task")
    stdout.write("hello %s\n" % name)

if __name__ == "__main__":
    task()