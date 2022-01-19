import logging
import math
import platform
import subprocess
import threading
import tkinter as tk
import webbrowser
from enum import Enum
from time import sleep
from tkinter import Tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk

import matplotlib.pyplot as plt
import numpy as np
import serial
from PIL import ImageTk, Image
from bitstring import BitArray
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from serial.tools.list_ports import comports

from ._audio import pcm_to_wave
from ._firmware import upload_firmware
from ._gui_param import *
from ._hardware import Boards
from ._param import upload_params

LICENSE = dict(
    picovoice=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'LICENSE'),
    st=os.path.join(os.path.abspath((os.path.dirname(__file__))), 'thirdparty/st/license.txt'),
    nxp=os.path.join(os.path.abspath((os.path.dirname(__file__))), 'thirdparty/nxp/license.txt')
)

DEFAULT_PORCUPINE_MODEL = dict(
    en={
        'name': 'Picovoice',
        'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_files/picovoice_cortexm.ppn')
    },
    de={
        'name': 'Hey Computer',
        'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_files/hey computer_cortexm.ppn')
    },
    es={'name': 'Hola Computadora',
        'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_files/hola computadora_cortexm.ppn')
        },
    fr={
        'name': 'Salut Ordinateur',
        'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_files/salut ordinateur_cortexm.ppn')
    }
)

DEFAULT_RHINO_MODEL = dict(
    en={
        'name': 'Smart Lighting [en]',
        'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_files/smart_lighting_cortexm.rhn')
    },
    de={
        'name': 'Beleuchtung [de]',
        'path': os.path.join(os.path.abspath(os.path.dirname(__file__)), 'sample_files/beleuchtung_cortexm.rhn')
    },
    es={
        'name': 'Iluminación Inteligente [es]',
        'path': os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'sample_files/iluminación_inteligente_cortexm.rhn')
    },
    fr={
        'name': 'éclairage intelligent [fr]',
        'path': os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),
            'sample_files/éclairage_intelligent_cortexm.rhn')
    }
)


class MessageCode(Enum):
    PV_MESSAGE_CODE_HANDSHAKE = '[00]',
    PV_MESSAGE_CODE_INFO = '[01]',
    PV_MESSAGE_CODE_CONTEXT = '[02]',
    PV_MESSAGE_CODE_WAKE_DETECTED = '[03]',
    PV_MESSAGE_CODE_INFERENCE = '[04]',
    PV_MESSAGE_CODE_PORCUPINE_SENSITIVITY = '[05]',
    PV_MESSAGE_CODE_RHINO_SENSITIVITY = '[06]',
    PV_MESSAGE_CODE_UUID = '[07]',
    PV_MESSAGE_CODE_CPU_USAGE = '[08]',
    PV_MESSAGE_CODE_VOLUME = '[09]',
    PV_MESSAGE_CODE_AUDIO_DUMP = '[10]',
    PV_MESSAGE_CODE_ERROR = '[11]'


BOARDS = [
    Boards.STM32F407G_DISCO.value,
    Boards.STM32F411E_DISCO.value,
    Boards.STM32F469I_DISCO.value,
    Boards.STM32F769I_DISCO.value,
    Boards.STM32H735G_DK.value,
    Boards.STM32H747I_DISCO.value,
    Boards.IMXRT1050_EVKB.value,
]

LANGUAGES = [
    'English',
    'Deutsch',
    'Español',
    'Français',
]

LANGUAGE_TO_CODE = dict(
    English='en',
    Français='fr',
    Deutsch='de',
    Español='es'
)

AUDIO_DEBUG_RECORD_DURATION_SEC = {
    Boards.STM32F469I_DISCO.value: 3,
    Boards.STM32F769I_DISCO.value: 3,
    Boards.STM32H747I_DISCO.value: 3,
    Boards.STM32F407G_DISCO.value: 1,
    Boards.STM32F411E_DISCO.value: 1,
    Boards.STM32H735G_DK.value: 3,
    Boards.IMXRT1050_EVKB.value: 3
}

AUDIO_DEBUG_FFT_WINDOW_SIZE = 512
AUDIO_DEBUG_FFT_OVERLAP = AUDIO_DEBUG_FFT_WINDOW_SIZE - 160
AUDIO_DEBUG_SAMPLING_FREQUENCY = 16000

MONITORING_CENTER_VU_METER_MIN_DB = -50
MONITORING_CENTER_SMOOTHING_FACTOR_VU_METER = 0.3
MONITORING_CENTER_SMOOTHING_FACTOR_CPU_USAGE = 0.3

SERIAL_CONNECTION_RETRIES = 10

NO_UPLOAD = False
DEBUG = False

log = logging.getLogger('shepherd')
log.setLevel(logging.DEBUG if DEBUG else logging.WARNING)


class PicoFrame(object):

    def consume(self, code, payload):
        raise NotImplementedError()

    def clean(self):
        raise NotImplementedError()

    def connection_error(self):
        raise NotImplementedError()

    def draw_next_frame(self):
        raise NotImplementedError()

    def draw_previous_frame(self):
        raise NotImplementedError()


class PicovoiceApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.config(**FRAME_COMMON_PARAMS)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.iconphoto(False, tk.PhotoImage(file=IMAGES['window_icon']))
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.option_add('*font', FONT)
        self.title(TITLE)

        pv_style = ttk.Style()
        pv_style.theme_use('default')
        pv_style.configure("P.TButton", **PRIMARY_BUTTONS_COMMON_PARAMS_CONFIG)
        pv_style.map("P.TButton", **PRIMARY_BUTTONS_COMMON_PARAMS_MAP)
        pv_style.configure("B.TButton", **BACK_BUTTONS_COMMON_PARAMS_CONFIG)
        pv_style.map("B.TButton", **BACK_BUTTONS_COMMON_PARAMS_MAP)
        pv_style.configure("S.TButton", **SECONDARY_BUTTONS_COMMON_PARAMS_CONFIG)
        pv_style.map("S.TButton", **SECONDARY_BUTTONS_COMMON_PARAMS_MAP)
        pv_style.configure("A.TButton", **SECONDARY_AUDIO_BUTTONS_COMMON_PARAMS_CONFIG)
        pv_style.map("A.TButton", **SECONDARY_AUDIO_BUTTONS_COMMON_PARAMS_MAP)
        pv_style.configure("TNotebook", **NOTEBOOK_PARAMS)
        pv_style.configure("TNotebook.Tab", **NOTEBOOK_TAB_PARAMS)
        pv_style.map("TNotebook.Tab", **NOTEBOOK_ACTIVE_TAB_PARAMS)
        pv_style.configure("TProgressbar", **PROGRESSBAR_PARAMS)

        pv_style.element_create("plain.field", "from", "clam")
        pv_style.layout("EntryStyle.TEntry",
                        [('Entry.plain.field', {'children': [(
                            'Entry.background', {'children': [(
                                'Entry.padding', {'children': [(
                                    'Entry.textarea', {'sticky': 'news'})],
                                    'sticky': 'news'})], 'sticky': 'news'})],
                            'border': '2', 'sticky': 'news'})])
        pv_style.configure("EntryStyle.TEntry", **ENTRY_PARAMS_CONFIG)
        pv_style.map("EntryStyle.TEntry", **ENTRY_PARAMS_MAP)
        pv_style.configure("Treeview", **LIST_BOX_COMMON_PARAMS_CONFIG)
        pv_style.map('Treeview', **LIST_BOX_COMMON_PARAMS_MAP)

        self._active_frame = UploadFirmwareFrame(master=self)

        self._menu_bar = tk.Menu(master=self, **MENU_BAR_PARAMS)
        self._file_menu = tk.Menu(master=self._menu_bar, tearoff=0, **MENU_BAR_PARAMS)
        self._file_menu.add_command(label="Quit", underline=0, command=self._destroy)
        self._menu_bar.add_cascade(label="File", underline=0, menu=self._file_menu)

        self._help_menu = tk.Menu(master=self._menu_bar, tearoff=0, **MENU_BAR_PARAMS)
        self._help_menu.add_command(
            label="Shepherd Help...",
            underline=0,
            command=lambda: webbrowser.open('https://picovoice.ai/docs/picovoice-shepherd/', new=0)
        )
        self._help_menu.add_command(
            label="Picovoice Help...",
            underline=0,
            command=lambda: webbrowser.open('https://picovoice.ai/docs/picovoice/', new=0)
        )
        self._help_menu.add_separator()
        self._help_menu.add_command(
            label="License Information",
            underline=0,
            command=self._license_popup
        )
        self._help_menu.add_separator()
        self._help_menu.add_command(
            label="Submit a Bug Report...",
            underline=1,
            command=lambda: webbrowser.open(
                'https://github.com/Picovoice/picovoice/issues/new?assignees=&labels=bug'
                '&template=bug_report.md'
                '&title=Picovoice+Shepherd+bug on ' +
                platform.uname()[0] + '-' +
                platform.uname()[2] + '-' +
                platform.uname()[4] + '-' +
                platform.uname()[5],
                new=0)
        )
        self._help_menu.add_command(
            label="Contact Sales...",
            underline=0,
            command=lambda: webbrowser.open('https://picovoice.ai/contact/sales/', new=0)
        )
        self._menu_bar.add_cascade(label="Help", menu=self._help_menu, underline=0)
        self.config(menu=self._menu_bar)

        self._status_bar = ttk.Label(
            self,
            text='',
            borderwidth=1,
            relief='flat',
            background=FRAME_COMMON_PARAMS['background'],
            anchor=tk.W)
        self._status_bar.grid(row=1, column=0, sticky='swe')

        self.protocol("WM_DELETE_WINDOW", self._destroy)

    def _license_popup(self):
        self._license_viewer = tk.Toplevel()
        self._license_viewer.wm_title('Licence Information')
        self._license_viewer.minsize(300, 200)
        self._license_viewer.grid_rowconfigure(0, weight=1)
        self._license_viewer.grid_columnconfigure(0, weight=1)
        self._license_viewer.option_add('*font', FONT)
        self._license_viewer.config(**FRAME_COMMON_PARAMS)
        license_scrolled_text = scrolledtext.ScrolledText(
            self._license_viewer,
            bg=SOFT_GREY,
            foreground='#000000',
            height=20,
            wrap='word',
        )
        license_scrolled_text.grid(row=0, column=0, padx=10, pady=10, sticky='news')

        for item in LICENSE.items():
            with open(item[1], 'r', encoding="utf8") as license_file:
                license_scrolled_text.insert('end', ' %s\n' % license_file.read())
                license_scrolled_text.insert('end', '-------------------------\n')
        license_scrolled_text.config(state='disabled')

    def _destroy(self):
        self._active_frame.clean()
        Tk.destroy(self)

    def update_status_bar(self, text):
        self._status_bar.config(text=text)

    def draw_upload_firmware_frame(self):
        old_frame = self._active_frame
        self._active_frame = UploadFirmwareFrame(self)
        old_frame.destroy()
        del old_frame

    def draw_upload_models_frame(self, board, language):
        self.update_status_bar("Connected to '%s-%s'" % (board, language))
        old_frame = self._active_frame
        self._active_frame = UploadModelsFrame(self, board, language)
        old_frame.destroy()
        del old_frame

    def draw_control_panel_frame(self, board, language, picovoice_models):
        self.update_status_bar("Connected to '%s-%s'" % (board, language))
        old_frame = self._active_frame
        self._active_frame = ControlPanel(self, board, language, picovoice_models)
        old_frame.destroy()
        del old_frame


