import os
import itertools

from Accuinsight.modeler.core import get, metricsLightgbm
from Accuinsight.modeler.core.LcConst.LcConst import RUN_ROOT_PATH
from Accuinsight.modeler.core.Run.RunInfo.RunInfo import get_or_create_run_directory


def get_file_path(model_name, root_path=RUN_ROOT_PATH, **kwargs):
    """
    ML 모델 저장을 위한 `add_experiment()`, 또는 DL 모델 저장을 위한 `autolog()` 실행시 output 저장을 위한 경로 생성 함수

    :model_name: 실행된 모델의 이름
    :root_path:
    :kwargs: DL framework를 구분하기 위한 변수 입력, (eg. usedFramework = 'keras')

    """
    
    # 기존 path 저장 - path 변경으로인한 에러 방지
    original_path = os.getcwd()
    
    # data 저장 상위 폴더
    home = get_or_create_run_directory()
    os.chdir(home)
    
    try:
        # DL frameworks(keras/tf/pytorch)
        a_dict = {}
        for key, value in kwargs.items():
            a_dict[key] = value
    
        prefix_path = 'results' + '-' + list(a_dict.values())[0] + '/'
    
    except IndexError:
        # ML
        prefix_path = 'results' + '-' + get.model_type(model_name) + '/'

    if not os.path.isdir(prefix_path):
        try:
            os.mkdir(prefix_path)
        except:
            pass
    
    os.chdir(prefix_path)

    # make dir 'best_model'
    save_best_model = 'best-model' # train 중 가장 좋은 모델의 weight 정보 저장
    save_model_path = home + save_best_model + '/'

    if not os.path.isdir(home + save_best_model):
        try:
            os.mkdir(home + save_best_model)
        except:
            pass

    ## 모델별 path 구성
    json_path_model = 'model-info-json'     # 기본적인 모형 관련 정보가 저장되는 json_path(ML/DL 공통)
    json_path_visual = 'for-visual-json'    # classification일 경우, json_path 하나 더 생성됨
    json_path_shap = 'shap-value-json'      # shap_value(feature_contribution) json 파일 저장하는 path(ML/DL 공통)

    path_list = list()
    if 'keras' in get.model_type(model_name) or 'tf' in get.model_type(model_name) or 'pytorch' in get.model_type(model_name):
        csv_path_visual = 'for-visual-csv'            # learning history가 저장되는 csv_path

        path_list = [json_path_model, csv_path_visual, json_path_visual, json_path_shap]   # DL

    elif 'lightgbm' in get.model_type(model_name):
        metric_lightgbm = get.from_model(model_name).all_params()['metric']
        if metric_lightgbm in metricsLightgbm.CLASSIFICATION:
            path_list = [json_path_model, json_path_visual, json_path_shap]       # lightgbm & Classification
        elif metric_lightgbm in metricsLightgbm.REGRESSION:
            path_list = [json_path_model, json_path_shap]                         # lightgbm & Regression
        else:
            pass
        
    elif 'Classifier' in get.model_type(model_name) or 'Logistic' in get.model_type(model_name) or 'SVC' in get.model_type(model_name) or 'NB' in get.model_type(model_name):
        path_list = [json_path_model, json_path_visual, json_path_shap]       # ML & Classification

    else:
        path_list = [json_path_model, json_path_shap]                         # ML & Regression
    
    for j in [i for i in path_list if not os.path.isdir(i)]:
        try:
            os.mkdir(j)
        except FileExistsError:
            pass

    
    ## 모델별 trial_num 생성
    if 'csv_path_visual' in locals():
        trial_num_list = list([get.trial_number_all(i, 'json') for i in path_list if 'json' in i])
        trial_num_list.append([get.trial_number_all(i, 'csv') for i in path_list if 'csv' in i])
        merged_list = list(itertools.chain.from_iterable(trial_num_list))
        merged_list = list(map(int, merged_list))
        trial_num = str(max(merged_list))

    else:
        trial_num_list = [get.trial_number_all(i, 'json') for i in path_list if 'json' in i]
        trial_num = str(max(trial_num_list))
    
    ## 최종 path
    if len(path_list) == 2:     # ML & Regression
        json_file_name_model = json_path_model + '/' + get.model_type(model_name) + '-' + trial_num + '.json'
        json_file_name_shap = json_path_shap + '/' + get.model_type(model_name) + '-shap-' + trial_num + '.json'
        dir_dict = {'home_path': home,
                    'prefix_path': prefix_path,
                    'save_model_dir': save_best_model,
                    'save_model_joblib': save_model_path,
                    'model_json': json_file_name_model,
                    'shap_json': json_file_name_shap,
                    'model_json_full': home + prefix_path + json_file_name_model,
                    'shap_json_full': home + prefix_path + json_file_name_shap}

    elif 'json' in path_list[1]:  # ML & Classification
        json_file_name_model = json_path_model + '/' + get.model_type(model_name) + '-' + trial_num + '.json'
        json_file_name_visual = json_path_visual + '/' + get.model_type(model_name) + '-visual-' + trial_num + '.json'
        json_file_name_shap = json_path_shap + '/' + get.model_type(model_name) + '-shap-' + trial_num + '.json'

        dir_dict = {'home_path': home,
                    'prefix_path': prefix_path,
                    'save_model_dir': save_best_model,
                    'save_model_joblib': save_model_path,
                    'model_json': json_file_name_model,
                    'visual_json': json_file_name_visual,
                    'shap_json': json_file_name_shap,
                    'model_json_full': home + prefix_path + json_file_name_model,
                    'visual_json_full': home + prefix_path + json_file_name_visual,
                    'shap_json_full': home + prefix_path + json_file_name_shap}

    elif len(path_list) == 4:  # DL
        csv_file_name_visual = csv_path_visual + '/' + get.model_type(model_name) + '-history-' + trial_num + '.csv'
        json_file_name_model = json_path_model + '/' + get.model_type(model_name) + '-' + get.trial_num_json(csv_path_visual, 'csv') + '.json'
        json_file_name_visual = json_path_visual + '/' + get.model_type(model_name) + '-visual-' + get.trial_num_json(csv_path_visual, 'csv') + '.json'
        json_file_name_shap = json_path_shap + '/' + get.model_type(model_name) + '-shap-' + get.trial_num_json(csv_path_visual, 'csv') + '.json'

#         save_model_hdf5 = home + prefix_path + save_best_model + '/'  + 'trial-' + get.trial_num_json(csv_path_visual, 'csv')
#         save_model_hdf5 = home + save_best_model + '/'

        dir_dict = {'home_path': home,
                    'prefix_path': prefix_path,
                    'save_model_dir': save_best_model,
                    'save_model_path': save_model_path,
                    'model_json': json_file_name_model,
                    'visual_csv': csv_file_name_visual,
                    'visual_json': json_file_name_visual,
                    'shap_json': json_file_name_shap,
                    'model_json_full': home + prefix_path + json_file_name_model,
                    'visual_csv_full': home + prefix_path + csv_file_name_visual,
                    'visual_json_full': home + prefix_path + json_file_name_visual,
                    'shap_json_full': home + prefix_path + json_file_name_shap}

    else:
        dir_dict = dict()

    # 기존 path로 변경
    os.chdir(original_path)
    
    return dir_dict


