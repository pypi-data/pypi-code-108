import tkinter as tk
import tkinter.filedialog

import pathlib


class OpenFileName(tk.Frame):
    """conbined widget for tk.filedialog.askopenfilename
    """
    def __init__(self, master=None, textvariable=None,
                 diagdefaultextension='',
                 diagfiletypes=[('All', '*')],
                 diagtitle='',
                 *args, **kw):
        """
        textvariable is pathname stored in this widget.
        diagdefaultextension is defaultextension option for fileopendialog
        diagfiletypes is filetypes option for fileopendialog
        diagtitle is title option for fileopendialog
        """
        tk.Frame.__init__(self, master)
        self.textvariable = textvariable
        self.diagdefaultextension = diagdefaultextension
        self.diagfiletypes = diagfiletypes
        self.diagtitle = diagtitle

        if self.textvariable is None:
            self.textvariable = tk.StringVar()

        self.filepath = tk.Entry(self, textvariable=self.textvariable)
        self.btn = tk.Button(self, text='browse', command=self.selectfilepath)

        self.filepath.pack(side=tk.LEFT, expand=1, fill=tk.X)
        self.btn.pack(side=tk.LEFT)

    def selectfilepath(self):
        # get current filename
        currentpath = pathlib.Path(self.textvariable.get())
        # split path
        if currentpath.is_dir():
            dirname = str(currentpath)
            filename = ''
        else:
            filename = currentpath.name
            dirname = str(currentpath.parent)

        fname = tkinter.filedialog.askopenfilename(
            defaultextension=self.diagdefaultextension,
            filetypes=self.diagfiletypes,
            initialdir=dirname,
            initialfile=filename,
            title=self.diagtitle)

        if fname:
            self.textvariable.set(fname)

    def set(self, v):
        self.textvariable.set(v)

    def get(self):
        return self.textvariable.get()

    def clear(self):
        self.textvariable.set('')

    def validate(self):
        return None
