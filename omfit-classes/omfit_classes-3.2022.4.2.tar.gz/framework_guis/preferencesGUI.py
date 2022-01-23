OMFITx.TitleGUI('File > Preferences ...')
try:
    from tkinter import font as tkinter_font
except ImportError:
    import tkFont as tkinter_font
from utils_widgets import _defaultFont
from omfit_classes.OMFITx import update_gui_theme


def savePrefs(location=None):
    OMFIT.addMainSettings(updateUserSettings=True)


def showPref(location, translate={}, skip=(), postcommand=None):
    try:
        eval(location)
    except Exception:
        return

    if postcommand is None:
        showPrefCommand = savePrefs
    else:

        def showPrefCommand(*args, **kw):
            tmp = postcommand(*args, **kw)
            savePrefs()
            return tmp

    for item in eval(location).keys():
        if item in eval(location) and not isinstance(eval(location)[item], dict) and item not in skip:
            try:
                default = eval(location.replace("OMFIT", "OMFIT.tmpSkel") + "[%s]" % repr(item))
            except Exception as _excp:
                default = OMFITx.special1

            if item in ['workDir', 'version']:
                continue
            if item in translate:
                tmp = translate[item]
            else:
                tmp = re.sub('_', ' ', item)
                tmp = tmp[0].upper() + tmp[1:]

            if item == 'email':
                OMFITx.Entry(location + "[" + repr(item) + "]", tmp, check=is_email, postcommand=showPrefCommand, updateGUI=True)
            elif isinstance(eval(location)[item], bool):
                OMFITx.CheckBox(location + "[" + repr(item) + "]", tmp, postcommand=showPrefCommand, default=default)
            else:
                OMFITx.Entry(location + "[" + repr(item) + "]", tmp, postcommand=showPrefCommand, default=default)


def copyServer(location):
    if MainScratch['__preferences__newServer__'] != '':
        if MainScratch['__preferences__newServer__'] not in OMFIT['MainSettings']['SERVER']:
            OMFIT['MainSettings']['SERVER'][MainScratch['__preferences__newServer__']] = copy.deepcopy(
                OMFIT['MainSettings']['SERVER'][MainScratch['__preferences__editServer__']]
            )
            MainScratch['__preferences__editServer__'] = MainScratch['__preferences__newServer__']
        else:
            printe(MainScratch['__preferences__editServer__'] + ' already exists!')
        MainScratch['__preferences__newServer__'] = ''


OMFITx.Button(
    "Compare to installation default settings",
    lambda: diffTreeGUI(OMFIT['MainSettings'], OMFIT.tmpSkel['MainSettings'], deepcopyOther=True),
)
OMFITx.Button("Save settings", savePrefs, style='bold.TButton')

# ----------------------------
# Main
# ----------------------------
OMFITx.Tab('Main')
translate = {}
translate['institution'] = 'Installation'
translate['projectsDir'] = 'Projects directory'
translate['modulesDir'] = 'Modules directories'
translate['stats_file'] = 'Statistics file'
showPref("OMFIT['MainSettings']['SETUP']", translate)

# ----------------------------
# Remote servers
# ----------------------------
OMFITx.Tab('Remote servers')
if not isinstance(OMFIT['MainSettings']['SERVER']['default'], str):
    OMFIT['MainSettings']['SERVER']['default'] = OMFIT.tmpSkel['MainSettings']['SERVER']['default']

usernames = map(str, [OMFIT['MainSettings']['SERVER'][item] for item in OMFIT['MainSettings']['SERVER'] if item.endswith('_username')])
if not ''.join(usernames):
    OMFITx.Label(
        '>> All institutional usernames are empty! <<\n' 'Set the ones for which you have access to the workstations.',
        font=OMFITfont('bold'),
        foreground='red',
        align='center',
    )
location = "OMFIT['MainSettings']['SERVER']"
servers = []
for item in eval(location).keys():
    if isinstance(eval(location)[item], str) and item.endswith('_username') or eval(location)[item] is None:
        tmp = re.sub('_', ' ', item)
        OMFITx.Entry(location + "[" + repr(item) + "]", tmp[0].upper() + tmp[1:], postcommand=savePrefs, check=is_string, default='')
    elif isinstance(eval(location)[item], dict):
        if 'server' in eval(location)[item]:
            servers.append(item)

OMFITx.Separator()

OMFITx.ComboBox("OMFIT['MainSettings']['SERVER']['default']", servers, 'Default server', postcommand=savePrefs)

OMFITx.Separator()

if (
    '__preferences__editServer__' not in MainScratch
    or MainScratch['__preferences__editServer__'] not in OMFIT['MainSettings']['SERVER']
    or not isinstance(OMFIT['MainSettings']['SERVER'][MainScratch['__preferences__editServer__']], dict)
):
    MainScratch['__preferences__editServer__'] = OMFIT['MainSettings']['SERVER']['default']
