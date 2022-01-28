# ------------------------------------------------------------------------------


def get_display_offset(x, y):
    try:
        import screeninfo  # pylint: disable=import-outside-toplevel
    except ImportError:
        return (0, 0)

    def get_monitor_from_coord(x, y):
        monitors = screeninfo.get_monitors()

        for m in reversed(monitors):
            if m.x <= x <= m.width + m.x and m.y <= y <= m.height + m.y:
                return m
        return monitors[0]

    current_screen = get_monitor_from_coord(x, y)

    return (current_screen.x, current_screen.y)


# ------------------------------------------------------------------------------


def center_window_geometry(
    width, height, screen_width, screen_height, mouse_x, mouse_y
):
    offset_x, offset_y = get_display_offset(mouse_x, mouse_y)
    x = offset_x + (screen_width // 2) - (width // 2)
    y = offset_y + (screen_height // 2) - (height // 2)
    return f"{width}x{height}+{x}+{y}"


# ------------------------------------------------------------------------------
