"""GUI for the login page"""

from tkinter import Tk, Entry

from Magic import theme
from Magic.tkinterlib import TButton, tkinter_initialise, TLabel
from Magic.usergui import user_page


def SecurityUI() -> tuple:
    """This function deals with the login page"""
    text_color = theme.read_theme()[1]
    win = Tk()
    tkinter_initialise(win, opacity=0.8)
    win.geometry("200x100+700+300")
    e, e1 = Entry(win, show="*", fg=text_color, width=10), Entry(win, width=10, fg=text_color)
    e.place(x=104, y=30)
    e1.place(x=104, y=10)
    TLabel(win, text="Username:").place(x=20, y=10)
    TLabel(win, text="Password:").place(x=20, y=30)

    def password(event="") -> None:
        """Used to get the username and password entered"""
        password.passgui,password.usergui = e.get(),e1.get()
        win.destroy()

    TButton(win, text="Add User", command=user_page).place(x=120, y=60)
    TButton(win, text="x", command=exit).place(x=30, y=60)
    TButton(win, text="Verify", command=password).place(x=70, y=60)
    win.bind("<Return>", password)
    win.mainloop()
    return password.usergui, password.passgui
