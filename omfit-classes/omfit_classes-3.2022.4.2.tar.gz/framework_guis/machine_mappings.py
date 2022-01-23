from pprint import pformat

if compare_version(omas.__version__, '0.70') < 0:
    raise Exception('machine to OMAS mappings is supported only after version 0.70.0 of OMAS')

from omas.omas_machine import machine_to_omas, machine_mappings, machine_expression_types, reload_machine_mappings
from omas.omas_utils import *
from omas.omas_physics import cocos_signals

json_opts = dict(indent=1, separators=(',', ': '), sort_keys=True)

OMFITx.TitleGUI('Machine to OMAS mapper GUI')

if 'omas_mappings' not in scratch:
    scratch['omas_mappings'] = {}
scratch['omas_mappings']['user'] = os.environ['USER']


def load_ids():
    if 'omas_mappings' not in OMFIT:
        OMFIT['omas_mappings'] = {}
    OMFIT['omas_mappings']['ids_info'] = omas_info(scratch['omas_mappings']['IDS'])


def load_tree():
    if 'omas_mappings' not in OMFIT:
        OMFIT['omas_mappings'] = {}
    treename = scratch['omas_mappings']['treename'].format(**scratch['omas_mappings']['options'])
    OMFIT['omas_mappings'][treename] = OMFITmds(scratch['omas_mappings']['machine'], treename, scratch['omas_mappings']['pulse'])


def set_machine(location):
    scratch['omas_mappings']['machine'] = tokamak(scratch['omas_mappings']['machine'], 'GPEC')
    reset_confidence()


def set_defaults(location=None):
    scratch['omas_mappings']['location'] = o2u(scratch['omas_mappings']['location'])

    if scratch['omas_mappings']['location'] in mappings:
        scratch['omas_mappings'].update(mappings[scratch['omas_mappings']['location']])
        for exp in machine_expression_types:
            if exp in mappings[scratch['omas_mappings']['location']]:
                scratch['omas_mappings']['expression_type'] = exp
                break
        if 'options' not in scratch['omas_mappings']:
            scratch['omas_mappings']['options'] = {}
        for k in mappings['__options__']:
            if k in scratch['omas_mappings'][scratch['omas_mappings']['expression_type']]:
                scratch['omas_mappings']['options'][k] = mappings['__options__'][k]


def clear_old_expression(location):
    if scratch['omas_mappings']['expression_type'] in scratch['omas_mappings']:
        del scratch['omas_mappings'][scratch['omas_mappings']['expression_type']]
    reset_confidence()


def clear_old_location(location):
    scratch['omas_mappings']['location'] = ''
    reset_confidence()


def reset_confidence(location=None):
    scratch['omas_mappings']['confidence'] = 0


# ================

with OMFITx.same_row():
    OMFITx.Entry(
        "scratch['omas_mappings']['machine']",
        'Device',
        default=tokamak(MainSettings['EXPERIMENT']['device'], 'GPEC'),
        postcommand=set_machine,
        updateGUI=True,
    )
    OMFITx.Entry("scratch['omas_mappings']['pulse']", 'Shot', default=MainSettings['EXPERIMENT']['shot'])
    OMFITx.Button('Reset mappings', reload_machine_mappings, updateGUI=True)
scratch['omas_mappings']['branch'] = ''
# OMFITx.ComboBox("scratch['omas_mappings']['branch']", {'Local': '', 'master': 'master'}, 'GitHub branch', default=None, state='normal')

OMFITx.Separator()

# ================

mappings = machine_mappings(scratch['omas_mappings']['machine'], scratch['omas_mappings']['branch'])

if 'location' not in scratch['omas_mappings']:
    scratch['omas_mappings']['IDS'] = 'equilibrium'
    scratch['omas_mappings']['location'] = 'equilibrium.time_slice.:.global_quantities.ip'
    set_defaults()

