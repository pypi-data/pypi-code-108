try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.utils_base import _streams
from omfit_classes.omfit_json import OMFITjson
from omfit_classes.omfit_base import OMFITexpression, evalExpr
from omfit_classes.omfit_mds import translate_MDSserver, tunneled_MDSserver

import numpy as np
import glob
import omas
from omas import *


# hook up function to process OMFITexpressions
def process_OMFITexpression(value):
    if isinstance(value, OMFITexpression):
        return evalExpr(value)
    return value


try:
    omas.omas_core.input_data_process_functions.append(process_OMFITexpression)
except AttributeError:
    # avoid OMFIT not starting if OMAS version is not the latest
    printe(f'WARNING: Your OMAS installation {os.path.dirname(omas.__file__)} is old. Please update it.')

# hook up omfit and omas print streams
omas.omas_utils._streams = _streams


def tunnel_mds(server, treename):
    """
    Resolve MDS+ server
    NOTE: This function makes use of the optional `omfit_classes` dependency to establish a SSH tunnel to the MDS+ server.

    :param server: MDS+ server address:port

    :param treename: treename (in case treename affects server to be used)

    :return: string with MDS+ server and port to be used
    """
    try:
        import omfit_classes.omfit_mds
    except (ImportError, ModuleNotFoundError):
        return server.format(**os.environ)
    else:
        server0 = omfit_classes.omfit_mds.translate_MDSserver(server, treename)
        tunneled_server = omfit_classes.omfit_mds.tunneled_MDSserver(server0, quiet=False)
        return tunneled_server

    return server.format(**os.environ)


try:
    omas.omas_machine.tunnel_mds = tunnel_mds
except AttributeError:
    # avoid OMFIT not starting if OMAS version is not the latest
    printe(f'WARNING: Your OMAS installation {os.path.dirname(omas.__file__)} is old. Please update it.')

# export __all__ from omas.__all__
__all__ = list([x for x in ['omas'] + list(omas.__dict__.keys()) if not x.startswith('_')])


def pprint_imas_data_dictionary_info(location):
    """
    pretty print IMAS data dictionary info

    :param location: location in IMAS data dictionary
    """
    location = omas.omas_utils.p2l(location)
    location = omas.omas_utils.l2u(location)
    info = omas_info_node(location.rstrip('.:'))
    printi('\n' + location)
    printi('-' * len(location))
    prioritize = ['documentation', 'units', 'data_type', 'coordinates']
    skip = ['full_path', 'structure_reference', 'type']
    for item in prioritize:
        if item in info:
            printi(f'* {item}: ', end='')
            print(f'{info[item]}')
    for item in sorted(info):
        if item not in prioritize + skip:
            printi(f'* {item}: ', end='')
            print(f'{info[item]}')


