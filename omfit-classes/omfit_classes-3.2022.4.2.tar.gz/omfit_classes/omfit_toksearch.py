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

from sys import version_info
from socket import gethostname
from psutil import virtual_memory
from omfit_classes.utils_fusion import is_device

__all__ = ['OMFITtoksearch', 'TKS_MdsSignal', 'TKS_PtDataSignal', 'TKS_Aligner', 'TKS_OMFITLoader']

# https://vali.gat.com/toksearch/toksearch

# CONSTANTS
LOGIN_NODE_LIMIT = 5  # max gb fetch on iris login node, set by policy
SERVER_MEM = {'iris': 120, 'saga': 120}  # TO DO: need to use remote_sysinfo to find this
SERVER_NAME = gethostname().split('.')[0]
PYTHON_VERSION = version_info[0]
TOKSEARCH_VERSION = 'toksearch/release'

allowed_partitions = set(['short', 'medium', 'long', 'nodes'])

bash_script = """#!/bin/sh -l
#SBATCH --job-name=toksearch_omfit_remote
#SBATCH --output=toksearch_omfit_remote.out
#SBATCH --partition={partition}
#SBATCH --ntasks={n}
#SBATCH --nodes=1
#SBATCH --mem={mem}G
#SBATCH --time={hours}:{minutes}:00
CUDA_VISIBLE_DEVICES=''
module purge
module load %s
python3 toksearch_python.py
"""

executables = {'iris': 'sbatch %s',
               'saga': 'sbatch %s',
               'iris_batch': bash_script % (TOKSEARCH_VERSION),
               'saga_batch': bash_script % (TOKSEARCH_VERSION)}

login_nodes = set(('irisa', 'irisb', 'irisc', 'irisd'))

toksearchQueryString = """
def toksearchQueryRun(shots, signals, server_info, datasets=None, aligners=None, functions=None, where=None, keep=None,
                      compute_type='ray', return_data='by_shot', warn=True, use_dask=True, **compute_kwargs):
    from sys import path
    path.insert(0, '/fusion/projects/omfit-results/toksearch')
    from toksearchQuery import toksearchQuery
    return toksearchQuery(shots, signals, server_info, datasets, aligners, functions, where, keep,
                          compute_type, return_data, warn, use_dask, **compute_kwargs)
"""


# helper functions
def format_time_limit(hours=1,minutes=0):
    #avoid invalid times
    minutes = int(minutes)
    hours = int(hours)
    if minutes < 0 or minutes > 60:
        raise ValueError('Minutes for time limit must be an integer between [0,60), you entered: %s'%(minutes))
    if hours < 0 or hours > 24:
        raise ValueError('Hours for time limit must be an integer between [0,24], you entered: %s'%(hours))
    hours = '%02d'%(hours)
    minutes = '%02d'%(minutes)
    return hours, minutes

def server_info():
    from resource import getrusage, RUSAGE_SELF
    return {'start_memory_usage': getrusage(RUSAGE_SELF).ru_maxrss,
            'omfit_server': SERVER_NAME,
            'memory_available': virtual_memory().available,
            'python_version': PYTHON_VERSION}


def toksearch_wrapper(basename, *args, **kw):
    kw = {} if kw is None else kw
    args = [] if args is None else args
    return [basename, args, kw]


def TKS_MdsSignal(*args, **kw):
    return toksearch_wrapper('MdsSignal', *args, **kw)


def TKS_PtDataSignal(*args, **kw):
    return toksearch_wrapper('PtDataSignal', *args, **kw)


def TKS_OMFITLoader(*args, **kw):
    return toksearch_wrapper('OMFITLoader', *args, **kw)


def TKS_Aligner(align_with, **kw):
    '''
    Function that takes in a signal name, and keyword arguments and puts them in correct format that the toksearch query method expects.
    The signal specified is the one that the dataset is intended to be aligned with.

    :param align_with: A string respresenting the name of the signal name in 'signals' that the dataset is to be aligned with respect to.
    '''
    return (align_with, kw)