mapped_idss = np.unique([k.split('.')[0] for k in mappings.keys()])
m_in_idss = lambda m: '@ ' + m if m in mapped_idss else m
idss = {m_in_idss(k): k for k in list_structures('develop.3')}

with OMFITx.same_row():

    OMFITx.ComboBox(
        "scratch['omas_mappings']['IDS']",
        idss,
        'IDS',
        help=pformat(omas_info_node(scratch['omas_mappings']['IDS'])),
        updateGUI=True,
        state='search',
        postcommand=clear_old_location,
    )
    OMFITx.Button('Load this IDS', load_ids)

# list of possible locations (we hide obsolescent values on purpose!)
m_in_mapping = lambda m: '@ ' + m if m in mappings else m
locations = {}
for k in map(
    lambda x: scratch['omas_mappings']['IDS'] + '.' + o2u(x),
    omas_info(scratch['omas_mappings']['IDS'])[scratch['omas_mappings']['IDS']].flat().keys(),
):
    if omas_info_node(m_in_mapping(k)).get('lifecycle_status', '') != 'obsolescent':
        locations[m_in_mapping(k)] = k

OMFITx.ComboBox(
    "scratch['omas_mappings']['location']",
    locations,
    'IMAS path',
    width=55,
    help=pformat(omas_info_node(scratch['omas_mappings']['location'])),
    updateGUI=True,
    state='search',
    postcommand=set_defaults,
)

OMFITx.ComboBox(
    "scratch['omas_mappings']['expression_type']",
    machine_expression_types,
    'Expression trype',
    updateGUI=True,
    postcommand=clear_old_expression,
)

OMFITx.Entry(
    "scratch['omas_mappings']['%s']" % scratch['omas_mappings']['expression_type'],
    scratch['omas_mappings']['expression_type'],
    default=mappings.get(scratch['omas_mappings']['location'], {}).get(scratch['omas_mappings']['expression_type'], ''),
    postcommand=reset_confidence,
    multiline=True,
)

if scratch['omas_mappings']['location'] in cocos_signals:
    cocos_options = SortedDict()
    cocos_options['?'] = '?'
    for cocos_rule in mappings['__cocos_rules__']:
        if scratch['omas_mappings']['location'] in mappings and re.findall(
            cocos_rule, mappings[scratch['omas_mappings']['location']]['TDI']
        ):
            cocos_options = {'auto': '?'}
            scratch['omas_mappings']['COCOSIO'] = '?'
    cocos_options.update({str(k): k for k in list(range(1, 9)) + list(range(11, 19))})

    OMFITx.ComboBox("scratch['omas_mappings']['COCOSIO']", cocos_options, 'COCOS', default='?', state='normal')
elif 'COCOSIO' in scratch['omas_mappings']:
    del scratch['omas_mappings']['COCOSIO']

if 'TDI' in scratch['omas_mappings']['expression_type']:
    with OMFITx.same_row():
        OMFITx.Entry("scratch['omas_mappings']['treename']", 'treename')
        OMFITx.Button('Load this MDS+ tree', load_tree)

OMFITx.Entry("scratch['omas_mappings']['options']", 'Default options', default={})

# ================
OMFITx.Separator()


