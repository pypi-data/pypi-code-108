import pandas as pd
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, regularizers, initializers
from tensorflow.keras.layers import BatchNormalization
import tensorflow_docs as tfdocs
import tensorflow_docs.modeling
import time
import matplotlib as mpl
import random
from joblib import Parallel, delayed, parallel_backend
import multiprocessing
import pickle
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MaxNLocator

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from numpy.random import seed
seed(1)
tf.random.set_seed(1)


def vectorize_random(array):
    """Returns a column vector and randomply shuffles the elements"""
    np.random.shuffle(array)
    return np.array(array).reshape(len(array), 1)


def vectorize(array):
    """Returns a column vector from the input array"""
    return np.array(array).reshape(len(array), 1)


class Dataset:
    """The Dataset class is aimed to simplify data pre-processing for fitting neural networks

    Constructing a Dataset object requires inputing a labelled dataset csv file,
    which must have an index column and a header row describing what each column represents.

    Through the argument qoi=<str>, the user selects from the columns, the one corresponding to the quantity
    of interest.

    Normalisation of the inputs and the quantity of interest can be achieved through the
    x_norm and qoi_norm parameters.

    Attributes
    ----------

    qoi_label : str
        the label of the qoi column in the csv file
    x_stats : pd.DataFrame
        a dataframe containing the statistical description of the inputs.
    qoi_stats : pd.DataFrame
        a dataframe containing the statistical description of the quantity of interest
    qoi : pd.DataFrame
        a dataframe containing the quantity of interest values
    x : pd.DataFrame
        a dataframe containing the inputs values
    n_samples : int
        the number of samples present in the dataset
    n_params : int
        the number of parameters describing the quantity of interest
    normalisation_x : str or None
        a string defining the normalisation method for the inputs.
        It can take values of 'mean_std', 'max_min', 'ones', or None
    normalisation_qoi : str or None
        a string defining the normalisation method for the quantity.
        It can take values of 'mean_std', 'max_min', 'ones', or None
    x_normed : pd.DataFrame
        a dataframe containint the normalised inputs values
    qoi_normed : pd.DataFrame
        a dataframe containing the normalised qoi values
    folds : dict
        a dictionary of the form:
        folds[i] = {'train_x': train_x,
                             'train_qoi': train_qoi,
                             'test_x': test_x,
                             'test_qoi': test_qoi
                    }
        Created by the method gen_folds()

    Methods
    ----------

    norm_x(x, verbose=True)
        returns a pd.DataFrame object with the normalised values of the input x, according to normalisation_x
    norm_qoi(qoi)
        returns a pd.DataFrame object with the normalised values of the input qoi, according to normalisation_qoi
    ret_qoi(qoi)
        returns a pd.DataFrame object to the original values reversing the normalisation, according to normalisation_qoi
    gen_folds(k):
        populates the folds dictionary by randomly partitioning the data into k folds
    save(fout='Dataset')
        saves a picked dataset object to the fout filename. It appends .dts to the name if not already there
    load(fin='Dataset.dts')
        returns a Dataset object by loading the input filename
    """

    def __init__(self, fin, qoi, remove=None, x_norm='mean_std', qoi_norm='mean_std', n_ranges_x=None,
                 n_ranges_qoi=None):
        """
        Parameters
        ----------
        fin : str
            the path to the csv file containing the entries.
            The file must have an index column and a header row describing what each column represents.
        qoi : str
            the label of the quantity of interest column in the csv file
        remove : str, array or None
            In the input cvs, any entry not defined as "qoi" will be taken as an input. This keyword can
            be used to remove columns in the dataset which are neither inputs nor qoi

            a single entry in the form of a str with the label of a column to be removed from the dataset
            an array of str with labels for columns to be removed from the dataset
        x_norm : str
            default: 'mean_std;
            Defines the normalisation method for the inputs. Options are:
                'mean_std' : normalises the data to have zero mean and standard deviation of 1
                'ones' : normalises the data to be in the [-1, 1] range
                'max_min' : if no additional arguments are passed, normalises the data to be in the [0, 1] range
                            according to the data max and min values. The behaviour of this method can be tailored
                            with the n_ranges_x parameter, defining the max and min values for normalisation
        n_ranges_x : array;
            Defines the min and max values for inputs normalisation if the method is 'max_min'. Does nothing if
            another method is selected
        qoi_norm : str
            default: 'mean_std;
            Defines the normalisation method for the qoi. Options are:
                'mean_std' : normalises the data to have zero mean and standard deviation of 1
                'ones' : normalises the data to be in the [-1, 1] range
                'max_min' : if no additional arguments are passed, normalises the data to be in the [0, 1] range
                            according to the data max and min values. The behaviour of this method can be tailored
                            with the n_ranges_qoi parameter, defining the max and min values for normalisation
        n_ranges_qoi : array;
            Defines the min and max values for qoi normalisation if the method is 'max_min'. Does nothing if
            another method is selected

        """

        self.dataset = pd.read_csv(fin, comment='\t', sep=",", skipinitialspace=False, index_col=0)

        if remove is not None:
            # Removing column from dataset
            if type(remove) == list:
                for item in remove:
                    _ = self.dataset.pop(item)
            else:
                _ = self.dataset.pop(remove)

        self.qoi_label = qoi

        # Getting stats from dataset (mean, std, max, min, etc..)
        self.x_stats = self.dataset.describe()
        self.qoi_stats = self.x_stats.pop(qoi)

        self.x_stats = self.x_stats.transpose()
        self.qoi_stats = self.qoi_stats.transpose()

        # Splitting x and qoi to their own db
        self.qoi = self.dataset.pop(qoi)
        self.x = self.dataset

        self.n_samples, self.n_params = self.x.shape

        print ('Read %s samples from the dataset' % self.n_samples)
        print ('The dimensionality is %s' % self.n_params)
        print ('The QOI for the model is %s' % qoi)

        self.normalisation_x = x_norm
        self.normalisation_qoi = qoi_norm

        if self.normalisation_x == 'max_min':
            if n_ranges_x is not None:
                self.n_ranges_x = n_ranges_x
            else:
                self.n_ranges_x = [self.x_stats['min'], self.x_stats['max']]

        if self.normalisation_qoi == 'max_min':
            if n_ranges_qoi is not None:
                self.n_ranges_qoi = n_ranges_qoi
            else:
                self.n_ranges_qoi = [self.qoi_stats['min'], self.qoi_stats['max']]

        self.x_normed = self.norm_x(self.x)
        self.qoi_normed = self.norm_qoi(self.qoi)

        self.folds = {}

    def norm_x(self, x, verbose=True):
        """

        Parameters
        ----------
        x : list, np.array, pd.DataFrame
            Contains the inputs to be normalised according to self.normalisation_x
        verbose : bool
            if True, prints out the normalisation method being applied

        Returns
        -------
        pd.DataFrame containing the normalised values of x

        """

        if not isinstance(x, pd.core.frame.DataFrame):
            x = np.array(x)
            
            if len(x.shape) == 1:
                x = pd.DataFrame(vectorize(x).T, columns=self.x.columns)
            else:
                x = pd.DataFrame(x, columns=self.x.columns)

        if self.normalisation_x == 'mean_std':
            if verbose:
                print('Normalising inputs to have zero mean and std of 1')
            return (x - self.x_stats['mean']) / self.x_stats['std']
        elif self.normalisation_x == 'max_min':
            if verbose:
                print('Normalising inputs with max-min values')
            return (x - self.n_ranges_x[0]) / (self.n_ranges_x[1] - self.n_ranges_x[0])
        elif self.normalisation_x is None:
            if verbose:
                print('Not normalising inputs')
            return x
        elif self.normalisation_x == 'ones':
            if verbose:
                print ('Normalising inputs to the [-1, 1] range')
            return 2 * (x - self.x_stats['min']) / (self.x_stats['max'] - self.x_stats['min']) - 1.0
        else:
            raise ValueError('Incorrect normalisation scheme for x. Choose "mean_std", "max_min", "ones" or "None"')

    def norm_qoi(self, qoi):
        """

        Parameters
        ----------
        qoi : list, np.array, pd.DataFrame
            Contains the inputs to be normalised according to self.normalisation_qoi

        Returns
        -------
        pd.DataFrame containing the normalised values of qoi

        """
        if self.normalisation_qoi == 'mean_std':
            print('Normalising qoi to have zero mean and std of 1')
            return (qoi - self.qoi_stats['mean']) / self.qoi_stats['std']
        elif self.normalisation_qoi == 'max_min':
            print('Normalising qoi with max-min values: [%.4f, %.4f]' % (self.n_ranges_qoi[0], self.n_ranges_qoi[1]))
            return (qoi - self.n_ranges_qoi[0]) / (self.n_ranges_qoi[1] - self.n_ranges_qoi[0])
        elif self.normalisation_qoi is None:
            print('Not normalising qoi')
            return qoi
        elif self.normalisation_qoi == 'ones':
            print ('Normalising qoi to the [-1, 1] range')
            return 2 * (qoi - self.qoi_stats['min']) / (self.qoi_stats['max'] - self.qoi_stats['min']) - 1.0
        else:
            raise ValueError('Incorrect normalisation scheme for qoi. Choose from "mean_std",  "max_min" or "None"')

    def ret_qoi(self, qoi):
        """

        Parameters
        ----------
        qoi : pd.DataFrame contaning the inputs to be brought back from normalisation

        Returns
        -------
        pd.DataFrame containing un-normalised values of qoi, according to self.normalisation_qoi

        """
        if self.normalisation_qoi == 'mean_std':
            return qoi * self.qoi_stats['std'] + self.qoi_stats['mean']
        elif self.normalisation_qoi == 'max_min':
            return qoi * (self.n_ranges_qoi[1] - self.n_ranges_qoi[0]) + self.n_ranges_qoi[0]
        elif self.normalisation_qoi == 'ones':
            return (qoi + 1.0) * (self.qoi_stats['max'] - self.qoi_stats['min']) / 2 + self.qoi_stats['min']
        elif self.normalisation_qoi is None:
            return qoi

    def gen_folds(self, k):
        """
        Populates the self.folds dictionary with k entries
        self.folds[i] = {'train_x': train_x,
                        'train_qoi': train_qoi,
                        'test_x': test_x,
                        'test_qoi': test_qoi
                        }
        train_x : pd.DataFrame containing the training inputs of the whole dataset except those present in test_x.
        train_qoi : pd.DataFrame containing the training qoi to be used with this fold
        test_x : pd.DataFrame contains a subset of the whole dataset to be used for testing
        test_qoi : pd.DataFrame containing the testing qoi to be used with this fold

        Parameters
        ----------
        k : int
            The number of folds to be created

        Returns
        -------
        None

        """

        print ('Generating %s folds for CV' % k)

        # Getting array indices
        indices = self.x.index

        lFold = int(self.n_samples / k)  # length of each fold
        print ('The length of each fold is %s' % lFold)

        if (self.n_samples % k) != 0:
            add = self.n_samples % k  # the number of folds that will have an extra sample
            print ('%s folds will have an additional sample' % add)

        else:
            add = -1

        for i in range(k):
            fold = []  # the collection of indices in each fold

            if i < add:
                lFold_current = lFold + 1
            else:
                lFold_current = lFold

            while len(fold) < lFold_current:
                index = random.randint(min(indices), max(indices))
                if index in indices:
                    fold.append(index)
                    indices = np.delete(indices,
                                        np.argwhere(indices == index))  # removing index from array to avoid repetition

            # Generating datasets
            x = self.x_normed
            qoi = self.qoi_normed

            test_x = x.iloc[fold, :]
            test_qoi = qoi.iloc[fold]

            train_x = x.drop(test_x.index)
            train_qoi = qoi.drop(test_qoi.index)

            self.folds[i] = {'train_x': train_x,
                             'train_qoi': train_qoi,
                             'test_x': test_x,
                             'test_qoi': test_qoi
                             }

    def save(self, fout='Dataset'):
        """
        Saves the Dataset to a pickled object
        Parameters
        ----------
        fout : str
            an output file name

        Returns
        -------
        None

        """
        if '.dts' not in fout:
            fout += '.dts'
        with open(fout,'wb') as output:
            pickle.dump(self,output,pickle.HIGHEST_PROTOCOL)

    def load(fin='Dataset.dts'):
        """
        Creates a Dataset object based on the pickled filename
        Returns
        -------
        a Dataset object
        """
        with open(fin, 'rb') as input:
            return pickle.load(input)


