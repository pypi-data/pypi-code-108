import tkinter as tk
import tkinter.messagebox as op
o = tk.Tk()
o.withdraw()
def info(t,m):
    op.showinfo(str(t),str(m))
def warning(t,m):
    op.showwarning(str(t),str(m))
def error(t,m):
    op.showerror(str(t),str(m))
def ask(t,m):
    op.askquestion(str(t),str(m))
def ok(t,m):
    op.askokcancel(str(t),str(m))
def yes(t,m):
    op.askyesno(str(t),str(m))
def retry(t,m):
    op.askretrycancel(str(t),str(m))
def ync(t,m):
    op.askyesnocancel(str(t),str(m))