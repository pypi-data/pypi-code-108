import tkinter as tk


class OptionFrame(tk.LabelFrame):
    def __init__(self, parent=None, title=''):
        tk.LabelFrame.__init__(self, parent)

        # checkbutton
        self.checkvar = tk.IntVar(self, True)
        self.checkbutton = tk.Checkbutton(
            self,
            variable=self.checkvar,
            text=title,
            command=self.oncheck)

        self.layoutlabel()

        self.config(labelwidget=self.checkbutton)
        self.bodywidget = self.body()

    def layoutlabel(self):
        # override position and layout labelframe
        # position of labelwidget
        pass

    def body(self):
        # override body
        # layout method such as .pack and .grid should be issued in this method
        pass

    def set_checkbutton(self, val):
        self.checkvar.set(val)
        if self.bodywidget:
            if val:
                self.bodywidget.enable()
            else:
                self.bodywidget.disable()

    def oncheck(self):
        self.set_checkbutton(self.checkvar.get())

    def get(self):
        if self.checkvar.get():
            if self.bodywidget:
                return self.bodywidget.get()
        return None

    def set(self, d):
        if d is None:
            # nothing to do, disable checkbox
            self.set_checkbutton(False)
        else:
            self.set_checkbutton(True)
            self.bodywidget.set(d)
