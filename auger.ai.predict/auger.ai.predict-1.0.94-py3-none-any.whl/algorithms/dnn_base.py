from celery.utils.log import get_task_logger
logging = get_task_logger(__name__)
from auger_ml.Utils import get_app_node_cpu, get_app_node_ram_mb
from os import environ

import numpy as np
from numpy.random import seed

from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.model_selection import train_test_split

from tensorflow.compat.v1.keras.backend import set_floatx, cast_to_floatx
from tensorflow.compat.v1.keras.backend import backend as get_backend
from tensorflow.compat.v1.keras.utils import Sequence
from tensorflow.compat.v1.keras import optimizers
from tensorflow.compat.v1.keras.models import Model, Sequential
from tensorflow.compat.v1.keras.layers import Input, Dense, Dropout, Embedding, Reshape, concatenate, Concatenate, deserialize, serialize
from tensorflow.compat.v1.keras.callbacks import EarlyStopping, LearningRateScheduler
from tensorflow.python.keras.saving import saving_utils

#from auger_ml.algorithms.adam_wd import AdamWeightDecay

# Allow dynamic GPU memory allocation if Tensorflow backend is used
from auger_ml.algorithms.keras_mem import infer_batch_size

def unpack(model, training_config, weights):
    restored_model = deserialize(model)
    if training_config is not None:
        restored_model.compile(
            **saving_utils.compile_args_from_training_config(
                training_config
            )
        )
    restored_model.set_weights(weights)
    return restored_model

# Hotfix function
def make_keras_picklable():

    def __reduce__(self):
        model_metadata = saving_utils.model_metadata(self)
        training_config = model_metadata.get("training_config", None)
        model = serialize(self)
        weights = self.get_weights()
        return (unpack, (model, training_config, weights))

    cls = Model
    cls.__reduce__ = __reduce__

if get_backend() == "tensorflow":
    #from keras.backend.tensorflow_backend import set_session
    # import tensorflow as tf
    # TODO: migrate to tensorflow 2.0
    import tensorflow.compat.v1 as tf
    tf.disable_v2_behavior()

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
    config.log_device_placement = False  # to log device placement (on which device the operation ran)
    sess = tf.Session(config=config)
    #set_session(sess)
    tf.keras.backend.set_session(sess)

    make_keras_picklable()

# Get memory limit
def infer_max_mem(workers_count):
    auger_mem_lim = workers_count * get_app_node_ram_mb()

    if auger_mem_lim > 0:
        # Use worker memory limit to set the batch size
        num_cpus = workers_count * get_app_node_cpu()
        max_mem = int(0.5 * auger_mem_lim * 1024 * 1024 / num_cpus)
    else:
        if environ.get('AUGER_WORKER_TYPE_GPU', False):
            # On GPU instance use VRAM size
            max_mem = 10000 * 1024 * 1024
        else:
            # Fallback do default mem size of 4 GB
            max_mem = 4096 * 1024 * 1024
    return max_mem


# Set float format for batch generator
DNN_KERAS_FLOATX = 'float32'
DNN_NP_DTYPE = float  # np.float32

set_floatx(DNN_KERAS_FLOATX)


def dnn_convert_float(x):
    return DNN_NP_DTYPE(x)


class DNNBatchGenerator(Sequence):
    def __init__(self, Xs, y, batch_size=32):
        """
        Batch generator allows to use both dense and sparse matrices as inputs
        to default Keras' Model.fit_generator method.
        :param Xs: list of input arrays. must have the same number of rows.
        :param y: true output values.
        :param batch_size:
        """

        self.Xs = Xs
        self.y = y
        self.batch_size = batch_size

        self.num_samples = len(Xs[0])
        self.sparse = hasattr(Xs[0], 'toarray')
        self.batches_in_epoch = int((self.num_samples - 1) / batch_size) + 1
        self.shuffle_indices = np.random.permutation(np.arange(self.num_samples))

        if self.sparse:
            self._convert = lambda x: x.toarray()
        else:
            self._convert = lambda x: x

        # print("num_samples = {}".format(self.num_samples))
        # print("batches_in_epoch = {}".format(self.batches_in_epoch))
        # print("shuffle_indices = {}".format(self.shuffle_indices))

    def __len__(self):
        return self.batches_in_epoch

    def __getitem__(self, batch_num):
        start = batch_num * self.batch_size
        stop = min((batch_num + 1) * self.batch_size, self.num_samples)
        idxs = self.shuffle_indices[start:stop]

        bXs = [self._convert(X[idxs]) for X in self.Xs]
        bY = self.y[idxs]

        return bXs, bY

    def on_epoch_end(self):
        self.shuffle_indices = np.random.permutation(np.arange(self.num_samples))


