# load ODS from IMAS
def load():
    ods = load_omas_imas_remote(
        imas_settings['serverPicker'], user=None, machine=imas_settings['machine'], pulse=imas_settings['pulse'], run=imas_settings['run']
    )
    loc = parseLocation(location)
    eval(buildLocation(loc[:-1]))[loc[-1]] = ods
    if postcommand:
        postcommand()


# save ODS to IMAS
def save():
    save_omas_imas_remote(
        imas_settings['serverPicker'],
        eval(location),
        user=None,
        machine=imas_settings['machine'],
        pulse=imas_settings['pulse'],
        run=imas_settings['run'],
        new=True,
    )
    if postcommand:
        postcommand()


# delete ODS from tree
def delete():
    loc = parseLocation(location)
    del eval(buildLocation(loc[:-1]))[loc[-1]]


# =======================
defaultVars(
    base_root=None,
    action=['load', 'save', 'save_user', 'load_user', 'run'][0],
    location=None,
    postcommand=None,
    imas_settings_location=None,
    state='normal',
    updateGUI=False,
)

rl = relativeLocations(base_root)
root = rl['root']

# set ODS location based on action
if location is None:
    if action.startswith('load'):
        location = "root['INPUTS']['ods']"
    elif action.startswith('save'):
        location = "root['OUTPUTS']['ods']"

# if ODS already exists and action is load, allow de-loading
if location is not None:
    tmp = parseLocation(location)

if action == 'load' and tmp[-1] in eval(buildLocation(tmp[:-1])):
    OMFITx.Button('Load a different ODS', delete, updateGUI=True)
    OMFITx.End()

# other actions
else:
    # imas settings location
    if imas_settings_location is None:
        imas_settings_location = rl['thisName'] + "['__scratch__']"
    imas_settings = eval(imas_settings_location)

    # imas servers
    IMAS_SERVERS = {'ITER': 'iter_login', 'WPCD': 'itm_gateway', 'KFE': 'sophie', 'JET': 'heimdall', 'MAST': 'freia'}
    default_server = 'itm_gateway'
    if 'serverPicker' in root['SETTINGS']['REMOTE_SETUP'] and root['SETTINGS']['REMOTE_SETUP']['serverPicker'] in IMAS_SERVERS.values():
        default_server = root['SETTINGS']['REMOTE_SETUP']['serverPicker']

    # GUI entries
    with OMFITx.same_row():
        OMFITx.ComboBox(imas_settings_location + "['serverPicker']", IMAS_SERVERS, 'Server', default=default_server)
        OMFITx.Entry(imas_settings_location + "['machine']", 'Machine', default=root['SETTINGS']['EXPERIMENT']['device'])
    with OMFITx.same_row():
        OMFITx.Entry(imas_settings_location + "['pulse']", 'Pulse', check=is_int, default=root['SETTINGS']['EXPERIMENT']['shot'])
        if action == 'run':
            OMFITx.Entry(imas_settings_location + "['run_in']", 'Run in', check=is_int, default=root['SETTINGS']['EXPERIMENT']['time'])
            OMFITx.Entry(imas_settings_location + "['run_out']", 'Run out', check=is_int, default=root['SETTINGS']['EXPERIMENT']['time'])
        else:
            OMFITx.Entry(imas_settings_location + "['run']", 'Run', check=is_int, default=root['SETTINGS']['EXPERIMENT']['time'])

    # handle actions
    if action == 'run':
        pass
    elif action.startswith('load'):
        if action == 'load_user':
            OMFITx.Button('Load ODS from IMAS', postcommand, state=state, updateGUI=updateGUI)
        else:
            OMFITx.Button('Load ODS from IMAS', load, state=state, updateGUI=True)
    elif action.startswith('save'):
        if action == 'save_user':
            OMFITx.Button('Save ODS to IMAS', postcommand, state=state, updateGUI=updateGUI)
        else:
            OMFITx.Button('Save ODS to IMAS', save, state=state, updateGUI=updateGUI)
    else:
        raise ValueError('Action `%s` was not recognized' % action)