def _base_omas_remote(
    serverPicker,
    target_function,
    python_script='from omas import *',
    python_prelude=None,
    python_command=None,
    quiet=False,
    forceRemote=False,
    IMAS_module=None,
    OMAS_module=None,
    UDA_module=None,
    **kw,
):
    r"""
    low-level function that uses OMFITx.remote_python to interface with remote IMAS servers

    :param serverPicker: remote server name

    :param target_function: 'save_omas_imas' or 'load_omas_imas'

    :param python_script: string with python script to execute 'from omas import *'

    :param python_prelude: anything before the python command

    :param python_command: python command

    :param quiet: verbose output or not

    :param forceRemote: force remote connection

    :param IMAS_module: allow specifying IMAS module version when doing `module load XXX`

    :param OMAS_module: allow specifying OMAS module version when doing `module load XXX`

    :param UDA_module: allow specifying UDA module version when doing `module load XXX`

    :param \**kw: parameters to be fed to the target_function

    :return: output of the target function
    """

    serverPicker = SERVER(serverPicker)

    # set python_prelude and python_command based on what is run and where
    if python_prelude is not None and python_command is not None:
        pass

    elif python_prelude is not None and python_command is None:
        raise ValueError('If python_prelude is specified, so must be python_command')

    elif python_prelude is None and python_command is not None:
        raise ValueError('If python_command is specified, so must be python_prelude')

    elif 'iter' in target_function or is_server(serverPicker, ['iter']):

        if IMAS_module is None:
            IMAS_module = 'IMAS'

        if OMAS_module is None:
            OMAS_module = 'OMAS'

        python_prelude = '''#!/bin/sh -l
module purge
module load {IMAS_module}
# module load {OMAS_module} ## disabled since OMAS module at ITER is not kept up-to-date
export PYTHONPATH=/home/ITER/menghio/atom/omas:$PYTHONPATH
export PYTHONPATH=/home/ITER/menghio/atom/omas/site-packages:$PYTHONPATH
imasdb {machine}
'''

    elif is_server(serverPicker, ['altair', 'andromede']):

        if IMAS_module is None:
            IMAS_module = 'IMAS'

        if OMAS_module is None:
            OMAS_module = 'OMAS'

        python_prelude = '''#!/bin/sh -l
module purge
module load {IMAS_module}/3.30.0-4.8.4
# module load {OMAS_module} ## disabled since OMAS module at WEST does not exist
export PYTHONPATH=/Applications/omfit/atom/omas:$PYTHONPATH
export PYTHONPATH=/Applications/omfit/atom/omas/site-packages:$PYTHONPATH
imasdb {machine}
'''

    elif is_server(serverPicker, 'itm_gateway'):

        if IMAS_module is None:
            IMAS_module = 'imasenv'

        if OMAS_module is None:
            OMAS_module = 'omas'

        # notice no `module purge` for itm_gateway
        python_prelude = '''#!/bin/sh -l
module load {IMAS_module}
module load {OMAS_module}
imasdb {machine}
'''

    elif is_server(serverPicker, ['freia', 'heimdall']):
        python_prelude = '''#!/bin/sh -l
module purge
module load imas-modules
module load imasenv/3.23.3
module load OMAS
export PYTHONPATH=/common/transp_shared/omfit/atom-dev/omas/site-packages:$PYTHONPATH
imasdb {machine}
'''

    elif is_server(serverPicker, ['sophie']):
        python_prelude = '''#!/bin/sh -l
module purge
module use /work/imas/etc/modulefiles
module load java/jdk/1.8.0_231
module load python/3.6/9
module load mdsplus/alpha3
module load Blitz++/0.10p
module load GCC/6.5.0
module load IMAS4OMAS
imasdb {machine}
'''
    else:
        if is_localhost(serverPicker):
            python_command = sys.executable
        else:
            python_command = 'python'

    # use the default Python from the module load IMAS_module
    if python_command is None:
        python_command = 'python'

    if python_prelude is None:
        python_prelude = ''

    # if IMAS_module/OMAS_module have not been set yet, set them as imas/omas
    if IMAS_module is None:
        IMAS_module = 'imas'

    if OMAS_module is None:
        OMAS_module = 'omas'

    if UDA_module is None:
        UDA_module = 'uda'

    # note: user=None gets the user on remote
    user = kw.pop('user', None)
    if user is None:
        user = parse_server(SERVER[serverPicker]['server'])[0]
    if user:
        kw['user'] = user

    # substitute format strings
    python = (
        python_prelude.strip().format(
            machine=kw.get('machine', ''), IMAS_module=IMAS_module, OMAS_module=OMAS_module, UDA_module=UDA_module, user=user
        )
        + '\nexport OMAS_DEBUG_STDOUT=1\n'
        + python_command
    )

    import omfit_classes.OMFITx as OMFITx

    return OMFITx.remote_python(
        None,
        executable=python + ' -u %s',
        python_script=python_script,
        target_function=target_function,
        workdir='./',
        server=SERVER[serverPicker]['server'],
        tunnel=SERVER[serverPicker]['tunnel'],
        remotedir=os.path.abspath(str(SERVER[serverPicker]['workdir']) + os.sep + 'OMAS_tmp') + os.sep,
        namespace=kw,
        quiet=quiet,
        forceRemote=forceRemote,
    )


def save_omas_imas_remote(serverPicker, ods, **kw):
    r"""
    Save OMAS data set to a remote IMAS server

    :param serverPicker: remote server name where to connect to

    :param \**kw: all other parameters are passed to the save_omas_imas function
    """
    kw['ods'] = ods
    return _base_omas_remote(serverPicker, 'save_omas_imas', **kw)


try:
    save_omas_imas_remote.__doc__ += save_omas_imas.__doc__.replace('\n    ', '\n        ')
except (NameError, AttributeError):
    pass


def load_omas_imas_remote(serverPicker, **kw):
    r"""
    Load OMAS data set from a remote IMAS server

    :param serverPicker: remote server name where to connect to

    :param \**kw: all other parameters are passed to the load_omas_imas function
    """
    return _base_omas_remote(serverPicker, 'load_omas_imas', **kw)


try:
    load_omas_imas_remote.__doc__ += load_omas_imas.__doc__.replace('\n    ', '\n        ')
except (NameError, AttributeError):
    pass


