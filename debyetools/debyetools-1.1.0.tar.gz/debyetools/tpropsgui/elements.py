import PySimpleGUI as sg

def C(lo,key):
    return sg.Column(layout=lo,key='||Col_'+key, vertical_alignment='top')

def T(txt, key, pad=None, visible=True,right_click_menu=None):
    return sg.Text(txt, key='||T_'+key, pad=pad, font=("Helvetica", 10), visible=visible,right_click_menu=right_click_menu)

def dI(txt, key, w, disabled=True,enable_events=True,visible=True):
    return sg.InputText(disabled=disabled,default_text=txt, key = '--I_'+key,size=(w,1),disabled_readonly_background_color = 'gray',font=("Helvetica", 10),enable_events=enable_events,visible=visible)#, enable_events=True)

def I(txt, key,w, enable_events=True):
    return  dI(txt, key, w, disabled=False, enable_events=enable_events)

def Br(key):
    return sg.FolderBrowse(key='||Br_'+key,enable_events=True,font=("Helvetica", 10),pad=(1,1))

def F(txt,lo,key, tooltip=None,right_click_menu=None):
    return sg.Frame(txt,layout=lo, key='||F_'+key,font=("Helvetica", 10), tooltip=tooltip, right_click_menu=right_click_menu)

def dChk(txt,key,default_value,disabled=False):
    return sg.Checkbox(txt, key='--Chk_'+key, enable_events=True,default=default_value,font=("Helvetica", 10),disabled=disabled)

def Chk(txt,key,disabled=False):
    return dChk(txt,key,False,disabled=disabled)

def collapse(layout, key):
    return sg.pin(sg.Column(layout, key='||Col_'+key,visible=False, vertical_alignment='top'))

def Bc(txt,key,colors,right_click_menu=None):
    return sg.Button(txt,key='||B_'+key,disabled=True,font=("Helvetica", 10),right_click_menu=right_click_menu,pad=(1,1))

def Be(txt,key,colors,right_click_menu=None):
    return sg.Button(txt,key='||B_'+key,disabled=False,font=("Helvetica", 10),right_click_menu=right_click_menu,pad=(1,1))

def VS():
    return sg.VSeperator()

def sCol(lo, key, w, h):
    return sg.Column(lo,size=(w,h), scrollable=True,key='--Col_'+key, vertical_alignment='top')

def M(txt, key, w, h):
    return sg.Multiline(default_text=txt,size=(w,h),key='--M_'+key,font=('Courier',8),enable_events=True)

def TG(lo, key):
    return sg.TabGroup(lo,key='--TG_'+key,font=("Helvetica", 10))

def Tab(txt, lo, key, visible,right_click_menu=None):
    return sg.Tab(txt, layout=lo, key='--Tab_'+key, visible=visible,font=("Helvetica", 10),right_click_menu=right_click_menu)

def ICombo(lst, key, w, h):
    return sg.Combo(lst, key='--IC_'+key, enable_events=True,font=("Helvetica", 10))#, size=(w,h), key='--IC_'+key, enable_events=True,font=("Helvetica", 10))

def theme_background_color():
    return sg.theme_background_color()

def Ipad(txt, key, w, visible=True, enable_events=True, pad=None,disabled=True):
    return sg.Input(disabled=disabled,default_text=txt, key = '--I_'+key,size=(w,1), pad=pad,font=("Helvetica", 10),
                    disabled_readonly_background_color = 'gray',enable_events=enable_events,visible=visible)

def listbox(values,key):
    return sg.Listbox(values=values,select_mode='extended',size=(20,8),enable_events=True,key='--LBx_'+key)
