import os

MIN_WIDTH = 800
MIN_HEIGHT = 650

BLUE = '#377DFF'
DARK_BLUE = '#1164FF'
DARK_GREY = '#cfcfcf'
GREEN = '#00a388'
LIGHT_GREEN = '#00c9a7'
ORANGE = '#FFC107'
RED = '#FF0059'
SOFT_GREY = '#F8F9FA'
WHITE = '#FFFFFF'
YELLOW = '#FFC107'

FONT = ('Ubuntu', 12)

TITLE = 'Picovoice Shepherd'

FRAME_COMMON_PARAMS = dict(background=SOFT_GREY)

MENU_BAR_PARAMS = dict(
    background=SOFT_GREY,
    activebackground=LIGHT_GREEN,
    activeborderwidth=1,
    cursor='hand2',
    relief='flat',
    bd=0
)

PRIMARY_BUTTONS_COMMON_PARAMS_CONFIG = dict(
    background=BLUE,
    foreground=SOFT_GREY,
    borderwidth=1,
    focusthickness=1,
    focuscolor='none',
    font=FONT,
)

PRIMARY_BUTTONS_COMMON_PARAMS_MAP = dict(
    background=[('active', DARK_BLUE), ('disabled', DARK_GREY)],
    foreground=[('active', WHITE), ('disabled', WHITE)]
)

BACK_BUTTONS_COMMON_PARAMS_CONFIG = dict(
    background=WHITE,
    foreground=DARK_BLUE,
    borderwidth=1,
    focusthickness=1,
    focuscolor='none',
    font=FONT,
)

BACK_BUTTONS_COMMON_PARAMS_MAP = dict(
    background=[('active', DARK_GREY), ('disabled', DARK_GREY)],
    foreground=[('active', BLUE), ('disabled', WHITE)]
)

SECONDARY_BUTTONS_COMMON_PARAMS_CONFIG = dict(
    background=LIGHT_GREEN,
    foreground=WHITE,
    borderwidth=1,
    focusthickness=1,
    focuscolor='none',
    font=FONT,
)

SECONDARY_BUTTONS_COMMON_PARAMS_MAP = dict(
    background=[('active', GREEN), ('disabled', DARK_GREY)],
    foreground=[('active', WHITE), ('disabled', WHITE)]
)

SECONDARY_AUDIO_BUTTONS_COMMON_PARAMS_CONFIG = dict(
    background=LIGHT_GREEN,
    foreground=WHITE,
    borderwidth=1,
    focusthickness=1,
    focuscolor='none',
    font=FONT,
    width=25,
)

SECONDARY_AUDIO_BUTTONS_COMMON_PARAMS_MAP = dict(
    background=[('active', GREEN), ('disabled', DARK_GREY)],
    foreground=[('active', WHITE), ('disabled', WHITE)]
)

LIST_BOX_COMMON_PARAMS_CONFIG = dict(
    font=FONT,
    width=40,
    rowheight=25
)

LIST_BOX_COMMON_PARAMS_MAP = dict(
    background=[('selected', GREEN)],
    forground=[('selected', WHITE)]
)

SCALE_PARAMS = dict(
    background=SOFT_GREY,
    activebackground=BLUE,
    borderwidth=2,
    cursor='hand2',
    highlightbackground=SOFT_GREY,
    highlightcolor=SOFT_GREY,
    from_=0,
    to=100,
    length=200,
    troughcolor=WHITE,
    relief='flat',
    sliderrelief='groove',
    orient='horizontal',
    width=15)

PROGRESSBAR_PARAMS = dict(
    troughcolor=WHITE,
    bordercolor=WHITE,
    background=BLUE,
    lightcolor=BLUE,
    darkcolor=BLUE,
    relief='flat')

ENTRY_PARAMS_ttk = dict(
    width=30,
    font=(FONT[0], int(FONT[1] * 1.5))
)

ENTRY_PARAMS_CONFIG = dict(
    background=WHITE,
    disabledbackground=WHITE,
    relief='flat',
)

ENTRY_PARAMS_MAP = dict(
    background=[('active', 'black'), ('disabled', 'black')],
    foreground=[('active', 'green'), ('disabled', 'green')]
)

BUTTON_DISABLED_BACKGROUND_COLOR = SOFT_GREY

SCROLLED_TEXT_COMMON_PARAMS = dict(bd=0, bg='#25187E', fg=SOFT_GREY)

NOTEBOOK_ACTIVE_TAB_PARAMS = dict(
    background=[("selected", BLUE)],
    foreground=[("selected", WHITE)])

NOTEBOOK_PARAMS = dict(
    background=SOFT_GREY,
    tabposition='n')

NOTEBOOK_TAB_PARAMS = dict(
    background=DARK_GREY,
    bordercolor=DARK_BLUE,
    expand=[2, 2, 2, 0],
    font=FONT,
    foreground=DARK_BLUE,
    padding=[50, 5])

IMAGES = dict(
    clipboard=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'asset/clipboard_white.png'),
    floppy=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'asset/save_white.png'),
    mic=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'asset/mic_white.png'),
    picovoice=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'asset/pv_wordmark.jpg'),
    loading_animation=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'asset/loading.gif'),
    window_icon=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'asset/picovoice.png')
)