class UploadFirmwareFrame(tk.Frame, PicoFrame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        self._is_uploading_done = False
        self._is_status_update_done = False
        self._board = None
        self._language = None

        self.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1, minsize=120)
        self.grid_rowconfigure(4, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.configure(**FRAME_COMMON_PARAMS)

        self._picovoice_image = ImageTk.PhotoImage(Image.open(IMAGES['picovoice']))
        self._picovoice_image_label = ttk.Label(
            self,
            image=self._picovoice_image,
            borderwidth=1,
            relief='flat',
            background=FRAME_COMMON_PARAMS['background'])
        self._picovoice_image_label.grid(row=0, column=0, columnspan=4, pady=20, sticky='s')

        self._hint_label = ttk.Label(
            self,
            text="Select Your Board and language:",
            background=FRAME_COMMON_PARAMS['background'],
            font=(FONT[0], int(FONT[1] * 1.5)))
        self._hint_label.grid(row=1, column=0, columnspan=4, pady=20, sticky='s')

        self._boards_tree_view = ttk.Treeview(
            self,
            cursor='hand2',
            height=8,
            show='tree')
        for i, x in enumerate(BOARDS):
            self._boards_tree_view.insert('', 'end', text=x)
        self._boards_tree_view.column("#0", anchor="center")
        self._boards_tree_view.grid(row=2, column=0, columnspan=2, sticky='es')
        self._boards_tree_view.bind('<ButtonRelease-1>', self._update_selected_board)
        self._languages_tree_view = ttk.Treeview(
            self,
            cursor='hand2',
            height=8,
            show='tree')
        for i, x in enumerate(LANGUAGES):
            self._languages_tree_view.insert('', 'end', text=x)
        self._languages_tree_view.column("#0", anchor="center")
        self._languages_tree_view.grid(row=2, column=2, columnspan=2, sticky='ws')
        self._languages_tree_view.bind('<ButtonRelease-1>', self._update_selected_language)

        self._uploading_label = LoadingAnimation(self)
        self._uploading_label.grid(row=3, column=0, columnspan=4, sticky='ns')

        self._upload_button = ttk.Button(
            self,
            command=self._upload_firmware,
            cursor='hand2',
            style="P.TButton",
            text='Upload Firmware ⇨'
        )
        self._upload_button.grid(row=4, column=3, pady=20, padx=20, ipady=10, ipadx=10, sticky='se')
        self._upload_button.state(["disabled"])

    def _update_selected_board(self, _):
        selected_board = self._boards_tree_view.focus()
        self._board = self._boards_tree_view.item(selected_board)['text']
        if self._board is not None and self._language is not None:
            self._upload_button.state(["!disabled"])
            self.master.update_status_bar("Selected '%s-%s'" % (self._board, self._language))

    def _update_selected_language(self, _):
        selected_language = self._languages_tree_view.focus()
        self._language = self._languages_tree_view.item(selected_language)['text']
        if self._language is not None and self._board is not None:
            self._upload_button.state(["!disabled"])
            self.master.update_status_bar("Selected '%s-%s'" % (self._board, self._language))

    def _upload_firmware(self):
        self._is_status_update_done = False
        self._is_uploading_done = False
        self._uploading_label.start_loading()
        self.master.update_status_bar('Uploading firmware')
        self._update_thread = threading.Thread(target=self._upload_helper)
        self._update_thread.start()
        self._check_uploading(1)

    def _upload_helper(self):
        self._upload_button.state(["disabled"])
        self._boards_tree_view.state(["disabled"])
        self._boards_tree_view.unbind('<ButtonRelease-1>')
        try:
            if not NO_UPLOAD:
                upload_firmware(Boards(self._board), LANGUAGE_TO_CODE[self._language])
                self._is_status_update_done = True
        except RuntimeError as e:
            self.master.update_status_bar("Selected '%s-%s'" % (self._board, self._language))
            messagebox.showerror(title='Error', message=str(e))
            self._upload_button.state(["!disabled"])
            self._boards_tree_view.state(["!disabled"])
            self._boards_tree_view.bind('<ButtonRelease-1>', self._update_selected_board)
            self._uploading_label.stop_loading()
            self._is_status_update_done = True
        else:
            self._is_uploading_done = True

    def _check_uploading(self, n):
        if self._is_uploading_done:
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
            self.draw_next_frame()
        elif not self._is_status_update_done:
            n = (n + 1) % 10
            self.master.update_status_bar('Uploading firmware  ▏' + '▊' * n + '▁' * (9 - n) + '▕')
            self.after(200, self._check_uploading, n)
        else:
            self.master.update_status_bar("Selected '%s-%s'" % (self._board, self._language))

    def clean(self):
        pass

    def consume(self, code, payload):
        pass

    def connection_error(self):
        messagebox.showerror(title='Error', message='Connection to %s was lost' % self._board)
        self.master.update_status_bar('')
        self.master.draw_upload_firmware_frame()

    def draw_next_frame(self):
        self.clean()
        self.master.draw_upload_models_frame(self._board, self._language)

    def draw_previous_frame(self):
        raise NotImplementedError()


class UploadModelsFrame(tk.Frame, PicoFrame):
    def __init__(self, master, board, language):
        tk.Frame.__init__(self, master)

        self._board = board
        self._language = language
        self._ports = None
        self._port = None
        self._serial_driver = None
        self._message_thread = None
        self._is_connecting_done = False

        self._uuid = None
        self._is_uploading_done = False
        self._is_status_update_done = False
        self._is_responded = False
        self._selected_models = dict(
            porcupine=DEFAULT_PORCUPINE_MODEL[LANGUAGE_TO_CODE[self._language]]['name'],
            rhino=DEFAULT_RHINO_MODEL[LANGUAGE_TO_CODE[self._language]]['name']
        )

        self.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1, minsize=100)
        self.grid_rowconfigure(4, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.configure(**FRAME_COMMON_PARAMS)

        self._porcupine_model_path = DEFAULT_PORCUPINE_MODEL[LANGUAGE_TO_CODE[self._language]]['path']
        self._rhino_model_path = DEFAULT_RHINO_MODEL[LANGUAGE_TO_CODE[self._language]]['path']

        self._uuid_label_frame = tk.LabelFrame(
            self,
            text=' Chip UUID ',
            foreground='black',
            **FRAME_COMMON_PARAMS)
        self._uuid_label_frame.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky='s')
        self._uuid_entry = ttk.Entry(
            self._uuid_label_frame,
            style="EntryStyle.TEntry",
            **ENTRY_PARAMS_ttk)
        self._uuid_entry.grid(row=0, column=0, pady=20, padx=10, sticky='se')
        if self._board.startswith('STM32'):
            self._uuid_entry.insert(0, '__ __ __ __ __ __ __ __ __ __ __ __')
        elif self._board.startswith('IMXRT'):
            self._uuid_entry.insert(0, '__ __ __ __ __ __ __ __')
        self._uuid_entry.state(["disabled"])

        self._clipboard_photo = ImageTk.PhotoImage(Image.open(IMAGES['clipboard']))

        self._uuid_copy_button = ttk.Button(
            self._uuid_label_frame,
            command=self._copy_to_clipboard,
            cursor='hand2',
            style="S.TButton",
            text='Copy',
            image=self._clipboard_photo,
            compound='right',
            width=10
        )

        self._uuid_copy_button.grid(row=0, column=2, padx=(0, 10), pady=20, ipady=4, sticky='sw')
        self._uuid_copy_button.state(["disabled"])

        self._access_key_label_frame = tk.LabelFrame(
            self,
            text=' AccessKey ',
            foreground='black',
            **FRAME_COMMON_PARAMS)
        self._access_key_label_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky='s')
        self._access_key_entry = ttk.Entry(
            self._access_key_label_frame,
            style="EntryStyle.TEntry",
            **ENTRY_PARAMS_ttk)
        self._access_key_entry.grid(row=0, column=0, pady=20, padx=10, sticky='se')
        self._access_key_paste_button = ttk.Button(
            self._access_key_label_frame,
            command=self._paste_from_clipboard,
            cursor='hand2',
            style="S.TButton",
            text='Paste',
            image=self._clipboard_photo,
            compound='right',
            width=10
        )

        self._access_key_paste_button.grid(row=0, column=2, padx=(0, 10), pady=20, ipady=4, sticky='sw')

        self._upload_models_label_frame = tk.LabelFrame(
            self,
            text=' Models ',
            foreground='black',
            **FRAME_COMMON_PARAMS)
        self._upload_models_label_frame.grid(row=2, column=0, columnspan=3, pady=20, sticky='s')
        self._upload_models_label_frame.grid_rowconfigure(0, weight=0)
        self._upload_models_label_frame.grid_rowconfigure(1, weight=1)
        self._upload_models_label_frame.grid_rowconfigure(2, weight=1, minsize=10)
        self._upload_models_label_frame.grid_rowconfigure(3, weight=0)
        self._upload_models_label_frame.grid_rowconfigure(4, weight=1)
        self._upload_models_label_frame.grid_columnconfigure(0, weight=1)
        self._upload_models_label_frame.grid_columnconfigure(1, weight=1)

        self._porcupine_model_label = ttk.Label(
            self._upload_models_label_frame,
            text='Porcupine:',
            background=FRAME_COMMON_PARAMS['background'],
            anchor='w',
            width=20,
            font=(FONT[0], int(FONT[1] * 1.5)))
        self._porcupine_model_label.grid(row=0, column=0, padx=10, sticky='ws')

        self._porcupine_selected_model_entry = ttk.Entry(
            self._upload_models_label_frame,
            style="EntryStyle.TEntry",
            **ENTRY_PARAMS_ttk)
        self._porcupine_selected_model_entry.grid(row=1, column=0, padx=10)
        self._porcupine_selected_model_entry.delete(0, tk.END)
        self._porcupine_selected_model_entry.insert(0,
                                                    DEFAULT_PORCUPINE_MODEL[LANGUAGE_TO_CODE[self._language]]['name'])
        self._porcupine_selected_model_entry.state(["disabled"])

        self._select_porcupine_model_button = ttk.Button(
            self._upload_models_label_frame,
            command=self._select_porcupine_model,
            cursor='hand2',
            style="S.TButton",
            text=' Select... ',
            width=12
        )
        self._select_porcupine_model_button.grid(row=1, column=1, padx=(0, 10), ipady=4)
        self._select_porcupine_model_button.state(["disabled"])

        self._rhino_model_label = ttk.Label(
            self._upload_models_label_frame,
            text='Rhino:',
            anchor='w',
            width=20,
            background=FRAME_COMMON_PARAMS['background'],
            font=(FONT[0], int(FONT[1] * 1.5)))
        self._rhino_model_label.grid(row=3, column=0, padx=10, sticky='ws')

        self._rhino_selected_model_entry = ttk.Entry(
            self._upload_models_label_frame,
            style="EntryStyle.TEntry",
            **ENTRY_PARAMS_ttk)
        self._rhino_selected_model_entry.grid(row=4, column=0, padx=10, pady=(0, 10))
        self._rhino_selected_model_entry.delete(0, tk.END)
        self._rhino_selected_model_entry.insert(0, DEFAULT_RHINO_MODEL[LANGUAGE_TO_CODE[self._language]]['name'])
        self._rhino_selected_model_entry.state(["disabled"])

        self._select_rhino_model_button = ttk.Button(
            self._upload_models_label_frame,
            command=self._select_rhino_model,
            cursor='hand2',
            style="S.TButton",
            text=' Select... ',
            width=12
        )
        self._select_rhino_model_button.grid(row=4, column=1, padx=(0, 10), pady=(0, 10), ipady=4, )
        self._select_rhino_model_button.state(["disabled"])

        self._upload_label = LoadingAnimation(self)
        self._upload_label.grid(row=3, column=0, columnspan=3)

        self._back_button = ttk.Button(
            self,
            command=self.draw_previous_frame,
            cursor='hand2',
            style="B.TButton",
            text='⇦ Back'
        )

        self._back_button.grid(row=4, column=0, pady=20, padx=20, ipady=10, ipadx=10, sticky='sw')

        self._upload_models_button = ttk.Button(
            self,
            command=self._upload_models,
            cursor='hand2',
            style="P.TButton",
            text='Use Default Models ⇨'
        )
        self._upload_models_button.grid(row=4, column=2, pady=20, padx=20, ipady=10, ipadx=10, sticky='se')
        self._upload_models_button.state(["disabled"])

        self.master.update_status_bar('Connecting to the board')
        self._update_thread = threading.Thread(target=self._connect)
        self.after(2000, self._update_thread.start)
        self._check_connecting(1)

    def _connect(self):
        for _ in range(SERIAL_CONNECTION_RETRIES):
            for port in serial.tools.list_ports.comports():
                try:
                    self._port = port
                    self._serial_driver = serial.Serial(port=port.device, baudrate=115200)
                    self._message_thread = MessageControlThread(self._serial_driver, port, self)
                    self._message_thread.start_communicate()
                    self._message_thread.send_message("%s 0000000000"
                                                      % MessageCode.PV_MESSAGE_CODE_HANDSHAKE.value[0])
                    sleep(0.5)
                except serial.SerialException:
                    continue
                if self._is_connecting_done:
                    break
                else:
                    self._message_thread.request_disconnect()
            if self._is_connecting_done:
                break

        if not self._is_connecting_done:
            self._is_status_update_done = True
            messagebox.showerror(title='Error', message='No serial connection was detected for %s' % self._board)
            self.master.update_status_bar("Selected '%s-%s'" % (self._board, self._language))
            self.master.draw_upload_firmware_frame()

    def _check_connecting(self, n):
        if self._is_connecting_done:
            self._is_status_update_done = True
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
            self.after(200, self._get_uuid)
        elif not self._is_status_update_done:
            n = (n + 1) % 10
            self.master.update_status_bar('Connecting to the board  ▏' + '▊' * n + '▁' * (9 - n) + '▕')
            self.after(200, self._check_connecting, n)
        else:
            self.master.update_status_bar('No serial connection was detected for %s' % self._board)

    def _get_uuid(self):
        if not self._is_responded:
            self._message_thread.send_message("%s 0000000000" % MessageCode.PV_MESSAGE_CODE_UUID.value[0])
            self.after(200, self._get_uuid)
        else:
            self._message_thread.change_consumer(None)
            self._message_thread.request_disconnect()
            self._uuid_entry.state(["!disabled"])
            self._uuid_entry.delete(0, tk.END)
            self._uuid_entry.insert(0, self._uuid)
            self._uuid_entry.state(["disabled"])
            self._uuid_copy_button.state(["!disabled"])
            self._upload_models_button.state(["!disabled"])
            self._select_rhino_model_button.state(["!disabled"])
            self._select_porcupine_model_button.state(["!disabled"])

    def _upload_models(self):
        self._is_uploading_done = False
        self._is_status_update_done = False
        self.master.update_status_bar('Uploading models')
        self.update_Thread = threading.Thread(target=self._upload_models_helper)
        self.update_Thread.start()
        self._check_uploading(1)

    def _check_uploading(self, n):
        if self._is_uploading_done:
            self.draw_next_frame()
        elif not self._is_status_update_done:
            n = (n + 1) % 10
            self.master.update_status_bar('Uploading models ▏' + '▊' * n + '▁' * (9 - n) + '▕')
            self.after(200, self._check_uploading, n)
        else:
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))

    def _upload_models_helper(self):
        if self._access_key_entry.get() == '':
            messagebox.showerror(
                title='AccessKey is required',
                message='Enter a valid AccessKey obtained from Picovoice Console (https://picovoice.ai/console/)')
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
        elif self._porcupine_model_path is None:
            messagebox.showerror(
                title='Porcupine wake word model is not selected!',
                message='Select a valid Porcupine wake word model file (.PPN)')
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
        elif self._rhino_model_path is None:
            messagebox.showerror(
                title='Rhino Speech-to-Intent model is not selected',
                message='Select a valid Rhino Speech-to-Intent model file (.RHN)')
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
        else:
            self._upload_label.start_loading()
            self._back_button.state(["disabled"])
            self._upload_models_button.state(["disabled"])
            self._select_porcupine_model_button.state(["disabled"])
            self._select_rhino_model_button.state(["disabled"])
            try:
                if not NO_UPLOAD:
                    upload_params(
                        ppn_path=self._porcupine_model_path,
                        rhn_path=self._rhino_model_path,
                        access_key=self._access_key_entry.get(),
                        board=Boards(self._board))
            except RuntimeError as e:
                self._is_status_update_done = True
                self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
                messagebox.showerror(title='Error', message=str(e))
                self._upload_label.stop_loading()
                self._back_button.state(["!disabled"])
                self._upload_models_button.state(["!disabled"])
                self._select_porcupine_model_button.state(["!disabled"])
                self._select_rhino_model_button.state(["!disabled"])
            else:
                self._is_uploading_done = True
                
        self._is_status_update_done = True

    def _select_porcupine_model(self):
        self._porcupine_model_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.expanduser('~/')),
            title="Select Porcupine Wake Word Model (.PPN)",
            filetypes=(("ppn files", "*.ppn"), ("all files", "*.*")))

        if (type(self._porcupine_model_path) is not tuple) and self._porcupine_model_path:
            if '_cortexm_' not in os.path.basename(self._porcupine_model_path):
                messagebox.showwarning(
                    title='warning',
                    message='It seems that the selected model belongs to a '
                            'different platform.\n Please make sure that the '
                            'right model is chosen before proceeding.')
            porcupine_model_name = os.path.basename(self._porcupine_model_path).split('_cortexm')[0].replace('_', ' ')
            porcupine_model_name = ' '.join([x.capitalize() for x in porcupine_model_name.split()])
            self._selected_models['porcupine'] = porcupine_model_name
            self._porcupine_selected_model_entry.state(["!disabled"])
            self._porcupine_selected_model_entry.delete(0, tk.END)
            self._porcupine_selected_model_entry.insert(0, porcupine_model_name)
            self._porcupine_selected_model_entry.state(["disabled"])
            self._upload_models_button.config(text='Upload ⇨', command=self._upload_models)
        else:
            self._porcupine_model_path = None
            self._porcupine_selected_model_entry.insert(0, '')
            self._upload_models_button.state(["!disabled"])

    def _select_rhino_model(self):
        self._rhino_model_path = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.expanduser('~/')),
            title="Select Rhino Speech-to-Intent Model (.RHN)",
            filetypes=(("rhn files", "*.rhn"), ("all files", "*.*")))
        if (type(self._rhino_model_path) is not tuple) and self._rhino_model_path:
            if '_cortexm_' not in os.path.basename(self._rhino_model_path) or \
                    ('_%s_' % LANGUAGE_TO_CODE[self._language]) not in os.path.basename(self._rhino_model_path):
                messagebox.showwarning(
                    title='warning',
                    message='It seems that the selected model belongs to a '
                            'different platform\language.\n '
                            'Please make sure that the '
                            'right model is chosen before proceeding.')
            raw_name = os.path.basename(self._rhino_model_path).split('_cortexm')[0].split('_')
            rhino_model_name = ' '.join(raw_name[0:-1]) + ' [' + raw_name[-1] + ']'
            rhino_model_name = ' '.join([x.capitalize() for x in rhino_model_name.split()])
            self._selected_models['rhino'] = rhino_model_name
            self._rhino_selected_model_entry.state(["!disabled"])
            self._rhino_selected_model_entry.delete(0, tk.END)
            self._rhino_selected_model_entry.insert(0, rhino_model_name)
            self._rhino_selected_model_entry.state(["disabled"])
            self._upload_models_button.config(text='Upload ⇨', command=self._upload_models)
        else:
            self._rhino_model_path = None
            self._rhino_selected_model_entry.insert(0, '')
            self._upload_models_button.state(["!disabled"])

    def _copy_to_clipboard(self):
        clip = Tk()
        clip.withdraw()
        clip.clipboard_clear()
        clip.clipboard_append(self._uuid)
        clip.destroy()

    def _paste_from_clipboard(self):
        clip = Tk()
        clip.withdraw()
        self._access_key_entry.delete(0, tk.END)
        self._access_key_entry.insert(0, clip.clipboard_get())
        clip.destroy()

    def consume(self, code, payload):
        if code is MessageCode.PV_MESSAGE_CODE_UUID.value[0]:
            self._is_responded = True
            self._uuid = payload
            self.clean()
        elif code is MessageCode.PV_MESSAGE_CODE_HANDSHAKE.value[0]:
            if payload == self._board:
                self._is_connecting_done = True

    def clean(self):
        if self._message_thread:
            self._message_thread.request_disconnect()

    def connection_error(self):
        messagebox.showerror(title='Error', message='Connection to %s was lost' % self._board)
        self.master.draw_upload_firmware_frame()

    def draw_next_frame(self):
        self.clean()
        self.master.draw_control_panel_frame(self._board, self._language, self._selected_models)

    def draw_previous_frame(self):
        self.clean()
        self.master.draw_upload_firmware_frame()