def WARN(size):
    message = "WARNING: It is estimated that you are requesting approx. %.2f GB of data. Are you sure you want to do this?" % (size / (1024 ** 3))
    if OMFITaux.get('GUI', None):
        from omfit_classes.OMFITx import Dialog
        return Dialog(message, ['Yes', 'No'], 'warning', "TOKSEARCH REQUESTING LARGE FILE SIZE")
    else:
        printw(message)


def NOTIFY(size):
    if SERVER_NAME in login_nodes:
        message = "ERROR: You are trying to pull back approx. %.2f GB of data. This will put you beyond the allowed limit of %s GB of accumulated data on a login node. \nPlease reduce your query size, or use SLURM que or another machine to run OMFIT." % (size * 1e-9, LOGIN_NODE_LIMIT)
    else:
        message = "ERROR: You are trying to pull back approx. %.2f GB of data. Which is beyond the available limit on your machine." % (size / (1024 ** 3))
    from omfit_classes.OMFITx import Dialog
    return Dialog(message, ['Ok'], 'error', "TOKSEARCH MEMORY LIMIT HIT")


def predictTokUse(mem_required):
    return round(mem_required * 4 + 25)


class OMFITtksValue():
    '''
    Wrapper for toksearch class, to be interfaced as an OMFIT MDS plus class.
    '''

    def __init__(self, record, server=None, treename=None, shot=None, TDI=None, quiet=False):
        self.record = record
        self.server = server
        self.treename = treename
        self.shot = shot
        self.TDI = TDI
        if shot is None or TDI is None:
            self.is_dataset = False
        else:
            self.is_dataset = isinstance(self.record[self.shot][self.TDI], xarray.core.dataset.Dataset)

    def data(self, sig_name=None):
        try:
            if self.is_dataset:
                if sig_name is None:
                    return self.record[self.shot][self.TDI].variables
                else:
                    return self.record[self.shot][self.TDI][sig_name]
            else:
                return self.record[self.shot][self.TDI]['data']
        except Exception as ex:
            print("Error while fetching data: " + str(ex))

    def dim_of(self, dim):
        if self.is_dataset:
            dim_name = list(self.record[self.shot][self.TDI].dims.keys())[dim]
        else:
            dim_name = self.record[self.shot][self.TDI]['dims'][dim]
        return self.record[self.shot][self.TDI][dim_name]

    def units(self, sig_name=None):
        try:
            if self.is_dataset:
                if sig_name is None:
                    return self.record[self.shot][self.TDI].attrs['units']
                else:
                    return self.record[self.shot][self.TDI][sig_name].attrs['units']
            else:
                return self.record[self.shot][self.TDI]['units']['data']
        except Exception as ex:
            return '?'

    def units_dim_of(self, dim):
        try:
            if self.is_dataset:
                dim_name = list(self.record[self.shot][self.TDI].dims.keys())[dim]
                return self.record[self.shot][self.TDI][dim_name].attrs['units']
            else:
                dim_name = self.record[self.shot][self.TDI]['dims'][dim]
                return self.record[self.shot][self.TDI]['units'][dim_name]
        except Exception as ex:
            return '?'

    def xarray(self):
        """
        :return: DataArray with information from this node
        """

        data = self.data()
        if self.is_dataset:
            dims = list(self.record[self.shot][self.TDI].dims.keys())
        else:
            dims = list(self.record[self.shot][self.TDI]['dims'])
        clist=[]
        for k, c in enumerate(dims):
            clist.append(self.dim_of(k))

        if data.shape != tuple([len(k) if np.ndim(k) == 1 else k.shape[ik] for ik,k in enumerate(clist)]):
            dims=dims[::-1]
            clist=clist[::-1]

        coords = {}
        for k, c in enumerate(dims):
            if np.ndim(clist[k]) == 1:
                ck=c
                coords[ck]=([c],clist[k],{'units': self.units_dim_of(k)})
            else:
                ck=c+'_val'
                coords[ck]=(dims, clist[k],{'units': self.units_dim_of(k)})

        xdata = DataArray(data, dims=dims, coords=coords, attrs={'units': self.units()})
        return xdata


