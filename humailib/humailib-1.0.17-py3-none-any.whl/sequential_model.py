import numpy as np
import pandas as pd
import tensorflow as tf
from matplotlib import pyplot as plt
import pickle
import os

from humailib.hasher import XORHasher

from tensorflow.contrib import learn
from sklearn.metrics import mean_squared_error

from humailib.lstm import lstm_model
#from libraries.data_processing import generate_data
from humailib.cloud_tools import loadDatasetToPandas
from humailib.sequential_model_helper import GetWeekdaySequencesIncNonOpens

class HumaiSequentialTimingModel:

    # ==========
    #   MODEL
    # ==========

    # Parameters
    learning_rate = 0.005
    training_steps = -1
    batch_size = 128
    display_step = batch_size*2
    epochs = 5

    # Network Parameters
    seq_min_len = 2
    seq_max_len = 10 # Sequence max length
    n_hidden = 256 # hidden layer num of features
    n_classes = 8 # days in the week [0,6] and 'non-open' (day 7)

    dropout_keepprob = 0.5
    clip_gradients = False

    def __init__(self, learning_rate=learning_rate, dropout_keepprob=dropout_keepprob):

        self.session = None
        self.learning_rate = learning_rate
        self.dropout_keepprob = dropout_keepprob

    def setNetworkParams(self, seq_min_len=2, seq_max_len=1, n_hidden=256, n_classes=8):

        self.seq_min_len = seq_min_len
        self.seq_max_len = seq_max_len
        self.n_hidden = n_hidden
        self.n_classes = n_classes

    def learn(self, histories, labels, seqlens, val_size=0.1, test_size=0.1, learning_rate=0.005, batch_size=128, epochs=5, clip_gradients=True, save_intermediate=True, verbose=True):

        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.clip_gradients = clip_gradients
        self.epochs = epochs

        train_x, val_x, test_x = self.__splitData(histories, val_size, test_size)
        train_y, val_y, test_y = self.__splitData(labels, val_size, test_size)
        train_sl, val_sl, test_sl = self.__splitData(seqlens, val_size, test_size)

        X = dict(train=train_x, val=val_x, test=test_x)
        y = dict(train=train_y, val=val_y, test=test_y)
        sl = dict(train=train_sl, val=val_sl, test=test_sl)
            
        del histories
        del labels
        del seqlens
        del train_x, val_x, test_x
        del train_y, val_y, test_y
        del train_sl, val_sl, test_sl

        X['train'] = np.reshape(X['train'], (len(X['train']), self.seq_max_len, 1))
        X['val'] = np.reshape(X['val'], (len(X['val']), self.seq_max_len, 1))
        X['test'] = np.reshape(X['test'], (len(X['test']), self.seq_max_len, 1))

        pickle.dump( X, open( "seq_model_learn_data_X.p", "wb" ) )
        pickle.dump( y, open( "seq_model_learn_data_y.p", "wb" ) )
        pickle.dump( sl, open( "seq_model_learn_data_sl.p", "wb") )

        self.training_steps = int( np.floor(len(X['train'])*self.epochs / self.batch_size) )
        if verbose:
            print("training samples n = {0}, validation n = {1}, test n = {2}".format(len(X['train']), len(X['val']), len(X['test'])))
            print("Number of epochs: {0}, batch size: {1}, size of training data: {2} samples".format(self.epochs, self.batch_size, len(X['train'])))
            print("Number of steps required: {0}".format(self.training_steps))

        self.__setupModel()

        # Initialize the variables (i.e. assign their default value)
        init = tf.global_variables_initializer()

        # Start training
        sess = tf.Session()
        if True:

            # Run the initializer
            sess.run(init)

            feeder = dataFeeder(X['train'], y['train'], sl['train'])

            for step in range(1, self.training_steps+1):

                batch_x, batch_y, batch_seqlen = feeder.getNext(self.batch_size)
                #print("n=({0}, {1}, {2})".format(len(batch_x), len(batch_y), len(batch_seqlen)))
                
                # Run optimization op (backprop)
                sess.run(self.optimizer, feed_dict={self.gix: batch_x, 
                                            self.giy: batch_y,
                                            self.seqlen: batch_seqlen, 
                                            self.keep_prob:self.dropout_keepprob})

                if step % self.display_step == 0 or step == 1:
                    # Calculate batch accuracy & loss
                    acc, loss = sess.run([self.accuracy, self.cost], feed_dict={self.gix: batch_x,
                                                        self.giy: batch_y,
                                                        self.seqlen: batch_seqlen, 
                                                        self.keep_prob:1.0})

                    if verbose:
                        print("Train: Step " + str(step) + ", Minibatch Loss= " + \
                            "{:.6f}".format(loss) + ", Training Accuracy= " + \
                            "{:.5f}".format(acc))

                    acc, loss = sess.run([self.accuracy, self.cost], feed_dict={self.gix: X['val'], 
                                                        self.giy: y['val'],
                                                        self.seqlen: sl['val'], 
                                                        self.keep_prob:1.0})

                    if verbose:
                        print("  Validation Loss= " + \
                            "{:.6f}".format(loss) + ", Validation Accuracy= " + \
                            "{:.5f}".format(acc))

            if verbose:
                print("Optimization Finished!")

            # Calculate accuracy
            test_data = X['test']
            test_label = y['test']
            test_seqlen = sl['test']

            accuracy = sess.run(self.accuracy, feed_dict={self.gix: test_data, self.giy: test_label,
                                                self.seqlen: test_seqlen, self.keep_prob:1.0})
                                                
            if verbose:
                print("Testing Accuracy: {}".format(accuracy))

            conf_matrix = sess.run([self.confusion_matrix], feed_dict={self.gix: test_data, self.giy: test_label, self.seqlen: test_seqlen, self.keep_prob:1.0})

            if verbose:
                print("Confusion matrix on test set:\n{0}".format(conf_matrix))

            self.session = sess

        return True, conf_matrix

    def predict(self, sequences, seqlens):

        if self.session is None:
            return False

        sequences = np.reshape(sequences, (len(sequences), self.seq_max_len, 1))
        predictions = self.session.run(self.pred, feed_dict={self.gix: sequences,
                                                self.seqlen: seqlens, 
                                                self.keep_prob:1.0})

        return predictions

    def saveModel(self, modelname, hyperparamname):

        if self.session is None:
            return False

        # Add ops to save and restore all the variables.
        self.saver = tf.train.Saver(save_relative_paths=True)

        # Save graph, variables, and hyper-parameters.

        save_path = self.saver.save(self.session, modelname, write_meta_graph=True)
        print("Model saved in path: '{0}'".format(save_path))
            
        pickle.dump( [self.learning_rate, self.training_steps,
            self.batch_size, self.display_step,
            self.seq_min_len, self.seq_max_len,
            self.n_hidden, self.n_classes,
            self.dropout_keepprob,
            self.clip_gradients], open( hyperparamname, "wb" ) )
        print("Hyper parameters saved in: '{0}'".format(hyperparamname))

        return True

    def loadModel(self, modelname, hyperparamname):

        if self.session is not None:
            self.session.close()

        #self.saver = tr.train.Saver()

        self.session = tf.Session()
        self.loaded_model = tf.train.import_meta_graph(modelname + '.meta')
        self.loaded_model.restore(self.session, tf.train.latest_checkpoint(os.path.dirname(modelname)))

        self.learning_rate, self.training_steps,
        self.batch_size, self.display_step,
        self.seq_min_len, self.seq_max_len,
        self.n_hidden, self.n_classes,
        self.dropout_keepprob,
        self.clip_gradients = pickle.load(open(hyperparamname, "rb"))

        # Restore tensors
        graph = tf.get_default_graph()
   
        self.gix = graph.get_tensor_by_name("gix:0")
        self.giy = graph.get_tensor_by_name("giy:0")
        self.seqlen = graph.get_tensor_by_name("seqlen:0")
        self.keep_prob = graph.get_tensor_by_name("keep_prob:0")
        self.pred = graph.get_tensor_by_name("pred:0")

        return True

    def __splitData(self, data, val_size=0.1, test_size=0.1):
        """
        splits data to training, validation and testing parts
        """
        ntest = int(round(len(data) * (1 - test_size)))
        nval = int(round(len(data[:ntest]) * (1 - val_size)))

        #df_train, df_val, df_test = np.array(data[:nval], dtype=np.float32), np.array(data[nval:ntest], dtype=np.float32), np.array(data[ntest:], dtype=np.float32)
        df_train, df_val, df_test = np.array(data[:nval]), np.array(data[nval:ntest]), np.array(data[ntest:])

        return df_train, df_val, df_test

    def __setupModel(self):

        # ==========
        #   MODEL
        # ==========

        # tf Graph input
        self.gix = tf.placeholder("float", [None, self.seq_max_len, 1], name="gix")
        self.giy = tf.placeholder("float", [None, self.n_classes], name="giy")
        # A placeholder for indicating each sequence length
        self.seqlen = tf.placeholder(tf.int32, [None], name="seqlen")

        self.keep_prob = tf.placeholder("float", shape=None, name="keep_prob")

        # Define weights
        self.weights = {
            'out': tf.Variable(tf.random_normal([self.n_hidden, self.n_classes]), name="weights")
        }
        self.biases = {
            'out': tf.Variable(tf.random_normal([self.n_classes]), name="biases")
        }

        self.pred = self.__dynamicRNN(self.gix, self.seqlen, self.keep_prob, self.weights, self.biases)
        # Give it a name, so we can use it for model restoring
        self.pred = tf.identity(self.pred, name="pred")

        # Define loss and optimizer
        self.cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits_v2(logits=self.pred, labels=self.giy), name="cost")
        if self.clip_gradients == True:
            org_opt = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate)
            self.opt = tf.contrib.estimator.clip_gradients_by_norm(org_opt, clip_norm=1.0)
        else:
            self.opt = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate)
        self.optimizer = self.opt.minimize(self.cost, name="optimizer")

        # Evaluate model
        #correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(giy,1), name="correct_pred")
        #accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32), name="accuracy")
        self.accuracy = tf.contrib.metrics.accuracy(tf.argmax(self.giy,1), tf.argmax(self.pred,1), name="accuracy")
        self.f1_score = tf.contrib.metrics.f1_score(tf.argmax(self.giy,1), tf.argmax(self.pred,1), name="f1_score")
        self.confusion_matrix = tf.confusion_matrix(tf.argmax(self.giy,1), tf.argmax(self.pred,1), name="confusion_matrix")
    

    def __dynamicRNN(self, x, seqlen, keep_prob, weights, biases):

        # Prepare data shape to match `rnn` function requirements
        # Current data input shape: (batch_size, n_steps, n_input)
        # Required shape: 'n_steps' tensors list of shape (batch_size, n_input)
        
        # Unstack to get a list of 'n_steps' tensors of shape (batch_size, n_input)
        x = tf.unstack(x, self.seq_max_len, 1)

        # Define a lstm cell with tensorflow
        lstm_cell = tf.contrib.rnn.BasicLSTMCell(self.n_hidden)

        #cell = tf.nn.rnn_cell.LSTMCell(state_size, state_is_tuple=True)
        #cell = tf.nn.rnn_cell.DropoutWrapper(cell, output_keep_prob=0.5)
        #cell = tf.nn.rnn_cell.MultiRNNCell([cell] * num_layers, state_is_tuple=True)
        lstm_cell = tf.nn.rnn_cell.DropoutWrapper(lstm_cell, output_keep_prob=keep_prob)

        # Get lstm cell output, providing 'sequence_length' will perform dynamic
        # calculation.
        outputs, _ = tf.contrib.rnn.static_rnn(lstm_cell, x, dtype=tf.float32,
                                    sequence_length=seqlen)

        # When performing dynamic calculation, we must retrieve the last
        # dynamically computed output, i.e., if a sequence length is 10, we need
        # to retrieve the 10th output.
        # However TensorFlow doesn't support advanced indexing yet, so we build
        # a custom op that for each sample in batch size, get its length and
        # get the corresponding relevant output.

        # 'outputs' is a list of output at every timestep, we pack them in a Tensor
        # and change back dimension to [batch_size, n_step, n_input]
        outputs = tf.stack(outputs)
        outputs = tf.transpose(outputs, [1, 0, 2])

        # Hack to build the indexing and retrieve the right output.
        batch_size = tf.shape(outputs)[0]
        # Start indices for each sample
        index = tf.range(0, batch_size) * self.seq_max_len + (seqlen - 1)
        # Indexing
        outputs = tf.gather(tf.reshape(outputs, [-1, self.n_hidden]), index)

        # Linear activation, using outputs computed above
        ppp = 0.99*(tf.matmul(outputs, weights['out']) + biases['out']) + 0.001
        #print(ppp)
        
        return ppp

class dataFeeder:

    def __init__(self, X, y, seqlen):
        self.X = X
        self.y = y
        self.seqlen = seqlen

        self.index = 0

    def getNext(self, batch_size = 128):

        ofs = self.index

        if ofs + batch_size > len(self.X):
            ofs = 0

        X = self.X[ofs:ofs+batch_size]
        y = self.y[ofs:ofs+batch_size]
        seqlen = self.seqlen[ofs:ofs+batch_size]

        self.index = batch_size + self.index

        return X, y, seqlen


    