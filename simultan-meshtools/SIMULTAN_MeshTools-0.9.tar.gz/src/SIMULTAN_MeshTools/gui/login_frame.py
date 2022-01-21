import os
import sys
import time
from tkinter import END, Tk, Label, Entry, Button
from tkinter.filedialog import askopenfile
from tkinter.scrolledtext import ScrolledText
# import colorlog
# import threading
# from time import sleep
import traceback

import logging
from ..logger import logger
from ..shading_analysis import ProjectLoader

from multiprocessing import Queue, Process
# import queue

logger2 = logging.getLogger('PySimultan')


class WidgetLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.setLevel(logging.DEBUG)
        self.widget = widget
        self.widget.config(state='disabled')
        self.widget.tag_config("INFO", foreground="black")
        self.widget.tag_config("DEBUG", foreground="grey")
        self.widget.tag_config("WARNING", foreground="orange")
        self.widget.tag_config("ERROR", foreground="red")
        self.widget.tag_config("CRITICAL", foreground="red", underline=1)

        self.red = self.widget.tag_configure("red", foreground="red")

        self.t_update = time.time()

    def emit(self, record):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        self.widget.insert(END, self.format(record) + '\n', record.levelname)
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state='disabled')
        self.widget.update() # Refresh the widget

    def insert_str(self, str):
        self.widget.config(state='normal')
        # Append message (record) to the widget
        self.widget.insert(END, str)
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state='disabled')
        self.widget.update()  # Refresh the widget

    def overwrite(self, str):
        t_cur = time.time()
        if t_cur - self.t_update < 0.5:
            return

        self.t_update = t_cur

        self.widget.config(state='normal')
        self.widget.delete("end-2l", "end-1l")
        self.widget.insert(END, str)
        self.widget.see(END)  # Scroll to the bottom
        self.widget.config(state='disabled')
        self.widget.update()  # Refresh the widget


class MainWindow:
    def __init__(self):

        self.queue = Queue()
        self.app = Tk()

        def on_closing():
            self.app.destroy()
            sys.exit()

        self.app.protocol("WM_DELETE_WINDOW", on_closing)

        # self.app.protocol("WM_DELETE_WINDOW", self.app.iconify)
        # self.app.bind('<Escape>', lambda e: self.app.destroy())
        self.app.title('PySimultanRadiation')
        self.app.geometry('850x650')

        x = 70

        Label(self.app, text='Username').place(x=5, y=40, width=x, height=30)
        Label(self.app, text='Password').place(x=5, y=80, width=x, height=30)
        Label(self.app, text='Project').place(x=5, y=120, width=x, height=30)

        self.entry_username = Entry(self.app)
        self.entry_password = Entry(self.app, show="*")
        self.entry_project = Entry(self.app)

        self.entry_username.place(x=x+10, y=40, width=550, height=30)
        self.entry_password.place(x=x+10, y=80, width=550, height=30)
        self.entry_project.place(x=x+10, y=120, width=350, height=30)

        Button(self.app, text='Choose Project', pady=5, padx=30, command=self.choose_project).place(x=450, y=120)

        Button(self.app, text='Load Project', pady=5, padx=30, command=self.load_project).place(x=50, y=180)
        Button(self.app, text='Run simulation', pady=5, padx=30, command=self.run_simulation).place(x=250, y=180)
        Button(self.app, text='Close Project', pady=5, padx=30, command=self.close_project).place(x=450, y=180)

        self.st = ScrolledText(self.app, state='disabled')
        self.st.configure(font='TkFixedFont')
        self.st.place(x=5, y=220, width=840, height=400)

        self.text_handler = WidgetLogger(self.st)
        logger.addHandler(self.text_handler)
        logger2.addHandler(self.text_handler)

        logger2.setLevel('INFO')

        self._project_loader = None

    @property
    def project_filename(self):
        return self.entry_project.get()

    @property
    def username(self):
        return self.entry_username.get()

    @property
    def password(self):
        return self.entry_password.get()

    @property
    def project_loader(self):
        if self._project_loader is None:

            if not self.project_filename:
                logger2.error(f'No project selected. Please select a project!')
                return
            else:
                # check if file exists:
                if not os.path.isfile(self.project_filename):
                    logger2.error(f'Project {self.project_filename} not found. Please check the path and the name of the project!')
                    return

            if not self.username:
                logger2.error(f'No user name defined. Please define a user name!')
                return
            if not self.password:
                logger2.error(f'No password defined. Please define a password!')
                return

            try:
                self._project_loader = ProjectLoader(project_filename=self.project_filename,
                                                     user_name=self.username,
                                                     password=self.password,
                                                     app=self)
            except Exception as e:
                logger2.error(f'Error creating project loader:\n{e}')

        return self._project_loader

    @project_loader.setter
    def project_loader(self, value):
        self._project_loader = value

    def run(self):
        self.app.mainloop()

    def choose_project(self):
        file = askopenfile(title='Select a SIMULTAN Project...',
                           filetypes=[("SIMULTAN", ".simultan")])
        if file is not None:
            self.entry_project.delete(0, "end")
            self.entry_project.insert(0, file.name)

    def load_project(self):
        if self.project_loader is None:
            logger2.error(f'No project loader')
            return

        try:
            self.project_loader.load_project()
        except Exception as e:
            logger.error(f'Error loading project:\n{e}')

        logger.info(f'Project loaded successfully\n\n')

    def close_project(self):
        if self.project_loader is None:
            logger2.error(f'No project loader')
            return

        if self.project_loader.loaded:
            self.project_loader.close_project()
            self.project_loader = None

            logger.info('Project closed')

    def run_simulation(self):
        if self.project_loader is None:
            logger2.error(f'No project loader')
            return
        logger2.info('start running simulation')

        if not self.project_loader.loaded:
            self.load_project()

        try:
            self.project_loader.run()
        except Exception as e:
            logger.error(f'Simulation ended with errors:\n{e}\n')

        logger.info(f'Simulation(s) finished\n\n')


def run_simulation(project, username, password):
    project_loader = ProjectLoader(project_filename=project,
                                   user_name=username,
                                   password=password)

    try:
        project_loader.load_project()
    except Exception as e:
        logger.error(
            f'Error while loading Project:\n{e}\n{traceback.format_exc()}\n{sys.exc_info()[2]}')
        return

    project_loader.run()
