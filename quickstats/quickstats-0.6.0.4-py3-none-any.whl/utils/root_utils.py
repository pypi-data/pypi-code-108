import os
import time
from six import string_types

import numpy as np

import ROOT
import quickstats

def is_corrupt(f:ROOT.TFile):
    if f.IsZombie():
        return True
    if f.TestBit(ROOT.TFile.kRecovered):
        return True
    if f.GetNkeys() == 0:
        return True
    return False

def release_tfiles():
    for f in ROOT.gROOT.GetListOfFiles():
        f.Close()

def compile_macro(name:str):
    macros_dir = os.path.join(quickstats.macro_path, 'macros')
    macros_path = os.path.join(macros_dir, name + '.cxx')
    print('INFO: Compiling macro "{}"...'.format(name))
    if not os.path.exists(macros_path):
        print('ERROR: Cannot locate macro files from {}. ROOT macros will not be compiled.'.format(macros_dir))
        return -1
    return ROOT.gROOT.LoadMacro('{}++'.format(macros_path))

def load_macro(name:str):
    auto_load = ROOT.gInterpreter.AutoLoad(name)
    # already loaded by quickstats / third-party
    if auto_load == 1:
        return None
    macros_dir = os.path.join(quickstats.macro_path, 'macros')
    macros_path = os.path.join(macros_dir, name + '_cxx')
    if not os.path.exists(macros_path + '.so'):
        return compile_macro(name)
    result = ROOT.gSystem.Load(macros_path)
    if (result != 0) and (result != 1):
        raise RuntimeError("Shared library for the macro {} is incompatible with the current pyROOT version. "
                           "Please recompile by typing \"quickstats compile\".".format(name))
    return result


def print_resource_used(start):
    proc_info = ROOT.ProcInfo_t()
    flag = ROOT.gSystem.GetProcInfo(proc_info)
    if flag < 0:
        return None
    cpu_time = proc_info.fCpuUser + proc_info.fCpuSys
    wall_time = time.time()-start
    print('Resources Used: cpu_time={:.3f}s, mem={}kb, vmem={}kb, wall_time={:.3f}s'.format(
          cpu_time, proc_info.fMemResident, proc_info.fMemVirtual, wall_time))
    return None

def process_uproot_array(source):
    result = np.array(source)
    if (result.dtype == np.dtype('O')) and (isinstance(result[0], bytes)):
        result = result.astype(str)
    return result

def get_data_size(data):
    if isinstance(data, (tuple, list, np.ndarray)):
        return len(data)
    else:
        return 1

def uproot_to_dict(file):
    result = {}
    for tree in file.values():
        tree_name = tree.name.decode('utf-8')
        result[tree_name] = {}
        for branch in tree.values():
            branch_name = branch.name.decode('utf-8')
            arr = process_uproot_array(branch.array())
            value = arr[0] if len(arr) == 1 else arr
            result[tree_name][branch_name] = value    
    return result
    
def get_leaf_type_str(data):
    type_str = None
    data_type = None

    if isinstance(data, (tuple, list, np.ndarray)):
        data_type = type(data[0])
        if data_type in string_types:
            return None
    elif isinstance(data, string_types):
        return None
    else:
        data_type = type(data)
        
    if data_type in [float, np.float64]:
        type_str = 'D'
    elif data_type in [int, np.int64]:
        type_str = 'L'
    elif data_type in [np.int32]:
        type_str = 'I'
    elif data_type in [np.uint32]:
        type_str = 'i'        
    elif data_type in [bool, np.bool_]:
        type_str = 'O'        
    elif data_type in [np.float32]:
        type_str = 'F'
    elif data_type in [np.int8]:
        type_str = 'B'
    elif data_type in [np.uint8]:
        type_str = 'b'
    else:
        raise ValueError('cannot infer leaf type for {}'.format(data_type))
    return type_str

        
        
def fill_branch(tree, values_dict):
    buffer = {}
    leaf_types = {}
    data_sizes = list(set([get_data_size(v) for k,v in values_dict.items()]))
    if len(data_sizes) > 1:
        raise ValueError('cannot fill tree with values of inconsistent entry sizes')
    data_size = data_sizes[0]
    if data_size == 1:
        for k, v in values_dict.items():
            leaf_type_str = get_leaf_type_str(v)
            leaf_types[k] = leaf_type_str
            if leaf_type_str is not None:
                buffer[k] = np.array([v], dtype=type(v))
                tree.Branch(k, buffer[k], '{}/{}'.format(k, leaf_type_str))
            else:
                buffer[k] = ROOT.std.string(v)
                tree.Branch(k, buffer[k])
        tree.Fill()
    else:
        for k, v in values_dict.items():
            leaf_type_str = get_leaf_type_str(v)
            leaf_types[k] = leaf_type_str
            if leaf_type_str is not None:
                buffer[k] = np.array([v[0]], dtype=type(v[0]))
                tree.Branch(k, buffer[k], '{}/{}'.format(k, leaf_type_str))
            else:
                buffer[k] = ROOT.std.string(v[0])
                tree.Branch(k, buffer[k])
        for i in range(data_size):
            for k, v in values_dict.items():
                if leaf_types[k] is not None:
                    buffer[k][0] = v[i]
                else:
                    buffer[k].replace(0, ROOT.std.string.npos, v[i])
            tree.Fill()
    