class ControlPanel(tk.Frame, PicoFrame):
    def __init__(self, master, board, language, models):
        tk.Frame.__init__(self, master)

        self._board = board
        self._language = language
        self._ports = None
        self._port = None
        self._serial_driver = None
        self._message_thread = None
        self._is_connecting_done = False
        self._is_responded = False
        self._models = models
        self._rhino_context = None
        self._context_viewer = None
        self._monitoring_center_frame = MonitoringCenter(self, self._board, self._models)
        self._audio_debugging_frame = AudioDebugging(self, self._board)

        self.grid(row=0, column=0, sticky='news')
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.configure(**FRAME_COMMON_PARAMS)

        self._control_notebook = ttk.Notebook(self)
        self._control_notebook.grid(row=0, column=0, columnspan=2, pady=(20, 0), sticky='news')

        self._control_notebook.add(self._monitoring_center_frame, text='Monitoring Center')
        self._monitoring_center_frame.tkraise()
        self._control_notebook.add(self._audio_debugging_frame, text='Audio Debugging')
        self._audio_debugging_frame.tkraise()

        self._back_button = ttk.Button(
            self,
            command=self.draw_previous_frame,
            cursor='hand2',
            style="B.TButton",
            text='⇦ Back'
        )

        self._back_button.grid(row=1, column=0, pady=(5, 20), padx=20, ipady=10, ipadx=10, sticky='sw')

        self._show_context_button = ttk.Button(
            self,
            command=self._context_popup,
            cursor='hand2',
            style="S.TButton",
            text='Show Context...'
        )
        self._show_context_button.grid(row=1, column=1, pady=(5, 20), padx=20, ipady=10, ipadx=10, sticky='se')
        self._show_context_button.state(["disabled"])

        self.master.update_status_bar('Connecting to the board')
        self._update_thread = threading.Thread(target=self._connect)
        self.after(2000, self._update_thread.start)
        self._check_connecting(1)

    def _connect(self):
        for _ in range(SERIAL_CONNECTION_RETRIES):
            for port in serial.tools.list_ports.comports():
                try:
                    self._port = port
                    self._serial_driver = serial.Serial(port=port.device, baudrate=115200)
                    self._message_thread = MessageControlThread(self._serial_driver, port, self)
                    self._message_thread.start_communicate()
                    self._message_thread.send_message("%s 0000000000"
                                                      % MessageCode.PV_MESSAGE_CODE_HANDSHAKE.value[0])
                    sleep(0.5)
                except serial.SerialException:
                    continue
                if self._is_connecting_done:
                    break
                else:
                    self._message_thread.request_disconnect()
            if self._is_connecting_done:
                break

        if not self._is_connecting_done:
            messagebox.showerror(title='Error', message='No serial connection was detected for %s' % self._board)
            self.master.update_status_bar("Selected '%s-%s'" % (self._board, self._language))
            self.master.draw_upload_firmware_frame()

    def _check_connecting(self, n):
        if self._is_connecting_done:
            self.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))
            self.after(200, self._get_context)
        else:
            n = (n + 1) % 10
            self.master.update_status_bar('Connecting to the board  ▏' + '▊' * n + '▁' * (9 - n) + '▕')
            self.after(200, self._check_connecting, n)

    def _get_context(self):
        if not self._is_responded:
            self._message_thread.send_message("%s 0000000000" % MessageCode.PV_MESSAGE_CODE_CONTEXT.value[0])
            self.after(200, self._get_context)

    def _context_popup(self):
        self._context_viewer = tk.Toplevel()
        self._context_viewer.wm_title('%s' % self._models['rhino'])
        self._context_viewer.minsize(300, 200)
        self._context_viewer.grid_rowconfigure(0, weight=1)
        self._context_viewer.grid_columnconfigure(0, weight=1)
        self._context_viewer.option_add('*font', FONT)
        self._context_viewer.config(**FRAME_COMMON_PARAMS)
        context_scrolled_text = scrolledtext.ScrolledText(
            self._context_viewer,
            bg=SOFT_GREY,
            foreground="#000000",
            height=20,
            wrap="word")
        context_scrolled_text.grid(row=0, column=0, padx=10, pady=10, sticky='news')
        context_scrolled_text.insert('end', ' %s\n' % self._rhino_context)
        self._context_viewer.protocol('WM_DELETE_WINDOW', self._context_exit)
        self._show_context_button.state(["disabled"])

    def _context_exit(self):
        self._show_context_button.state(["!disabled"])
        if self._context_viewer is not None:
            self._context_viewer.destroy()
            self._context_viewer = None

    def send_message(self, message):
        self._message_thread.send_message(message)

    def change_button_state(self, state):
        if state == 'normal':
            self._control_notebook.tab(0, state='normal')
            self._back_button.state(["!disabled"])
            self._show_context_button.state(["!disabled"])
        elif state == 'disabled':
            self._control_notebook.tab(0, state='disabled')
            self._back_button.state(["disabled"])
            self._show_context_button.state(["disabled"])

    def invalid_state(self):
        self._control_notebook.tab(1, state='disabled')
        self._show_context_button.state(["disabled"])

    _MONITORING_CENTER_CODES = {
        MessageCode.PV_MESSAGE_CODE_INFO.value[0],
        MessageCode.PV_MESSAGE_CODE_CONTEXT.value[0],
        MessageCode.PV_MESSAGE_CODE_WAKE_DETECTED.value[0],
        MessageCode.PV_MESSAGE_CODE_INFERENCE.value[0],
        MessageCode.PV_MESSAGE_CODE_PORCUPINE_SENSITIVITY.value[0],
        MessageCode.PV_MESSAGE_CODE_RHINO_SENSITIVITY.value[0],
        MessageCode.PV_MESSAGE_CODE_CPU_USAGE.value[0],
        MessageCode.PV_MESSAGE_CODE_VOLUME.value[0],
        MessageCode.PV_MESSAGE_CODE_ERROR.value[0],
        '[DEBUG]',
        '[WARN]',
        '[ERROR]'
    }

    def consume(self, code, payload):
        if code is MessageCode.PV_MESSAGE_CODE_HANDSHAKE.value[0]:
            if payload == self._board:
                self._is_connecting_done = True
        elif code is MessageCode.PV_MESSAGE_CODE_CONTEXT.value[0]:
            self._is_responded = True
            self._rhino_context = payload
            self._show_context_button.state(["!disabled"])
        elif code in self._MONITORING_CENTER_CODES:
            self._monitoring_center_frame.consume(code, payload)
        elif code in [MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0]]:
            self._audio_debugging_frame.consume(code, payload)

    def clean(self):
        if self._message_thread:
            self._message_thread.request_disconnect()

    def connection_error(self):
        messagebox.showerror(title='Error', message='Connection to %s was lost' % self._board)
        self.master.update_status_bar('')
        self.master.draw_upload_firmware_frame()

    def draw_next_frame(self):
        raise NotImplementedError()

    def draw_previous_frame(self):
        self._context_exit()
        self.clean()
        self.master.draw_upload_models_frame(self._board, self._language)


