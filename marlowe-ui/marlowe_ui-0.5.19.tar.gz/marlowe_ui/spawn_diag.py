import tkinter as tk
import tkinter.simpledialog

class SpawnDialog(tkinter.simpledialog.Dialog):
    def __init__(self, parent, title=None,
            cmdline=None, input=None, workdir=None, shell=True):
        self.cmdline_raw = cmdline
        self.input = input
        self.workdir = workdir
        self.shell_raw = shell
        # Dialog.__init__ calls self.body in it 
        tkinter.simpledialog.Dialog.__init__(self, parent, title)

    def body(self, master):
        # comment 
        text_inst = """\
Start Marlowe Program?
Put proper command line and push "OK", or "Cancel" """
        self.label_inst = tk.Label(master, text=text_inst, justify=tk.LEFT)
        self.label_inst.grid(row=0, column=0, sticky=tk.W)

        # shell mode?
        self.shell = tk.IntVar(master, self.shell_raw)
        self.shellbutton = tk.Checkbutton(master, text='Execute in new shell. If you need redirection, pipe or running multiple commands, enable this option.', variable=self.shell)
        self.shellbutton.grid(row=1, column=0, sticky=tk.W)

        # command
        self.cmdline = tk.StringVar(master, self.cmdline_raw)
        self.cmdline_e = tk.Entry(master, textvariable=self.cmdline)
        self.cmdline_e.grid(row=2, column=0, sticky=tk.EW)

        # note on format
        text_notice = """NOTES:
  {{input}} is replaced by {0}
  working directory is {1}""".format(self.input, self.workdir)
        self.label_notice = tk.Label(master, text=text_notice, justify=tk.LEFT)
        self.label_notice.grid(row=3, column=0, sticky=tk.W)

        master.grid_rowconfigure(0,weight=1)

        return self.cmdline_e

    def apply(self):
        self.result = {'command':self.cmdline.get(),
                'shellexec':self.shell.get()}

