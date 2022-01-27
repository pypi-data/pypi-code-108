import sys
from tkinter import *
from tkinter import ttk
from bundlesnake.Commands import Commands

root = Tk()
root['bg'] ="#222222"
root.title('Get Package')
root.geometry('400x500')

Label(text="Package Name :",bg ="#222222",fg ="#fff").place(relx = 0.1, rely = 0.2, relwidth = 0.8 , relheight = 0.1)
packname = ttk.Entry(font = 12)
packname.place(relx = 0.1, rely = 0.3 , relwidth = 0.8 , relheight = 0.1)
submit = Button(text='Create',bg ="#222222",fg ="#fff" ,command =lambda :commands.create(packname.get(), path = 0 )).place(relx = 0.1, rely = 0.5 , relwidth = 0.8 , relheight = 0.1)



if __name__ == "__main__":
    commands = Commands()
    if len(sys.argv) > 1 : commands.create(sys.argv[1],path = 1)
    else:
        root.mainloop()