class DeepNeuralNetworkBase(BaseEstimator):
    max_num_epochs_ = 500
    keras_optimizers_map = {
        'adam': optimizers.Adam,
        'nadam': optimizers.Nadam,
        'sgd': optimizers.SGD,
        'adagrad': optimizers.Adagrad,
        'adadelta': optimizers.Adadelta
    }

    def __init__(self, **kwargs):
        self._parse_kwargs(kwargs)

    def _parse_kwargs(self, kwargs):
        self.workers_count = kwargs.get('augerInfo').get('workers_count')

        # Fill all parameters to make sklearn-compatible
        self.numeric_features = kwargs.get('numeric_features', ())
        self.categorical_features_sets = kwargs.get('categorical_features_sets', ())
        self.label_encoding_features = kwargs.get('label_encoding_features', ())

        # NN training hyperparameters
        self.batch_size = kwargs.get('batch_size', 32)
        logging.info("batch size from trial: {}".format(self.batch_size))
        self.num_updates = kwargs.get('num_updates', 32)
        self.learning_rate = dnn_convert_float(kwargs.get('learning_rate', 0.01))
        self.weight_decay = dnn_convert_float(kwargs.get('weight_decay', 0.003))
        self.dropout_rate_final_layer = dnn_convert_float(kwargs.get('dropout_rate_final_layer', 0.5))
        self.solver_type = kwargs.get('solver_type', 'adam')
        self.lr_policy = kwargs.get('lr_policy', 'fixed')
        self.learning_rate_gamma = dnn_convert_float(kwargs.get('learning_rate_gamma', 0.01))
        self.learning_rate_k = dnn_convert_float(kwargs.get('learning_rate_k', 0.5))
        self.learning_rate_s = kwargs.get('learning_rate_s', 2)
        self.num_epochs = kwargs.get('num_epochs', DeepNeuralNetworkBase.max_num_epochs_)

        self.layer_sizes = []
        self.layer_acts = []
        self.embed_sizes = []
        self.layer_drops = []
        self.layer_initializers = []

        all_params = sorted(list(kwargs.keys()))
        for k in all_params:
            if k.startswith('hidden_layer_sizes_'):
                self.layer_sizes.append(kwargs[k])
            elif k.startswith('hidden_layer_act_'):
                self.layer_acts.append(kwargs[k])
            elif k.startswith('embed_sizes_'):
                self.embed_sizes.append(kwargs[k])
            elif k.startswith('dropout_rates_'):
                self.layer_drops.append(dnn_convert_float(kwargs[k]))
            elif k.startswith('layer_initializers_'):
                self.layer_initializers.append(kwargs[k])

    def get_params(self, deep=True):
        p = self._get_shared_params()
        pl = self._get_per_layer_params()
        p.update(pl)
        return p

    def _get_shared_params(self):
        params = {
            'numeric_features': self.numeric_features,
            'categorical_features_sets': self.categorical_features_sets,
            'label_encoding_features': self.label_encoding_features,
            'batch_size': self.batch_size,
            'num_updates': self.num_updates,
            'learning_rate': self.learning_rate,
            'weight_decay': self.weight_decay,
            'dropout_rate_final_layer': self.dropout_rate_final_layer,
            'solver_type': self.solver_type,
            'lr_policy': self.lr_policy,
            'learning_rate_gamma': self.learning_rate_gamma,
            'learning_rate_k': self.learning_rate_k,
            'learning_rate_s': self.learning_rate_s,
        }

        return params

    def _get_per_layer_params(self):
        params = {}
        for i, s in enumerate(self.layer_sizes):
            params['hidden_layer_sizes_{}'.format(i)] = s
        for i, a in enumerate(self.layer_acts):
            params['hidden_layer_act_{}'.format(i)] = a
        for i, e in enumerate(self.embed_sizes):
            params['embed_sizes_{}'.format(i)] = e
        for i, d in enumerate(self.layer_drops):
            params['dropout_rates_{}'.format(i)] = d
        for i, ki in enumerate(self.layer_initializers):
            params['layer_initializers_{}'.format(i)] = ki

        return params

    def _infer_last_layer(self, X, y):
        self.last_layer_size_ = None
        self.last_layer_act_ = None
        self.loss_ = None

    def _infer_additional_params(self):
        self.num_categoricals_ = len(self.categorical_features_sets)

        # TODO: remove and pass from DataSource
        # print("Num categoricals: {}".format(self.num_categoricals_))
        if len(self.embed_sizes) < self.num_categoricals_:
            self.embed_sizes = []
            for s in self.categorical_features_sets:
                self.embed_sizes.append(max(1, int(np.log(len(s)))))
        # print(self.embed_sizes)

        self.num_numeric_inputs_ = len(self.numeric_features)
        self.numeric_features_ = self.numeric_features
        num_cat_inputs = np.sum([len(s) for s in self.categorical_features_sets])

        if self.num_numeric_inputs_ < 1 and num_cat_inputs < self.num_inputs_:
            numeric_features = set(range(self.num_inputs_))
            for s in self.categorical_features_sets:
                numeric_features -= set(s)
            self.num_numeric_inputs_ = len(numeric_features)
            self.numeric_features_ = sorted(list(numeric_features))

        self.categorical_sizes_ = tuple(len(s) for s in self.categorical_features_sets)

    def lr_policy_fixed(self, epoch, lr):
        return lr * 1.0

    def lr_policy_inv(self, epoch, lr):
        return lr * np.power(1.0 + self.learning_rate_gamma * epoch, -self.learning_rate_k)

    def lr_policy_exp(self, epoch, lr):
        return lr * np.power(self.learning_rate_gamma, epoch)

    def lr_policy_step(self, epoch, lr):
        return lr * np.power(self.learning_rate_gamma, np.floor(np.float(epoch) / np.float(self.learning_rate_s)))

    @staticmethod
    def concatenate_any(l):
        if len(l) > 1:
            layer = Concatenate(axis=-1)
            res = layer(l)
            # print("Concat: {}".format(layer.output_shape))
            # print("res: {}".format(res.shape))
            return res
        else:
            return l[0]

    def _get_nn_inputs(self):
        # Get inputs for Keras Model constructor as well as single merged input vector to build network on top

        k_numeric_inputs = Input(shape=(self.num_numeric_inputs_,))
        k_categorical_inputs = [Input(shape=(s,)) for s in self.categorical_sizes_]
        k_le_inputs = [Input(shape=(1,)) for _ in self.label_encoding_features]

        model_inputs = [k_numeric_inputs] + k_categorical_inputs + k_le_inputs

        k_inputs_to_merge = [k_numeric_inputs]

        input_layer_shape = self.num_numeric_inputs_
        # Attach Embedding to each categorical input
        if self.embed_sizes:
            k_embedded_categoricals = [Dense(units=s,
                                             activation='linear')(x) for s, x in
                                       zip(self.embed_sizes, k_categorical_inputs)]
            k_inputs_to_merge += k_embedded_categoricals
            input_layer_shape += np.sum(self.embed_sizes)

        if self.label_encoding_features:
            k_embedded_les = [Reshape(target_shape=(-1,))(Embedding(input_dim=s,
                                                                    output_dim=o,
                                                                    input_length=1)(x)) for s, o, x in
                              zip(self.le_input_sizes_, self.le_output_sizes_, k_le_inputs)]
            k_inputs_to_merge += k_embedded_les

            input_layer_shape += np.sum(self.le_output_sizes_)

        input_layer = self.concatenate_any(k_inputs_to_merge)

        return model_inputs, input_layer, input_layer_shape

    def _build_model(self):
        # Build model equipped with optimizer
        # print("Build model called")

        model_inputs, input_layer, input_layer_shape = self._get_nn_inputs()

        model = self._create_model(model_inputs, input_layer, input_layer_shape)

        self.learning_rate_ = self.learning_rate
        #TODO: fix adam_wd
        if self.solver_type in self.keras_optimizers_map.keys():
            solver = self.keras_optimizers_map[self.solver_type](lr=self.learning_rate_)
        # elif self.solver_type == 'adam_wd':
        #     alpha = self.learning_rate
        #     self.learning_rate_ = 1.0
        #     solver = AdamWeightDecay(lr=self.learning_rate_, alpha=alpha, weight_decay=self.weight_decay)
        else:
            logging.error("Error: unknown solver type <{}>".format(self.solver_type))
            solver = optimizers.Adam(lr=self.learning_rate_)

        # print("Calling Keras Model compile")
        model.compile(optimizer=solver, loss=self.loss_)
        # print("After Compile")

        return model

    def _create_model(self, model_inputs, input_layer, input_layer_shape):
        # Create internal layer structure of the network

        layer = input_layer
        # Stack fully connected layers on top
        for s, a, d, ki in zip(self.layer_sizes, self.layer_acts, self.layer_drops, self.layer_initializers):
            layer = Dense(units=s,
                          activation=a,
                          kernel_initializer=ki)(
                Dropout(rate=d)(layer)
            )
        layer = Dense(units=self.last_layer_size_,
                      activation=self.last_layer_act_)(
            Dropout(rate=self.dropout_rate_final_layer)(layer)
        )
        # print("Calling Keras Model constructor")
        model = Model(inputs=model_inputs,
                      outputs=layer)
        return model

    def _convert_inputs(self, X):
        X_n = X[:, list(self.numeric_features_)]
        X_c = [X[:, cs] for cs in self.categorical_features_sets]
        X_le = [X[:, lc] for lc in self.label_encoding_features]

        return [X_n] + X_c + X_le

    def _convert_outputs(self, y):
        return y

    def _val_split(self, Xs, y, y_orig, test_size=0.1):
        ans = train_test_split(y, *Xs, test_size=test_size)

        trains = ans[0::2]
        tests = ans[1::2]

        return trains[1:], tests[1:], trains[0], tests[0]

    def build_model_for_data(self, X, y):
        seed(1)
        self.num_inputs_ = X.shape[1]
        self._infer_additional_params()
        self._infer_le_sizes(X)
        self._infer_last_layer(X, y)

        model = self._build_model()
        return model

    def fit(self, X, y):
        #logging.info("fit started")
        seed(1)

        # Input validation
        X, y = check_X_y(X, y)

        model = self.build_model_for_data(X, y)

        # print("num_classes: {}".format(getattr(self, 'num_classes', None)))
        # print("Model created, callig Keras fit")
        _X = self._convert_inputs(X)
        _y = self._convert_outputs(y)

        _X_train, _X_test, _y_train, _y_test = self._val_split(_X, _y, y, test_size=0.1)

        early_stop = EarlyStopping(monitor='val_loss',
                                   min_delta=0,
                                   patience=2,
                                   verbose=0, mode='auto')

        # Get LR decay policy method
        lr_policy_func = getattr(self, 'lr_policy_{}'.format(self.lr_policy), None)
        if not lr_policy_func:
            logging.error("Error: unknown LR policy type <{}>".format(self.lr_policy))
            lr_policy_func = self.lr_policy_fixed
        lr_decay = LearningRateScheduler(lr_policy_func)

        # model.fit(_X, _y, verbose=0, epochs=500, validation_split=0.1, callbacks=[early_stop, lr_decay])
        # model.fit(_X, _y, verbose=0, epochs=10)

        max_mem = infer_max_mem(self.workers_count)

        self.batch_size = max(self.batch_size, min(infer_batch_size(model, max_mem=max_mem), len(y)))
        logging.info("Inferred batch size: {}".format(self.batch_size))

        model.fit_generator(DNNBatchGenerator(_X_train, _y_train, batch_size=self.batch_size),
                            verbose=0,
                            epochs=self.num_epochs,
                            # use_multiprocessing=True,
                            # workers=4,
                            validation_data=DNNBatchGenerator(_X_test, _y_test, batch_size=len(_y_test)),
                            callbacks=[early_stop, lr_decay])

        self.X_ = X
        self.y_ = y
        self.weights_ = model.get_weights()
        self.model_ = model
        # print("Keras fit finished")
        #logging.info("fit finished")

        # Return the classifier
        return self

    def predict(self, X):
        pass

    @staticmethod
    def infer_additional_params(trial):
        # logging.info("trial: {}".format(trial))
        all_features_names = trial['featureColumns']
        cat_features_names = trial.get('categoricalFeatures', [])
        le_features_names = trial.get('labelEncodingFeatures', [])

        cat_features_sets = [[] for _ in cat_features_names]
        numeric_features = []
        le_features = []
        for i in range(len(all_features_names)):
            if all_features_names[i] in le_features_names:
                le_features.append(i)
            else:
                f = True
                for j in range(len(cat_features_names)):
                    if all_features_names[i].startswith(cat_features_names[j] + "__"):
                        cat_features_sets[j].append(i)
                        f = False
                        break
                if f:
                    numeric_features.append(i)

        categorical_features_sets = tuple(
            tuple(l) for l in cat_features_sets if len(l) > 0
        )

        ans = {"numeric_features": tuple(numeric_features),
               "categorical_features_sets": categorical_features_sets}
        if len(le_features) > 0:
            ans['label_encoding_features'] = le_features

        r = trial.get('ratio', 1.0)
        if r < 1.0:
            ans['num_epochs'] = int(DeepNeuralNetworkBase.max_num_epochs_ * r)

        return ans

    def _infer_le_sizes(self, X):
        if self.label_encoding_features:
            self.le_input_sizes_ = [len(np.unique(X[:, i])) + 1 for i in self.label_encoding_features]
            self.le_output_sizes_ = [max(1, int(np.log(s))) for s in self.le_input_sizes_]
        else:
            self.le_input_sizes_ = []
            self.le_output_sizes_ = []


