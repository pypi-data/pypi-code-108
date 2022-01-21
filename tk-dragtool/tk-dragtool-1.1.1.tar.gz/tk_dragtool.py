"""提供用鼠标拖动、缩放tkinter控件工具的模块。
A module which supplies tools to drag and resize
tkinter window and widgets with the mouse."""
import tkinter as tk
import tkinter.ttk as ttk
from ctypes import *

__author__="qfcy"
__version__="1.1.1"

class _PointAPI(Structure):
    _fields_ = [("x", c_ulong), ("y", c_ulong)]

def getpos():
    # 调用API函数获取当前鼠标位置。返回值以(x,y)形式表示。
    po = _PointAPI()
    windll.user32.GetCursorPos(byref(po))
    return int(po.x), int(po.y)
def xpos():return getpos()[0]
def ypos():return getpos()[1]

# tkinter控件支持作为字典键。
# bound的键是dragger, 值是包含1个或多个绑定事件的列表
# 列表的一项是对应tkwidget和其他信息的元组
bound = {}
def __add(wid,data):
    bound[wid]=bound.get(wid,[])+[data]
def __remove(wid,key):
    for i in range(len(bound[wid])):
        if bound[wid][i][0]==key:
            del bound[wid][i]
def __get(wid,key=''):
    if not key:return bound[wid][0]
    if key=='resize':
        for i in range(len(bound[wid])):
            for s in 'nwse':
                if s in bound[wid][i][0].lower():
                    return bound[wid][i]
    for i in range(len(bound[wid])):
        if bound[wid][i][0]==key:
            return bound[wid][i]
def move(widget,x=None,y=None,width=None,height=None):
    "移动控件或窗口widget, 参数皆可选。"
    x=x if x!=None else widget.winfo_x()
    y=y if y!=None else widget.winfo_y()
    width=width if width!=None else widget.winfo_width()
    height=height if height!=None else widget.winfo_height()
    if isinstance(widget,tk.Wm):
        widget.geometry("%dx%d+%d+%d"%(width,height,x,y))
    else:
        widget.place(x=x,y=y,width=width,height=height)
    return x,y,width,height

def _mousedown(event):
    if event.widget not in bound:return
    lst=bound[event.widget]
    for data in lst: # 开始拖动时, 在每一个控件记录位置和控件尺寸
        widget=data[1]
        widget.mousex,widget.mousey = getpos()
        widget.startx,widget.starty = widget.winfo_x(),widget.winfo_y()
        widget.start_w=widget.winfo_width()
        widget.start_h=widget.winfo_height()
def _drag(event):
    if event.widget not in bound:return
    lst=bound[event.widget]
    for data in lst: # 多个绑定
        if data[0]!='drag':return
        widget=data[1]
        dx = xpos()-widget.mousex # 计算鼠标当前位置和开始拖动时位置的差距
        dy = ypos()-widget.mousey # 鼠标位置不能用event.x和event.y
        move(widget,widget.startx + dx,widget.starty + dy)
def _resize(event):
    data=__get(event.widget,'resize')
    if data is None:return
    widget=data[1]
    dx = xpos()-widget.mousex # 计算位置差
    dy = ypos()-widget.mousey

    type = data[0].lower()
    minw,minh = data[2:4]
    if 's' in type:
        move(widget,height=max(widget.start_h+dy,minh))
    elif 'n' in type:
        move(widget,y=min(widget.starty+dy,widget.starty+widget.start_h-minh),
                    height=max(widget.start_h-dy,minh))

    __remove(event.widget,data[0])# 取消绑定
    widget.update()
    __add(event.widget,data) # 重新绑定
    
    if 'e' in type:
        move(widget,width=max(widget.start_w+dx,minw))
    elif 'w' in type:
        move(widget,x=min(widget.startx+dx,widget.startx+widget.start_w-minw),
                    width=max(widget.start_w-dx,minw))

def draggable(tkwidget):
    """调用draggable(tkwidget) 使tkwidget可拖动。
tkwidget: 一个控件(Widget)或一个窗口(Wm)。"""
    tkwidget.bind("<Button-1>",_mousedown,add='+')# add='+',不覆盖之前绑定的事件
    tkwidget.bind("<B1-Motion>",_drag,add='+')
    __add(tkwidget,('drag',tkwidget))

def bind_drag(tkwidget,dragger):
    """绑定拖曳事件。
tkwidget: 被拖动的控件或窗口,
dragger: 接收鼠标事件的控件,
调用bind_drag后,当鼠标在dragger上拖动时, tkwidget会被拖动, 但dragger
作为接收鼠标事件的控件, 位置不会改变。"""
    dragger.bind("<Button-1>",_mousedown,add='+')
    dragger.bind("<B1-Motion>",_drag,add='+')
    __add(dragger,('drag',tkwidget))

def bind_resize(tkwidget,dragger,anchor,min_w=0,min_h=0,move_dragger=True):
    """绑定缩放事件。
anchor: 缩放"手柄"的方位, 取值为N,S,W,E,NW,NE,SW,SE,分别表示东、西、南、北。
min_w,min_h: 该方向tkwidget缩放的最小宽度(或高度)。
move_dragger: 缩放时是否移动dragger。
其他说明同bind_drag函数。"""
    dragger.bind("<Button-1>",_mousedown,add='+')
    dragger.bind("<B1-Motion>",_resize,add='+')
    data=(anchor,tkwidget,min_w,min_h,move_dragger)
    __add(dragger,data)

def test():
    root=tk.Tk()
    root.title("Test")
    button=ttk.Button(root,text="拖动窗口")
    button.place(x=0,y=0)
    button2=ttk.Button(root,text="缩放窗口")
    button2.place(y=30)
    bind_drag(root,button)
    bind_drag(button,button2)
    draggable(button2)
    bind_resize(root,button2,'se',min_w=200,min_h=150)
    root.mainloop()

if __name__=="__main__":test()
