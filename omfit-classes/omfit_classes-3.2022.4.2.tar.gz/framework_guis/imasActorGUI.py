# -*-Python-*-
# Created by meneghini at 12 Jul 2019  16:06

defaultVars(prepend="root['INPUTS']['chease.xml']", GUIschema=None, objs=None, debug=False)  # OMFITxml object with xsd file parsed

if objs is None:
    objs = GUIschema[u'xs:schema'][u'xs:element'][u'xs:complexType'][u'xs:all'][u'xs:element']

for obj0 in objs:
    name0 = obj0['@name']
    niceName0 = re.sub('_', ' ', name0)

    # by default hide extra GUI parameters
    if name0.lower() == 'others':
        OMFITx.Tab(niceName0)
        OMFITx.CheckBox("MainScratch['showImasActorsGUIothers']", 'Show extra parameters in this GUI', default=False, updateGUI=True)
        if not MainScratch['showImasActorsGUIothers']:
            continue

    # DOCUMENTATION (help)
    helptxt = ''
    if 'xs:annotation' in obj0 and 'xs:documentation' in obj0['xs:annotation']:
        helptxt = obj0['xs:annotation']['xs:documentation']

    # SIMPLE (Entry)
    if not 'xs:complexType' in obj0:
        if debug:
            print('%s: ENTRY' % name0.ljust(30))
        OMFITx.Entry(prepend + "['%s']" % (name0), niceName0, default=obj0['@default'], help=helptxt)

    # COMPLEX (CompoundGUI)
    elif 'xs:complexType' in obj0 and 'xs:sequence' in obj0['xs:complexType']:
        if 'xs:element' in obj0['xs:complexType']['xs:sequence']:
            if debug:
                print('%s: COMPLEX' % name0.ljust(30))
            OMFITx.Tab(niceName0)
            OMFITx._setDefault(OMFITx._absLocation(prepend + "['%s']" % (name0)), SortedDict())
            OMFITx.CompoundGUI(
                MainScratch['__imasActorGUI__'],
                objs=obj0['xs:complexType']['xs:sequence']['xs:element'],
                prepend=prepend + "['%s']" % (name0),
                debug=debug,
                title='',
            )

    # CHOICE (ComboBox)
    elif 'xs:complexType' in obj0 and 'xs:choice' in obj0['xs:complexType']:
        if debug:
            print('%s: CHOICE' % name0.ljust(30))
        try:
            options = SortedDict()
            for obj1 in tolist(obj0['xs:complexType']['xs:choice']['xs:element']):
                name1 = obj1['@name']
                niceName1 = re.sub('_', ' ', name1)

                options[niceName1] = SortedDict()
                options[niceName1][name1] = SortedDict()

                try:
                    for opt in tolist(obj1[u'xs:complexType'][u'xs:sequence'][u'xs:element']):
                        if '@default' in opt:
                            options[niceName1][name1][opt['@name']] = opt['@default']
                        if '@fixed' in opt:
                            options[niceName1][name1][opt['@name']] = opt['@fixed']
                except KeyError as _excp:
                    printe(treeLocation(obj1)[-1] + ': ' + repr(_excp))
            if len(options):
                OMFITx.ComboBox(prepend + "['%s']" % (name0), options, niceName0, help=helptxt, default=options[options.keys()[0]])
        except KeyError as _excp:
            if debug:
                printe(treeLocation(obj0)[-1] + ': ' + _excp)

    # UNKNOWN (should never happen)
    else:
        print('%s: ??????????' % name0.ljust(30))
