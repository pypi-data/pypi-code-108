import copy

from . import format_fort


def format_bool(d):
    """format TF array"""
    return 'T' if d else 'F'


def format_boolarray(d):
    """format TF array"""
    return ','.join(['T' if i else 'F' for i in d])


def format_intarray(d):
    """format integer array"""
    return ','.join(['{0:d}'.format(i) for i in d])


def format_floatarray(d, format='.12g'):
    """format float array"""
    form = '{0:'+format+'}'
    return ','.join([form.format(i) for i in d])


def format_strarray(d):
    """format string array"""
    return ','.join(["'{0:s}'".format(i) for i in d])


def modl(d, stream):
    """&MODL record"""
    # record keyword
    stream.write(' &MODL ')
    elems = []
    # file
    if 'file' in d:
        for i, f in enumerate(d['file']):
            if f is not None:
                elems.append('FILE({0:d})={1:s}'.format(i+1, f))

    # rdnml
    if 'rdnml' in d:
        elems.append('RDNML='+format_boolarray(d['rdnml']))

    # metric
    if 'metric' in d:
        elems.append('METRIC={0:d}'.format(d['metric']))
    # tram
    if 'tram' in d:
        elems.append('TRAM='+format_bool(d['tram']))
    # surfce
    if 'surfce' in d:
        elems.append('SURFCE={0:d}'.format(d['surfce']))

    if 'klay' in d:
        elems.append('KLAY={0:d}'.format(d['klay']))

    if 'nm' in d:
        elems.append('NM={0:d}'.format(d['nm']))

    if 'lorg' in d:
        elems.append('LORG={0:d}'.format(d['lorg']))

    if 'ichan' in d:
        elems.append('ICHAN='+format_intarray(d['ichan']))

    if 'delta' in d:
        elems.append('DELTA='+format_floatarray(d['delta']))

    if 'tim' in d:
        elems.append('TIM='+format_boolarray(d['tim']))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def xtal_elem(d, stream):
    """&XTAL record"""
    # record keyword
    stream.write(' &XTAL ')
    elems = []

    # only for the first line
    if 'quit' in d:
        elems.append('QUIT='+format_bool(d['quit']))
    if 'news' in d:
        elems.append('NEWS={0:d}'.format(d['news']))
    if 'unit' in d:
        elems.append('UNIT={0:d}'.format(d['unit']))
    if 'base' in d:
        elems.append('BASE={0:f}'.format(d['base']))

    # common for all layer elements
    if 'lyr' in d:
        elems.append('LYR={0:d}'.format(d['lyr']))
    if 'alat' in d:
        elems.append('ALAT='+format_floatarray(d['alat']))
    if 'centre' in d:
        elems.append('CENTRE={0:d}'.format(d['centre']))
    if 'dmax' in d:
        elems.append('DMAX={0:f}'.format(d['dmax']))
    if 'poly' in d:
        elems.append('POLY={0:d}'.format(d['poly']))
    if 'axis' in d:
        da = d['axis']
        if 'axisa' in da:
            elems.append('AXISA='+format_floatarray(da['axisa']))
        if 'axisb' in da:
            elems.append('AXISB='+format_floatarray(da['axisb']))
    if 'rz' in d:
        elems.append('RZ='+format_floatarray(d['rz']))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def xtal(d, stream):
    """&XTAL record, multiple records are allowed"""
    if 'layer' not in d:
        # nothing to do
        return
    for i, re in enumerate(d['layer']):
        i = i + 1
        # create deep copy
        e = copy.deepcopy(re)
        if i == 1:
            # only the first target element, quit, news, unit and base
            # are superimposed
            e['quit'] = d['quit']
            e['news'] = d['news']
            e['unit'] = d['unit']
            e['base'] = d['base']
        # lyr are imposed
        e['lyr'] = i

        xtal_elem(e, stream)


