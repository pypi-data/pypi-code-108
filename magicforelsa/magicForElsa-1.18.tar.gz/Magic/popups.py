import time
from tkinter import Tk

from task1.task import web

from Magic import tkinterlib, chat_client
from Magic.tkinterlib import TButton, TLabel


def popups(srch: str)->None:
    """A yes or no gui box to know if the user needs to search things in the internet"""
    popupWindow = Tk()
    screen_height = popupWindow.winfo_screenheight()
    screen_width = popupWindow.winfo_screenwidth()
    tkinterlib.tkinter_initialise(popupWindow, x=screen_width - 130, y=screen_height - 130)

    def srchYes(event="")->None:
        popupWindow.destroy()
        web(srch)

    TButton(popupWindow, text="Yes", command=srchYes).grid(row=1, column=0)
    TButton(popupWindow, text="No", command=popupWindow.destroy).grid(row=1, column=1)
    popupWindow.mainloop()


def resetelsapopup()->None:
    """Gui and backend for resetting Elsa"""
    import os
    import shutil
    from talk1.talk1 import talk
    from pathlib import Path
    popupWindow = Tk()
    screen_height, screen_width = popupWindow.winfo_screenheight(), popupWindow.winfo_screenwidth()
    tkinterlib.tkinter_initialise(popupWindow, x=int(screen_width / 2), y=int(screen_height / 2))
    popupWindow.geometry(f"193x50+{int(screen_width / 2)}+{int(screen_height / 2)}")
    talk("Are you sure that you want to reset Elsa")
    TLabel(popupWindow, text="Are you sure you want to reset Elsa?").place(x=0, y=0)

    def Yes(event="")->None:
        talk("Please wait for a moment. Elsa is being reset")
        talk("Just run elsa after it shutdowns")
        print("Resetting Elsa")
        time.sleep(1)
        shutil.rmtree(Path(os.getcwd() + "/resources"))
        try: chat_client.closeClient()  # Closing chat client as it is not daemonic thread
        except: pass
        exit()
    TButton(popupWindow, text="Yes", command=Yes).place(x=60, y=20)
    TButton(popupWindow, text="No", command=popupWindow.destroy).place(x=100, y=20)
    popupWindow.mainloop()