class MonitoringCenter(tk.Frame):
    def __init__(self, master, _, models):
        tk.Frame.__init__(self, master)

        self._old_volume = 0
        self._old_cpu = 0
        self._models = models

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.config(**FRAME_COMMON_PARAMS)

        self._variable_label_frame = tk.LabelFrame(self, text=' Metrics ', foreground='black', **FRAME_COMMON_PARAMS)
        self._variable_label_frame.grid(column=0, row=0, padx=5, pady=5, sticky='news')
        self._variable_label_frame.grid_rowconfigure(0, weight=1)
        self._variable_label_frame.grid_rowconfigure(1, weight=1)
        self._variable_label_frame.grid_columnconfigure(0, weight=0)
        self._variable_label_frame.grid_columnconfigure(1, weight=1)
        self._vu_meter_label = ttk.Label(
            self._variable_label_frame,
            text="Mic:",
            background=FRAME_COMMON_PARAMS['background'])
        self._vu_meter_label.grid(column=0, row=0, padx=(20, 5), sticky='w')
        self._vu_meter_progress_bar = ttk.Progressbar(
            self._variable_label_frame, orient=tk.HORIZONTAL, length=200,
            mode='determinate',
            maximum=100)
        self._vu_meter_progress_bar.grid(row=0, column=1, padx=(5, 20), pady=20, sticky='w')
        self._cpu_usage_label = ttk.Label(
            self._variable_label_frame,
            text="CPU:",
            background=FRAME_COMMON_PARAMS['background'])
        self._cpu_usage_label.grid(row=1, column=0, padx=(20, 5), sticky='w')
        self._cpu_usage_progress_bar = ttk.Progressbar(
            self._variable_label_frame,
            orient=tk.HORIZONTAL,
            length=200,
            mode='determinate',
            maximum=100)
        self._cpu_usage_progress_bar.grid(row=1, column=1, padx=(5, 20), pady=20, sticky='w')

        self._parameter_label_frame = tk.LabelFrame(
            self,
            text=' Parameters ',
            foreground='black', **FRAME_COMMON_PARAMS)
        self._parameter_label_frame.grid(row=0, column=1, padx=5, pady=5, sticky='news')
        self._parameter_label_frame.grid_rowconfigure(0, weight=1)
        self._parameter_label_frame.grid_rowconfigure(1, weight=1)
        self._parameter_label_frame.grid_columnconfigure(0, weight=0)
        self._parameter_label_frame.grid_columnconfigure(1, weight=0)
        self._porcupine_sensitivity_label = ttk.Label(
            self._parameter_label_frame,
            text="Porcupine sensitivity",
            background=FRAME_COMMON_PARAMS['background'])
        self._porcupine_sensitivity_label.grid(row=0, column=0, padx=(20, 5), sticky='w')
        self._porcupine_sensitivity_scale = tk.Scale(self._parameter_label_frame, **SCALE_PARAMS)
        self._porcupine_sensitivity_scale.grid(row=0, column=1, sticky='w')
        self._porcupine_sensitivity_scale.bind("<ButtonRelease-1>", self._update_porcupine_sensitivity)

        self._rhino_sensitivity_label = ttk.Label(
            self._parameter_label_frame,
            text="Rhino sensitivity",
            background=FRAME_COMMON_PARAMS['background'])
        self._rhino_sensitivity_label.grid(row=1, column=0, padx=(20, 5), sticky='w')
        self._rhino_sensitivity_scale = tk.Scale(self._parameter_label_frame, **SCALE_PARAMS)
        self._rhino_sensitivity_scale.grid(row=1, column=1, sticky='w')
        self._rhino_sensitivity_scale.bind("<ButtonRelease-1>", self._update_rhino_sensitivity)

        self._console_label_frame = tk.LabelFrame(
            self,
            text=' Console ',
            foreground='black', **FRAME_COMMON_PARAMS)
        self._console_label_frame.grid(column=0, row=1, columnspan=2, padx=5, pady=5, sticky='news')

        self._console_label_frame.grid_rowconfigure(0, weight=1)
        self._console_label_frame.grid_rowconfigure(1, weight=0)
        self._console_label_frame.grid_columnconfigure(0, weight=1)
        self._console_label_frame.grid_columnconfigure(1, weight=1)
        self._console_label_frame.grid_columnconfigure(2, weight=1)

        self._log_scrolled_text = scrolledtext.ScrolledText(
            self._console_label_frame,
            **SCROLLED_TEXT_COMMON_PARAMS,
            height=5)
        self._log_scrolled_text.grid(row=0, column=0, columnspan=5, pady=10, padx=10, sticky='news')
        self._log_scrolled_text.tag_config('DEBUG', foreground=YELLOW)
        self._log_scrolled_text.tag_config('WARN', foreground=YELLOW)
        self._log_scrolled_text.tag_config('ERROR', foreground=RED)
        self._log_scrolled_text.insert('end', ' %s \"%s\"... \n\n' % ('Listening for ', self._models['porcupine']))
        self._log_scrolled_text.see('end')

        self._clear_button = ttk.Button(
            self._console_label_frame,
            command=lambda: self._log_scrolled_text.delete('1.0', 'end'),
            cursor='hand2',
            style="S.TButton",
            text='Clear Console'
        )

        self._clear_button.grid(row=1, column=1, pady=(0, 5), padx=20, ipadx=10, ipady=10, sticky='n')

    def _update_porcupine_sensitivity(self, _):
        self.master.send_message("%s %.8f" % (MessageCode.PV_MESSAGE_CODE_PORCUPINE_SENSITIVITY.value[0],
                                              self._porcupine_sensitivity_scale.get() / 100))
        self._log_scrolled_text.delete('1.0', 'end')
        self._log_scrolled_text.insert(
            'end',
            ' The porcupine sensitivity has been updated to %d%%\n' % self._porcupine_sensitivity_scale.get())
        self._log_scrolled_text.insert('end', ' %s \"%s\"... \n\n' % ('Listening for ', self._models['porcupine']))
        self._log_scrolled_text.see('end')

    def _update_rhino_sensitivity(self, _):
        self.master.send_message("%s %.8f" % (MessageCode.PV_MESSAGE_CODE_RHINO_SENSITIVITY.value[0],
                                              self._rhino_sensitivity_scale.get() / 100))
        self._log_scrolled_text.delete('1.0', 'end')
        self._log_scrolled_text.insert(
            'end',
            ' The rhino sensitivity has been updated to %d%%\n' % self._rhino_sensitivity_scale.get())
        self._log_scrolled_text.insert('end', ' %s \"%s\"... \n\n' % ('Listening for ', self._models['porcupine']))
        self._log_scrolled_text.see('end')

    def consume(self, code, payload):
        if code == '[DEBUG]':
            self._log_scrolled_text.insert('end', ' %s\n' % payload, 'DEBUG')
            self._log_scrolled_text.see('end')

        elif code == '[WARN]':
            self._log_scrolled_text.insert('end', ' %s\n' % payload, 'WARN')
            self._log_scrolled_text.see('end')

        elif code == '[ERROR]':
            self._log_scrolled_text.insert('end', ' %s\n' % payload, 'ERROR')
            self._log_scrolled_text.see('end')
            self.master.invalid_state()
            self._porcupine_sensitivity_scale.configure(state=tk.DISABLED, takefocus=0)
            self._rhino_sensitivity_scale.configure(state=tk.DISABLED, takefocus=0)
            self._clear_button.state(["disabled"])

        elif code is MessageCode.PV_MESSAGE_CODE_INFO.value[0]:
            pass

        elif code is MessageCode.PV_MESSAGE_CODE_WAKE_DETECTED.value[0]:
            self._log_scrolled_text.delete('1.0', 'end')
            self._log_scrolled_text.insert('end', ' \"%s\" detected ...\n' % self._models['porcupine'])
            self._log_scrolled_text.insert('end', ' Listening for follow-on command ...\n\n')
            self._log_scrolled_text.see('end')

        elif code is MessageCode.PV_MESSAGE_CODE_INFERENCE.value[0]:
            text = payload.strip()
            parts = text.split(";")
            is_understood = parts[0].split(":")[1] == 'true'
            intent = None
            slots = None
            if is_understood:
                intent = parts[1].split(":")[1]
                slots = dict([tuple(x.split(":")) for x in parts[2:]])
            self._log_scrolled_text.insert('end', ' {\n')
            self._log_scrolled_text.insert('end', '   is_understood : %s,\n' % is_understood)
            if is_understood:
                self._log_scrolled_text.insert('end', '   intent : %s,\n' % intent)
                if len(slots) > 0:
                    self._log_scrolled_text.insert('end', '   slots {\n')
                    for k, v in slots.items():
                        pass
                        self._log_scrolled_text.insert('end', '     %s : %s,\n' % (k, v))
                    self._log_scrolled_text.insert('end', '   }\n')
            self._log_scrolled_text.insert('end', ' }\n\n')
            self._log_scrolled_text.insert('end', ' %s \"%s\"... \n\n' % ('Listening for ', self._models['porcupine']))
            self._log_scrolled_text.see('end')

        elif code is MessageCode.PV_MESSAGE_CODE_PORCUPINE_SENSITIVITY.value[0]:
            if payload.isnumeric():
                self._porcupine_sensitivity_scale.set(int(payload))

        elif code is MessageCode.PV_MESSAGE_CODE_RHINO_SENSITIVITY.value[0]:
            if payload.isnumeric():
                self._rhino_sensitivity_scale.set(int(payload))

        elif code is MessageCode.PV_MESSAGE_CODE_CPU_USAGE.value[0]:
            if payload.isnumeric():
                self._cpu_usage_progress_bar['value'] = \
                    (1 - MONITORING_CENTER_SMOOTHING_FACTOR_CPU_USAGE) * int(payload) + \
                    MONITORING_CENTER_SMOOTHING_FACTOR_CPU_USAGE * self._old_cpu
                self._old_cpu = self._cpu_usage_progress_bar['value']

        elif code is MessageCode.PV_MESSAGE_CODE_VOLUME.value[0]:
            try:
                volume_percentage = (
                        (int(payload) - MONITORING_CENTER_VU_METER_MIN_DB) * 100 / (-MONITORING_CENTER_VU_METER_MIN_DB))
                self._vu_meter_progress_bar['value'] = \
                    (1 - MONITORING_CENTER_SMOOTHING_FACTOR_VU_METER) * volume_percentage + \
                    MONITORING_CENTER_SMOOTHING_FACTOR_VU_METER * self._old_volume
                self._old_volume = self._vu_meter_progress_bar['value']
            except ValueError as error:
                log.debug(error)

        elif code is MessageCode.PV_MESSAGE_CODE_ERROR.value[0]:
            self._log_scrolled_text.insert('end', ' %s\n' % payload, 'ERROR')
            self._log_scrolled_text.see('end')
            self.master.invalid_state()
            self._porcupine_sensitivity_scale.configure(state=tk.DISABLED, takefocus=0)
            self._rhino_sensitivity_scale.configure(state=tk.DISABLED, takefocus=0)
            self._clear_button.state(["disabled"])