def atom(d, stream):
    """&ATOM record"""
    # record keyword
    stream.write(' &ATOM ')
    elems = []

    ntype = 0

    # atomtbl: ntype, type, z w, inel, equit
    if 'atomtbl' in d and len(d['atomtbl']) > 0:
        # ntype
        ntype = len(d['atomtbl'])
        elems.append('NTYPE={0:d}'.format(ntype))
        types = []
        zs = []
        ws = []
        inels = []
        equits = []
        for a in d['atomtbl']:
            types.append(a['type'])
            zs.append(a['z'])
            ws.append(a['w'])
            inels.append(a['inel'])
            equits.append(a['equit'])
        # type
        elems.append('TYPE='+format_strarray(types))
        # z
        elems.append('Z='+format_floatarray(zs))
        # w
        elems.append('W='+format_floatarray(ws))
        # inel
        elems.append('INEL='+format_intarray(inels))
        # equit
        elems.append('EQUIT='+format_floatarray(equits))

    # lox
    if 'lox' in d:
        elems.append('LOX={0:d}'.format(d['lox']))

    # ebend
    if 'ebnd' in d:
        elems.append('EBND='+format_floatarray(d['ebnd']))

    # lbnd
    if 'lbnd' in d:
        elems.append('LBND={0:d}'.format(d['lbnd']))

    # lock
    if 'lock' in d:
        for i, j in d['lock']:
            elems.append('LOCK({1:d})={0:d}'.format(i, j))

    # order
    if 'order' in d:
        for i, j, val in d['order']:
            if 1 <= i <= ntype:
                elems.append('ORDER({0:d},{1:d})={2:.12g}'.format(i, j, val))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def surf(d, stream):
    # surf is optional
    if d is None:
        return
    # record keyword
    stream.write(' &SURF ')
    elems = []

    # origin
    if 'origin' in d:
        elems.append('ORIGIN='+format_floatarray(d['origin']))
    # lo
    if 'lo' in d:
        elems.append('LO='+format_intarray(d['lo']))
    # lyme
    if 'lyme' in d:
        elems.append('LYME={0:d}'.format(d['lyme']))
    # depth
    if 'depth' in d:
        elems.append('DEPTH='+format_floatarray(d['depth']))
    # sbnd
    # scale
    # sheath
    # calc
    # sides
    if 'sides' in d:
        elems.append('SIDES='+format_floatarray(d['sides']))
    # rsrf
    if 'rsrf' in d:
        elems.append('RSRF='+format_floatarray(d['rsrf']))
    # corner
    if 'corner' in d:
        elems.append('CORNER='+format_floatarray(d['corner']))
    # edge
    if 'edge' in d:
        elems.append('EDGE='+format_floatarray(d['edge']))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def size(d, stream):
    # size record is optional
    if d is None:
        return
    # record keyword
    stream.write(' &SIZE ')
    elems = []
    # rb
    if 'rb' in d:
        elems.append('RB='+format_floatarray(d['rb']))

    # xilim
    if 'xilim' in d:
        elems.append('XILIM='+format_floatarray(d['xilim']))

    # slice
    if 'slice' in d:
        elems.append('SLICE={0:f}'.format(d['slice']))

    # step
    if 'step' in d:
        elems.append('STEP={0:f}'.format(d['step']))

    # lifo
    if 'lifo' in d:
        elems.append('LIFO='+format_bool(d['lifo']))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def outp(d, stream):
    # record keyword
    stream.write(' &OUTP ')
    elems = []

    # drng
    if 'drng' in d:
        elems.append('DRNG='+format_floatarray(d['drng']))
    # lcs
    if 'lcs' in d:
        elems.append('LCS='+format_intarray(d['lcs']))
    # trace
    if 'trace' in d:
        elems.append('TRACE='+format_intarray(d['trace']))
    # look
    if 'look' in d:
        elems.append('LOOK={0:d}'.format(d['look']))
    # grex
    if 'grex' in d:
        elems.append('GREX='+format_bool(d['grex']))
    # inform
    if 'inform' in d:
        elems.append('INFORM='+format_boolarray(d['inform']))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def proj_elem(d, stream):
    """&PROJ record, multiple records are allowed"""
    # record keyword
    stream.write(' &PROJ ')
    elems = []

    # ranx
    if 'ranx' in d:
        elems.append('RANX='+format_intarray(d['ranx']))
    # maxrun
    if 'maxrun' in d:
        elems.append('MAXRUN={0:d}'.format(d['maxrun']))
    # prim
    if 'prim' in d:
        elems.append('PRIM={0:d}'.format(d['prim']))
    # new
    if 'new' in d:
        elems.append('NEW={0:d}'.format(d['new']))
    # ekip
    if 'ekip' in d:
        elems.append('EKIP={0:.12g}'.format(d['ekip']))
    # leap
    if 'leap' in d:
        elems.append('LEAP={0:d}'.format(d['leap']))
    # trmp
    if 'trmp' in d:
        elems.append('TRMP='+format_bool(d['trmp']))
    # raip
    if 'raip' in d:
        elems.append('RAIP='+format_floatarray(d['raip']))
    # laip
    if 'laip' in d:
        elems.append('LAIP={0:d}'.format(d['laip']))
    # refip
    if 'refip' in d:
        elems.append('REFIP='+format_floatarray(d['refip']))
    # lrip
    if 'lrip' in d:
        elems.append('LRIP={0:d}'.format(d['lrip']))
    # miller
    if 'miller' in d:
        elems.append('MILLER='+format_bool(d['miller']))
        if d['miller']:
            # beam
            if 'beam' in d:
                elems.append('BEAM='+format_floatarray(d['beam']))
        else:
            # tha
            if 'tha' in d:
                elems.append('THA={0:.12g}'.format(d['tha']))
            # phi
            if 'phi' in d:
                elems.append('PHI={0:.12g}'.format(d['phi']))
    # dvrg
    if 'dvrg' in d:
        elems.append('DVRG={0:.12g}'.format(d['dvrg']))
    # ngr
    if 'ngr' in d:
        elems.append('NGR={0:d}'.format(d['ngr']))
    # vcr
    if 'vcr' in d:
        elems.append('VCR={0:d}'.format(d['vcr']))

    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def proj(d, stream):
    """&PROJ record, multiple records are allowed"""
    for i in d:
        proj_elem(i, stream)


