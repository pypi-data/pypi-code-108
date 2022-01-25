from tkinter import *

def doctrl(event:Event):
    print(event)
    print(text.index("end -100 lines"))
    return "break"

root=Tk()
text=Text(root,foreground="white",background="black")
text.pack(fill=BOTH, expand=True)
text.insert("1.0","Mary had a little lamb\nIt's fleece was white as snow.")
text.tag_configure("thing",background="steel blue", foreground="white")
print(text["selectbackground"])
text.tag_add("thing","1.0","1.end")
text.bind("<Control-Key-h>",doctrl)
text.bind("<Control-Key-H>",doctrl)
root.mainloop()
