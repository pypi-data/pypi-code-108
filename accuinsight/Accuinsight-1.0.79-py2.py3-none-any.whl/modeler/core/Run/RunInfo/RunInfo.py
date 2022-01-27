import os
import json
import logging
from collections import OrderedDict
from Accuinsight.modeler.core.Run.RunOjbject import RunObject
from Accuinsight.modeler.core.LcConst import LcConst

# RUN_MODEL_HDF5_PATH, RUN_RESULT_PATH,
# RUN_MODEL_JSON_PATH, RUN_MODEL_VISUAL_CSV_PATH, RUN_MODEL_VISUAL_JSON_PATH,
# RUN_PREFIX_PATH

_runData = []


def set_current_runs(run_name):
    global _runData

    run_dir = get_or_create_run_directory()

    if len(_runData) > 0:
        _runData.clear()
        #raise Exception("{} is already running".format(_runData[0]))

    run_obj = RunObject()
    run_obj[LcConst.RUN_OBJ_NAME] = run_name
    run_obj[LcConst.RUN_BASE_PATH] = run_dir
    run_obj[LcConst.RUN_RESULT_PATH] = {}

    # Initialize: all paths are none.
    run_obj[LcConst.RUN_OBJ_MODEL_JSON_PATH] = None
    run_obj[LcConst.RUN_OBJ_VISUAL_CSV_PATH] = None
    run_obj[LcConst.RUN_OBJ_VISUAL_JSON_PATH] = None
    run_obj[LcConst.RUN_OBJ_SHAP_JSON_PATH] = None
    run_obj[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH] = None
    run_obj[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] = None
    run_obj[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] = None

    _runData.append(run_obj)

    return _runData


def clear_runs(start_time, end_time, delta_time):
    global _runData
    run_obj = _runData[0]
    run_meta = OrderedDict()

    for key in run_obj.__dict__.keys():
        run_meta[key] = run_obj[key]

    run_meta[LcConst.START_TIME] = start_time
    run_meta[LcConst.END_TIME] = end_time
    run_meta[LcConst.DELTA_TIME] = delta_time

    save_result_path = run_meta[LcConst.RUN_RESULT_PATH] = {}
    save_result_path[LcConst.RUN_BASE_PATH] = run_meta[LcConst.RUN_BASE_PATH]
    save_result_path[LcConst.RUN_PREFIX_PATH] = run_meta[LcConst.RUN_PREFIX_PATH]
    save_result_path[LcConst.RUN_MODEL_JSON_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                            save_result_path[LcConst.RUN_PREFIX_PATH],
                                                            run_meta[LcConst.RUN_OBJ_MODEL_JSON_PATH]
                                                            ])

    if run_meta[LcConst.RUN_OBJ_VISUAL_CSV_PATH] is not None:
        save_result_path[LcConst.RUN_MODEL_VISUAL_CSV_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                                      save_result_path[LcConst.RUN_PREFIX_PATH],
                                                                      run_meta[LcConst.RUN_OBJ_VISUAL_CSV_PATH]
                                                                      ])

    if run_meta[LcConst.RUN_OBJ_VISUAL_JSON_PATH] is not None:
        save_result_path[LcConst.RUN_MODEL_VISUAL_JSON_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                                       save_result_path[LcConst.RUN_PREFIX_PATH],
                                                                       run_meta[LcConst.RUN_OBJ_VISUAL_JSON_PATH]
                                                                       ])
    if run_meta[LcConst.RUN_OBJ_SHAP_JSON_PATH] is not None:
        save_result_path[LcConst.RUN_MODEL_SHAP_JSON_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                                       save_result_path[LcConst.RUN_PREFIX_PATH],
                                                                       run_meta[LcConst.RUN_OBJ_SHAP_JSON_PATH]
                                                                       ])
    if run_meta[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH ] is not None:
        save_result_path[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                                    save_result_path[LcConst.RUN_PREFIX_PATH],
                                                                    run_meta[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH]
                                                                    ])
    if run_meta[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] is not None:
        save_result_path[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                                    save_result_path[LcConst.RUN_PREFIX_PATH],
                                                                    run_meta[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH]
                                                                    ])
    if run_meta[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] is not None:
        save_result_path[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] = ''.join([save_result_path[LcConst.RUN_BASE_PATH],
                                                                    save_result_path[LcConst.RUN_PREFIX_PATH],
                                                                    run_meta[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH]
                                                                    ])

    save_path = run_meta[LcConst.RUN_BASE_PATH] + 'run_info.json'
    with open(save_path, 'w', encoding='utf-8') as save_file:
        json.dump(run_meta, save_file, indent="\t")

    _runData.pop()

    return run_meta


