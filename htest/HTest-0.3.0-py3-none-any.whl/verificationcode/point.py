#!/usr/bin/env python3.7
# encoding: utf-8
# 获取验证码坐标

import pyHook
import pythoncom


def onMouseEvent(event):
    print("Position:" + event.Position)
    return True


def main():
    hm = pyHook.HookManager()
    hm.HookKeyboard()
    hm.MouseAllButtonsDown = onMouseEvent
    hm.MouseAllButtonsUp = onMouseEvent
    hm.HookMouse()
    pythoncom.PumpMessages()


if __name__ == "__main__":
    main()
