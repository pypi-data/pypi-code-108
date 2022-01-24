# -*- coding: utf-8 -*-
# Copyright (c) 2022, KarjaKAK
# All rights reserved.

from tkinter import Tk, ttk, simpledialog, messagebox
from Clien.clien import cmsk
from contextlib import redirect_stdout
from DecAn.decan import deconstruct, construct
from datetime import datetime
from .dbase import Ziper
from ast import literal_eval
from envarclear import Cleaner
from pathlib import Path
from filepmon.pgf import FilePermission as fpm
from filfla.ffl import FilFla as ff
from filatt.filatt import WinAtt, AttSet
from functools import wraps
from typing import Any
import tkinter as tk
import sys, os, io
import subprocess
import ctypes
import ctypes.wintypes as w
import traceback

# Ref from: https://stackoverflow.com/questions/
# 46132401/read-text-from-clipboard-in-windows-using-ctypes
# 53226110/how-to-clear-clipboard-in-using-python/53226144


class Clipper:
    def __init__(self, root):
        self.root = root
        self.root.title("Clipper")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)

        self.aft = None
        self.upt = tuple()
        self.sel = []
        self.lock = None

        self.fr1 = tk.Frame(self.root, pady=2, padx=2)
        self.fr1.pack(side="left", fill="both", expand=1)

        self.ls = tk.Listbox(self.fr1, selectmode="multiple")
        self.ls.pack(side="left", pady=2, padx=2, expand=1, fill="both")
        self.ls.bind("<ButtonRelease>", self.updatesel)
        self.ls.bind("<Control-d>", self.clear)

        self.scr = tk.Scrollbar(self.fr1, orient="vertical")
        self.scr.pack(side="right", fill="y")
        self.scr.config(command=self.ls.yview)
        self.ls.config(yscrollcommand=self.scr.set)

        self.fr2 = tk.Frame(self.root)
        self.fr2.pack(side="right", fill="both", expand=1)

        self.bto = ttk.Button(self.fr2, text="Start clipping!", command=self.clipon)
        self.bto.pack(pady=1, padx=2, expand=1, fill="both")

        self.bts = ttk.Button(self.fr2, text="Stop clipping!", command=self.stc)
        self.bts.pack(pady=1, padx=2, expand=1, fill="both")

        self.btp = ttk.Button(self.fr2, text="Structure", command=self.struc)
        self.btp.pack(pady=1, padx=2, expand=1, fill="both")

        self.btr = ttk.Button(self.fr2, text="Read Construct", command=self.readec)
        self.btr.pack(pady=1, padx=2, expand=1, fill="both")

        self.btsr = ttk.Button(self.fr2, text="Set Construct", command=self.setdec)
        self.btsr.pack(pady=1, padx=2, expand=1, fill="both")

        self.btd = ttk.Button(self.fr2, text="Delete Archive", command=self.deldec)
        self.btd.pack(pady=1, padx=2, expand=1, fill="both")

        self.btc = ttk.Button(self.fr2, text="Clean Variable", command=self.clenvar)
        self.btc.pack(pady=1, padx=2, expand=1, fill="both")

        self.clipon()

    def clear(self, event=None):
        if self.ls.curselection():
            m = 0
            sem = None
            for d in iter(self.ls.curselection()):
                sem = d - m
                self.ls.delete(sem, sem)
                m += 1
            del m, sem

    def updatesel(self, event=None):
        if self.upt:
            if set(self.ls.curselection()) - set(self.upt):
                x = list(set(self.ls.curselection()) - set(self.upt)).pop()
                self.sel.append(x)
                self.upt = self.ls.curselection()
            elif set(self.upt) - set(self.ls.curselection()):
                x = list(set(self.upt) - set(self.ls.curselection())).pop()
                del self.sel[self.sel.index(x)]
                self.upt = self.ls.curselection()
        else:
            self.upt = self.ls.curselection()
            if self.upt:
                self.sel.append(self.upt[0])

    def topm(self):
        match self.root.wm_attributes("-topmost"):
            case 1:
                self.root.attributes("-topmost", 0)
            case _:
                self.root.attributes("-topmost", 1)

    def copasw(self) -> str:

        CF_UNICODETEXT = 13

        u32 = ctypes.WinDLL("user32")
        k32 = ctypes.WinDLL("kernel32")

        OpenClipboard = u32.OpenClipboard
        OpenClipboard.argtypes = (w.HWND,)
        OpenClipboard.restype = w.BOOL
        GetClipboardData = u32.GetClipboardData
        GetClipboardData.argtypes = (w.UINT,)
        GetClipboardData.restype = w.HANDLE
        GlobalLock = k32.GlobalLock
        GlobalLock.argtypes = (w.HGLOBAL,)
        GlobalLock.restype = w.LPVOID
        GlobalUnlock = k32.GlobalUnlock
        GlobalUnlock.argtypes = (w.HGLOBAL,)
        GlobalUnlock.restype = w.BOOL
        EmptyClipboard = u32.EmptyClipboard
        CloseClipboard = u32.CloseClipboard
        CloseClipboard.argtypes = None
        CloseClipboard.restype = w.BOOL

        text = ""
        if OpenClipboard(None):
            if h_clip_mem := GetClipboardData(CF_UNICODETEXT):
                text = ctypes.wstring_at(GlobalLock(h_clip_mem))
                GlobalUnlock(h_clip_mem)
                EmptyClipboard()
            CloseClipboard()
            del h_clip_mem
        del (
            OpenClipboard,
            GetClipboardData,
            GlobalLock,
            GlobalUnlock,
            EmptyClipboard,
            CloseClipboard,
            u32,
            k32,
            CF_UNICODETEXT,
        )
        return text

    def pbcopas(self) -> str:
        if sys.platform.startswith("win"):
            gt = self.copasw()
            return gt
        else:
            with subprocess.Popen(
                "pbpaste",
                stdout=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                text=True,
            ) as p:
                if gt := p.stdout.read():
                    os.system("pbcopy < /dev/null")
            return gt

    def clipon(self):
        clip = self.pbcopas()
        match clip:
            case "":
                self.aft = self.root.after(500, self.clipon)
            case _:
                self.ls.insert(self.ls.winfo_cells() + 1, clip)
                self.aft = self.root.after(500, self.clipon)

    def stc(self):
        if self.aft:
            self.root.after_cancel(self.aft)
            self.aft = None

    def fold(self) -> str:
        fl = (
            os.path.join(os.environ["USERPROFILE"], "ClipperSaver")
            if sys.platform.startswith("win")
            else os.path.join(os.environ["HOME"], "ClipperSaver")
        )
        if not os.path.isdir(fl):
            os.mkdir(fl)
        return fl

    def prre(self, pth: str, lock: bool = True) -> None:
        """MacOS X file protection"""

        v = None
        pr = None
        fl = None

        if lock:
            v = io.StringIO()
            with redirect_stdout(v):
                fl = ff(pth)
                fl.flagger("IMMUTABLE")
                pr = fpm(pth)
                pr.changeperm(644)
                v.flush()
        else:
            v = io.StringIO()
            with redirect_stdout(v):
                pr = fpm(pth)
                pr.changeperm(000, True)
                fl = ff(pth)
                fl.flagger("IMMUTABLE")
                v.flush()
        del pth, v, pr, fl

    def winatt(self, pth: str, lock: bool = True) -> None:
        """Windows file protection."""

        a = None
        if lock:
            a = AttSet(pth)
            for i in [
                WinAtt.HIDDEN.att,
                WinAtt.SYSTEM.att,
                WinAtt.READONLY.att
            ]:
                a.set_file_attrib(i)
        else:
            a = AttSet(pth, True)
            for i in [
                WinAtt.HIDDEN.att,
                WinAtt.SYSTEM.att,
                WinAtt.READONLY.att
            ]:
                a.set_file_attrib(i)
        del a
    
    def pltfuse(self, pth: str, lock: bool = True):

        match sys.platform:
            case plt if plt.startswith("win"):
                if lock:
                    self.winatt(pth)
                else:
                    self.winatt(pth, False)
            case _:
                if lock:
                    self.prre(pth)
                else:
                    self.prre(pth, False)

    def varsave(self, nvar: str, st: bool = True):
        pick = Path(os.path.join(self.fold(), f".clipvars.json"))
        pth = os.path.join(pick.parent, f".clipvars")
        lvar = [f"{nvar}"]
        co = None

        match st:
            case True:
                if not os.path.exists(pth):
                    deconstruct(f"{lvar}", pick.name, pick.parent)
                    os.rename(pick, pth)
                    self.pltfuse(pth, False)
                else:
                    self.pltfuse(pth)
                    os.rename(pth, pick)
                    co = construct(str(pick))
                    co = literal_eval(co)
                    lvar = lvar + co if not lvar[0] in co else co
                    deconstruct(f"{lvar}", pick.name, pick.parent)
                    os.rename(pick, pth)
                    self.pltfuse(pth, False)
            case False:
                if os.path.exists(pth):
                    self.pltfuse(pth)
                    os.rename(pth, pick)
                    co = construct(str(pick))
                    co = literal_eval(co)
                    co.pop(co.index(nvar))
                    if co:
                        deconstruct(f"{co}", pick.name, pick.parent)
                        os.rename(pick, pth)
                        self.pltfuse(pth, False)
                    else:
                        os.remove(pick)

        del pick, pth, lvar, co

    def rdvars(self) -> list | None:
        pick = Path(os.path.join(self.fold(), f".clipvars.json"))
        pth = os.path.join(pick.parent, f".clipvars")
        co = None

        if os.path.exists(pth):
            self.pltfuse(pth)
            os.rename(pth, pick)
            co = construct(str(pick))
            os.rename(pick, pth)
            self.pltfuse(pth, False)
        del pick, pth

        if co:
            return literal_eval(co)
        else:
            return co

    def sett(self, data: str | list, psd: str = None):
        v = None
        take = None
        if self.lock is None:
            self.lock = 1
            self.topm()

            class MyDialog(simpledialog.Dialog):
                def body(self, master):
                    tk.Label(master, text="Pass: ").grid(row=0, column=0, sticky=tk.E)
                    self.e1 = tk.Entry(master, show="-")
                    self.e1.grid(row=0, column=1)
                    if psd:
                        self.e1.insert(0, psd)
                    tk.Label(master, text="Var: ").grid(row=1, column=0, sticky=tk.E)
                    self.e2 = tk.Entry(master)
                    self.e2.grid(row=1, column=1)
                    return self.e1

                def apply(self):
                    if self.e1.get() and self.e2.get():
                        self.result = (
                            self.e1.get(),
                            self.e2.get(),
                        )
                    else:
                        self.result = None

            d = MyDialog(self.root)
            self.lock = None
            self.topm()
            if d.result:
                take = "".join(data) if isinstance(data, list) else data
                v = io.StringIO()
                with redirect_stdout(v):
                    cmsk(take, d.result[0], d.result[1])
                self.varsave(d.result[1])
                messagebox.showinfo("Clippers", f"{v.getvalue()[:-1]}")
                v.flush()
        del v, take, data, psd

    def gpss(self):
        pssd = simpledialog.askstring(
            "Clippers", "Password:", parent=self.root, show="-"
        )
        if pssd:
            return pssd

    def zipex(self, name: str, pssd: str, st: bool = True):
        ori = os.getcwd()
        os.chdir(self.fold())
        if st:
            zippy(name=name, pssd=pssd)
            os.remove(name)
            os.chdir(ori)
        else:
            zippy(name=name, pssd=pssd, st=False)
            os.chdir(ori)

    def struc(self):
        coll = []
        if self.sel:
            ask = messagebox.askyesno(
                "Clippers", "Do you want to set Environment Variable or Deconstruct?"
            )
            for i in self.sel:
                coll.append(self.ls.get(i))
            if ask:
                self.sett(coll)
            else:
                match (fname := simpledialog.askstring("Clippers", "File name:")):
                    case fname if fname in ["", None]:
                        fname = f'{str(datetime.timestamp(datetime.today())).replace(".", "_")}.json'
                    case _:
                        fname = f"{fname}.json"
                if pssd := self.gpss():
                    deconstruct(f"{coll}", fname, self.fold())
                    self.zipex(name=fname, pssd=pssd)
                else:
                    messagebox.showinfo(
                        "Clippers", "The Deconstruct has been canceled!"
                    )
                del fname, pssd
            self.ls.selection_clear(0, tk.END)
            self.sel = []
            self.upt = tuple()
        del coll

    def chfl(self, group: list):
        fl = group
        if fl and self.lock is None:
            self.lock = 1
            self.topm()

            class Mdialog(simpledialog.Dialog):
                def body(self, master) -> None:
                    self.e1 = tk.Listbox(master, selectmode="browse")
                    for i in fl:
                        self.e1.insert(self.e1.winfo_cells() + 1, i)
                    self.e1.pack(side="left", expand=1, fill="both")
                    self.e2 = tk.Scrollbar(master, orient="vertical")
                    self.e2.pack(side="right", fill="y")
                    self.e2.config(command=self.e1.yview)
                    self.e1.config(yscrollcommand=self.e2.set)
                    return self.e1

                def apply(self):
                    if self.e1.curselection():
                        self.result = fl[int(self.e1.curselection()[0])]

            d = Mdialog(self.root)
            self.lock = None
            self.topm()
            if d.result:
                return d.result

    def _retl(self, z: bool = True):
        if z:
            return [i for i in os.listdir(self.fold()) if ".7z" in i]
        else:
            return self.rdvars()

    def readec(self):
        if take := self.chfl(self._retl()):
            fld = self.fold()
            fln = take.rpartition(".")[0] + ".json"
            jn = os.path.join(fld, fln)
            if pssd := self.gpss():
                try:
                    self.zipex(name=fln, pssd=pssd, st=False)
                    con = construct(jn)
                    con = "".join(literal_eval(con))
                    os.remove(jn)
                    messagebox.showinfo("Clippers", con)
                    del con
                except Exception as e:
                    messagebox.showerror("Clippers", e)
            del fld, fln, jn, pssd, take

    def setdec(self):
        take = self.chfl(self._retl())
        psd = self.gpss() if take else None
        if take and psd:
            try:
                take = take.rpartition(".")[0] + ".json"
                jn = os.path.join(self.fold(), take)
                self.zipex(take, psd, False)
                con = literal_eval(construct(jn))
                os.remove(jn)
                self.sett(con, psd)
                del jn, con
            except Exception as e:
                messagebox.showerror("Clippers", e)
        del take, psd

    def deldec(self):
        if gt := self.chfl(self._retl()):
            if os.path.exists(pth := os.path.join(self.fold(), gt)):
                os.remove(pth)
                messagebox.showinfo("Clippers", f"{gt} has been deleted!")
            del pth
        del gt

    def ckpro(self):
        pth = [i for i in os.listdir(os.environ["HOME"]) if ".z" in i]
        if pth:
            for fi in pth:
                if any(fi in ck for ck in [".zprofile", ".zshrc", ".zshenv"]):
                    return True
            else:
                return False
        else:
            return False

    def clenvar(self):
        msg = sys.platform.startswith("win")
        if result := self.chfl(self._retl(z=False)):
            cl = Cleaner()
            v = io.StringIO()
            with redirect_stdout(v):
                if msg:
                    cl.wind(result)
                else:
                    fname = ".zprofile" if self.ckpro() else ".bash_profile"
                    cl.macs(result, fname)
                    del fname
                del cl
            self.varsave(result, False)
            msg = (
                v.getvalue() if msg else f"Var: {result}\nSuccessfully deleted!"
            )
            messagebox.showinfo("Clippers", f"{msg}")
            v.flush()
        del result, msg


def main():
    root = Tk()
    start = Clipper(root)
    start.root.mainloop()


def zippy(name: str, pssd: str, st: bool = True):
    if st:
        if os.path.isfile(name):
            arc = Ziper(name)
            arc.ziper7z(name=name.rpartition(".")[0], pssd=pssd)
    else:
        fln = name.rpartition(".")[0] + ".7z"
        if os.path.isfile(fln):
            arc = Ziper(name)
            arc.extfile(name=fln.rpartition(".")[0], pssd=pssd)
        del fln


if __name__ == "__main__":
    main()