def vpar(d, ntype, stream):
    """&VPAR record, this is optional"""
    if d['type'] == 'None':
        # nothing to do
        return

    # record keyword
    stream.write(' &VPAR ')

    # should be d['type'] == 'Moliere'
    # d['moliere_param'] may contain all (I,J) pairs 1<=I,J<=SCON.KIND
    # but output only (I,J) <= ntype

    elems = []
    bpar = d['moliere_param']['BPAR']
    for i in range(1, ntype+1):
        for j in range(i, ntype+1):
            key = (i, j)
            if key in bpar:
                elems.append('BPAR({0:d},{1:d})={2:f}'.format(i, j, bpar[key]))
    stream.write(format_fort.format_fort(elems))
    stream.write('/\n')


def to_marlowe(rd, stream):
    """tranlate gui data obtained by get() method to marlowe control format
    d is parameter data compatible to guidata.default"""

    # make deepcopy
    d = copy.deepcopy(rd['root'])

    # &modl.klay = len(xtal.layer)
    d['modl']['klay'] = len(d['xtal']['layer'])

    # &modl.RDNML
    d['modl']['rdnml'] = [False] * 6

    # &modl.RDNML(3)
    if d['size'] is not None:
        d['modl']['rdnml'][2] = True

    # surface
    # &modl.surfce = surf.surfce
    d['modl']['surfce'] = d['surf']['surfce']
    # &modl.RDNML(1)
    if d['modl']['klay'] > 1 or d['modl']['surfce'] > 0:
        d['modl']['rdnml'][0] = True

    # consider internal primary atom mode
    if d['modl']['klay'] == 1 and d['modl']['surfce'] == -1:
        d['modl']['rdnml'][0] = True
        d['modl']['surfce'] = 0
    elif d['modl']['rdnml'][0]:
        # drop side[2] and rsrf[2]
        if len(d['surf']['sides']) > 2:
            del d['surf']['sides'][2:]
        if len(d['surf']['rsrf']) > 2:
            del d['surf']['rsrf'][2:]

    # set &SURF.DEPTH, ORIGN, LO, which are imported from gui_layer
    if not d['modl']['rdnml'][0]:
        # no surface mode
        d['surf'] = None
    else:
        d['surf']['depth'] = []
        d['surf']['origin'] = []
        d['surf']['lo'] = []

        for layer in d['xtal']['layer']:
            d['surf']['depth'].append(layer['surfopt']['depth'])
            d['surf']['lo'].append(layer['surfopt']['lo'])
            d['surf']['origin'] += layer['surfopt']['origin']

    # set &XTAL.RZ, &ATOM.LOCK, &ATOM.ORDER, &ATOM.EBND
    atom_lock = []  # [(I, J) for LOCK(J)=I)]
    atom_order = []  # [(I, J, VAL) for ORDER(I,J)=VAL]
    atom_ebnd = []
    site_id = 1
    for lay in d['xtal']['layer']:
        rz = []
        if 'site' not in lay:
            continue
        for s in lay['site']:
            rz += s['rz']
            lock = s['lock']
            # atom_lock
            atom_lock.append((lock, site_id))
            # atom_order
            if lock == -1:
                # dump ORDER(I,J)=VAL all anyway
                # index base starts from 1
                # so i == scon.kind+1 is regarded as vacancy (but is not used)
                for i, v in enumerate(s['order']):
                    atom_order.append((i+1, site_id, v))
            # atom_ebnd
            atom_ebnd += s.get('ebnd', [0.0, 0.0, 0.0])

            # next site
            site_id += 1
        # creat new entry for 'rz' for current layer
        if rz:
            lay['rz'] = rz
    # create new entry atom.lock and atom.order
    d['atom']['lock'] = atom_lock
    d['atom']['order'] = atom_order
    d['atom']['ebnd'] = atom_ebnd

    # translate &SIZE.XILIM(1) and (3) from nm to base unit
    if 'size' in d and d['size'] and 'xilim' in d['size']:
        # get base length
        if d['xtal']['unit'] == 1:
            base = d['xtal']['layer'][0]['alat'][0]
        elif d['xtal']['unit'] == 2:
            base = d['xtal']['layer'][0]['alat'][1]
        elif d['xtal']['unit'] == 3:
            base = d['xtal']['layer'][0]['alat'][2]
        elif d['xtal']['unit'] == 0:
            base = 1.0
        elif d['xtal']['unit'] == -1:
            base = d['xtal']['base']
        # AA -> nm
        if d['modl']['metric'] == 1:
            base /= 10

        d['size']['xilim'][0] /= base
        d['size']['xilim'][2] /= base

    # VPAR record
    if 'vpar' in d and d['vpar']['type'] != 'None':
        # lit &MODL.RDNML(4) flag
        d['modl']['rdnml'][3] = True
    else:
        # add fake record
        d['vpar'] = {'type': 'None'}

    # comment1
    stream.write('{0:s}\n'.format(d['comment1']))
    # comment2
    stream.write('{0:s}\n'.format(d['comment2']))

    modl(d['modl'], stream)
    xtal(d['xtal'], stream)
    atom(d['atom'], stream)
    surf(d['surf'], stream)
    size(d['size'], stream)
    ntype = len(d['atom'].get('atomtbl', []))
    vpar(d['vpar'], ntype, stream)
    outp(d['outp'], stream)
    proj(d['proj'], stream)
