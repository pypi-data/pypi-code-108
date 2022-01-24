"""This is the list of panels and widgets for those panels."""
from libqtile.widget import (
    Battery,
    CPU,
    CapsNumLockIndicator,
    Clock,
    CurrentLayout,
    GroupBox,
    HDDGraph,
    Memory,
    Net,
    QuickExit,
    Spacer,
    Sep,
    Systray,
    TextBox,
    Volume,
    WindowName,
)

from libqtile.bar import Bar, STRETCH

from stonecharioteer.constants import colors


def autorandr(config):
    from libqtile import qtile

    qtile.cmd_spawn(f"/opt/qtile/bin/autorandr {config}")


def get_top_bar():
    current_layout = CurrentLayout(
        font="JetBrains Mono",
        fontsize=12,
        foreground=colors[6],
        background=colors[0],
    )
    system_tray = Systray(foreground=colors[6], background=colors[0], padding=5)
    capslock_numlock_indicator = CapsNumLockIndicator(
        foreground=colors[6],
        background=colors[0],
    )
    cpu_indicator = CPU(
        foreground=colors[6],
        background=colors[0],
    )
    memory_indicator = Memory(
        foreground=colors[6],
        background=colors[0],
    )
    hdd_indicator = HDDGraph(
        foreground=colors[6],
        background=colors[0],
    )
    volume_control = Volume(cardid="1")
    # TODO: Figure out what the current layout is and highlight that.
    autorandr_home_button = TextBox(
        foreground=colors[6],
        background=colors[0],
        font="JetBrains Mono",
        fontsize=12,
        text="HOME",
        mouse_callbacks={"Button1": lambda: autorandr("home")},
    )
    autorandr_center_button = TextBox(
        foreground=colors[6],
        background=colors[0],
        font="JetBrains Mono",
        fontsize=12,
        text="CENT",
        mouse_callbacks={"Button1": lambda: autorandr("center-monitor")},
    )
    autorandr_external_button = TextBox(
        foreground=colors[6],
        background=colors[0],
        font="JetBrains Mono",
        fontsize=12,
        text="EXT",
        mouse_callbacks={"Button1": lambda: autorandr("external")},
    )
    autorandr_mobile_button = TextBox(
        foreground=colors[6],
        background=colors[0],
        font="JetBrains Mono",
        fontsize=12,
        text="MOBILE",
        mouse_callbacks={"Button1": lambda: autorandr("mobile")},
    )

    network_indicator = Net(
        foreground=colors[6],
        background=colors[0],
    )

    default_size = 24

    default_top_bar = Bar(
        [
            Sep(linewidth=0, padding=5, foreground=colors[2], background=colors[0]),
            current_layout,
            get_sep(),
            Spacer(length=10, foreground=colors[2], background=colors[0]),
            autorandr_home_button,
            autorandr_center_button,
            autorandr_external_button,
            autorandr_mobile_button,
            get_sep(),
            Spacer(length=STRETCH, foreground=colors[2], background=colors[0]),
            cpu_indicator,
            get_sep(),
            memory_indicator,
            get_sep(),
            TextBox(text="HDD:", foreground=colors[6], background=colors[0]),
            hdd_indicator,
            get_sep(),
            system_tray,
            TextBox(text="Net:", foreground=colors[6], background=colors[0]),
            network_indicator,
            get_sep(),
            TextBox(text="Vol:", foreground=colors[6], background=colors[0]),
            volume_control,
            get_sep(),
            capslock_numlock_indicator,
            Sep(linewidth=0, padding=5, foreground=colors[2], background=colors[0]),
        ],
        default_size,
    )
    return default_top_bar


def get_bottom_bar():
    group_box = GroupBox(
        font="JetBrains Mono",
        fontsize=12,
        margin_x=5,
        margin_y=3,
        padding_y=5,
        padding_x=5,
        borderwidth=3,
        active=colors[2],
        inactive=colors[9],
        rounded=False,
        highlight_color=colors[1],
        highlight_method="line",
        this_current_screen_border=colors[3],
        this_screen_border=colors[4],
        other_current_screen_border=colors[6],
        other_screen_border=colors[4],
        foreground=colors[2],
        background=colors[0],
        use_mouse_wheel=False,
    )

    window_name = WindowName(
        font="JetBrains Mono",
        fontsize=14,
        foreground=colors[3],
        background=colors[0],
        padding_x=10,
        margin_x=10,
    )
    clock_widget = Clock(
        foreground=colors[6], background=colors[0], format="%A, %B %d - %H:%M"
    )
    quick_exit = QuickExit(
        foreground=colors[6],
        background=colors[0],
    )

    # TODO: Only add this if this is a laptop, control through config.
    battery_indicator = Battery(
        foreground=colors[6],
        background=colors[0],
    )

    default_size = 24

    default_bottom_bar = Bar(
        [
            group_box,
            get_sep(),
            window_name,
            get_sep(),
            clock_widget,
            TextBox(
                text="Battery [",
                foreground=colors[6],
                background=colors[0],
            ),
            battery_indicator,
            TextBox(
                text="]",
                foreground=colors[6],
                background=colors[0],
            ),
            quick_exit,
        ],
        default_size,
    )
    return default_bottom_bar


def get_sep():
    return TextBox(
        text="|",
        font="JetBrains Mono",
        background=colors[0],
        foreground=colors[10],
        padding=2,
        fontsize=14,
    )
