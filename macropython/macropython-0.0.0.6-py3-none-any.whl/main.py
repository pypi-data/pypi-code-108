import threading
import pynput, time, os
from .classes import _Data
from .mouse_functions import on_mouse_click, on_mouse_move, on_mouse_scroll
from .keyboard_functions import on_keyboard_press, on_keyboard_release
from .misc_functions import save_file, load_file


KEYBOARD_ACTIONS = ["press_key", "release_key"]
MOUSE_ACTIONS = ["mouse_press", "mouse_release", "mouse_move", "mouse_scroll"]
SPECIAL_KEYS = {'Key.' + key: eval(f"pynput.keyboard.Key.{key}") for key in dir(pynput.keyboard.Key)}

class RecordMacro:
    def __init__(self, _filename: str = "My Macro.txt", _startup_delay: float = 5, _enable_output: bool = True):
        if not os.path.exists(_filename): self.filename = _filename # path to file to save to
        else: raise FileExistsError(f"file '{_filename}' already exists")

        if _startup_delay > 0: self.startup_delay = _startup_delay
        else: raise ValueError(f"argument '_startup_delay' must be a positive float.")

        self.macro_data: list[_Data] = []
        self.keyboard_listener = None
        self.mouse_listener = None

        self.enable_output = _enable_output

    def logic(self, stuff: dict | bool):
        if stuff == False:
            try: self.keyboard_listener.stop()
            except: pass

            try: self.mouse_listener.stop()
            except: pass

            return stuff
        else:
            self.macro_data.append(_Data(**stuff))


    def start(self, startup_delay: float = None):
        if self.enable_output: print(f"waiting {self.startup_delay} before recording")
        time.sleep(startup_delay or self.startup_delay) # wait startup_delay before recording
        if self.enable_output: print(f"recording started. press Escape key to exit")

        self.keyboard_listener = pynput.keyboard.Listener(
            on_press = lambda key: self.logic(on_keyboard_press(key)),
            on_release = lambda key: self.logic(on_keyboard_release(key))
        ) # thread that listens to keyboard inputs

        self.mouse_listener = pynput.mouse.Listener(
            on_click = lambda x, y, button, pressed: self.logic(on_mouse_click(x, y, button, pressed)),
            on_scroll = lambda x, y, dx, dy: self.logic(on_mouse_scroll(x, y, dx, dy)),
            on_move = lambda x, y: self.logic(on_mouse_move(x, y))
        ) # thread that listens to your mouse actions

        start_time = time.time()

        self.keyboard_listener.start()
        self.mouse_listener.start()
        self.keyboard_listener.join()
        self.mouse_listener.join()

        if self.macro_data == []:
            if self.enable_output: print("No Data To Save")

        else:
            _save_data = [d._to_dict() for d in self.macro_data]

            for i in range(len(_save_data)):
                _d = _save_data[i]
                _save_data[i]['time'] = _d['time'] - start_time

            if self.enable_output: print(f"Saving {len(_save_data)} Inputs")
            save_file(self.filename, _save_data)
            if self.enable_output: print(f"Saved {len(_save_data)} Inputs")

class PlayMacro:
    def __init__(self, _filename: str = "My Macro.txt", _startup_delay: float = 5, _enable_output: bool = False):
        if os.path.exists(_filename): self.filename = _filename
        else: raise FileNotFoundError(f"file '{_filename}' does not exist.")

        if _startup_delay > 0: self.startup_delay = _startup_delay
        else: raise ValueError(f"argument '_startup_delay' must be a positive float.")

        self.mouse_controller = None
        self.keyboard_controller = None

        self.enable_output = _enable_output

    def start(self, startup_delay: float = None):
        delay = startup_delay or self.startup_delay
        if self.enable_output: print(f"waiting {startup_delay} before playing macro '{self.filename}'.")
        time.sleep(delay)
        if self.enable_output: print(f"playing macro '{self.filename}'.")

        self.mouse_controller = pynput.mouse.Controller()
        self.keyboard_controller = pynput.keyboard.Controller()

        _before = None
        _current = None
        _future = None

        _data: list[_Data] = [_Data(**action) for action in load_file(self.filename)]

        action_len = len(_data)-1

        for i in range(action_len):
            
            if not i == action_len: _future: _Data = _data[i+1]
            if not i == 0: _before: _Data = _data[i-1]
            _current: _Data = _data[i]

            if _current.action in KEYBOARD_ACTIONS:
                key = _current.key if not "Key." in _current.key else SPECIAL_KEYS[_current.key]

                if _current.action == "press_key":
                    self.keyboard_controller.press(key)

                elif _current.action == "release_key":
                    self.keyboard_controller.release(key)

            elif _current.action in MOUSE_ACTIONS:
                if _current.action in ["mouse_press", "mouse_release"]:
                    button = pynput.mouse.Button.left if _current.button == "Button.left" else pynput.mouse.Button.right

                if _current.action == "mouse_move":
                    self.mouse_controller.position = (_current.x, _current.y)
                
                elif _current.action == "mouse_press":
                    self.mouse_controller.press(button)
                
                elif _current.action == "mouse_release":
                    self.mouse_controller.release(button)

                elif _current.action == "mouse_scroll":
                    self.mouse_controller.scroll(_current.dx, _current.dy)

            else:
                print(f"unknown action '{_current.action}'.")

            if not _future == None:
                time.sleep(_future.time - _current.time)

