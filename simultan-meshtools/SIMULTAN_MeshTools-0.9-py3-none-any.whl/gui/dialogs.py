from tkinter import Tk
import tkinter as tk
from tkinter import ttk


Tk().withdraw()


def askComboValue(values, question):

    top = tk.Toplevel()     # use Toplevel() instead of Tk()
    tk.Label(top, text=question).pack()
    box_value = tk.StringVar()
    combo = ttk.Combobox(top, textvariable=box_value, values=values)
    combo.pack()
    combo.bind('<<ComboboxSelected>>', lambda _: top.destroy())
    top.grab_set()
    top.wait_window(top)  # wait for itself destroyed, so like a modal dialog
    return box_value.get()


if __name__ == '__main__':

    print(askComboValue(values=['bla', 'bli', 'blo'],
                        question='please select'))
    print('done')