class NeuralNet:
    """
    The NeuralNet class is a wrapper on Keras functionality, aiming to simplify the creation and training of
    neural networks used for regression

    Attributes
    ----------

    EPOCHS : int
        the number of training epochs
    BATCH_SIZE : int
        the batch size to be used in training
    VALIDATION_SPLIT : float
        fraction of the training fata that will be spared for validation monitoring during training
    KERNEL_INI : str
        a string defining the initialization method for the weights
    BIAS_INI : str
        a string defining the initialization method for the biases
    LLA : string or None
        the activation function for the last layer. Can be 'linear' or None
    BATCH_NORM : bool
        whether to use batch normalisation
    PATIENCE : the number of epochs without change in the validation loss before early-stopping
    optimiser : the optimiser to be used in training
    nNeurons : array
        an array of int describing the number of neurons per hidden layer
    l2Reg : array
        an array of float describing the l2 regularization coefficient on each hidden layer
    dropout : array
        an array of float describing the dropout coefficient on each hidden layer

    Methods
    ----------

    setup_model(function)
        sets up the model based on the input architecture, number of hidden layers and activation function
    fit_model(x, y, verbose=False)
        starts the training process using inputs x and qoi y.
        if verbose=True, uses the tfdocs.modeling.EpochDots() callback
    save_model()
        saves the model to a directory called saved_model/my_model
    load_model(name='saved_model')
        returns a NeuralNet object from the loaded model
    plot_convergence(name='NN')
        plots the training convergence of the neural network for MAE and MSE validation and training loss
    measure_accuracy(x_test, y_test):
        evaluates the model on the testing inputs and returns metrics for R2, MAE and MSE
    predict(x)
        employs the neural network to predict the qoi value based on the inputs x

    """


    EPOCHS = 4000
    BATCH_SIZE = 2 ** 5
    VALIDATION_SPLIT = 0.2  # 20% of the training data will be spared for validation monitoring during training
    KERNEL_INI = 'glorot_uniform'  # glorot_uniform, glorot_normal, he_normal, he_uniform, ones, zeros
    BIAS_INI = 'zeros'
    LLA = 'linear'  # last layer activation can be 'linear' or None
    BATCH_NORM = False
    PATIENCE = 500

    def __init__(self, inputs, hl, n_params):
        """

        Parameters
        ----------
        hl : int
            the number of hidden layers of the network
        inputs : array
            an array of inputs defining the architecture of the network. Input and Output layers should not be included
            The first hl entries must contain int values describing the number of neurons in each hidden layer
            the second hl entries must contain float values describing the l2 regularization coefficient for each hidden layer
            the last hl entries must contain float values describing the dropout coefficient for each hidden layer
        n_params : int
            The number of parameters that describes the output. Will be used to define the input layer
        """

        self.inputs = inputs
        self.HIDDEN_LAYERS = hl

        self.nNeurons = self.inputs[:self.HIDDEN_LAYERS]
        self.l2Reg = self.inputs[self.HIDDEN_LAYERS:2 * self.HIDDEN_LAYERS]
        self.dropout = self.inputs[2 * self.HIDDEN_LAYERS:]

        self.n_params = n_params  # number of parameters in the model

        # Neural Network parameters
        self.model = keras.Sequential()
        self.optimizer = tf.keras.optimizers.RMSprop(0.001)
        self.early_stop = keras.callbacks.EarlyStopping(monitor='val_mse', patience=self.PATIENCE)

        # Convergence history
        self.history = None

    def setup_model(self, function):
        """
        Sets up the network model
        Parameters
        ----------
        function : str
            the activation function for all the hidden layers

        Returns
        -------
        None

        """

        # print ('Setting up model')

        for i in range(self.HIDDEN_LAYERS):
            if i == 0:
                if self.l2Reg[i] != 0:
                    self.model.add(layers.Dense(self.nNeurons[i],
                                                activation=function,
                                                kernel_regularizer=regularizers.l2(self.l2Reg[i]),
                                                input_shape=[self.n_params],
                                                kernel_initializer=self.KERNEL_INI,
                                                bias_initializer=self.BIAS_INI
                                                )
                                   )
                else:
                    self.model.add(layers.Dense(self.nNeurons[i],
                                                activation=function,
                                                input_shape=[self.n_params],
                                                kernel_initializer=self.KERNEL_INI,
                                                bias_initializer=self.BIAS_INI
                                                )
                                   )
            else:
                if self.l2Reg[i] != 0:
                    self.model.add(layers.Dense(self.nNeurons[i],
                                                activation=function,
                                                kernel_regularizer=regularizers.l2(self.l2Reg[i]),
                                                kernel_initializer=self.KERNEL_INI,
                                                bias_initializer=self.BIAS_INI
                                                )
                                   )
                else:
                    self.model.add(layers.Dense(self.nNeurons[i],
                                                activation=function,
                                                kernel_initializer=self.KERNEL_INI,
                                                bias_initializer=self.BIAS_INI
                                                )
                                   )

            if self.dropout[i] != 0:
                self.model.add(layers.Dropout(self.dropout[i]))

            if self.BATCH_NORM:
                # ADDING BATCH NORMALISATION
                self.model.add(BatchNormalization())

        if self.LLA is not None:
            self.model.add(layers.Dense(1,
                                        activation=self.LLA))
        else:
            self.model.add(layers.Dense(1))

        self.model.compile(loss='mse', optimizer=self.optimizer, metrics=['mae', 'mse'])

        # print (self.model.summary())

    def fit_model(self, x, y, verbose=False):
        """
        Carries out the training of the network
        Parameters
        ----------
        x : array
            defines the training inputs
        y : array
            defines the training outputs
        verbose : bool
            if True, uses the tfdocs.modeling.EpochDots() callback to monitor training

        Returns
        -------
        None

        """
        startTime = time.time()

        if verbose:
            callback = [self.early_stop , tfdocs.modeling.EpochDots()]
        else:
            callback = [self.early_stop]

        self.history = self.model.fit(x,
                                      y,
                                      epochs=self.EPOCHS,
                                      validation_split=self.VALIDATION_SPLIT,
                                      batch_size=self.BATCH_SIZE,
                                      verbose=0,
                                      callbacks=callback
                                      )

        endTime = time.time()
        print ('execution time = %.3f sec' % (endTime - startTime))

    def save_model(self):
        """
        Saves the network model to a directory called saved_model/my_model
        Returns
        -------
        None
        """
        # Save the entire model as a SavedModel.
        os.system('mkdir -p saved_model')
        self.model.save('saved_model/my_model')

    def load_model(name='saved_model'):
        """
        Loads a NeuralNet object
        Returns
        -------
        A NeuralNet object based on the input directory name
        """
        if os.path.exists(name):
            model = tf.keras.models.load_model('%s/my_model' % name)
            network = NeuralNet(inputs=[100,0,0], hl=1, n_params=1)
            network.model = model
            return network
        else:
            raise ValueError('%s model not found' % name)

    def format_axes(self, axes, label):
        axes.tick_params(direction='in', which='both')
        axes.xaxis.set_major_locator(MaxNLocator(8))
        axes.xaxis.set_minor_locator(AutoMinorLocator())
        axes.yaxis.set_minor_locator(AutoMinorLocator())
        axes.xaxis.set_ticks_position('both')
        axes.yaxis.set_ticks_position('both')
        axes.set_xlabel('Epochs')
        axes.set_ylabel(label)
        axes.legend(loc='best', fancybox=True)

    def plot_convergence(self, name='NN'):
        """
        Plots the training convergence of the neural network for MAE and MSE validation and training loss
        Parameters
        ----------
        name : str
            the name of the file to save the plot

        Returns
        -------
        None
        """

        epochs = np.arange(1, len(self.history.history['loss']) + 1, 1)
        self.history.history['epochs'] = epochs
        df = pd.DataFrame(self.history.history)

        if epochs[-1] < 2000:
            skip = int(epochs[-1] * 0.1)
        else:
            skip = 200

        fig, ax = plt.subplots(2, 1)
        ax[0].plot('epochs', 'mse', data=df.iloc[skip:], c='k', lw=0.75, label='Train')
        ax[0].plot('epochs', 'val_mse', data=df.iloc[skip:], c='b', lw=0.75, label='Validation')
        self.format_axes(ax[0], 'MSE')
        ax[0].set_xticklabels([])
        ax[0].set_xlabel('')
        ax[1].plot('epochs', 'mae', data=df.iloc[skip:], c='k', lw=1, label='Train')
        ax[1].plot('epochs', 'val_mae', data=df.iloc[skip:], c='b', lw=1, label='Validation')
        self.format_axes(ax[1], 'MAE')

        plt.suptitle('%s Train History' % name)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig('%s_Train_History.png' % name)
        plt.close()

    def measure_accuracy(self, x_test, y_test):
        """
        Evaluates the model on the testing inputs and returns metrics for R2, MAE and MSE
        Parameters
        ----------
        x_test : array
            an array of inputs to use for testing
        y_test : array
            an array of qoi to use for testing

        Returns
        -------
        loss : float
            loss function value for the test inputs
        mae : float
            mean-absolute-error for the test inputs
        mse : float
            mean-squared-error for the test inputs

        """
        # Check accuracy on test data
        loss, mae, mse = self.model.evaluate(x_test, y_test, verbose=0)
        print("Testing set Mean Abs Error: {:5.2f}".format(mae))
        print ("Testing set Mean Squared Error: {:5.2}".format(mse))

        return loss, mae, mse

    def predict(self, x):
        """
        Employs the neural network to predict the qoi value based on the inputs x
        Parameters
        ----------
        x : array
            an array of inputs on which to evaluate the model

        Returns
        -------
        y : array
            the predicted qoi value for the inputs

        """
        y = self.model.predict(x).flatten()
        return y


