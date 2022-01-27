import re
import os


def delete_files_except_best(run_id = None, epochs = None, path = None):
    directory = path['save_model_path']

    pattern1 = run_id
    pattern2 = run_id + '-epoch-' + epochs.zfill(5)
    regex1 = re.compile(pattern1)
    regex2 = re.compile(pattern2)
    
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            if regex1.search(filename) and not regex2.search(filename):
                os.remove(os.path.join(directory, filename))


def get_best_model_path(run_id = None, path = None):
    hdf5_path = path['save_model_path']
    pattern = str(run_id) 
    regex = re.compile(pattern)
    best_model_path = []
    best_model_path_dict = dict()
    for subdir, dirs, files in os.walk(hdf5_path):
        for filename in files:
            if regex.search(filename):
                best_model_path.append(str('/' + filename))

    if 'json' in best_model_path[0]:
        best_model_path_dict['json'] = best_model_path[0]
        best_model_path_dict['h5'] = best_model_path[1]
    else:
        best_model_path_dict['json'] = best_model_path[1]
        best_model_path_dict['h5'] = best_model_path[0]

    return best_model_path_dict

