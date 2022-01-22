import time

def on_mouse_click(x: int, y: int, button, pressed: bool):
    current_time = time.time()

    return {"time": current_time, "action": "mouse_press" if pressed else "mouse_release", "button": str(button), "x": x, "y": y}

def on_mouse_scroll(x: int, y: int, dx: int, dy: int):
    current_time = time.time()

    return {"time": current_time, "action": "mouse_scroll", "x": x, "y": y, "dx": dx, "dy": dy}

def on_mouse_move(x: int, y: int):
    current_time = time.time()

    return {"time": current_time, "action": "mouse_move", "x": x, "y": y}