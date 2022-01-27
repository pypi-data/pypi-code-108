from pathlib import Path
import pickle
import tkinter as tk
import tkinter.filedialog


def open_dialog(**opt):
    """Parameters
    ----------
    Options will be passed to `tkinter.filedialog.askopenfilename`.
    See also tkinter's document.
    Followings are example of frequently used options.
    - filetypes=[(label, ext), ...]
        - label: str
        - ext: str, semicolon separated extentions
    - initialdir: str, default Path.cwd()
    - multiple: bool, default False

    Returns
    --------
    filename, str
    """
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)

    opt_default = dict(initialdir=Path.cwd())
    _opt = dict(opt_default, **opt)

    return tk.filedialog.askopenfilename(**_opt)


def saveas_dialog(**opt):
    """Parameters
    ----------
    Options will be passed to `tkinter.filedialog.asksaveasfilename`.
    See also tkinter's document.
    Followings are example of frequently used options.
    - filetypes=[(label, ext), ...]
        - label: str
        - ext: str, semicolon separated extentions
    - initialdir: str, default Path.cwd()
    - initialfile: str, default isn't set

    Returns
    --------
    filename, str
    """
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)

    opt_default = dict(initialdir=Path.cwd())
    _opt = dict(opt_default, **opt)

    return tk.filedialog.asksaveasfilename(**_opt)


def load_pickle_with_dialog(mode='rb', **opt):
    """Load a pickled object with a filename assigned by tkinter's open dialog.

    kwargs will be passed to saveas_dialog.
    """
    opt_default = dict(filetypes=[('pickled data', '*.pkl'), ('all', '*')])
    _opt = dict(opt_default, **opt)
    fn = open_dialog(**_opt)
    if fn == '':  # canceled
        return None

    with Path(fn).open(mode) as f:
        data = pickle.load(f)
    return data


def dump_pickle_with_dialog(obj, mode='wb', **opt):
    """Pickle an object with a filename assigned by tkinter's saveas dialog.

    kwargs will be passed to saveas_dialog.

    Returns
    --------
    filename: str
    """
    opt_default = dict(filetypes=[('pickled data', '*.pkl'), ('all', '*')])
    _opt = dict(opt_default, **opt)
    fn = saveas_dialog(**_opt)
    if fn == '':  # canceled
        return ''
    # note: 上書き確認はtkinterがやってくれるのでここではチェックしない

    with Path(fn).open(mode) as f:
        pickle.dump(obj, f)

    return fn
