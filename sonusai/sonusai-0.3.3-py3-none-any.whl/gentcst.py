"""gentcst

usage: gentcst [-hvru] [-o OUTPUT] [-f FOLD] [-y ONTOLOGY]

options:
    -h, --help
    -v, --verbose                       Be verbose.
    -o OUTPUT, --output OUTPUT          Output file name.
    -f FOLD, --fold FOLD                Fold(s) to include. [default: *].
    -y ONTOLOGY, --ontology ONTOLOGY    Reference ontology JSON file for cross-check and adding metadata. [default: ontology.json].
    -r, --hierarchical                  Generate hierarchical multiclass truth for non-leaf nodes.
    -u, --update                        Write JSON metadata into the tree.

Generate a target SonusAI configuration file from a hierarchical subdirectory tree
under the local directory. Leaves in the subdirectory tree define classes by providing SonusAI list
.txt files for class data and additional truth config definitions. This offers a way to simplify and
more clearly manage hierarchical class structure similar to the Audioset ontology.

Features:
    - automatically compiles the target configuration with the number of classes and each truth
      index and the associated files (note: files should use absolute path with env variable)
    - supports hierarchical multilabel class truth generation, where higher nodes in the tree
      are included with leaf truth index, and different leaves with the same name will have the
      same index (i.e. door/squeak, chair/squeak, and brief-tone/squeak)
    - support config overrides for class config.yml or filename.yml for specific file config
    - manages folds via file prefix naming convention, i.e. 1-*.txt, 2-*.txt, etc.
      specifies data for fold 1, 2, etc.
    - cross-check node definitions with the reference ontology and auto copy class metadata into
      the tree to help define/collect data
    - class label is also generated (in the .yml or referencing a .csv)

Inputs:
    The local subdirectory tree with expected top-level configuration file config.yml. This
    file must at least define the feature and can have additional parameters treated as default
    (for truth, augmentation, etc.) which will be included in the generated output yaml file.
    An entire class dataset config parameter can be overridden by including it in a config.yml
    file in the class subdirectory. Individual file config parameters can be further overridden
    or specified in a file of the same name but with .yml (i.e. 1-data.yml with the 1-data.txt)

Outputs:
    output.yml
    output.csv
    gentcst.log

"""
import csv
import json
import re
from os import getcwd
from os.path import basename
from os.path import dirname
from os.path import exists
from os.path import splitext

import numpy as np
import sh
import yaml
from docopt import docopt

import sonusai
from sonusai import create_file_handler
from sonusai import initial_log_messages
from sonusai import logger
from sonusai import update_console_handler
from sonusai.utils import trim_docstring


def gentcst(fold: str = '*',
            ontology: str = 'ontology.json',
            hierarchical: bool = False,
            update: bool = False,
            verbose: bool = False) -> (dict, dict):
    update_console_handler(verbose)
    initial_log_messages('gentcst')

    if update:
        logger.info('Updating tree with JSON metadata')
        logger.info('')

    logger.debug('fold:         {}'.format(fold))
    logger.debug('ontology:     {}'.format(ontology))
    logger.debug('hierarchical: {}'.format(hierarchical))
    logger.debug('update:       {}'.format(update))
    logger.debug('')

    config = get_config('config.yml')

    if config['truth_mode'] == 'mutex' and hierarchical:
        logger.error('Multi-class truth is incompatible with truth_mode mutex')
        exit()

    all_files = get_all_files(hierarchical)
    all_folds = get_folds_from_files(all_files)
    use_folds = get_use_folds(all_folds, fold)
    use_files = get_files_from_folds(all_files, use_folds)
    report_leaf_fold_data_usage(all_files, use_files)

    ontology_data = validate_ontology(ontology, use_files)

    labels = get_labels_from_files(all_files)
    logger.debug('Truth indices:')
    for item in labels:
        logger.debug(' {:3} {}'.format(item['index'], item['display_name']))
    logger.debug('')

    gen_truth_indices(use_files, labels)

    config['num_classes'] = len(labels)
    if config['truth_mode'] == 'mutex':
        config['num_classes'] = config['num_classes'] + 1

    config['targets'] = []

    logger.info('Processing {} entries in tree'.format(len(use_files)))
    for file in use_files:
        local_config = {}
        local_name = dirname(file['file']) + '/config.yml'
        if exists(local_name):
            with open(local_name, mode='r') as yaml_file:
                local_config = yaml.safe_load(yaml_file)

        specific_name = splitext(file['file'])[0] + '.yml'
        if exists(specific_name):
            with open(specific_name, mode='r') as yaml_file:
                specific_config = yaml.safe_load(yaml_file)

            for key in specific_config:
                local_config[key] = specific_config[key]

        if 'feature' in local_config.keys():
            if config['feature'] != local_config['feature']:
                logger.warning('Local feature for {} ({}) is not the same as top level ({})'.format(
                    file['file'], local_config['feature'], config['feature']))

        target = {'target_name': file['file'], 'truth_index': file['truth_index']}
        if 'truth_function' in local_config.keys():
            target['truth_function'] = local_config['truth_function']
        if 'truth_config' in local_config.keys():
            target['truth_config'] = local_config['truth_config']

        config['targets'].append(target)

        if update:
            write_metadata_to_tree(ontology_data, file)

    return config, labels