def load_omas_uda_remote(serverPicker, **kw):
    r"""
    Load OMAS data set from a remote UDA server

    :param serverPicker: remote server name where to connect to

    :param \**kw: all other parameters are passed to the load_omas_uda function
    """
    kw['user'] = False
    return _base_omas_remote(serverPicker, 'load_omas_uda', **kw)


try:
    load_omas_uda_remote.__doc__ += load_omas_uda.__doc__.replace('\n    ', '\n        ')
except (NameError, AttributeError):
    pass


def browse_imas_remote(serverPicker, **kw):
    r"""
    Browse available IMAS data (machine/pulse/run) for given user on remote IMAS server

    :param serverPicker: remote server name where to connect to

    :param \**kw: all other parameters are passed to the browse_imas function
    """
    return _base_omas_remote(serverPicker, 'browse_imas', **kw)


try:
    load_omas_imas_remote.__doc__ += load_omas_imas.__doc__.replace('\n    ', '\n        ')
except (NameError, AttributeError):
    pass


class OMFITiterscenario(OMFITjson):
    def __str__(self):
        output = []
        space = 2
        fields = {k: len(k) + space for k in list(self.values())[0]}
        for item in self:
            for k in fields:
                fields[k] = max([fields[k], len('%s' % self[item][k]) + space])
        header = ''.join([k.ljust(fields[k]) for k in fields])
        output.append(header)
        output.append('-' * len(header))
        for item in self:
            row = []
            for k in fields:
                row.append(('%s' % self[item][k]).ljust(fields[k]))
            output.append(''.join(row))
        return '\n'.join(output)

    def filter(self, conditions, squash=False):
        """
        Filter database for certain conditions

        :param conditions: dictionary with conditions for returning a match. For example:
                {'List of IDSs':['equilibrium','core_profiles','core_sources','summary'], 'Workflow':'CORSICA', 'Fuelling':'D-T'}

        :param squash: remove attributes that are equal among all entries

        :return: OMFITiterscenario dictionary only with matching entries
        """
        matches = OMFITiterscenario('filtered.json')

        for item in self:
            match = True
            for cnd in conditions:
                # mismatch of None
                if self[item][cnd] is not None and conditions[cnd] is None:
                    match = False
                # mismatch of None
                elif self[item][cnd] is None and conditions[cnd] is not None:
                    match = False
                # mismatch of strings
                elif isinstance(self[item][cnd], str) and conditions[cnd] not in self[item][cnd]:
                    match = False
                # mismatch of numbers
                elif isinstance(self[item][cnd], (int, float)) and conditions[cnd] != self[item][cnd]:
                    match = False
                # mismatch of entries in a list
                elif isinstance(self[item][cnd], list) and not np.all([v in self[item][cnd] for v in conditions[cnd]]):
                    match = False
            if match:
                matches[item] = copy.deepcopy(self[item])

        if squash and len(matches) > 1:
            fields = [k for k in list(self.values())[0]]
            different_fields = []
            for k in fields:
                if np.all([matches[item][k] == list(matches.values())[0][k] for item in matches]):
                    for item in matches:
                        del matches[item][k]

        return matches


def iter_scenario_summary_remote(quiet=False, environment="module purge\nmodule load IMAS"):
    """
    Access iter server and sun `scenario_summary` command

    :param quiet: print output of scenario_summary to screen or not

    :param environment: `module load {IMAS_module}` or the like

    :return: dictionary with info from available scenarios
    """

    # fields to be read
    # 'composition',
    what = [
        'ref_name',
        'ro_name',
        'shot',
        'run',
        'type',
        'workflow',
        'database',
        'confinement',
        'ip',
        'b0',
        'fuelling',
        'ne0',
        'zeff',
        'npeak',
        'p_hcd',
        'p_ec',
        'p_ic',
        'p_nbi',
        'p_lh',
        'location',
        'idslist',
    ]

    # execute scenario_summary remotely
    executable = (
        environment
        + '''
scenario_summary -c {what}
'''.format(
            what=','.join(what)
        )
    )
    std_out = []
    std_err = []
    import omfit_classes.OMFITx as OMFITx

    try:
        OMFITx.remote_execute(
            SERVER['iter_login']['server'],
            executable,
            './',
            tunnel=SERVER['iter_login']['tunnel'],
            std_out=std_out,
            std_err=std_err,
            quiet=True,
        )
        # identify scenario_summary block
        # (read data in reverse order because the ITER terminal prints out a lot of unwanted infos when connecting)
        count = 0
        for k, line in enumerate(reversed(std_out)):
            if line.startswith('----'):
                if count != 0:
                    break
                count = k
        header = std_out[-k - 2]
        headers = re.sub(r'\s\s+', '\t', header).strip().split('\t')
        header_start = [header.index(h) for h in headers] + [None]
        scenario_summary = std_out[-k : len(std_out) - count - 1]
    except Exception:
        tag_print('\n'.join(std_out), tag='PROGRAM_OUT')
        tag_print('\n'.join(std_err), tag='PROGRAM_ERR')
        raise
    # print original output to screen
    if not quiet:
        print('\n'.join(std_out[-k - 3 : len(std_out) - count]))

    # parse scenario_summary output
    scenarios = OMFITiterscenario('iter_scenarios.json')
    for li, line in enumerate(scenario_summary):
        items = []
        for hi, start in enumerate(header_start[:-1]):
            items.append(line[start : header_start[hi + 1]].strip())
        if len(items) != len(headers):
            print('items=', items)
            print('headers=', headers)
            print('Error in parsing table')
            raise OMFITexception('Did not parse scenario summary table correctly')
        scenario = dict(list(zip(map(lambda x: x.strip(), headers), items)))
        for k in headers:
            if scenario[k] == 'tbd':
                scenario[k] = None
        for k in [h for h in headers if '[' in h] + ['Zeff']:
            try:
                scenario[k] = float(scenario[k])
            except (TypeError, ValueError):
                pass
        for k in ['Pulse', 'Run']:
            scenario[k] = int(scenario[k])
        for k in ['List of IDSs']:
            scenario[k] = scenario[k].split()
        scenarios['%d_%d' % (scenario['Pulse'], scenario['Run'])] = scenario

    return scenarios


