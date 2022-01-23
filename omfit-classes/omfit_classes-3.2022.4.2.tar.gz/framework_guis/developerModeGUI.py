"""
This GUI guides users through conversion of modules scripts to developer mode
"""
defaultVars(module_link=OMFIT)

if module_link is OMFIT:
    OMFITx.TitleGUI('OMFIT')

else:
    try:
        module_link_loc = relativeLocations(module_link)['OMFITlocationName'][-1]
        OMFITx.TitleGUI(module_link_loc)
    except Exception:
        printe(f"Specify module_link when running {os.path.split(__file__)[1]}")
        OMFITx.End()

options = SortedDict()
options['Developer mode'] = 'DEVEL'
options['Standard mode'] = 'FREEZE'
options['Standard mode (RELOAD)'] = 'RELOAD'

writable_dirs = OMFITmodule.directories(checkIsWriteable=True)
if len(writable_dirs):
    default_operation = ['RELOAD', 'DEVEL'][os.path.abspath(OMFITsrc + '/../modules') in writable_dirs]
    OMFITx.ComboBox("MainScratch['developerMode_operation']", options, 'Convert scripts to', default=default_operation, updateGUI=True)
else:
    MainScratch['developerMode_operation'] = 'RELOAD'

if MainScratch['developerMode_operation'] == 'DEVEL':
    OMFITx.Label(
        '''
    Reload all scripts with modifyOriginal=TRUE (useful for developers)
    - This will OVERWRITE unexported changes to scripts in your tree
    '''.lstrip(),
        foreground='red',
        align='left',
    )
elif MainScratch['developerMode_operation'] == 'RELOAD':
    OMFITx.Label(
        '''
    Reload all scripts with modifyOriginal=FALSE (the default for normal users)
    - This will OVERWRITE unexported changes to scripts in your tree
    '''.lstrip(),
        foreground='red',
        align='left',
    )
elif MainScratch['developerMode_operation'] == 'FREEZE':
    OMFITx.Label(
        '''
    Freeze all scripts with modifyOriginal=FALSE (the default for normal users)
    - This will not overwrite anything and it is always safe
    '''.lstrip(),
        foreground='blue',
        align='left',
    )


def uncapitalize(s):
    if len(s) > 0:
        s = s[0].lower() + s[1:]
    return s


OMFITx.Separator()
dirs = OMFITmodule.directories(checkIsWriteable=(MainScratch['developerMode_operation'] == 'DEVEL'))
if 'developerMode_modules_directory' in MainScratch and MainScratch['developerMode_modules_directory'] not in dirs:
    MainScratch['developerMode_modules_directory'] = dirs[0]
OMFITx.ComboBox("MainScratch['developerMode_modules_directory']", dirs, "Modules directory", default=dirs[0])
OMFITx.CheckBox("MainScratch['developerMode_convert_submodules']", "Convert submodules", default=True, updateGUI=True)
if MainScratch['developerMode_operation'] != 'FREEZE':
    OMFITx.CheckBox("MainScratch['developerMode_load_new_settings']", "Update module settings with new entries", default=True)
OMFITx.Separator()


def convert(event=None):
    developer_mode(module_link)
    destroy()


with OMFITx.same_row():
    OMFITx.Button(
        'Convert to {operation_text:} all scripts in {module:}{and_sub:}'.format(
            operation_text=uncapitalize(flip_values_and_keys(options)[MainScratch['developerMode_operation']]),
            module='OMFIT' if module_link is OMFIT else module_link.ID + ' module',
            and_sub=['', ' and all sub-modules'][MainScratch['developerMode_convert_submodules']],
        ),
        convert,
    )
    MainScratch.setdefault('developerMode_quiet', True)
    OMFITx.CheckBox("MainScratch['developerMode_quiet']", "Quiet")

topGUI = OMFITx._aux['topGUI']


def destroy():
    OMFITx._clearClosedGUI(topGUI)
