import logging
import re
import os

logging.basicConfig(level=logging.DEBUG)


class AbcNotifier:
    def completed_message(self, **kwargs):
        pass


def load_model(run_name):
    k = []
    best_model_path_dict = dict()

    model_type = run_name.split('-')[0]
    t = run_name.split('-')[1].split('_')[0]
    filename = model_type + '-' + t[0:8] + '-' + t[8:12] + '-' + t[12:16] + '-' + t[16:20] + '-' +  t[20:]
    regex = re.compile(filename)

    common_path = '/home/work/runs/best-model'

    for subdir, dirs, files in os.walk(common_path):
        for filename in files:
            if regex.search(filename):
                k.append(os.path.join(common_path, filename))

    if 'json' in k[0]:
        best_model_path_dict['json'] = k[0]
        best_model_path_dict['h5'] = k[1]
    elif 'h5' in k[0]:
        best_model_path_dict['json'] = k[1]
        best_model_path_dict['h5'] = k[0]
    else:
        best_model_path_dict['joblib'] = k[0]

    # load model trained using keras
    if model_type == 'keras':
        from keras.models import model_from_json
        # load json and create model
        json_file = open(best_model_path_dict['json'], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        loaded_model.load_weights(best_model_path_dict['h5'])

    # load model trained using tensorflow
    elif model_type == 'tf.keras':
        from tensorflow.keras.models import model_from_json
        # load json and create model
        json_file = open(best_model_path_dict['json'], 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)

        # load weights into new model
        loaded_model.load_weights(best_model_path_dict['h5'])

    else:
        import joblib
        loaded_model = joblib.load(best_model_path_dict['joblib'])

    return loaded_model