class Case:
    """
    A utility class for performing Cross-Validation and Repeats
    """

    def __init__(self, dataset=None,
                 architecture=None,
                 hidden_layers=None,
                 function='relu',
                 folds=10, repeats=3,
                 networkClass = NeuralNet):

        self.dataset = dataset
        self.ARCHITECTURE = architecture
        self.HL = hidden_layers
        self.FUNCTION = function
        self.FOLDS = folds
        self.REPEATS = repeats

        self.networkClass = networkClass

        self.LOSS = -1
        self.MAE = -1
        self.MSE = -1
        self.R2 = 0

        self.figs = os.path.join(os.getcwd(), 'figures')
        if not os.path.exists(self.figs):
            os.mkdir(self.figs)

        if self.dataset is None:
            raise ValueError('Please input a Dataset instance')
        if self.ARCHITECTURE is None:
            raise ValueError('Please input an architecture')

        # creating a dummy network
        network = self.networkClass(inputs=self.ARCHITECTURE, hl=self.HL, n_params=self.dataset.n_params)
        network.setup_model(self.FUNCTION)
        # print('The case model is defined as follows: ')
        # print(network.model.summary())

    def run(self):
        os.system('rm *.hist > /dev/null')

        for j in range(self.REPEATS):
            print ("======= On Repeat Iteration %.2d/%.2d =======" % (j + 1, self.REPEATS))
            self.dataset.gen_folds(self.FOLDS)
            self.networks = [None] * self.FOLDS
            with parallel_backend("loky"):
                _ = Parallel(n_jobs=multiprocessing.cpu_count(), prefer='threads')(
                    delayed(self.run_fold)(i) for i in range(self.FOLDS))

        self.LOSS = np.mean(np.genfromtxt('loss.hist'))
        self.MAE = np.mean(np.genfromtxt('mae.hist'))
        self.MSE = np.mean(np.genfromtxt('mse.hist'))
        self.R2 = np.mean(np.genfromtxt('r2.hist'))

        with parallel_backend("loky"):
            _ = Parallel(n_jobs=multiprocessing.cpu_count(), prefer='threads')(delayed(self.final)() for i in range(1))

    def final(self):
        print ("Training Final Network")
        network = self.networkClass(inputs=self.ARCHITECTURE, hl=self.HL, n_params=self.dataset.n_params)
        network.setup_model(self.FUNCTION)
        network.fit_model(self.dataset.x_normed, self.dataset.qoi_normed)
        network.save_model()
        network.plot_convergence(name='%s/FullData' % self.figs)

    def run_fold(self, i):

        print ("Training Fold %.2d/%.2d" % (i + 1, self.FOLDS))

        self.networks[i] = self.networkClass(inputs=self.ARCHITECTURE, hl=self.HL, n_params=self.dataset.n_params)
        self.networks[i].setup_model(self.FUNCTION)
        fold = self.dataset.folds[i]

        self.networks[i].fit_model(fold['train_x'], fold['train_qoi'])
        ret_qoi = np.array(self.dataset.ret_qoi(fold['test_qoi']))

        loss, mse, mae, r2, fig = self.measure_test_set(self.networks[i], fold['test_x'], ret_qoi)

        fig.savefig('%s/%s_r2.png' % (self.figs, i + 1))

        os.system('echo "%s" >> loss.hist' % loss)
        os.system('echo "%s" >> mae.hist' % mae)
        os.system('echo "%s" >> mse.hist' % mse)
        os.system('echo "%s" >> r2.hist' % r2)

        self.networks[i].plot_convergence(name='%s/%s' % (self.figs, i + 1))

    def measure_test_set(self, network, test_x, test_qoi):
        normed_y = network.predict(test_x)
        y = self.dataset.ret_qoi(normed_y)

        # this is to get the mse in the magnitude of the data
        mse = np.mean(np.square(test_qoi - y))
        mae = np.mean(np.absolute(test_qoi - y))
        loss = mse
        r2 = np.corrcoef(test_qoi, y)[0, 1]

        String = """NN Metrics:
MAE = %.4f
MSE = %.4f
$R^{2}$ = %.4f""" % (mae, mse, r2)

        fig, ax = plt.subplots()
        ax.plot(test_qoi, y, 'o', mfc='none')
        ax.set_xlabel('Real value')
        ax.set_ylabel('Prediction')
        lims = [min(min(y), min(test_qoi)), max(max(y), max(test_qoi))]
        ax.plot(lims, lims, '--', c='b', lw=0.75)
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.annotate(String, xy=(0.05, 0.5), xycoords='axes fraction')
        plt.close()

        return loss, mse, mae, r2, fig


