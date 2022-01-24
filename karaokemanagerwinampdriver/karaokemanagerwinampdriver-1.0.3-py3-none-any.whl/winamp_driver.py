from os import startfile, path
from win32ui import FindWindowEx
from win32api import SendMessage
from time import sleep
import threading
import ctypes

WM_APP = 0x8000
WM_USER = 0x0400
PM_SET_PITCH = WM_APP+7
WM_COPYDATA = 0x004A
WM_WA_IPC = WM_USER
IPC_PLAYFILEW = 1100
IPC_DELETE = 101
IPC_STARTPLAY = 102

class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ('dwData', ctypes.wintypes.LPARAM),
        ('cbData', ctypes.wintypes.DWORD),
        ('lpData', ctypes.c_wchar_p) # Really LPVOID, but we only wanna use strings.
    ]

class Driver:
	def __init__(self, config):
		exe_path=config.get("exe")
		if not exe_path is None:
			if path.exists(exe_path):
				startfile(exe_path)

	def play_karaoke_file(self, karaoke_file, key_change, errors):
		winamp_window=FindWindowEx(None,None, "Winamp v1.x", None)
		if winamp_window is None:
			errors.append("Cannot find Winamp window.")
			return
		winamp_hwnd=winamp_window.GetSafeHwnd()
		copy_data = COPYDATASTRUCT()
		copy_data.dwData = IPC_PLAYFILEW
		absolute_path=path.abspath(karaoke_file)
		absolute_path_pointer=ctypes.c_wchar_p(absolute_path)
		copy_data.cbData = (len(absolute_path)+1)*2 # Include null-terminator, and it's two bytes per character.
		copy_data.lpData = absolute_path_pointer
		SendMessage(winamp_hwnd, WM_WA_IPC, 0, IPC_DELETE)
		SendMessage(winamp_hwnd, WM_COPYDATA, 0, memoryview(copy_data))
		SendMessage(winamp_hwnd, WM_WA_IPC, 0, IPC_STARTPLAY)
		pacemaker_window=FindWindowEx(None, None, None, "PaceMaker Plug-in")
		if pacemaker_window is None:
			errors.append("Could not find PaceMaker window.")
		else:
			# Run a thread. We can't just set it once, cos the timing between
			# Pacemaker resetting itself when a new file starts, and us sending
			# this message to set a value, is too tight. We will set it once
			# every second for the next five seconds.
			# Can't pass the Pacemaker window object through, it gets sniffy
			# about thread contexts, so just use the raw HWND.
			pacemaker_hwnd=pacemaker_window.GetSafeHwnd()
			key_change_thread = threading.Thread(
				target=apply_key_change, args=(pacemaker_hwnd,key_change,5,))
			key_change_thread.daemon = True
			key_change_thread.start()

# Sends the PM_SET_PITCH message to the PaceMaker window (if available) to set
# the correct key change to whatever the user requested for a particular song.
def apply_key_change(pacemaker_hwnd,key_change,count):
	for _ in range(count):
		sleep(1)
		SendMessage(pacemaker_hwnd,PM_SET_PITCH,0,key_change*1000)
