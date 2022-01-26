# /usr/bin/python3

from . import read_config as rc
import pandas as pd

def get_options(options, name=None, type=None):
    """
     Reads the options for an object of given type and name
        first looks for options for the type, then for the name
        i.e. specialized options superseeds general ones
    """
    opt = {}
    keys = options.keys()
    if type in keys:
        opt = options[type]
        if name in opt.keys():
            opt = opt[name]
    if name in keys:
        try:
            opt.update(options[name])
        except:
            print("Invalid options format : format must be a dictionary")
    return opt

def get_prop_dicts(pile, key="set", type=None, name=None):
    """ Getting a dictionary of properties """
    com = [key, type, name]
    return get_dict_from_pile(pile, com)

def concatenate_dicts(*args):
    """ Dict concaternation """
    res={}
    for arg in args:
        res.update(arg)
    return res

def get_dict_from_pile(pile,com):
    """ Getting a dict from the config represented as a pile """
    prop_dict={}
    if pile is not None:
        try:
            obj = rc.get_command(pile, com)
            prop_dict = {key: obj.vals[key] for key in obj.values()}
        except:
            print("Warning : did not understand properties for %s" %com)
    return prop_dict

def export_analysis(analysis,fname='analysis.csv'):
    """
    Exports a dataframe to a csv file
    """
    if analysis is not None:
        return analysis.to_csv(fname)
    else:
        return None

def make_analysis(dict,*args,**kwargs):
    """
    iterates over a dict of object to perform analysis
    """
    res={}
    for key,item in dict.items():
        res[key]=objects_analysis(item,*args,**kwargs)
    return res

def objects_analysis(objects, analyzer=None, *args,**kwargs):
    """
    Iterate over an object set to analyze its objects
    technically could work for iterators ;)
    """
    datas = None
    keys = None

    type = objects.type
    name = objects.name

    lyzer = {}
    if type in analyzer.keys():
        lyzer = analyzer[type]

    if name in analyzer.keys():
        lyzer.update(analyzer[name])

    # Iteration
    for obj in objects:
        analysis=objects.analyze(obj, *args, analyzer = lyzer , **kwargs)
        if analysis:
            if datas is None:
                keys = analysis.keys()
                datas = pd.DataFrame(columns=keys)

            datas.loc[obj.id] = [analysis[key] for key in keys]

    return datas


# gets a block of lines between two "% frame" comments
def get_frame_block(iterator):
    return get_block(iterator, "% frame")


# gets a block of lines between two _key_ comments
def get_block(iterator,key):
    block = []
    if iterator is not None:
        for line in iterator:
            if line.find(key) < 0:
                block.append(line)
            else:
                break
    return block, len(block) > 0


# from a dictionary of filename dictionaries,
#   returns a dictionary of iterator dictionaries
def make_iter_dict(dict_dict):
    iter_dict = {}
    for name, report_dict in dict_dict.items():
        iters = {}
        for type, report_fname in report_dict.items():
            iters[type] = open(report_fname,'r')
        iter_dict[name] = iters

    return iter_dict


# from a dictionary of iterator dictionaries,
#   returns a dictionary of block dictionaries
def make_block_dict(dict_dict):
    block_dict = {}
    keep=False
    for name, report_dict in dict_dict.items():

        blocks = {}
        for type, report_iter in report_dict.items():
            blocks[type], flag = get_frame_block(report_iter)
            if flag:
                keep=True

        block_dict[name] = blocks

    return block_dict, keep