class AudioDebugging(tk.Frame):
    def __init__(self, master, board):
        tk.Frame.__init__(self, master)

        self._audio_pcm = []
        self._audio_string = None
        self._audio_pcm_single = None
        self._is_downloading = False
        self._board = board

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1, minsize=100)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.config(**FRAME_COMMON_PARAMS)

        self._hint_label_text = tk.StringVar()
        self._hint_label_text.set("")

        self._hint_label = ttk.Label(
            self,
            textvariable=self._hint_label_text,
            background=FRAME_COMMON_PARAMS['background'],
            font=(FONT[0], int(FONT[1] * 1.5)))
        self._hint_label.grid(row=0, column=0, columnspan=3, pady=20, sticky='s')

        self._downloading_label = LoadingAnimation(self)
        self._downloading_label.grid(row=2, column=0, columnspan=3, sticky='ns')

        self._plots_figure = plt.Figure(figsize=(6, 3.5), dpi=100)
        self._plots_figure.patch.set_facecolor(SOFT_GREY)
        self._audio_time_domain_plot = self._plots_figure.add_subplot(211)
        for direction in ["left", "bottom"]:
            self._audio_time_domain_plot.spines[direction].set_position('zero')
        for direction in ["right", "top"]:
            self._audio_time_domain_plot.spines[direction].set_color('none')
        self._audio_time_domain_plot.set_facecolor(SOFT_GREY)
        self._audio_frequency_domain_plot = self._plots_figure.add_subplot(212)
        self._audio_time_domain_plot.set_axis_off()
        self._audio_frequency_domain_plot.set_axis_off()
        self._audio_frequency_domain_plot.set_facecolor(SOFT_GREY)
        self._audio_frequency_domain_plot.set_xlabel('Time (s)')
        self._audio_frequency_domain_plot.set_ylabel('Frequency (Hz)')
        self._spectrogram_canvas = FigureCanvasTkAgg(self._plots_figure, self)
        self._draw_plots()

        self._audio_downloading = ttk.Progressbar(
            self,
            orient=tk.HORIZONTAL,
            length=270,
            mode='determinate',
            maximum=100)

        self._mic_photo = ImageTk.PhotoImage(Image.open(IMAGES['mic']))

        self._get_audio_button = ttk.Button(
            self,
            command=self.audio_get,
            cursor='hand2',
            style="A.TButton",
            text='Record Audio',
            image=self._mic_photo,
            compound='left'
        )

        self._get_audio_button.grid(row=3, column=0, padx=20, pady=(0, 10), ipadx=10, ipady=10, sticky='sw')

        self._floppy_photo = ImageTk.PhotoImage(Image.open(IMAGES['floppy']))

        self._save_button = ttk.Button(
            self,
            command=self.audio_save,
            cursor='hand2',
            style="A.TButton",
            text='Save...',
            image=self._floppy_photo,
            compound='left'
        )
        self._save_button.grid(row=3, column=2, padx=20, pady=(0, 10), ipadx=10, ipady=10, sticky='se')
        self._save_button.state(["disabled"])

    def audio_get(self):
        self._save_button.state(["disabled"])
        self._get_audio_button.state(["disabled"])
        self.master.change_button_state('disabled')
        self._spectrogram_canvas.get_tk_widget().grid_forget()
        self._hint_label.grid(row=0, column=0, columnspan=3, pady=20, sticky='s')
        self._downloading_label.grid(row=1, column=0, columnspan=3, sticky='ns')
        self._is_downloading = True
        self.update_status_bar_recording(5)

    def update_status_bar_recording(self, n):
        text = 'Prepare for audio recording in'
        self._hint_label_text.set('%s %d s' % (text, n))
        n = n - 1
        if self._is_downloading:
            if n < 0:

                self.master.send_message("%s 0000000000" % MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0])
                self.master.master.update_status_bar('Recording ...')
                self._hint_label_text.set('%s is now recording your voice ...' % self._board)
                self.after(AUDIO_DEBUG_RECORD_DURATION_SEC[self._board] * 1000, self.update_status_bar_downloading, 0)
                self.after(AUDIO_DEBUG_RECORD_DURATION_SEC[self._board] * 1000, self._downloading_label.start_loading)
            else:
                self.after(1000, self.update_status_bar_recording, n)
        else:
            self.master.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))

    def update_status_bar_downloading(self, n):
        self._audio_downloading.grid(row=1, column=0, columnspan=3, padx=20, pady=5, sticky='n')
        text = 'Downloading audio:'
        self.master.master.update_status_bar('Please wait ...')
        self._hint_label_text.set('%s %d' % (text, min(math.floor(n / 10) * 10, 100)) + '%')
        self._audio_downloading.tkraise()
        self._audio_downloading['value'] = n
        n = n + 1
        if self._is_downloading:
            self.after(AUDIO_DEBUG_RECORD_DURATION_SEC[self._board] * 70, self.update_status_bar_downloading, n)
        else:
            self._audio_downloading.grid_forget()
            self._downloading_label.stop_loading()
            self._downloading_label.grid_forget()
            self._hint_label.grid_forget()
            self._spectrogram_canvas.get_tk_widget().grid(
                row=0,
                column=0,
                rowspan=3,
                columnspan=3,
                pady=(0, 10),
                sticky='news')
            self.master.master.update_status_bar("Connected to '%s-%s'" % (self._board, self._language))

    def _audio_set(self, pcm_string):
        self._audio_string = pcm_string.strip('\n').split(' ')
        self._audio_pcm = []
        for a in self._audio_string:
            self._audio_pcm.append(BitArray('0x' + a).int)
        self._audio_pcm_single = np.array(self._audio_pcm).astype(np.single)
        self._save_button.state(["!disabled"])
        self._get_audio_button.state(["!disabled"])

        self._is_downloading = False
        self.master.change_button_state('normal')

    def _draw_plots(self):
        if self._audio_pcm_single is not None:
            self._audio_time_domain_plot.clear()
            for direction in ["right", "top", "bottom"]:
                self._audio_time_domain_plot.spines[direction].set_color('none')
            self._audio_time_domain_plot.plot(np.array(self._audio_pcm).astype(np.int16) / (2 ** 15), linewidth=0.5)
            self._audio_time_domain_plot.axes.get_xaxis().set_visible(False)
            self._audio_time_domain_plot.set_ylim(-1, 1)
            self._audio_time_domain_plot.set_xlim(0, len(self._audio_pcm) - 1)
            self._audio_frequency_domain_plot.specgram(
                self._audio_pcm_single,
                NFFT=AUDIO_DEBUG_FFT_WINDOW_SIZE,
                Fs=AUDIO_DEBUG_SAMPLING_FREQUENCY,
                noverlap=AUDIO_DEBUG_FFT_OVERLAP,
                scale='dB')
            self._audio_frequency_domain_plot.set_axis_on()
            self._spectrogram_canvas.draw()
            self._audio_pcm_single = None
        self.after(100, self._draw_plots)

    def audio_save(self):
        filename = filedialog.asksaveasfilename(filetypes=[("wav files", '*.wav')])
        if filename:
            if os.access(os.path.dirname(filename), os.W_OK):
                pcm_to_wave(self._audio_pcm, filename)
            else:
                messagebox.showerror(
                    title='Error',
                    message='You don\'t have permission to save in \"%s\"' % os.path.dirname(filename))

    def consume(self, code, payload):
        if code is MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0]:
            self._audio_set(payload)