class HotKeyMacro:
    """
    _data is a ``list`` of ``dict``

    the ``dict``s inside _data is structured as shown below

    {
        'trigger' : ``str`` - the key that starts the macro

        'file' : ``str`` - the location of the macro

        'repeat_forever' : ``bool`` - repeat the macro forever until the trigger is released
            ~ note: if set to False, the macro will only once when the trigger is pressed

        'repeat_delay' : ``float`` - time to wait before repeating the macro again
            ~ note: will only wait if repeat_forever is set to True
    }
    """


    def __init__(self, _data, _startup_delay: float = 5, _enable_output: bool = False):
        if _startup_delay > 0: self.startup_delay = _startup_delay
        else: raise ValueError(f"argument '_startup_delay' must be a positive float.")
        self._data: list[_Data] = []
        self.activate_keys: dict[str, list[int]] = {}
        for i in range(len(_data)):
            _d = _data[i]
            print(_d)

            if not os.path.exists(_d['file']):
                raise FileNotFoundError(f"file '{_d['file']}' does not exist.")

            if _d['trigger'] in self.activate_keys:
                self.activate_keys[_d['trigger']].append(i)
            else:
                self.activate_keys[_d['trigger']] = [i]

            _d['playing'] = False
            _d['stop'] = False
            _d['isheld'] = False

            self._data.append(_Data(**_d))

        self.mouse_controller = None
        self.keyboard_controller = None
        self.keyboard_listener = None
        self._threads: list[threading.Thread] = []

        self.enable_output = _enable_output

        print(self.activate_keys)

    def logic(self, stuff: dict | bool):
        if stuff == False: return None
        
        if stuff['action'] in KEYBOARD_ACTIONS:
            
            if stuff['action'] == "press_key":
                if stuff['key'] in self.activate_keys:
                    for i in self.activate_keys[stuff["key"]]:
                        if self._data[i].isheld == False:
                            self._data[i].playing = True
                            self._data[i].isheld = True

            elif stuff['action'] == "release_key":
                if stuff['key'] in self.activate_keys:
                    for i in self.activate_keys[stuff["key"]]:
                        self._data[i].playing = False
                        self._data[i].isheld = False

    def _stop_all_threads(self):
        try: self.keyboard_listener.stop()
        except: pass

        for i in range(len(self._data)):
            self._data[i].stop = True
        
        return

    def _play_thread(self, index: int):
        _macro_data = [_Data(**action) for action in load_file(self._data[index].file)]
        action_len = len(_macro_data)-1
        _future = None
        _current = None
        _before = None
        while not self._data[index].stop:
            time.sleep(0.02)
            _future = None
            _current = None
            _before = None
            if self._data[index].playing:
                for i in range(action_len):
                    if self._data[index].playing:
                    
                        if self._data[index].stop: return
                        
                        if i < action_len: _future: _Data = _macro_data[i+1]
                        if i > 0: _before: _Data = _macro_data[i-1]
                        _current: _Data = _macro_data[i]

                        if _current.action in KEYBOARD_ACTIONS:
                            key = _current.key if not "Key." in _current.key else SPECIAL_KEYS[_current.key]

                            if _current.action == "press_key":
                                if self._data[index].playing:
                                    self.keyboard_controller.press(key)

                            elif _current.action == "press_key":
                                if self._data[index].playing:
                                    self.keyboard_controller.release(key)

                        elif _current.action in MOUSE_ACTIONS:
                            if _current.action in ["mouse_press", "mouse_release"]:
                                button = pynput.mouse.Button.left if _current.button == "Button.left" else pynput.mouse.Button.right

                            if _current.action == "mouse_move":
                                if self._data[index].playing:
                                    self.mouse_controller.position = (_current.x, _current.y)
                            
                            elif _current.action == "mouse_press":
                                if self._data[index].playing:
                                    self.mouse_controller.press(button)
                            
                            elif _current.action == "mouse_release":
                                if self._data[index].playing:
                                    self.mouse_controller.release(button)

                            elif _current.action == "mouse_scroll":
                                if self._data[index].playing:
                                    self.mouse_controller.scroll(_current.dx, _current.dy)

                        else:
                            print(f"unknown action '{_current.action}'.")

                        if self._data[index].stop: return

                        if not _future == None:
                            if self._data[index].playing:
                                time.sleep(_future.time - _current.time)
                if self._data[index].repeat:
                    if self._data[index].playing:
                        time.sleep(self._data[index].delay)
                else:
                    self._data[index].playing = False

    def start(self, startup_delay: float = None):
        delay = startup_delay or self.startup_delay
        if self.enable_output: print(f"waiting {delay} before starting {len(self._data)} Hot Key Macro{'s' if not len(self._data) == 1 else ''}")
        time.sleep(delay)
        if self.enable_output: print(f"playing {len(self._data)} Hot Key Macro{'s' if not len(self._data) == 1 else ''}")
        self.keyboard_controller = pynput.keyboard.Controller()
        self.mouse_controller = pynput.mouse.Controller()
        self.keyboard_listener = pynput.keyboard.Listener(
            on_press = lambda key: self.logic(on_keyboard_press(key)),
            on_release = lambda key: self.logic(on_keyboard_release(key))
        )

        for i in range(len(self._data)):
            t = threading.Thread(target = lambda: self._play_thread(i))
            t.daemon = True
            t.start()
            self._threads.append(t)

        self.keyboard_listener.start()

        self._threads.append(self.keyboard_listener)

        [t.join() for t in self._threads]