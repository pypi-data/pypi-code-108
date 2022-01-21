import os
import time

try:
    if os.name == "nt":    
        import ctypes
        import ctypes.wintypes
except:
    pass


class _Getch:
    """Gets a single character from standard input. Does not echo to
    the screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, old_settings) # TCSADRAIN
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()


KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEY_NAMES = [
    "\t", "\n", "\r", " ", "!", '"', "#", "$", "%", "&", "'", "(", ")", "*",
    "+", ",", "-", ".", "/", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    ":", ";", "<", "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", 
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o",
    "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "{", "|", "}", "~",
    "accept", "add", "alt", "altleft", "altright", "apps", "backspace",
    "browserback", "browserfavorites", "browserforward", "browserhome",
    "browserrefresh", "browsersearch", "browserstop", "capslock", "clear",
    "convert", "ctrl", "ctrlleft", "ctrlright", "decimal", "del", "delete",
    "divide", "down", "end", "enter", "esc", "escape", "execute", "f1", "f10",
    "f11", "f12", "f13", "f14", "f15", "f16", "f17", "f18", "f19", "f2",
    "f20", "f21", "f22", "f23", "f24", "f3", "f4", "f5", "f6", "f7", "f8",
    "f9", "final", "fn", "hanguel", "hangul", "hanja", "help", "home",
    "insert", "junja", "kana", "kanji", "launchapp1", "launchapp2",
    "launchmail", "launchmediaselect", "left", "modechange", "multiply",
    "nexttrack", "nonconvert", "num0", "num1", "num2", "num3", "num4", "num5",
    "num6", "num7", "num8", "num9", "numlock", "pagedown", "pageup", "pause",
    "pgdn", "pgup", "playpause", "prevtrack", "print", "printscreen",
    "prntscrn", "prtsc", "prtscr", "return", "right", "scrolllock", "select",
    "separator", "shift", "shiftleft", "shiftright", "sleep", "space", "stop",
    "subtract", "tab", "up", "volumedown", "volumemute", "volumeup", "win",
    "winleft", "winright", "yen", "command", "option", "optionleft",
    "optionright",
]
keyboardMapping = dict([(key, None) for key in KEY_NAMES])
keyboardMapping.update({
    'backspace': 0x08, # VK_BACK
    '\b': 0x08, # VK_BACK
    'super': 0x5B, #VK_LWIN
    'tab': 0x09, # VK_TAB
    '\t': 0x09, # VK_TAB
    'clear': 0x0c, # VK_CLEAR
    'enter': 0x0d, # VK_RETURN
    '\n': 0x0d, # VK_RETURN
    'return': 0x0d, # VK_RETURN
    'shift': 0x10, # VK_SHIFT
    'ctrl': 0x11, # VK_CONTROL
    'alt': 0x12, # VK_MENU
    'pause': 0x13, # VK_PAUSE
    'capslock': 0x14, # VK_CAPITAL
    'esc': 0x1b, # VK_ESCAPE
    'escape': 0x1b, # VK_ESCAPE
    'accept': 0x1e, # VK_ACCEPT
    ' ': 0x20, # VK_SPACE
    'space': 0x20, # VK_SPACE
    'end': 0x23, # VK_END
    'left': 0x25, # VK_LEFT
    'up': 0x26, # VK_UP
    'right': 0x27, # VK_RIGHT
    'down': 0x28, # VK_DOWN
    'select': 0x29, # VK_SELECT
    'insert': 0x2d, # VK_INSERT
    'del': 0x2e, # VK_DELETE
    'delete': 0x2e, # VK_DELETE
    'win': 0x5b, # VK_LWIN
    'winleft': 0x5b, # VK_LWIN
    'winright': 0x5c, # VK_RWIN
    'num0': 0x60, # VK_NUMPAD0
    'num1': 0x61, # VK_NUMPAD1
    'num2': 0x62, # VK_NUMPAD2
    'num3': 0x63, # VK_NUMPAD3
    'num4': 0x64, # VK_NUMPAD4
    'num5': 0x65, # VK_NUMPAD5
    'num6': 0x66, # VK_NUMPAD6
    'num7': 0x67, # VK_NUMPAD7
    'num8': 0x68, # VK_NUMPAD8
    'num9': 0x69, # VK_NUMPAD9
    'multiply': 0x6a, # VK_MULTIPLY  ??? Is this the numpad *?
    'add': 0x6b, # VK_ADD  ??? Is this the numpad +?
    'separator': 0x6c, # VK_SEPARATOR  ??? Is this the numpad enter?
    'subtract': 0x6d, # VK_SUBTRACT  ??? Is this the numpad -?
    'decimal': 0x6e, # VK_DECIMAL
    'divide': 0x6f, # VK_DIVIDE
    'numlock': 0x90, # VK_NUMLOCK
    'shiftleft': 0xa0, # VK_LSHIFT
    'shiftright': 0xa1, # VK_RSHIFT
    'ctrlleft': 0xa2, # VK_LCONTROL
    'ctrlright': 0xa3, # VK_RCONTROL
    'altleft': 0xa4, # VK_LMENU
    'altright': 0xa5, # VK_RMENU
})

try: # TODO: add support for other platforms
    if os.name == "nt":
        for c in range(32, 128):
            keyboardMapping[chr(c)] = ctypes.windll.user32.VkKeyScanA(
                ctypes.wintypes.WCHAR(chr(c))
            )
except:
    pass


def isShiftCharacter(character: str) -> str:
    """Returns True if the character is a keyboard key that would
    require the shift key to be held down, such as uppercase letters or
    the symbols on the keyboard's number row.
    """
    return character.isupper() or character in set('~!@#$%^&*()_+{}|:"<>?')


def _keyDown(key: str) -> None:
    """Performs a keyboard key press without the release. This will put
    that key in a held down state.

    Args:
        key (str): The key to be pressed down. The valid names are
            listed in pyautogui.KEY_NAMES.
    """
    if key not in keyboardMapping or keyboardMapping[key] is None:
        return
    needsShift = isShiftCharacter(key)
    mods, vkCode = divmod(keyboardMapping[key], 0x100)
    for apply_mod, vk_mod in [(mods & 4, 0x12), (mods & 2, 0x11),
        (mods & 1 or needsShift, 0x10)]: 
        if apply_mod:
            ctypes.windll.user32.keybd_event(vk_mod, 0, KEYEVENTF_KEYDOWN, 0)
    ctypes.windll.user32.keybd_event(vkCode, 0, KEYEVENTF_KEYDOWN, 0)
    for apply_mod, vk_mod in [
        (mods & 1 or needsShift, 0x10), (mods & 2, 0x11), (mods & 4, 0x12)
    ]:
        if apply_mod:
            ctypes.windll.user32.keybd_event(vk_mod, 0, KEYEVENTF_KEYUP, 0)


def _keyUp(key: str) -> None:
    """Performs a keyboard key release (without the press down
    beforehand).
    
    Args:
        key (str): The key to be released up. The valid names are
            listed in KEY_NAMES.
    """
    if key not in keyboardMapping or keyboardMapping[key] is None:
        return
    needsShift = isShiftCharacter(key)
    mods, vkCode = divmod(keyboardMapping[key], 0x100)
    for apply_mod, vk_mod in [(mods & 4, 0x12), (mods & 2, 0x11),
        (mods & 1 or needsShift, 0x10)]: 
        if apply_mod:
            ctypes.windll.user32.keybd_event(vk_mod, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vkCode, 0, KEYEVENTF_KEYUP, 0)
    for apply_mod, vk_mod in [
        (mods & 1 or needsShift, 0x10), (mods & 2, 0x11), (mods & 4, 0x12)
    ]:
        if apply_mod:
            ctypes.windll.user32.keybd_event(vk_mod, 0, KEYEVENTF_KEYUP, 0)


def press(keys, presses=1, interval=0.0, _pause=True):
    """Performs a keyboard key press down, followed by a release.
    
    Args:
        key (str, list): The key to be pressed. Valid names are listed
            in KEYBOARD_KEYS. Can also be a list of such strings.
        presses (integer, optional): The number of press repetitions. 1
            by default, for just one press.
        interval (float, optional): How many seconds between each
            press. 0.0 by default, for no pause between presses.
        pause (float, optional): How many seconds in the end of
            function process.
    
    Returns:
        None
    """
    if type(keys) == str:
        if len(keys) > 1:
            keys = keys.lower()
        keys = [keys] # If keys is 'enter', convert it to ['enter'].
    else:
        lowerKeys = []
        for s in keys:
            if len(s) > 1:
                lowerKeys.append(s.lower())
            else:
                lowerKeys.append(s)
        keys = lowerKeys
    interval = float(interval)
    for _ in range(presses):
        for k in keys:
            _keyDown(k)
            _keyUp(k)
        time.sleep(interval)


def typewrite(message, interval=0.0, _pause=True) -> None:
    """Performs a keyboard key press down, followed by a release, for
    each of the characters in message.
    The message argument can also be list of strings, in which case
    any valid keyboard name can be used.
    Since this performs a sequence of keyboard presses and does not
    hold down keys, it cannot be used to perform keyboard shortcuts.
    
    Args:
        message (str, list): If a string, then the characters to be
            pressed. If a list, then the key names of the keys to press
            in order. The valid names are listed in KEYBOARD_KEYS.
        interval (float, optional): Seconds in between each press. 0.0
            by default, for no pause in between presses.
    """
    interval = float(interval)  # TODO - this should be taken out.
    for c in message:
        if len(c) > 1:
            c = c.lower()
        press(c, _pause=False)
        time.sleep(interval)


class Keyboard:
    """Keys pressed by the user.
    """
    
    UP = b'H' if os.name == 'nt' else 65 #b'\x1b[A'
    DOWN = b'P' if os.name == 'nt' else 66 #b'\x1b[B'
    LEFT = b'K' if os.name == 'nt' else b'\x1b[D'
    RIGHT = b'M' if os.name == 'nt' else b'\x1b[C'
    ENTER = b'\r' if os.name == 'nt' else b'\n'
    bENTER = b'\r'
    ENTER = 13 if os.name == 'nt' else 10
    ESC = 27
    BACKSPACE = (8, 127)
    bBACKSPACE = b'\x08\x7f'
    SPECIAL_KEYS = (224, 0) if os.name == 'nt' else (27, 91)

    @classmethod
    def action(cls, key_pressed):
        """Action done by the user."""
        return {
            cls.UP : "UP",
            cls.DOWN : "DOWN",
            cls.LEFT : "LEFT",
            cls.RIGHT : "RIGHT",
        }[key_pressed]


def arrow_position(position: int, size: int, event: str) -> int:
    """Returns the position of the element selected.

    Args:
        position (int): Current position.
        size (int): Size of the items (menu).
        event (str): Keyboard event.

    Returns:
        int: Position of the menu item.
    """
    if event == "DOWN" or event == "j":
        if position == 0:
            position += 1
        elif 0 < position < size - 1:
            position += 1
        elif position == size - 1:
            position = 0
    elif event == "UP" or event == "k":
        if position == size - 1:
            position -= 1
        elif 0 < position < size - 1:
            position  -=1
        elif position == 0:
            position = size - 1
    else:
        return 0
    return position