def toksearchQueryRemote(serverPicker, shots, signals, datasets=None, aligners=None, functions=None, where=None, keep=None,
                         compute_type='ray', mem_requested=30, return_data='by_shot', use_dask=True,
                         load_data=True, queue_args={}, warn=True, **compute_kwargs):
    '''

    This function creates a toksearch query on a designated server (server must support toksearch). Takes in a list shot
    numbers and signal point names.

    :param serverPicker: (string) A string designating the server to create the toksearch query on.

    :param shots: A list of shot numbers (ints) to be fetched

    :param signals: A dict where each key corresponds to the signal name returned by toksearch, and each entry is a list
        which corresponds to a signal object fetched by toksearch. The first element of the list is the string corresponding to each signal name, i.e. 'PtDataSignal', the 2nd and 3rd entries are the args (list), and keyword args (dict) respectively. Ex) ['PtDataSignal',['ip'],{}] corresponds to a fetch for
        PtData 'ip' signal.

    :param datasets: A dict representing xarray datasets to be created from fetched signals.

    :param aligners: A dict where the keys are name of the dataset to align and the entries are a corresponding list of Aligners
    :param functions: A list of functions or executable strings to be executed in the toksearch mapping stage

    :param where: (string) An evaluatable string (executed in namespace of record) which should return a boolean when
        the record should be returned by toksearch query. This shall be used when trying to filter out shots by certain
        criteria. i.e. return False when you wish to filter out a shot, when string evaluates to True.

    :param keep: A list of strings pertaining to which attributes (signal,dataset etc.) of each record to be
        returned by toksearch query default: returns all attrs in namespace record

    :param compute_type : (string) Type of method to be used to run the pipeline. Options: 'serial','spark','ray'
                                  compute_type='ray' gives better memory usage and parallelization
    :param return_data: (string) A string pertaining on how the data fetched by toksearch should be structured.
        Options: 'by_shot','by_signal'. 'by_shot' will return a dictionary with shots as keys, with each record namespace
        stored in each entry. 'by_signal' will return a dictionary organized with the union of all record attrs as keys,
        and a dictionary organized by shot numbers under it. default: 'by_shot'
        NOTE: When fetching 'by_signal' Datasets will concatinated together over all valid shots.

    :param use_dask: (bool) Boolean of whether to load datasets using dask. Loading with dasks reduces the amount of
        RAM used by saving the data to disk and only loading into memory by chunks. default: False

    :param load_data: return data or return list of files for the user to handle

    :param **compute_kwargs: keyword arguments to be passed into the toksearch compute functions

    :return: data or return list of files for the user to handle depending on `load_data` switch
    '''
    queued_system = {'clean_after': True}

    queue_args.setdefault('partition', 'short' if is_server(serverPicker, 'iris') else 'nodes')  # type of queue resource
    queue_args.setdefault('n', 10)  # number of cpus
    queue_args.setdefault('mem', int(mem_requested))  # amount of RAM allocated
    queue_args.setdefault('hours',1)
    queue_args.setdefault('minutes',0)
    queue_args['hours'], queue_args['minutes'] = format_time_limit(queue_args['hours'],queue_args['minutes'])

    if not queue_args['partition'] in allowed_partitions:
        raise RuntimeError("ERROR: Partition type %s not supported. Choose: 'short','medium' or 'long'" % (queue_args['partition']))

    if is_server(serverPicker, 'saga'):
        queued_system['script'] = (executables['saga_batch'].format(**queue_args), 'batch.sh')
        queued_system['queued'] = True
        queued_system['std_out'] = 'toksearch_omfit_remote.out'
    else:
        raise NotImplementedError(str(serverPicker) + " is not a supported server.")
        printe("Error: " + str(serverPicker) + " is not a supported server.")
        return

    namespace = {'shots': shots,
                 'signals': signals,
                 'functions': functions,
                 'where': where,
                 'keep': keep,
                 'aligners': aligners,
                 'datasets': datasets,
                 'compute_type': compute_type,
                 'use_dask': use_dask,
                 'return_data': return_data.lower(),
                 'warn': warn,
                 'server_info': server_info()}
    namespace.update(compute_kwargs)

    data_files = ['toksearch.toks']
    if return_data == 'by_signal':
        data_files.extend(ds + '.tokds' for ds in namespace['datasets'])

    from omfit_classes.OMFITx import remote_python
    from time import time
    date_time = now("%Y-%m-%d_%H_%M_%S_") + (str(hash(time()))[:6])
    run_folder = 'toksearch_run_' + date_time + '.tokrun'
    workDir = SERVER['localhost']['workDir']
    data_files, mem_usage, data_size, ret_code = remote_python(None,
                                                               python_script=(toksearchQueryString, 'toksearch_python.py'),
                                                               target_function='toksearchQueryRun',
                                                               namespace=namespace,
                                                               executable=executables[serverPicker],
                                                               server=SERVER[serverPicker]['server'],
                                                               workdir=workDir + run_folder,
                                                               remotedir=SERVER[serverPicker]['workDir'] + run_folder,
                                                               tunnel=SERVER[serverPicker]['tunnel'],
                                                               outputs=data_files,
                                                               **queued_system)
    move_data = OMFITsessionDir not in workDir
    data_path = OMFITsessionDir + '/' + run_folder
    if move_data:
        if not os.path.exists(data_path):
            os.makedirs(data_path)

    if load_data:
        with open('toksearch.toks', 'rb') as f:
            data = pickle.load(f)
        if return_data == 'by_signal' and use_dask:
            if move_data:
                shutil.move('toksearch.toks', data_path + '/toksearch_' + date_time + '.toks')
            for ds in namespace['datasets']:
                try:
                    if move_data:
                        shutil.move(ds + '.tokds', data_path + '/' + ds + '.tokds')
                    data[ds] = xarray.open_dataset(data_path + '/' + ds + '.tokds', chunks={'shot': 10})
                except Exception as ex:
                    print("FILE %s MISSING" % (ds + '.tokds'))
                    print(ex)
    else:
        if move_data:
            moved_files = []
            for file in data_files:
                shutil.move(file, data_path + '/toksearch_' + date_time + '.toks')
                moved_files.append(data_path + '/toksearch_' + date_time + '.toks')
            data = moved_files
        else:
            data = data_files

    if move_data:
        os.chdir(data_path)
        shutil.rmtree(workDir + run_folder)

    return data, mem_usage, data_size, ret_code


