from bdaserviceutils import task_args

import importlib


def get_args():

    args = task_args.get_args()

    if args["dataStorageType-input-dataset"].lower().startswith("presto"):
        args["input-columns"] = args["input-columns"] if "input-columns" in args else "*"

    return args


def get_class(module_name):

    module = importlib.import_module("." + module_name, "pysparkutilities")
    return getattr(module, module_name.capitalize())


def load_dataset(sc, read_all, input_dest='', header=True):
    # sc -> Spark context
    # read_all -> True to read all data, False to read 'input-columns' in 'args'

    args = get_args()
    data_storage = args["dataStorageType-input-dataset"]
    module_name = data_storage.split('-')[0].lower()

    class_ = get_class(module_name)
    instance = class_(args)

    return instance.load_dataset(sc, read_all, input_dest, header)


def save_dataset(df, output_dest=''):
    # df -> Spark dataframe to store
    # output_dest -> destinaion output, if not specified it takes 'output-dataset' destinaion from 'args'

    args = get_args()
    data_storage = args["dataStorageType-output-dataset"]
    module_name = data_storage.split('-')[0].lower()

    class_ = get_class(module_name)
    instance = class_(args)

    return instance.save_dataset(df, output_dest)


def lower_columns_list(columns_list):

    return [x.lower() for x in columns_list]