def test_mapping():
    user_machine_mappings = get_json_mapping()
    location = 'equilibrium.time_slice.:.global_quantities.beta_normal'
    ods, raw_data = machine_to_omas(
        ODS(),
        scratch['omas_mappings']['machine'],
        scratch['omas_mappings']['pulse'],
        scratch['omas_mappings']['location'],
        options={},
        branch='',
        user_machine_mappings=user_machine_mappings,
    )
    if 'omas_mappings' not in OMFIT:
        OMFIT['omas_mappings'] = {}
    OMFIT['omas_mappings']['raw_data'] = raw_data
    OMFIT['omas_mappings']['ods'] = ods
    data = ods[scratch['omas_mappings']['location']]
    info = omas_info_node(scratch['omas_mappings']['location'])
    printi(f"Successful retrieval of {scratch['omas_mappings']['location']}")
    if hasattr(ods[scratch['omas_mappings']['location']], 'shape'):
        printi(f"{scratch['omas_mappings']['location']} has shape {ods[scratch['omas_mappings']['location']].shape}")
        if len(squeeze(data).shape) == 1:
            plot(squeeze(data))
            title(scratch['omas_mappings']['location'])
            if 'units' in info:
                ylabel(f"[{info['units']}]")
            xlabel('1 st dimension')
        elif len(squeeze(data).shape) == 2:
            cs = contourf(squeeze(data))
            title(scratch['omas_mappings']['location'])
            if 'units' in info:
                colorbar(cs).set_label(f"[{info['units']}]")
            xlabel('2 st dimension')
            ylabel('1 nd dimension')
    else:
        printi(f"Value is: {ods[scratch['omas_mappings']['location']]}")
    pprint(info)


def get_json_mapping():
    tmp = {
        '__options__': scratch['omas_mappings']['options'],
        scratch['omas_mappings']['location']: {
            scratch['omas_mappings']['expression_type']: scratch['omas_mappings'][scratch['omas_mappings']['expression_type']]
        },
    }
    if 'TDI' in scratch['omas_mappings']['expression_type']:
        tmp[scratch['omas_mappings']['location']]['treename'] = scratch['omas_mappings']['treename']
    if 'COCOSIO' in scratch['omas_mappings'] and scratch['omas_mappings']['COCOSIO'] != '?':
        tmp[scratch['omas_mappings']['location']]['COCOSIO'] = scratch['omas_mappings']['COCOSIO']
    return tmp


def print_mapping():
    print('-' * 20)
    printi(json.dumps(get_json_mapping(), **json_opts))


def inject_mapping(update=False):
    from omas.omas_machine import _machine_mappings, _user_machine_mappings

    pprint(get_json_mapping())
    _user_machine_mappings.update(get_json_mapping())
    mappings = machine_mappings(scratch['omas_mappings']['machine'], '')
    if scratch['omas_mappings']['location'] in mappings:
        printi(f"{scratch['omas_mappings']['location']} **TEMPORARILY** added to mapping definitions")
    else:
        raise Exception(f"Failed to add {scratch['omas_mappings']['location']} to mapping definitions")


def update_mapping():
    from omas.omas_machine import update_mapping

    update_mapping(
        machine=scratch['omas_mappings']['machine'],
        location=scratch['omas_mappings']['location'],
        value=get_json_mapping()[scratch['omas_mappings']['location']],
        cocosio=None,
        default_options=scratch['omas_mappings']['options'],
        update_path=False,
    )


with OMFITx.same_row():
    OMFITx.Button('Print', print_mapping)
    OMFITx.Button('Test', test_mapping)
    OMFITx.Button('Inject', inject_mapping)
    OMFITx.Button('Update', update_mapping)


# ================


def suggest_mapping():
    from omas.omas_mongo import get_mongo_credentials
    from pymongo import MongoClient

    server = omas_rcparams['default_mongo_server']
    database = 'omas'
    collection = 'mappings'
    client = MongoClient(server.format(**get_mongo_credentials(server, database, collection)))
    db = client[database]
    coll = db[collection]
    print_mapping()
    res = coll.update(
        {'user': os.environ['USER'], 'location': scratch['omas_mappings']['location']}, copy.copy(scratch['omas_mappings']), upsert=True
    )
    if res['updatedExisting']:
        printw(f'Suggestion updated')
    else:
        printw(f'Suggestion posted')
    # printw(pformat(res))
    return str(res)


OMFITx.Separator()
with OMFITx.same_row():
    OMFITx.Slider("scratch['omas_mappings']['confidence']", [0, 3, 1], 'Confidence level', digits=0, default=1)
    OMFITx.Button('Suggest mapping', suggest_mapping)