class GradientComputation:
    """
    A utility class for performing finite-difference gradient computations using neural networks efficiently

    Attributes
    ----------

    dataset : Dataset
        a Dataset object which must have been used as inputs to the neural network
    network : NeuralNet
        a NeuralNet object which must be already trained and ready to use
    step : float
        the finite-difference step size

    Methods
    ----------
    central_diff(x)
        computes the central differences gradient at x

    """
    def __init__(self, dataset, network, step=0.1):
        self.dataset = dataset
        self.network = network
        self.step = step

    def central_diff(self, x):
        """
        Computes the central differences gradient at x
        Parameters
        ----------
        x : array
            an array of inputs on which to compute the gradient

        Returns
        -------
        grads : array
            an array containing the estimated gradient value at x
        """

        x = np.array(x)

        matrix = np.diag(np.ones(self.dataset.n_params) * self.step)

        if len(x.shape)==1:
            evals = np.vstack((x + matrix, x - matrix))
            evals = self.dataset.norm_x(evals, verbose=False)
            y = self.dataset.ret_qoi(self.network.predict(evals))

            y1 = y[:self.dataset.n_params]
            y2 = y[self.dataset.n_params:]
            grads = (y1 - y2) / (2 * self.step)

        else:

            evals = np.array([]).reshape(0, self.dataset.n_params)
            for point in x:
                evals = np.vstack((evals, point + matrix, point - matrix))

            evals = pd.DataFrame(evals, columns=self.dataset.x.columns)
            evals = self.dataset.norm_x(evals, verbose=False)
            y = self.dataset.ret_qoi(self.network.predict(evals))
            grads = np.array([]).reshape(0, self.dataset.n_params)
            for i in range(x.shape[0]):
                sector = y[self.dataset.n_params * 2 * i:self.dataset.n_params * 2 * (i + 1)]
                y1 = sector[:self.dataset.n_params]
                y2 = sector[self.dataset.n_params:]
                result = (y1 - y2) / (2 * self.step)

                grads = np.vstack((grads, result))

        return grads


