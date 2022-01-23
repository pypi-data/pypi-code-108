#!/usr/bin/env python3
# coding: utf-8

import subprocess


"""
command: pmset -g batt https://stackoverflow.com/a/42361337

Now drawing from 'AC Power'
 -InternalBattery-0 (id=3735651)	97%; charged; 0:00 remaining present: true
 
Now drawing from 'Battery Power'
 -InternalBattery-0 (id=3735651)	97%; discharging; (no estimate) present: true
"""


class MacPowerStatusQuery(object):
    cmd_args = ['pmset', '-g', 'batt']

    def __init__(self):
        p = subprocess.run(self.cmd_args, capture_output=True, text=True)
        self.resp = p.stdout

    def is_using_ac(self):
        return b'AC Power' in self.resp

    def is_using_battery(self):
        return b'Battery Power' in self.resp
