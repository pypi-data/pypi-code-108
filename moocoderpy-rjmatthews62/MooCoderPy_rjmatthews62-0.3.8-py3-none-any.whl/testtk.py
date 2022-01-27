from tkinter import *
from tkinter import ttk
from tkinter import filedialog

def doctrl(event:Event):
    print(event)
    print(text.index("end -100 lines"))
    return "break"

def toggle():
    global showlist
    if showlist:
        pane.forget(listbox)
    else:
        pane.add(listbox)
    showlist=not(showlist)


root=Tk()
pane=ttk.PanedWindow(root,orient=HORIZONTAL)
text=Text(pane,foreground="white",background="black")
pane.add(text)
listbox=Listbox(pane)
for v in ("This","Tsting a longer line","And a really other and much longer line"):
    listbox.insert(END,v)
pane.add(listbox)
pane.pack(fill=BOTH,expand=True)
# text.pack(fill=BOTH, expand=True)
text.insert("1.0","Mary had a little lamb\nIt's fleece was white as snow.")
text.tag_configure("thing",background="steel blue", foreground="white")
print(text["selectbackground"])
text.tag_add("thing","1.0","1.end")
text.bind("<Control-Key-h>",doctrl)
text.bind("<Control-Key-H>",doctrl)
menubar=Menu(root)
editmenu=Menu(menubar)
editmenu.add_command(label="Toggle",command=toggle)
menubar.add_cascade(label="Edit",menu=editmenu)
root.config(menu=menubar)
showlist=True
root.mainloop()
