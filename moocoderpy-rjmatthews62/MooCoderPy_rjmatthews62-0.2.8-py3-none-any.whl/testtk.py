from tkinter import *

def doctrl(event:Event):
    print(event)
    return "break"

root=Tk()
text=Text(root)
text.pack(fill=BOTH, expand=True)
text.insert("1.0","Mary had a little lamb\nIt's fleece was white as snow.")
text.tag_configure("thing",background="red", foreground="white")
text.tag_add("thing","1.0","1.end")
text.bind("<Control-Key-h>",doctrl)
text.bind("<Control-Key-H>",doctrl)
root.mainloop()
