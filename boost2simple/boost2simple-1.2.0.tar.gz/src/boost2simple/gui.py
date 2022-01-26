#  boost2simple - the BoostNote->SimpleNote converter
#  Copyright (c) 2021, Rafael Witak.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import tkinter as tk
import webbrowser
from ctypes import windll
from tkinter.filedialog import askdirectory
from tkinter.font import Font

from boost2simple import converter

primary_light = "#F7F7FF"
primary_dark = "#545E75"
intro_text = "For optimal results, use a directory for importing " \
             "which has no other contents " \
             "than a folder for each exported BoostNote workspace. \n" \
             "See instructions at: "
repo_url = "https://github.com/RWitak/boost2simple#boost2simple"
c_notice = "Copyright (c) 2021, Rafael Witak.\nReleased under the GNU General Public License."


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, background=primary_light)

        self.master = master
        self.pack(ipadx=16, ipady=8)
        self.input_dir = tk.StringVar(master=self,
                                      value=os.path.join(os.environ['USERPROFILE'], 'Desktop'))
        self.output_dir = tk.StringVar(master=self, value=os.path.join(os.environ['USERPROFILE'], 'Desktop'))
        self.markdown = tk.BooleanVar(value=True)
        self.title = tk.BooleanVar(value=True)
        self.finished = tk.BooleanVar(value=False)
        self.listener = Listener()

        self.create_widgets()

    def convert(self):
        conv = converter.Converter(self.input_dir.get(), self.output_dir.get(),
                                   self.markdown.get(), self.title.get())
        exit_code = conv.convert_and_export()
        if exit_code == 0:
            self.listener.trigger_success(message=conv.status)
        else:
            self.listener.trigger_failure(message=conv.status + "\nRetry?")

    def set_input_dir(self):
        d = askdirectory(title="Select BoostNote directory")
        if d:
            self.input_dir.set(d)

    def set_output_dir(self):
        d = askdirectory(title="Select export directory")
        if d:
            self.output_dir.set(d)

    def create_widgets(self):
        self.winfo_toplevel().title("boost2simple - the BoostNote->SimpleNote converter")
        self.winfo_toplevel()

        intro_frame = tk.Frame(self, bg=primary_light)
        intro_frame.pack(side="top", padx=8, pady=16)

        title_label = tk.Label(master=intro_frame,
                               bg=primary_light,
                               fg="red",
                               text="boost2simple",
                               font=Font(family="Helvetica",
                                         size=24,
                                         weight="bold",
                                         slant="italic",
                                         underline=True))
        title_label.pack(side="top", pady=(0, 16))

        manual = tk.Label(intro_frame,
                          text=intro_text,
                          wraplength=400,
                          bg=primary_light)
        manual.pack(side="top", fill=tk.X, padx=8, pady=8)
        manual_font = Font(manual, manual.cget("font"))
        manual_font.configure(slant="italic")
        manual.configure(font=manual_font)

        link = tk.Button(intro_frame,
                         bg=primary_light, fg="blue",
                         text=repo_url,
                         command=visit_repo)
        link.pack(side="top")
        link_font = Font(link, link.cget("font"))
        link_font.configure(underline=True)
        link.configure(font=link_font)

        input_frame = tk.Frame(self, bg=primary_light)
        input_frame.pack(side="top", fill=tk.X, padx=8, pady=12)

        input_label = tk.Label(master=input_frame, bg=primary_light)
        input_label["text"] = "Select BoostNote directory:"
        input_label.pack(side="left")

        input_dir_btn = tk.Button(master=input_frame, bg=primary_dark, fg=primary_light, height=1, width=3)
        input_dir_btn["text"] = "..."
        input_dir_btn["command"] = self.set_input_dir
        input_dir_btn.pack(side="right")

        input_dir_path = tk.Label(master=input_frame, fg=primary_dark, textvariable=self.input_dir)
        input_dir_path.pack(side="right")

        output_frame = tk.Frame(self, bg=primary_light)
        output_frame.pack(side="top", fill=tk.X, padx=8, pady=12)

        output_label = tk.Label(output_frame, bg=primary_light)
        output_label["text"] = "Select export directory:"
        output_label.pack(side="left", fill=tk.X)

        output_dir_btn = tk.Button(output_frame, bg=primary_dark, fg=primary_light, height=1, width=3)
        output_dir_btn["text"] = "..."
        output_dir_btn["command"] = self.set_output_dir
        output_dir_btn.pack(side="right")

        output_dir_path = tk.Label(master=output_frame, textvariable=self.output_dir, fg=primary_dark)
        output_dir_path.pack(side="right")

        checkbox_frame = tk.Frame(self, bg=primary_light)
        checkbox_frame.pack(side="top", pady=(12, 24))

        markdown_toggle = tk.Checkbutton(master=checkbox_frame,
                                         text="use Markdown",
                                         onvalue=True,
                                         offvalue=False,
                                         variable=self.markdown,
                                         bg=primary_light)
        markdown_toggle.select()
        markdown_toggle.pack(side="left")
        title_toggle = tk.Checkbutton(master=checkbox_frame,
                                      text="include original title",
                                      onvalue=True,
                                      offvalue=False,
                                      variable=self.title,
                                      bg=primary_light)
        title_toggle.select()
        title_toggle.pack(side="left")

        convert_btn = tk.Button(self,
                                bg=primary_dark,
                                fg=primary_light,
                                text="Convert",
                                command=self.convert,
                                font=("Helvetica", 12, "normal"),
                                )
        convert_btn.pack(side="top", padx=8, pady=8, ipadx=4, ipady=0)
        self.listener.set_success_button(convert_btn)

        quit_btn = tk.Button(self,
                             text="Exit",
                             bg="#C03221",
                             fg=primary_light,
                             command=self.master.destroy)
        quit_btn.pack(side="top", ipadx=0, ipady=0)

        copyright_label = tk.Label(self,
                                   text=c_notice,
                                   bg=primary_light)
        copyright_label.pack(side="top", padx=8, pady=(18, 0))
        c_label_font = Font(copyright_label, copyright_label.cget("font"))
        c_label_font.configure(slant="italic")
        copyright_label.configure(font=c_label_font)


class Listener:
    def __init__(self):
        self.success_button = tk.Button()

    def set_success_button(self, button: tk.Button):
        self.success_button = button

    def trigger_success(self, message="Success"):
        self.success_button.configure(bg="green",
                                      disabledforeground="white",
                                      text=message,
                                      state=tk.DISABLED,
                                      wraplength=400)

    def trigger_failure(self, message="Failure"):
        self.success_button.configure(bg="black",
                                      foreground="red",
                                      text=message,
                                      wraplength=400)


def visit_repo():
    webbrowser.open(repo_url)


def main():
    windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.resizable(False, False)
    app = Application(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()
