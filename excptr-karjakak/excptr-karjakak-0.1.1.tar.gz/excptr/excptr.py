# -*- coding: utf-8 -*-
# Copyright (c) 2022, KarjaKAK
# All rights reserved.

from functools import wraps
from textwrap import fill
from contextlib import redirect_stdout
import io, inspect


def prex(details, exc_tr, fc_name):
    print(f"Filename caller: {details[0].filename.upper()}\n")
    print(f"ERROR - <{fc_name}>:")
    print(f"{'-' * 70}", end="\n")
    print("Start at:\n")

    for detail in details:
        cc = fill(
            "".join(detail.code_context).strip(),
            initial_indent=" " * 4,
            subsequent_indent=" " * 4,
        )
        print(f"line {detail.lineno} in {detail.function}:\n" f"{cc}\n")
        del detail, cc

    tot = f"<- Exception raise: {exc_tr.__class__.__name__} ->"
    print("~" * len(tot))
    print(tot)
    print("~" * len(tot) + "\n")

    allextr = inspect.getinnerframes(exc_tr.__traceback__)[1:]
    for extr in allextr:
        cc = fill(
            "".join(extr.code_context).strip(),
            initial_indent=" " * 4,
            subsequent_indent=" " * 4,
        )
        print(f"line {extr.lineno} in {extr.function}:\n" f"{cc}\n")
        del extr, cc
    print(f"{exc_tr.__class__.__name__}: {exc_tr.args[0]}")
    print(f"{'-' * 70}", end="\n")
    del tot, allextr, details, exc_tr, fc_name


def crtk(v: str):
    import tkinter as tk

    root = tk.Tk()
    root.title("Exception Error Messages")
    text = tk.Listbox(root, relief=tk.FLAT, width=70, selectbackground="light green")
    text.pack(side="left", expand=1, fill=tk.BOTH, pady=2, padx=(2, 0))
    scr = tk.Scrollbar(root, orient=tk.VERTICAL)
    scr.pack(side="right", fill=tk.BOTH)
    scr.config(command=text.yview)
    text.config(yscrollcommand=scr.set)
    val = v.splitlines()
    for v in val:
        text.insert(tk.END, v)
    text.config(
        state=tk.DISABLED,
        bg="grey97",
        disabledforeground="black",
        font="courier 12",
        height=len(val),
    )
    del val, v
    root.mainloop()
    del root, text, scr


def excp(m: int = -1):
    match m:
        case m if not isinstance(m, int):
            raise ValueError(f'm = "{m}" Need to be int instead!')
        case m if m not in [-1, 0, 1]:
            raise ValueError(
                f'm = "{m}" Need to be either one of them, [-1 or 0 or 1]!'
            )

    def ckerr(f):
        ckb = m

        @wraps(f)
        def trac(*args, **kwargs):
            try:
                if fn := f(*args, **kwargs):
                    return fn
                del fn
            except Exception as e:
                details = inspect.stack()[1:][::-1]
                match ckb:
                    case -1:
                        raise
                    case 0:
                        prex(details, e, f.__name__)
                    case 1:
                        v = io.StringIO()
                        with redirect_stdout(v):
                            prex(details, e, f.__name__)
                        crtk(v.getvalue())
                        v.flush()
                del details

        return trac

    return ckerr
