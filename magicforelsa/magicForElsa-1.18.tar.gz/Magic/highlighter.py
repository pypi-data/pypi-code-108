"""This module is for syntax highlighting"""
from tkinter import END
import json,os
from Magic import theme

keywords = json.load(open(os.path.abspath(__file__)[:-2]+'json'))


def syntax_highlighting(event="", Search_box=None) -> None:
    """Function for syntax highlighting"""
    try:
        ord = Search_box.get()
        text_color = theme.read_theme()[1]
        if ord.split()[0].lower() in keywords:
            Search_box.delete(0, END)
            Search_box.config(fg="light green")
        else:
            Search_box.delete(0, END)
            Search_box.config(fg=text_color)
        Search_box.insert(0, ord)
    except: pass