def _set_result_full_path(dict_path):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_BASE_PATH] = get_or_create_run_directory()

    run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_PREFIX_PATH] = dict_path[LcConst.RUN_PREFIX_PATH]

    run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_MODEL_JSON_PATH] = dict_path[LcConst.RUN_MODEL_JSON_PATH]

    if LcConst.RUN_MODEL_VISUAL_CSV_PATH in dict_path:
        run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_MODEL_VISUAL_CSV_PATH] = dict_path[LcConst.RUN_MODEL_VISUAL_CSV_PATH]

    if LcConst.RUN_MODEL_VISUAL_JSON_PATH in dict_path:
        run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_MODEL_VISUAL_JSON_PATH] = dict_path[LcConst.RUN_MODEL_VISUAL_JSON_PATH]
        
    if LcConst.RUN_MODEL_SHAP_JSON_PATH in dict_path:
        run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_MODEL_SHAP_JSON_PATH] = dict_path[LcConst.RUN_MODEL_SHAP_JSON_PATH]

    if LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH in dict_path:
        run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] = dict_path[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH]

    if LcConst.RUN_OBJ_BEST_MODEL_H5_PATH in dict_path:
        run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_OBJ_BEST_MODEL_H5_PATH] = dict_path[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH]

    if LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH in dict_path:
        run_obj[LcConst.RUN_RESULT_PATH][LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] = dict_path[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH]


def _set_result_path(dict_path):
    set_model_json_path(dict_path['model_json'])

    if 'visual_json' in dict_path:
        set_visual_json_path(dict_path['visual_json'])


def set_run_name(model_type, run_id):
    global _runData

    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_NAME] = "{}-{}".format(model_type, run_id.replace('-', ''))


def set_prefix_path(prefix_path):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_PREFIX_PATH] = prefix_path


def set_model_json_path(json_path):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_MODEL_JSON_PATH] = json_path


def set_visual_csv_path(csv_path=None):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_VISUAL_CSV_PATH] = csv_path


def set_visual_json_path(json_path=None):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_VISUAL_JSON_PATH] = json_path


def set_shap_json_path(shap_path=None):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_SHAP_JSON_PATH] = shap_path


def set_best_model_h5_path(hdf5_path=None):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH] = 'runs/' + hdf5_path


def set_best_model_json_path(json_path=None):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_BEST_MODEL_JSON_PATH] = 'runs/' + json_path


def set_best_model_joblib_path(joblib_path=None):
    global _runData
    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH] = 'runs/' + joblib_path


def get_or_create_run_directory():
    run_dir = LcConst.ENV_JUPYTER_HOME_DIR + LcConst.RUN_ROOT_PATH

    if not os.path.isdir(run_dir):
        try:
            os.mkdir(run_dir)
        except:
            logging.info("Run directory is not created")

    return run_dir


def set_git_meta(fileinfo):
    # fileinfo (dict_keys(['filename', 'digest', 'repo', 'commit', 'is_dirty', 'run_path']))
    global _runData

    run_obj = _runData[0]
    run_obj[LcConst.SOURCE_FILE_GIT_META] = fileinfo


def set_model_file_path(model_file_path):
    global _runData

    run_obj = _runData[0]
    run_obj[LcConst.RUN_OBJ_MODEL_FILE_PATH] = model_file_path


def set_python_dependencies(py_depenpency):
    global _runData

    run_obj = _runData[0]
    run_obj[LcConst.PYTHON_DEPENDENCY] = py_depenpency


def dict_to_list(dict_data):
    # "dependency": {
    #     "numpy": "1.18.2",
    #     "scikit-learn": "0.22.2.post1",
    #     "xgboost": "1.1.0rc1",
    #     "ModelLifeCycle": "0.1.0"
    # }

    # [
    #     'Numpy==1.18.1',
    #     'Pandas==1.0.1',
    #     'LightGBM==2.3.2'
    # ]
    return ["{}=={}".format(key, dict_data[key] or "<unknown>") for key in dict_data.keys()]


def print_run_info(run_obj):

    # DL & Classification
    if 'keras' in run_obj[LcConst.RUN_OBJ_NAME]:
        print(f'\nThe outputs of run: \n'
              f'best_model_save_path: {run_obj[LcConst.RUN_OBJ_BEST_MODEL_H5_PATH]} \n'
              f'model_info_json_path: {run_obj[LcConst.RUN_OBJ_MODEL_JSON_PATH]} \n'
              f'model_history_csv_path: {run_obj[LcConst.RUN_OBJ_VISUAL_CSV_PATH]} \n'
              f'visual_json_path: {run_obj[LcConst.RUN_OBJ_VISUAL_JSON_PATH]} \n')

    # ML & Classification
    elif run_obj[LcConst.RUN_OBJ_VISUAL_JSON_PATH] is not None:
        print(f'\nThe outputs of run: \n'
              f'best_model_save_path: {run_obj[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH]} \n'
              f'model_info_json_path: {run_obj[LcConst.RUN_OBJ_MODEL_JSON_PATH]} \n'
              f'visual_json_path: {run_obj[LcConst.RUN_OBJ_VISUAL_JSON_PATH]} \n')

    # ML & Regression
    elif run_obj[LcConst.RUN_OBJ_VISUAL_JSON_PATH] is None:
        print(f'\nThe outputs of run: \n'
              f'best_model_save_path: {run_obj[LcConst.RUN_OBJ_BEST_MODEL_JOBLIB_PATH]} \n'
              f'model_info_json_path: {run_obj[LcConst.RUN_OBJ_MODEL_JSON_PATH]}')