def get_ontology(ontology: str) -> list:
    ontology_data = []

    if exists(ontology):
        with open(ontology, encoding='utf-8') as f:
            ontology_data = json.load(f)

    # Convert names to lowercase, convert spaces to '-', split into lists on ','
    for item in ontology_data:
        name = item['name'].lower()
        # Need to find ', ' before converting spaces so that we don't convert ', ' to ',-'
        name = name.replace(', ', ',')
        name = name.replace(' ', '-')
        name = name.split(',')
        item['name'] = name

    return ontology_data


def get_dirs() -> list:
    match = sh.find('.', '-type', 'd')
    match = list(map(str.strip, match))

    dirs = []
    for m in match:
        if not m.startswith('./gentcst') and m != '.':
            classes = m.split('/')
            # Remove first element because it is '.'
            classes.pop(0)

            dirs.append({'file': m, 'classes': classes})

    return dirs


def get_leaf_from_classes(classes: list) -> str:
    return '/'.join(classes)


def get_all_files(hierarchical: bool) -> list:
    match = sh.find('.', '-regex', '.*/[0-9]+-.*\.txt')
    match = list(map(str.strip, match))

    files = []
    fold_pattern = re.compile('.*/(\d+)-.*\.txt')
    for m in match:
        fold_match = fold_pattern.match(m)
        if fold_match:
            fold = int(fold_match.group(1))

            classes = m.split('/')
            # Remove first element because it is '.'
            classes.pop(0)
            # Remove last element because it is the file name
            classes.pop()

            leaf = get_leaf_from_classes(classes)

            if hierarchical:
                labels = classes
            else:
                labels = [leaf]

            files.append({'file': m, 'classes': classes, 'leaf': leaf, 'labels': labels, 'fold': fold})

    return files


def get_use_folds(all_folds: list, fold: str) -> list:
    req_folds = get_req_folds(all_folds, fold)
    use_folds = list(set(req_folds).intersection(all_folds))

    logger.debug('Fold information')
    logger.debug(' Available: {}'.format(all_folds))
    logger.debug(' Requested: {}'.format(req_folds))
    logger.debug(' Used:      {}'.format(use_folds))
    logger.debug(' Unused:    {}'.format(list(set(use_folds).symmetric_difference(all_folds))))
    logger.debug(' Missing:   {}'.format(list(np.setdiff1d(req_folds, all_folds))))
    logger.debug('')

    return use_folds


def get_files_from_folds(files: list, folds: list) -> list:
    use_files = []
    for item in files:
        if item['fold'] in folds:
            use_files.append(item)
    return use_files


def get_item_from_name(ontology_data: list, name: str) -> dict:
    return next((item for item in ontology_data if name in item['name']), None)


def get_item_from_id(ontology_data: list, identity: str) -> dict:
    return next((item for item in ontology_data if item['id'] == identity), None)


def get_name_from_id(ontology_data: list, identity: str) -> list:
    name = None
    found = False

    for item in ontology_data:
        if item['id'] == identity:
            if found:
                logger.error('id {} appears multiple times in ontology'.format(identity))
                exit()

            name = item['name']
            found = True

    return name


def get_id_from_name(ontology_data: list, name: str) -> str:
    identity = None
    found = False

    for item in ontology_data:
        if name in item['name']:
            if found:
                logger.error('name {} appears multiple times in ontology'.format(name))
                exit()

            identity = item['id']
            found = True

    return identity


def is_valid_name(ontology_data: list, name: str) -> bool:
    for item in ontology_data:
        if name in item['name']:
            return True
    return False


def is_valid_child(ontology_data: list, parent: str, child: str) -> bool:
    valid = False
    parent_item = get_item_from_name(ontology_data, parent)
    child_id = get_id_from_name(ontology_data, child)

    if child_id is not None and parent_item is not None:
        if child_id in parent_item['child_ids']:
            valid = True

    return valid


def is_valid_hierarchy(ontology_data: list, classes: list) -> bool:
    valid = True

    for parent, child in zip(classes, classes[1:]):
        if not is_valid_child(ontology_data, parent, child):
            valid = False

    return valid


def validate_class(ontology_data: list, file: dict) -> bool:
    valid = True
    classes = file['classes']

    for c in classes:
        if not is_valid_name(ontology_data, c):
            logger.warning(' Could not find {} in ontology for {}'.format(c, file['file']))
            valid = False

    if valid:
        if not is_valid_hierarchy(ontology_data, classes):
            logger.warning(' Invalid parent/child relationship for {}'.format(file['file']))
            valid = False

    return valid


def expand_range(s: str) -> list:
    r = []
    for i in s.split(','):
        if '-' not in i:
            r.append(int(i))
        else:
            l, h = map(int, i.split('-'))
            r += range(l, h + 1)
    return r


def get_req_folds(folds: list, fold: str) -> list:
    if fold == '*':
        return folds

    return expand_range(fold)