class ClientFunction:
    """
    A utility class to perform evaluations using neural networks and active subspaces.

    Attributes
    ----------
    dataset : Dataset
        A Dataset object which must have been written by the ADS process and used to train a NeuralNet
    network_name : str or None
        The path to a directory which has been saved with NeuralNet.save
    network : NeuralNet or None
        A NeuralNet object which has been trained
    ads : ADS
        An ADS object

    Methods
    ----------
    feval(x)
        A utility function to evaluate the network on a set of inputs x
    grad_eval(x)
        A utility function to evaluate the gradient via finite-differences at point x
    grad_eval_forMethod(x)
        A utility function to evaluate the gradient for the OptimisationMethod. Differs from
        grad_eval in that x here is a higher-dimensional input than the ones used to train the network.
        x will first be forward_mapped to the ADS and then employed to evaluate the gradient

    """
    def __init__(self, dataset=None, network_name=None, ads=None, network=None):
        self.dataset = dataset
        self.network_name = network_name
        self.network = network
        self.ads = ads

        if self.dataset is None:
            raise ValueError('Please introduce an input Dataset instance')
        if self.network_name is None:
            if self.network is None:
                raise ValueError('Please introduce an input neural network path via network_name, or a NeuralNet object via network')
        else:
            self.network = NeuralNet.load_model(self.network_name)

    def feval(self, x):
        """
        Evaluates the neural network on point x. It first normalises x according to self.dataset.normalisation_x
        The output is then returned based on self.dataset.normalisation_qoi
        Parameters
        ----------
        x : a set of inputs on which to evaluate the neural network

        Returns
        -------
        qoi : the neural network prediction at this point
        """
        xpred = self.dataset.norm_x(pd.DataFrame(vectorize(x).T, columns=self.dataset.x.columns), verbose=False)
        qoi = self.dataset.ret_qoi(self.network.predict(xpred))
        return qoi

    def grad_eval(self, x):
        """
        Performs finite-differences to estimate the gradient at point x
        Parameters
        ----------
        x : a set of inputs

        Returns
        -------
        Central-Difference gradient estimation
        """
        gcomp = GradientComputation(dataset=self.dataset, network=self.network, step=0.1)
        return gcomp.central_diff(x)

    def grad_eval_forMethod(self, x, step=0.1):
        """
        Performs the gradient evaluation to be used in the OptimisationMethod.
        x is of higher dimensions than the inputs used to train the network.
        A matrix of perturbations is first created according to the step size
        Each entry in the matrix is then forward_mapped to the ADS based on self.ads.forward_map
        Each entry in the low_dimensional matrix is then normalised according to self.dataset.normalisation_x
        The network is then used to predict the function value at each of the points in the matrix
        self.dataset.ret_qoi is finally used to return the predictions to the un-normalised values
        Finally, the gradient is calculated using central-differences
        Parameters
        ----------
        x : array
            the inputs value at which to evaluate the gradients
        step : float
            the step size to be used for finite-differences

        Returns
        -------
        The gradient value at x
        """

        if self.ads is None:
            raise ValueError('Please input an ADS object')

        n_params = np.shape(x)[0]
        matrix = np.diag(np.ones(n_params) * step)
        evals_hd = np.vstack((x + matrix, x - matrix))

        # evals_hd contains the evaluations needed for the gradient of x.
        # To use the current network, we need to map them to the lower dimensional space
        evals = self.ads.forward_map(evals_hd)

        # Now normalise it to the dataset, since the network was built on that
        evals = pd.DataFrame(evals, columns=self.dataset.x.columns)
        evals = self.dataset.norm_x(evals, verbose=False)

        # Use the network to predict the evaluations
        y = self.dataset.ret_qoi(self.network.predict(evals))

        # Now just compute the central differences
        y1 = y[:n_params]
        y2 = y[n_params:]
        grads = (y1 - y2) / (2 * step)

        return grads