class DeepNeuralNetworkClassifier(DeepNeuralNetworkBase, ClassifierMixin):
    def _infer_last_layer(self, X, y):
        if self.num_classes_train_ < 3:
            self.last_layer_size_ = 1
            self.last_layer_act_ = 'sigmoid'
            self.loss_ = 'binary_crossentropy'
        else:
            self.last_layer_size_ = self.num_classes_train_
            self.last_layer_act_ = 'softmax'
            self.loss_ = 'categorical_crossentropy'

    def _convert_outputs(self, y):
        if self.num_classes_train_ > 2:
            return to_categorical(y, num_classes=self.num_classes_train_)
        else:
            return y

    def fit(self, X, y):
        # check_X_y(X, y)
        self.classes_, y_new = np.unique(y, return_inverse=True)
        self.num_classes_train_ = len(self.classes_)
        return super(DeepNeuralNetworkClassifier, self).fit(X, y_new)

    def predict_proba(self, X):
        # logging.info("Predict.proba started")
        X = check_array(X)

        if hasattr(self, "model_"):
            model = self.model_
        else:
            model = self._build_model()
            model.set_weights(self.weights_)

        y_hat = model.predict(self._convert_inputs(X), batch_size=self.batch_size)

        if self.num_classes_train_ == 2:
            y_hat = y_hat.ravel()

        # logging.info("Predict.proba finished")
        if y_hat.ndim == 1:
            return np.vstack([1 - y_hat, y_hat]).T
        else:
            return y_hat

    def predict(self, X):
        # logging.info("Predict started")
        check_is_fitted(self, ['X_', 'y_'])
        X = check_array(X)
        y_hat = self.predict_proba(X)

        idx = y_hat.argmax(axis=1).clip(max=len(self.classes_) - 1)

        # logging.info("Predict finished")
        return self.classes_[idx]


