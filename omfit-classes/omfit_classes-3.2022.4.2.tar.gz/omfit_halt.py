from omfit_classes import unix_os as os
import sys
import platform
import subprocess
import distutils.spawn
import re
import time

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont


def b2s(bytes):
    return bytes.decode("utf-8")


os.chdir(os.environ['HOME'])


def OMFITfont(ftype, size=0, family=''):
    """
    :param ftype: 'normal' or 'bold'

    :param size: positive or negative number relative to the tkinter default

    :param family: family font

    :return: tk font object to be used in tkinter calls
    """
    tmp = ttk.Label(text="bla")
    f = tkFont.Font(font=tmp['font'])
    tmp.destroy()
    f['size'] = -(abs(f['size']) + size)
    if ftype == 'normal':
        pass
    else:
        f['weight'] = ftype
    if family:
        f['family'] = family
    return f


def is_running(process):
    """
    This function returns True or False depending on whether a process is running or not

    This relies on grep of the `ps axw` command

    :param process: string with process name or process ID

    :return: False if process is not running, otherwise line of `ps` command
    """
    process = str(process)
    s = subprocess.Popen(
        [distutils.spawn.find_executable('ps'), "axw"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    std_out, std_err = list(map(b2s, s.communicate()))
    for item in std_out.split('\n'):
        if re.search(' ' + process + ' ', item) or re.search(r'^' + process + ' ', item):
            return item
    return False


def sayGoodbye(mainPid):
    try:
        os.kill(mainPid, 2)
    except Exception:
        pass
    sys.exit()


mainPid = None
try:
    mainPid = int(sys.argv[1])
except Exception:
    mainPid = quit()

try:
    session_color = re.sub('\\', '', sys.argv[2])
except Exception:
    session_color = None

root = tk.Tk()
root.withdraw()
root.wm_minsize(400, 10)
root.wm_resizable(0, 0)
root.wm_title('Halt OMFIT PID ' + str(mainPid) + ' on ' + platform.uname()[1].split('.')[0])
root.protocol("WM_DELETE_WINDOW", 'break')

allertText = tk.StringVar()
allertText.set('')
ttk.Label(root, textvariable=allertText, justify=tk.LEFT, font=OMFITfont('normal', 0, 'Courier')).pack(
    side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=2, pady=2
)
if session_color is not None:
    tk.Frame(root, background=session_color, height=2).pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx=2, pady=2)
ttk.Button(root, text='Interrupt OMFIT instance with PID ' + str(mainPid), command=lambda: sayGoodbye(mainPid)).pack(
    side=tk.TOP, expand=tk.YES, fill=tk.X, padx=2, pady=2
)


def stats(mainPid):
    if platform.system() == 'Darwin':
        topstr = distutils.spawn.find_executable('top') + ' -l 1 -ncols 4 -o cpu -o time -pid ' + str(mainPid)
    else:
        topstr = distutils.spawn.find_executable('top') + ' -b -n 1 -p ' + str(mainPid)
    s = subprocess.Popen(topstr, shell=True, stdout=subprocess.PIPE)
    allertText.set(s.stdout.read())
    if is_running(mainPid):
        root.after(1000, lambda: stats(mainPid))
    else:
        root.destroy()
        sys.exit()


stats(mainPid)

if platform.system() == 'Darwin':
    root.deiconify()
    root.lower()
else:
    root.iconify()

root.mainloop()
