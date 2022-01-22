from tkinter import filedialog

def openFileAll():
    return filedialog.askopenfilename()

def selectPath():
    return filedialog.askdirectory()
    