class DeepNeuralNetworkRegressor(DeepNeuralNetworkBase, RegressorMixin):
    def _infer_last_layer(self, X, y):
        self.last_layer_size_ = 1
        self.last_layer_act_ = 'linear'
        self.loss_ = 'mse'

    def predict(self, X):
        X = check_array(X)

        if hasattr(self, "model_"):
            model = self.model_
        else:
            model = self._build_model()
            model.set_weights(self.weights_)

        y_hat = model.predict(self._convert_inputs(X), batch_size=self.batch_size)

        return y_hat[:, 0]


def to_categorical(y, num_classes=None):
    # Taken from Keras to avoid import bug
    """Converts a class vector (integers) to binary class matrix.

    E.g. for use with categorical_crossentropy.

    # Arguments
        y: class vector to be converted into a matrix
            (integers from 0 to num_classes).
        num_classes: total number of classes.

    # Returns
        A binary matrix representation of the input. The classes axis
        is placed last.
    """
    y = np.array(y, dtype='int')
    input_shape = y.shape
    if input_shape and input_shape[-1] == 1 and len(input_shape) > 1:
        input_shape = tuple(input_shape[:-1])
    y = y.ravel()
    if not num_classes:
        num_classes = np.max(y) + 1
    n = y.shape[0]
    categorical = np.zeros((n, num_classes), dtype=np.float32)
    categorical[np.arange(n), y] = 1
    output_shape = input_shape + (num_classes,)
    categorical = np.reshape(categorical, output_shape)
    return categorical


if __name__ == "__main__":
    from sklearn.utils.estimator_checks import check_estimator

    check_estimator(DeepNeuralNetworkClassifier)
    check_estimator(DeepNeuralNetworkRegressor)
