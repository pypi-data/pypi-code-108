if 'base_override' in locals():
    globals().update(base_override)

if 'dependencies' not in locals():
    dependencies = {}

OMFITx.TitleGUI(rootName)

# Dependencies
if 'comment' in root['SETTINGS']['MODULE']:
    OMFITx.Entry(rootName + "['SETTINGS']['MODULE']['comment']", 'Comment', updateGUI=False)
if 'defaultGUI' in root['SETTINGS']['MODULE']:
    OMFITx.TreeLocationPicker(rootName + "['SETTINGS']['MODULE']['defaultGUI']", 'Default GUI', base=root, updateGUI=True, width=60)

# Settings
if 'PHYSICS' in root['SETTINGS']:
    OMFITx.Separator('PHYSICS SETTINGS')
    scratch.setdefault('usersSettingsVariant', '')
    userSettings = root.listUserSettings()
    options = {k.replace('_', ' '): k for k in userSettings}
    options[''] = ''
    with OMFITx.same_row():
        OMFITx.ComboBox(rootName + "['__scratch__']['usersSettingsVariant']", options, "Settings tag", state='normal', updateGUI=True)
        OMFITx.Button(
            'Load',
            lambda: root.loadUserSettings(variant=root['__scratch__']['usersSettingsVariant'], diff=False),
            state=['disabled', 'normal'][int(scratch['usersSettingsVariant'] in userSettings)],
        )
        OMFITx.Button(
            'Diff',
            lambda: root.loadUserSettings(variant=root['__scratch__']['usersSettingsVariant'], diff=True),
            state=['disabled', 'normal'][int(scratch['usersSettingsVariant'] in userSettings)],
        )
        OMFITx.Button('Save', lambda: root.saveUserSettings(variant=root['__scratch__']['usersSettingsVariant']), updateGUI=True)
        OMFITx.Button(
            'Del',
            lambda: root.deleteUserSettings(variant=root['__scratch__']['usersSettingsVariant']),
            state=['disabled', 'normal'][int(scratch['usersSettingsVariant'] in userSettings)],
            updateGUI=True,
        )

# Dependencies
if len(root['SETTINGS']['DEPENDENCIES']):
    OMFITx.Separator('DEPENDENCIES')
    for item in root['SETTINGS']['DEPENDENCIES']:
        location = rootName + "['SETTINGS']['DEPENDENCIES'][%s]" % repr(item)
        OMFITx.TreeLocationPicker(location, item, base=root, updateGUI=True, width=60, **dependencies.get(item, {}))

# Execution
OMFITx.Separator('EXECUTION')
servers = {'localhost': 'localhost'}
for item in eval(rootName + "['SETTINGS']['REMOTE_SETUP']"):
    if isinstance(eval(rootName + "['SETTINGS']['REMOTE_SETUP'][%s]" % repr(item)), dict):
        if item != SERVER(item):
            servers['%s (%s)' % (item, SERVER(item))] = item
            servers['%s' % SERVER(item)] = SERVER(item)
        else:
            servers['%s' % (item)] = item
item = eval(rootName + "['SETTINGS']['REMOTE_SETUP']['serverPicker']")
if item != SERVER(item):
    servers['%s (%s)' % (item, SERVER(item))] = item
    servers[SERVER(item)] = SERVER(item)
else:
    servers['%s' % (item)] = item
OMFITx.ComboBox(rootName + "['SETTINGS']['REMOTE_SETUP']['serverPicker']", servers, 'Server picker', state='normal', updateGUI=True)
server = SERVER(eval(rootName + "['SETTINGS']['REMOTE_SETUP']['serverPicker']"))
if server in eval(rootName + "['SETTINGS']['REMOTE_SETUP']") and isinstance(
    eval(rootName + "['SETTINGS']['REMOTE_SETUP'][%s]" % repr(server)), dict
):
    for item in eval(rootName + "['SETTINGS']['REMOTE_SETUP'][%s]" % repr(server)):
        OMFITx.Entry(rootName + "['SETTINGS']['REMOTE_SETUP'][%s][%s]" % (repr(server), repr(item)), item)
