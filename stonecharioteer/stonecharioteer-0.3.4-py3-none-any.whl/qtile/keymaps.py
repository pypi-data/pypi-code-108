from libqtile.lazy import lazy
from libqtile.config import Key
from libqtile.utils import guess_terminal
from stonecharioteer.qtile.inputs import Keyboard, MOD
from stonecharioteer.utils.displays import get_display_info


def configure_keymaps(groups):
    """Configures keymaps"""
    terminal = "/bin/konsole"
    MODIFIER_SET_1 = [MOD.value]
    MODIFIER_SET_2 = [MOD.value, Keyboard.SHIFT.value]
    MODIFIER_SET_3 = [MOD.value, Keyboard.CTRL.value]
    # Movement keymaps
    keys = [
        # Switch between windows
        Key(MODIFIER_SET_1, "h", lazy.layout.left(), desc="Move focus to left"),
        Key(MODIFIER_SET_1, "l", lazy.layout.right(), desc="Move focus to right"),
        Key(MODIFIER_SET_1, "j", lazy.layout.down(), desc="Move focus down"),
        Key(MODIFIER_SET_1, "k", lazy.layout.up(), desc="Move focus up"),
        Key(
            MODIFIER_SET_1,
            "space",
            lazy.layout.next(),
            desc="Move window focus to other window",
        ),
        # Move windows between left/right columns or move up/down in current stack.
        # Moving out of range in Columns layout will create new column.
        Key(
            MODIFIER_SET_2,
            "h",
            lazy.layout.shuffle_left(),
            desc="Move window to the left",
        ),
        Key(
            MODIFIER_SET_2,
            "l",
            lazy.layout.shuffle_right(),
            desc="Move window to the right",
        ),
        Key(MODIFIER_SET_2, "j", lazy.layout.shuffle_down(), desc="Move window down"),
        Key(MODIFIER_SET_2, "k", lazy.layout.shuffle_up(), desc="Move window up"),
        # Grow windows. If current window is on the edge of screen and direction
        # will be to screen edge - window would shrink.
        Key(
            MODIFIER_SET_3, "h", lazy.layout.grow_left(), desc="Grow window to the left"
        ),
        Key(
            MODIFIER_SET_3,
            "l",
            lazy.layout.grow_right(),
            desc="Grow window to the right",
        ),
        Key(MODIFIER_SET_3, "j", lazy.layout.grow_down(), desc="Grow window down"),
        Key(MODIFIER_SET_3, "k", lazy.layout.grow_up(), desc="Grow window up"),
        Key(
            MODIFIER_SET_1, "n", lazy.layout.normalize(), desc="Reset all window sizes"
        ),
        # Toggle between split and unsplit sides of stack.
        # Split = all windows displayed
        # Unsplit = 1 window displayed, like Max layout, but still with
        # multiple stack panes
        Key(
            MODIFIER_SET_2,
            "Return",
            lazy.layout.toggle_split(),
            desc="Toggle between split and unsplit sides of stack",
        ),
        Key(MODIFIER_SET_1, "Return", lazy.spawn(terminal), desc="Launch terminal"),
        # Toggle between different layouts as defined below
        Key(MODIFIER_SET_1, "Tab", lazy.next_layout(), desc="Toggle between layouts"),
        Key(MODIFIER_SET_1, "w", lazy.window.kill(), desc="Kill focused window"),
        Key(
            MODIFIER_SET_3, "r", lazy.restart(), desc="Restart Qtile and reload config"
        ),
        Key(MODIFIER_SET_3, "q", lazy.shutdown(), desc="Shutdown Qtile"),
        Key(
            MODIFIER_SET_1,
            "r",
            lazy.spawn("""rofi -modi "drun,run,window,ssh" -show drun"""),
            desc="Spawn a command using a prompt widget",
        ),
    ]

    for ix, group in enumerate(groups):
        keys.extend(
            [
                Key(
                    MODIFIER_SET_1,
                    str(ix + 1),
                    lazy.group[group.name].toscreen(),
                    desc=f"Switch to group {group.name}",
                ),
                Key(
                    MODIFIER_SET_2,
                    str(ix + 1),
                    lazy.window.togroup(group.name, switch_group=True),
                    desc=f"Switch to & move focussed window to group {group.name}",
                ),
                Key(
                    MODIFIER_SET_3,
                    str(ix + 1),
                    lazy.window.togroup(group.name),
                    desc=f"Move focussed window to group {group.name}",
                ),
            ]
        )

    displays = get_display_info()
    if len(displays) == 2:
        # FIXME: Figure out which is on the left or right intuitively.
        display_keys = ["u", "y"]
    elif len(displays) == 3:
        display_keys = ["u", "i", "y"]
    else:
        display_keys = ["u"]

    # WIP: shift focus to monitor / screen

    try:
        for ix, key in enumerate(display_keys):
            keys.append(Key(MODIFIER_SET_1, key, lazy.to_screen(ix)))
    except:
        pass

    return keys
