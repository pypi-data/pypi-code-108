"""
Provides the GUI for editing OMFITnamelist instances in the tree when they are double-clicked.
"""

defaultVars(nml=None, misc_label='Other')
if nml is None:
    nml = OMFITnamelist('new_nml')

try:
    OMFITx.TitleGUI(relativeLocations(nml)['OMFITlocationName'][-1])
except Exception:
    OMFITx.End()

MainScratch.setdefault(id(nml), {})  # Set up a place to track the status of the filters
misc_tab_opened = False  # Track whether the misc tab has been opened yet so we don't create extra filter entries in it.

for kn, n in nml.items():
    if kn.startswith('__'):  # Hidden item: do nothing
        continue

    if isinstance(n, omfit_classes.namelist.NamelistName):  # Make a new tab for a NamelistName and load its children
        OMFITx.Tab(kn)
        OMFITx.Entry("MainScratch[%d]['%s_filter']" % (id(nml), kn), lbl='Filter:', default='', updateGUI=True)
        OMFITx.Separator()
        nml_loc = relativeLocations(nml[kn])['OMFITlocationName'][-1]

        for k, v in n.items():
            if k[:2] == '__':  # Don't display entries for hidden children
                continue
            if MainScratch[id(nml)]['%s_filter' % kn].lower() in k.lower():  # Make sure item name passes filter
                OMFITx.Entry(nml_loc + "['%s']" % k, lbl=k)  # Make an entry for an item within a NamelistName

    else:
        OMFITx.Tab(misc_label)
        if not misc_tab_opened:
            # Create the misc tab's filter (first time only)
            OMFITx.Entry("MainScratch[%d]['%s_filter']" % (id(nml), misc_label), lbl='Filter:', default='', updateGUI=True)
            OMFITx.Separator()
            misc_tab_opened = True

        try:
            nml_loc = relativeLocations(nml)['OMFITlocationName'][-1]
        except Exception as _excp:
            printe(repr(E))
            printe('Failed to parse %s' % kn)
            continue

        if MainScratch[id(nml)]['%s_filter' % misc_label] in kn.lower():  # Make sure item name passes filter
            OMFITx.Entry(nml_loc + "['%s']" % kn, lbl=kn)  # Make an entry for a top-level non-NamelistName item


def cleanup(topGUI):
    if id(nml) in MainScratch:
        del MainScratch[id(nml)]
    OMFITx._clearClosedGUI(topGUI)


OMFITx._aux['topGUI'].protocol('WM_DELETE_WINDOW', lambda topGUI=OMFITx._aux['topGUI']: cleanup(topGUI))
