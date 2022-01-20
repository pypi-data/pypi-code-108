from tkinter import Label, SUNKEN, W, BOTTOM
import tkinter as tk  # 待发布


class StatusBar(Label):
    """状态栏"""
    oldcfg = Label.config

    def __init__(self, root, status='On the way...', border=1, relief=SUNKEN, a=W):
        """初始化状态栏"""
        Label.__init__(self, root, text=status, bd=border, relief=relief, anchor=a)  # 初始化

    def config(self, status='On the way...', border=1, relief=SUNKEN, a=W, **kwargs):
        '''重新配置'''
        self.oldcfg(text=status, bd=border, relief=relief, anchor=a, **kwargs)

    def display(self, side=BOTTOM, fill=tk.X):
        '''显示状态栏'''
        self.pack(side=side, fill=fill)

    pass


if __name__ == "__main__":
    t = tk.Tk()
    s = StatusBar(t)
    s.display()
    t.mainloop()