class MessageControlThread(threading.Thread):
    def __init__(self, serial_driver, port, consumer):
        threading.Thread.__init__(self, daemon=True)

        self._consumer = consumer
        self._driver = serial_driver
        self._port = port
        self._stop_thread = False
        self._stop_serial = False
        self._is_serial_stopped = False

    def change_consumer(self, new_consumer):
        if self._driver.isOpen():
            self._driver.reset_input_buffer()
            self._driver.reset_output_buffer()
        self._consumer = new_consumer

    def request_disconnect(self):
        log.debug('Closing the serial port...')
        self._stop_thread = True
        self._stop_serial = True
        self._driver.close()
        while self._driver.isOpen():
            pass
        log.debug('The serial port is closed')

    def request_stop(self):
        log.debug('Closing the serial port...')
        self._stop_serial = True
        self._driver.close()
        while self._driver.isOpen() or not self._is_serial_stopped:
            pass
        log.debug('The serial port is closed')

    def send_message(self, text):
        try:
            self._driver.write(text.encode())
        except serial.serialutil.PortNotOpenError as error:
            log.debug(error)
            self._driver = serial.Serial(port=self._port.device, baudrate=115200)
            self._driver.reset_input_buffer()
            self._driver.reset_output_buffer()

    def start_communicate(self):
        self._driver.reset_input_buffer()
        self._driver.reset_output_buffer()
        self.start()

    def _reset(self):
        self.request_stop()
        self._driver = serial.Serial(port=self._port.device, baudrate=115200)
        self._driver.reset_input_buffer()
        self._driver.reset_output_buffer()
        log.debug('resetting the serial connection')
        self._stop_serial = False

    def run(self):
        message = ''
        while not self._stop_thread:
            while not self._stop_serial:
                try:
                    if self._driver.in_waiting > 0:
                        try:
                            message += self._driver.readline().decode('utf-8')
                            if len(message) > 2:
                                if message[-2] == '\r' and message[-1] == '\n':
                                    self._process_message(message[:-2])
                                    message = ''
                        except UnicodeDecodeError as error:
                            log.debug(error)
                            message = ''
                        except serial.serialutil.SerialException as error:
                            log.debug(error)
                            self._reset()
                            message = ''
                except TypeError as error:
                    log.debug(error)
                    message = ''
                except OSError as error:
                    message = ''
                    log.debug('The serial connection was lost with', error)
                    self._stop_thread = True
                    self._stop_serial = True
                    if self._consumer is not None:
                        self._consumer.connection_error()
            self._is_serial_stopped = True

    def _process_message(self, text):
        if text.startswith('[DEBUG]'):
            code = '[DEBUG]'
            message_context = text[8:]
        elif text.startswith('[WARN]'):
            code = '[WARN]'
            message_context = text[7:]
        elif text.startswith('[ERROR]'):
            code = '[ERROR]'
            message_context = text[8:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_HANDSHAKE.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_HANDSHAKE.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_CONTEXT.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_CONTEXT.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_WAKE_DETECTED.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_WAKE_DETECTED.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_INFERENCE.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_INFERENCE.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_PORCUPINE_SENSITIVITY.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_PORCUPINE_SENSITIVITY.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_RHINO_SENSITIVITY.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_RHINO_SENSITIVITY.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_VOLUME.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_VOLUME.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_CPU_USAGE.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_CPU_USAGE.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_UUID.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_UUID.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_AUDIO_DUMP.value[0]
            message_context = text[5:]
        elif text.startswith(MessageCode.PV_MESSAGE_CODE_ERROR.value[0]):
            code = MessageCode.PV_MESSAGE_CODE_ERROR.value[0]
            message_context = text[5:]
        else:
            code = None
            message_context = None

        if code and message_context and self._consumer:
            self._consumer.consume(code, message_context)


class LoadingAnimation(ttk.Label):
    def __init__(self, master):
        ttk.Label.__init__(self, master)
        self.config(borderwidth=1, relief=tk.FLAT, background=FRAME_COMMON_PARAMS['background'])
        self._frame_count = 160
        self._frames = [tk.PhotoImage(file=IMAGES['loading_animation'],
                                      format='gif -index %i' % i) for i in range(self._frame_count)]

        self._is_loading = False
        self._is_stopped = False

    def _update(self, n):
        frame = self._frames[n]
        n += 1
        if n == self._frame_count:
            n = 0
        self.configure(image=frame)
        if self._is_loading:
            self.master.after(20, self._update, n)
        else:
            self.configure(image=self._frames[self._frame_count - 1])
            self._is_stopped = True

    def stop_loading(self):
        self._is_loading = False

    def is_stopped(self):
        return self._is_stopped

    def start_loading(self):
        self._is_loading = True
        self._update(0)
        self.configure(image=self._frames[0])


def are_rules_copied():
    existing = set([x for x in os.listdir('/etc/udev/rules.d') if x.endswith('.rules')])

    for x in os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/nxp/linux/rules')):
        if x.endswith('.rules'):
            if x not in existing:
                return False

    for x in os.listdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/st/linux/rules')):
        if x.endswith('.rules'):
            if x not in existing:
                return False

    return True


def copy_rules():
    print("We need root access to make changes required for connection to the boards. This is a one time setup.")
    command = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'thirdparty/rules/udev-rules-install.sh')
    if not subprocess.run(command, shell=True, stderr=subprocess.STDOUT).returncode == 0:
        raise RuntimeError("failed to make required changes")
    else:
        print("Performed required changes.")


def main():
    if platform.system() == 'Linux':
        if not are_rules_copied():
            copy_rules()

    app = PicovoiceApp()
    try:
        app.mainloop()
    except Exception as error:
        log.debug('failed without catching any errors')
        log.debug(error)


if __name__ == "__main__":
    main()
