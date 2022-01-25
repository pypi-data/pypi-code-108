#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
#
# pc_utils.py: helper functions for dealing with keyboard, screen, network, OS
import os
import sys
import time
import socket 

from xtlib import console
from xtlib import constants

# ESCAPE CODES FOR SCREEN
#reference: https://www.codeproject.com/Tips/5255355/How-to-Put-Color-on-Windows-Console

# special actions
CLEAR_LINE = "\033[K"
CURSOR_UP = "\033[F"

# foreground colors
NORMAL = "\033[0m"
BOLD = "\033[1m"

UNDERLINE = "\033[1;4m"
NOUNDERLINE = "\033[1;24m"
NEGATIVE = "\033[1;7m"
POSITIVE = "\033[1;27m"

BLACK = "\033[1;30m"
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
GRAY = "\033[0;37m"         # default color

COLORS = [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, GRAY]

LIGHTRED = "\033[1;91m"
LIGHTGREEN = "\033[1;92m"
LIGHTYELLOW = "\033[1;93m"
LIGHTBLUE = "\033[1;94m"
LIGHTMAGENTA = "\033[1;95m"
LIGHTCYAN = "\033[1;96m"
DARKGRAY = "\033[1;90m"
WHITE = "\033[1;97m"

LIGHT_COLORS = [LIGHTRED, LIGHTGREEN, LIGHTYELLOW, LIGHTBLUE, LIGHTMAGENTA, LIGHTCYAN, DARKGRAY, WHITE]

def is_windows():   
    return os.name == "nt"

def has_gui():
    gui = is_windows() or os.environ.get('DISPLAY')
    return gui

def get_conda_env():
    conda_env = os.getenv("CONDA_DEFAULT_ENV")
    #console.print("conda_env=", conda_env)
    return conda_env

def get_kernel_display_name(kernel_name):
    from jupyter_client.kernelspecapp import KernelSpecManager
    specs = KernelSpecManager().find_kernel_specs()

    kernel_name = kernel_name.lower()
    if not kernel_name in specs:
        kernel_name = list(specs.keys())[0]

    dir_name = specs[kernel_name]
    path = dir_name + "/kernel.json"
    with open(path, "rt") as infile:
        text = infile.read()
    data = json.loads(text)
    return data["display_name"]

def get_hostname():
    return socket.gethostname().lower()

def get_username():
    ev_user = "username" if is_windows() else "user"
    username = os.getenv(ev_user)
    username = username if username else ""
    return username

def is_localhost(box_name=None, box_addr=None):
    is_local = False
    if not box_addr:
        box_addr = box_name

    if box_addr:
        box_addr = box_addr.lower()

        if "@" in box_addr:
            box_addr = box_addr.split("@")[1]

        host_ip = get_ip_address()
        host_name = get_hostname().lower()
    
        is_local = box_addr in ["local", "localhost", host_name, "127.0.0.1", host_ip]

    return is_local

def old_get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip  

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def make_text_display_safe(text):
    tbytes = text.encode(sys.stdout.encoding, errors='replace')
    text = tbytes.decode("utf-8", "replace")
    return text

def enable_ansi_escape_chars_on_windows_10():
    import ctypes

    if is_windows():
        #console.print("***** enabling ESCAPE CHARS on screen *******")
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

def expand_vars(text):
    if is_windows():
        text = text.replace("${HOME}", "${userprofile}")

    text = os.path.expandvars(text)
    return text

def input_with_default(prompt, default, dim_prompt=True, use_gray=False):
    ''' this shows the prompt in gray text and the default in normal text '''
    if is_windows():
        # WINDOWS
        import win32console
        _stdin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)
        keys = []
        for c in default:
            evt = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
            evt.Char = c
            evt.RepeatCount = 1
            evt.KeyDown = True
            keys.append(evt)

        _stdin.WriteConsoleInput(keys)

        if dim_prompt:
            enable_ansi_escape_chars_on_windows_10()
            value = input(DARKGRAY + prompt + GRAY)
        else:
            value = input(prompt)

    else:
        # LINUX
        import readline
        readline.set_startup_hook(lambda: readline.insert_text(default))
        try:
            value = input(prompt)  
        finally:
            readline.set_startup_hook()

    return value

def move_cursor_up(line_count, clear_lines=True):
    # if clear_lines:
    #     # clear current line
    #     sys.stdout.write("\r\033[K") 

    for _ in range(line_count):
        sys.stdout.write(CURSOR_UP) 
        if clear_lines:
            # clear line we just moved into
            sys.stdout.write(CLEAR_LINE) 

def highlight(text):
    sys.stdout.write(WHITE)
    print(text)
    sys.stdout.write(NORMAL)

def clear_line():
    sys.stdout.write(CLEAR_LINE) 

def wait_for_escape(checker, wait_time=1, check_time=.1):
    ''' 
    for this to work, it must be run inside of a
    "with KeyPressChecker() as checker:" type block
    '''

    found_escape = False
    checks = int(wait_time/check_time)  

    for check in range(checks):
        if checker.getch_nowait() == constants.ESCAPE:
            found_escape = True
            break
        time.sleep(check_time)

    return found_escape

def input_response(prompt, response):
    if response:
        console.print(prompt + response)
    else:
        response = input(prompt)

    return response

def is_compute_node():
    return bool(os.getenv("XT_STORE_CREDS"))

def is_xt_run():
    return bool(os.getenv("XT_IS_RUN"))
