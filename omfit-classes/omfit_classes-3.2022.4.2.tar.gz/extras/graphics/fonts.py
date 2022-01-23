import sys
from tkinter import *
import tkinter.font as tkFont
from tkinter import ttk
import re
import copy

root = Tk()

top = Frame(root)
top.grid(row=0, column=0)
canvas = Canvas(top)
vbar = Scrollbar(top, orient=VERTICAL)
vbar.pack(side=RIGHT, fill=Y)
vbar.config(command=canvas.yview)
canvas.config(yscrollcommand=vbar.set)
canvas.pack(side=LEFT, expand=True, fill=BOTH)

frame = Frame()
sys_fonts = list(tkFont.families(root))
sys_fonts.sort()

_tmp = Label(text="bla")
f = tkFont.Font(font=_tmp['font'])
_tmp.destroy()
font0 = f.actual()
for k in list(font0.keys()):
    if k not in ['family', 'weight', 'slant']:
        del font0[k]
font0['family'] = re.sub(' ', '\ ', font0['family'])

fonts = []
font = copy.deepcopy(font0)

font1 = copy.deepcopy(font)
fonts.append(tkFont.Font(**font1))

font2 = copy.deepcopy(font)
font2['slant'] = 'italic'
fonts.append(tkFont.Font(**font2))

font3 = copy.deepcopy(font)
font3['weight'] = 'bold'
fonts.append(tkFont.Font(**font3))

Label(frame, text='default: ' + f['family'], font=fonts[0]).pack(side=TOP, fill=X)
Label(frame, text='default: ' + f['family'], font=fonts[1]).pack(side=TOP, fill=X)
Label(frame, text='default: ' + f['family'], font=fonts[2]).pack(side=TOP, fill=X)
ttk.Separator(frame).pack(side=TOP, fill=X)

for item in sys_fonts:
    try:
        font = copy.deepcopy(font0)
        font['family'] = re.sub(' ', '\ ', item)

        font1 = copy.deepcopy(font)
        fonts.append(tkFont.Font(**font1))

        font2 = copy.deepcopy(font)
        font2['slant'] = 'italic'
        fonts.append(tkFont.Font(**font2))

        font3 = copy.deepcopy(font)
        font3['weight'] = 'bold'
        fonts.append(tkFont.Font(**font3))

        Label(frame, text=item, font=fonts[-3]).pack(side=TOP, fill=X)
        Label(frame, text=item, font=fonts[-2]).pack(side=TOP, fill=X)
        Label(frame, text=item, font=fonts[-1]).pack(side=TOP, fill=X)

        ttk.Separator(frame).pack(side=TOP, fill=X)
        print('OK', item)
    except Exception as _excp:
        print('NO', item, _excp)

canvas.create_window(0, 0, anchor=NW, window=frame)
canvas.update_idletasks()
top.configure(width=top.winfo_reqwidth())
canvas.configure(width=frame.winfo_reqwidth(), height=500)
canvas.configure(scrollregion=(0, 0, top.winfo_width(), frame.winfo_reqheight()))

root.mainloop()