def get_folds_from_files(files: list) -> list:
    result = [sub['fold'] for sub in files]
    # Converting to set and back to list ensures uniqueness
    return sorted(list(set(result)))


def get_leaves_from_files(files: list) -> list:
    result = [sub['leaf'] for sub in files]
    # Converting to set and back to list ensures uniqueness
    return sorted(list(set(result)))


def get_labels_from_files(files: list) -> list:
    label_list = []
    for item in files:
        for c in item['labels']:
            label_list.append(c)

    # Converting to set and back to list ensures uniqueness
    label_list = sorted(list(set(label_list)))

    labels = []
    for index, item in enumerate(label_list):
        labels.append({'index': index + 1, 'display_name': item})

    return labels


def gen_truth_indices(files: list, labels: list):
    for item in files:
        item['truth_index'] = []
        for label in item['labels']:
            item['truth_index'].append(get_index_from_label(labels, label))
        item['truth_index'] = sorted(item['truth_index'])


def get_index_from_label(labels: list, label: str) -> int:
    return next((item for item in labels if item['display_name'] == label), None)['index']


def get_config(config_name: str) -> dict:
    if not exists(config_name):
        logger.error('No confg.yml at top level')
        exit()

    with open(config_name, mode='r') as yaml_file:
        config = yaml.safe_load(yaml_file)

    if 'feature' not in config.keys():
        logger.error('feature not in top level config')
        exit()

    if 'truth_function' not in config.keys():
        logger.error('truth_function not in top level config')
        exit()

    if 'truth_config' not in config.keys():
        logger.error('truth_config not in top level config')
        exit()

    if 'truth_mode' not in config.keys():
        logger.error('truth_mode not in top level config')
        exit()

    if config['truth_mode'] not in ['normal', 'mutex']:
        logger.error('Invalid truth_mode in top level config')
        exit()

    return config


def validate_ontology(ontology: str, files: list) -> list:
    if exists(ontology):
        ontology_data = get_ontology(ontology)
        logger.debug('Reference ontology in {} has {} classes'.format(ontology, len(ontology_data)))
        logger.debug('')

        logger.info('Checking tree against reference ontology')
        all_dirs = get_dirs()
        valid = True
        for file in all_dirs:
            if not validate_class(ontology_data, file):
                valid = False
        if valid:
            logger.info('PASS')
        logger.info('')

        logger.info('Checking files against reference ontology')
        valid = True
        for file in files:
            if not validate_class(ontology_data, file):
                valid = False
        if valid:
            logger.info('PASS')
        logger.info('')

        return ontology_data

    return []


def get_node_from_name(ontology_data: list, name: str) -> dict:
    nodes = [item for item in ontology_data if name in item['name']]
    if len(nodes) == 1:
        return nodes[0]

    if nodes:
        logger.warning('Found multiple entries in reference ontology that match {}'.format(name))
    else:
        logger.warning('Could not find entry for {} in reference ontology'.format(name))

    return {}


def write_metadata_to_tree(ontology_data: list, file: dict):
    if ontology_data:
        node = get_node_from_name(ontology_data, file['classes'][-1])
        if node:
            dir_name = dirname(file['file'])
            json_name = dir_name + '/' + basename(dir_name) + '.json'
            with open(json_name, 'w') as json_file:
                json.dump(node, json_file)


def get_folds_from_leaf(all_files: list, leaf: str) -> list:
    files = [item for item in all_files if item['leaf'] == leaf]
    return get_folds_from_files(files)


def report_leaf_fold_data_usage(all_files: list, use_files: list):
    use_leaves = get_leaves_from_files(use_files)
    all_leaves = get_leaves_from_files(all_files)

    logger.debug('Data folds present in each leaf')
    leaf_len = len(max(all_leaves, key=len))
    for leaf in all_leaves:
        folds = get_folds_from_leaf(all_files, leaf)
        logger.debug(' {:{}} {}'.format(leaf, leaf_len, folds))
    logger.debug('')

    dif_leaves = set(all_leaves).symmetric_difference(use_leaves)
    if dif_leaves:
        logger.warning('This fold selection is missing data from the following leaves')
        for c in dif_leaves:
            logger.warning(' {}'.format(c))
        logger.warning('')


def main():
    try:
        args = docopt(trim_docstring(__doc__), version=sonusai.version(), options_first=True)

        verbose = args['--verbose']
        output_name = args['--output']
        fold = args['--fold']
        ontology = args['--ontology']
        hierarchical = args['--hierarchical']
        update = args['--update']

        if not output_name:
            output_name = basename(getcwd()) + '.yml'

        log_name = 'gentcst.log'

        create_file_handler(log_name)

        config, labels = gentcst(fold=fold,
                                 ontology=ontology,
                                 hierarchical=hierarchical,
                                 update=update,
                                 verbose=verbose)

        with open(output_name, 'w') as yaml_file:
            yaml.dump(config, yaml_file)
            logger.info('Wrote config to {}'.format(output_name))

        csv_fields = ['index', 'display_name']
        csv_name = splitext(output_name)[0] + '.csv'

        with open(csv_name, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
            writer.writeheader()
            writer.writerows(labels)
            logger.info('Wrote labels to {}'.format(csv_name))

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