MainScratch['__preferences__editServer__'] = SERVER(MainScratch['__preferences__editServer__'])
OMFITx.ComboBox("MainScratch['__preferences__editServer__']", servers, 'Edit server', updateGUI=True)
if MainScratch['__preferences__editServer__'] in OMFIT['MainSettings']['SERVER']:
    showPref("OMFIT['MainSettings']['SERVER']['" + MainScratch['__preferences__editServer__'] + "']")

OMFITx.Separator()

OMFITx.Entry(
    "MainScratch['__preferences__newServer__']",
    'Copy `%s` to new server' % MainScratch['__preferences__editServer__'],
    updateGUI=True,
    default='',
    postcommand=copyServer,
)

# ----------------------------
# Extensions
# ----------------------------
OMFITx.Tab('File extensions')
showPref("OMFIT['MainSettings']['SETUP']['Extensions']")

# ----------------------------
# Appearance
# ----------------------------
OMFITx.Tab('GUI appearance')
OMFITx.Separator()


def update_gui_font_size(location):
    _defaultFont['size'] = eval(location)
    _defaultFont['size2'] = MainSettings['SETUP']['GUIappearance'].get('commandBox_font_size', _defaultFont['size']) - _defaultFont['size']
    update_gui_theme()
    savePrefs()


def update_gui_font_family(location):
    _defaultFont['family'] = eval(location)
    update_gui_theme()
    savePrefs()


def update_commandbox_font_size(location):
    _defaultFont['size2'] = eval(location) - _defaultFont['size']
    update_gui_theme()
    savePrefs()


def update_commandbox_font_weight(location):
    _defaultFont['weight2'] = 'bold' * bool(eval(location))
    update_gui_theme()
    savePrefs()


def update_theme(location):
    update_gui_theme()
    savePrefs()


OMFITx.Label('Entries will update on re-opening this preferences window')

OMFITx.ComboBox(
    "OMFIT['MainSettings']['SETUP']['GUIappearance']['theme']",
    sorted(ttk.Style().theme_names()),
    "Theme",
    postcommand=update_theme,
    default='default',
    updateGUI=True,
)

good_fonts = ['TkDefaultFont']
for family in tkinter_font.families():
    try:
        family_str = str(family)  # some people have crazy str fonts available
        good_fonts.append(family_str)
    except Exception:
        pass
good_fonts = sorted(good_fonts)
OMFITx.ComboBox(
    "OMFIT['MainSettings']['SETUP']['GUIappearance']['GUI_font_family']",
    good_fonts,
    "Font family",
    postcommand=update_gui_font_family,
    default='TkDefaultFont',
    check=is_string,
    updateGUI=True,
)

OMFITx.Entry(
    "OMFIT['MainSettings']['SETUP']['GUIappearance']['GUI_font_size']",
    "Font size",
    updateGUI=True,
    postcommand=update_gui_font_size,
    default=10,
    check=lambda x: is_int(x) and x < 32 and x > 6,
)

OMFITx.Entry(
    "OMFIT['MainSettings']['SETUP']['GUIappearance']['commandBox_font_size']",
    "CommandBox size",
    postcommand=update_commandbox_font_size,
    default=10,
    check=lambda x: is_int(x) and x < 32 and x > 6,
)

OMFITx.CheckBox(
    "OMFIT['MainSettings']['SETUP']['GUIappearance']['commandBox_font_bold']",
    "CommandBox bold",
    postcommand=update_commandbox_font_weight,
    default=False,
)

showPref(
    "OMFIT['MainSettings']['SETUP']['GUIappearance']",
    skip=('theme', 'GUI_font_size', 'GUI_font_family', 'commandBox_font_size', 'commandBox_font_bold'),
    postcommand=update_gui_theme,
)

OMFITx.Separator()

OMFITx.Tab('Plot appearance')
OMFITx.Separator()

ordered_styles = [k for k in sorted(style.available + ['default'], key=lambda x: x.lower()) if not k.startswith('_')]
OMFITx.ComboBox(
    "OMFIT['MainSettings']['SETUP']['PlotAppearance']['startup_style']",
    ordered_styles,
    "Default style",
    default='default',
    check=is_string,
    updateGUI=False,
)

OMFITx.Separator()

# ----------------------------
# Key bindings
# ----------------------------
OMFITx.Tab('Key bindings')
showPref("OMFIT['MainSettings']['SETUP']['KeyBindings']")

# ----------------------------
# Stop until email is set
# ----------------------------
if OMFIT['MainSettings']['SETUP']['email'] is None:
    OMFITx._aux['topGUI'].protocol(
        'WM_DELETE_WINDOW',
        lambda: OMFITx.Dialog(
            'Must enter a valid email address\n\nREMEMBER:\nstrings in Python must be in (single or double) quotes\nand you must hit <Return> for an entry to be accepted in the GUI',
            ['ok'],
            'error',
        ),
    )
else:
    OMFITx._aux['topGUI'].protocol('WM_DELETE_WINDOW', lambda topGUI=OMFITx._aux['topGUI']: OMFITx._clearClosedGUI(topGUI))