def load_omas_iter_scenario_remote(**kw):
    r"""
    Load OMAS iter scenario from a remote ITER IMAS server

    :param \**kw: all other parameters are passed to the load_omas_iter_scenario function
    """
    kw['user'] = False
    return _base_omas_remote('iter_login', 'load_omas_iter_scenario', **kw)


try:
    load_omas_iter_scenario_remote.__doc__ += load_omas_iter_scenario.__doc__.replace('\n    ', '\n        ')
except (NameError, AttributeError):
    pass

ods_method_list = [func for func in dir(ODS) if callable(getattr(ODS, func)) and not func.startswith("__")]


class OMFITods(OMFITobject, ODS):
    def __init__(self, filename, **kw):
        ODS_kw = function_arguments(ODS.__init__)[1]
        for kwarg in list(kw.keys()):
            if kwarg in ODS_kw:
                ODS_kw[kwarg] = kw.pop(kwarg)
        OMFITobject.__init__(self, filename, **kw)
        self.dynaLoad = False
        ODS.__init__(self, **ODS_kw)
        self.dynaLoad = True

    def __getstate__(self):
        from omas.omas_core import omas_dictstate

        state = {}
        for item in omas_dictstate + [
            'OMFITproperties',
            'dynaLoad',
            'modifyOriginal',
            'readOnly',
            'file_type',
            'originalFilename',
            'filename',
            'link',
        ]:
            if item in self.__dict__:
                state[item] = self.__dict__[item]
        return state

    @dynaLoad
    def load(self):
        ODS.load(self, self.filename)

    @dynaSave
    def save(self):
        tmp = ODS()
        tmp.copy_attrs_from(self)
        tmp.update(self)
        tmp.save(self.filename)

    for func in ods_method_list:
        if func not in ['save', 'load']:
            exec(
                '''
def {func}(self, *args, **kw):
    r"""{doc}"""
    dynaLoader(self)
    return ODS.{func}(self, *args, **kw)
'''.format(
                    func=func, doc=getattr(ODS, func).__doc__
                )
            )


# use OMFIT MDS+ tunneling within OMAS
if compare_version(omas.__version__, '0.70') >= 0:

    def mds_machine_to_server_mapping(machine, treename, quiet=False):
        server0 = translate_MDSserver(machine, treename)
        tunneled_server = tunneled_MDSserver(server0, quiet=quiet)
        return tunneled_server

    from omas import omas_machine

    omas.omas_machine.mds_machine_to_server_mapping = mds_machine_to_server_mapping

__all__.extend(
    [
        'save_omas_imas_remote',
        'load_omas_imas_remote',
        'load_omas_uda_remote',
        'browse_imas_remote',
        'iter_scenario_summary_remote',
        'load_omas_iter_scenario_remote',
        'OMFITiterscenario',
        'OMFITods',
        'pprint_imas_data_dictionary_info',
    ]
)

if __name__ == '__main__':
    test_classes_main_header()  # Sets output to PDF if no display & changes to temporary directory to avoid messes

    ods = ODS()  # Just make sure it can initialize
