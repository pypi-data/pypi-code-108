import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date

class MyDateEntry(DateEntry):
    def __init__(self, master=None, **kw):
        DateEntry.__init__(self, master=None,**kw)
        # add black border around drop-down calendar
        self._top_cal.configure(bg='black', bd=1)
        # add label displaying today's date below
        tk.Label(self._top_cal, bg='gray90', anchor='w',
                 text='Сегодня: %s' % date.today().strftime('%x')).pack(fill='x')