class OMFITtoksearch(SortedDict):
    '''
        This class is used to query from database through tokesearch API

        :param serverPicker: (string)A string designating the server to create the toksearch query on.

        :param shots: A list of shot numbers (ints) to be fetched

        :param signals: A dict where each key corresponds to the signal name returned by toksearch, and each entry is a list
            which corresponds to a signal object fetched by toksearch. The first element of the list is the string
            corresponding to each signal name, i.e. 'PtDataSignal', the 2nd and 3rd entries are the args (list), and keyword
            args (dict) respectively. Ex) ['PtDataSignal',['ip'],{}] corresponds to a fetch for
            PtData 'ip' signal.

        :param datasets: A dict representing xarray datasets to be created from fetched signals.

        :param aligners: A dict where the keys are name of the dataset to align and the entries are a corresponding list of Aligners

        :param functions: A list of functions or executable strings to be executed in the toksearch mapping stage

        :param where: (string) An evaluatable string (executed in namespace of record) which should return a boolean when
            the record should be returned by toksearch query. This shall be used when trying to filter out shots by certain
            criteria. i.e. return False when you wish to filter out a shot, when string evaluates to True.

        :param keep: A list of strings pertaining to which attributes (signal,dataset etc.) of each record to be
            returned by toksearch query default: returns all attrs in namespace record

        :param compute_type: (string) Type of method to be used to run the pipeline. Options: 'serial','spark','ray'
                                      compute_type='ray' gives better memory usage and parallelization

        :param return_data: (string) A string pertaining on how the data fetched by toksearch should be structured.
            Options: 'by_shot','by_signal'. 'by_shot' will return a dictionary with shots as keys, with each record namespace
            stored in each entry. 'by_signal' will return a dictionary organized with the union of all record attrs as keys,
            and a dictionary organized by shot numbers under it. default: 'by_shot'
            NOTE: When fetching 'by_signal' Datasets will concatinated together over all valid shots.

        :param warn: (bool) If flag is true, the user will be warned if they are about to pull back more than 50% of their available memory and can respond accordingly. This is a safety precaution when pulling back large datasets that may cause you to run out of memory. (default: True).

        :param use_dask: (bool) If flag is True then created datasets will be loaded using dask. Loading with dasks reduces the amount of
            RAM used by saving the data to disk and only loading into memory by chunks. (default: False)

        :param load_data: (bool) If this flag is False, then data will be transferred to disk under OMFIT current working directory, but the data will not be loaded into memory (RAM) and thus the OMFITtree will not be updated. This is to be used when fetching data too large to fit into memory. (default True).

        :param **compute_kwargs: keyword arguments to be passed into the toksearch compute functions
    '''

    def __save_kw__(self):
        return self.args

    def __init__(self, shots, signals, server='saga', datasets=None, aligners=None, functions=None, where=None, keep=None, compute_type='spark', return_data='by_shot', warn=True, use_dask=False, load_data=True, queue_args={}, **compute_kwargs):
        SortedDict.__init__(self)
        self.kw = compute_kwargs
        self.kw['serverPicker'] = server
        self.kw['shots'] = shots
        self.kw['signals'] = signals
        self.kw['datasets'] = datasets
        self.kw['aligners'] = aligners
        self.kw['compute_type'] = compute_type
        self.kw['functions'] = functions
        self.kw['where'] = where
        self.kw['keep'] = keep
        self.kw['use_dask'] = use_dask
        self.kw['return_data'] = return_data.lower()
        self.kw['load_data'] = load_data
        self.kw['queue_args'] = queue_args.copy()
        self.kw['warn'] = warn
        self.args = self.kw.copy()
        self.kw['mem_requested'] = 60
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        kw = self.kw.copy()
        objs_as_dict, memory_usage, serial_mem, ret_code = toksearchQueryRemote(**kw)
        self.dynaLoad = False
        if not kw['load_data']:
            return objs_as_dict
        if ret_code == 1:  # pulling too much data
            ans = NOTIFY(serial_mem)
            self.dynaLoad = True
        elif ret_code == 3 and kw['warn']:  # will warn if self.warn == True
            pull_data = WARN(serial_mem)
            if pull_data == 'Yes':
                mem_needed = predictTokUse(serial_mem)
                kw['mem_requested'] = min(mem_needed, SERVER_MEM[kw['serverPicker']])
                kw['warn'] = False
                objs_as_dict, memory_usage, serial_mem, ret_code = toksearchQueryRemote(**kw)
                if ret_code == 1:
                    ans = NOTIFY(serial_mem)
                    self.dynaLoad = True
                else:
                    self.update(objs_as_dict)
            else:
                self.dynaLoad = True
        else:
            self.update(objs_as_dict)

    @dynaLoad
    def __call__(self, *args, **kw):
        if args or kw:
            return OMFITtksValue(self, *args, **kw)

############################################
if '__main__' == __name__:
    test_classes_main_header()
    if SERVER['saga']['workDir'] is None:
        printe(_using_toksearch_outside_framework_warning)
    filter_func = "not record['errors']"
    OMFIT['ts']=OMFITtoksearch([133221], {'ip':TKS_PtDataSignal('ip')}, where=filter_func)
    #successful creation of OMFIT object (no connections tested)
