import time, pynput

special_keys = {'Key.' + key: eval(f"pynput.keyboard.Key.{key}") for key in dir(pynput.keyboard.Key)}

def on_keyboard_press(key):
    if key == None: return

    if key == pynput.keyboard.Key.esc: return False

    current_time = time.time()

    try: return {"time": current_time, "action": "press_key", "key": key.char}
    except AttributeError: return {"time": current_time, "action": "press_key", "key": str(key)}

def on_keyboard_release(key):
    if key == None: return

    if key == pynput.keyboard.Key.esc: return False

    current_time = time.time()

    try: return {"time": current_time, "action": "release_key", "key": key.char}
    except AttributeError: return {"time": current_time, "action": "release_key", "key": str(key)}
