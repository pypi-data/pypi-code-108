import os
import re
import sys
import tkinter as tk
from tkinter import Tk

from .gui_utils import center_window_geometry


class ProgressWindow:
    root: Tk

    def __init__(self):
        bg = (  # Equivalent to value of Grapher's colours["fig_face"] = (0.95, 0.95, 0.90).
            "#F2F2E6"  # Keep in sync.
        )

        self.root = tk.Tk()

        png = os.path.join(os.path.dirname(__file__), "logo.png")
        self.logo = tk.PhotoImage(file=png).subsample(5)
        self.root.iconphoto(True, self.logo)

        self.root.attributes("-alpha", 0.0)
        self.root.configure(bg=bg)
        self.root.update_idletasks()  # Get up to date with current situation

        # Flip into fullscreen, stash geometry, flip out
        self.root.attributes("-fullscreen", True)
        self.root.state("iconic")
        self.screen_geometry = self.root.winfo_geometry()
        self.root.attributes("-fullscreen", False)

        # Setup fixed sized, always on top window
        self.root.title("topplot")
        self.root.geometry("500x150")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", 1)
        self.root.state("normal")

        if sys.platform.startswith("win"):
            # Don't add screen furniture
            self.root.overrideredirect(1)  # Messes up centering on my Linux WM

        # Setup frame and contained logo and label
        frame = tk.Frame(self.root, bd=1, relief="raised")
        frame.config(bg=bg)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        logo = tk.Label(frame, image=self.logo)
        logo.config(bg=bg)
        logo.pack(side=tk.TOP, padx=10, pady=10)

        self.status = tk.Label(
            frame, text="topplot is initializing...                 ",
        )
        self.status.config(bg=bg)
        self.status.pack(expand=True, side=tk.LEFT)

        frame.pack(fill=tk.BOTH, expand=True)

        self.root.update_idletasks()
        self.center()

        self.root.attributes("-alpha", 1.0)

    # ----------------------------------------------------------------------

    def center(self, win=None):
        if self.root is not None:
            if win is None:
                win = self.root
                self.root.update()
            else:
                self.root.update_idletasks()

            win_width = win.winfo_width()
            win_height = win.winfo_height()

            screen_width, screen_height = self.get_curr_screen_dimensions()

            # print(f"{win_width=}    {win_height=}")
            # print(f"{screen_width=}    {screen_height=}")

            new_geometry = center_window_geometry(
                win_width,
                win_height,
                screen_width,
                screen_height,
                self.root.winfo_pointerx(),
                self.root.winfo_pointery(),
            )

            # print(f"{new_geometry=}")

            win.geometry(new_geometry)

            win_width = win.winfo_width()
            win_height = win.winfo_height()

    # ----------------------------------------------------------------------

    def hide(self):
        if self.root is not None:
            self.root.withdraw()

    # ----------------------------------------------------------------------

    def show(self):
        if self.root is not None:
            self.root.deiconify()
            self.root.update()

    # ----------------------------------------------------------------------

    def destroy(self):
        if self.root is not None:
            self.root.quit()
            self.root.destroy()
            self.root = None

    # ----------------------------------------------------------------------

    def update_status(self, msg):
        if self.root is not None:
            self.status.configure(text=f"topplot is {msg}...")
            self.root.update()

    # ----------------------------------------------------------------------

    def get_curr_screen_dimensions(self, scale=1.0):
        if self.screen_geometry is None:
            return None

        m = re.match(
            r"^(?P<width>\d+)x(?P<height>\d+)\+(?P<position>\d+\+\d+)",
            self.screen_geometry,
        )
        groups = m.groupdict()
        return (
            int(int(groups["width"]) * scale),
            int(int(groups["height"]) * scale),
        )
