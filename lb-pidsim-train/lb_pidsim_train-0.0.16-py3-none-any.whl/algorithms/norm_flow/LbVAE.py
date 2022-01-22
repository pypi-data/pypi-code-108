import numpy as np
import tensorflow as tf


class LbVAE(tf.keras.models.Model):
    """LHCb Variational Autoencoder
    LbVAE is a hybrid model between a variational autoencoder and a normalizing flow.
    It is composed of three subsequent neural networks:
     * an encoder
     * a normalizing flow
     * a decoder
    The encoder produces output according to some non-constrained probability distribution, but synthesizing
    the information contained in the original dataset in a smaller number of variables.
    The normalizing flow provides and invertible transform of the encoded variables towards a multivariate normal
    distribution. Being invertible, such a transform does not remove any piece of information distilled by the encoder.
    The decoder takes the gaussian output produced by the normalizing flow as an input and produces and output that
    will be matched to the input of the encoder.
    Encoder and decoder are trained with a regression loss function to decoded features as similar as possible
    to the input features.
    The normalizing flow is trained as a maximum likelihood fit to the encoder output, with a pdf described by
    the transform of a Gaussian-distributed random variable by the invertible neural network.
    LbVAE is a Conditional VAE in the sense that it supports input conditions X together with the feature Y.
    The produced model is a probability density function for the variables Y conditioned to X: p(Y|X).
    The constructor expects the three neural network models to be passed as an input.
    Note the following constraints on the input and output shape of each model.
     * encoder:  Input_Shape -> `[None, n_features]`
     * normflow: `[None, n_gaussian + n_features]` -> `[None, n_features]`
     * decoder: `[None, n_gaussian + n_features]` -> Input_Shape
     where `n_features` is the arbitrary number of features in the latent space. It should be sufficiently large to
     describe all the variability of the input sample, and sufficiently small to make the inversion of the Jacobian
     matrix (of shape [n_features, n_features]) affordable.
    """
    def __init__(self, encoder, normflow, decoder):
        tf.keras.models.Model.__init__(self)
        self.encoder = encoder
        self.decoder = decoder
        self.normflow = normflow

    @staticmethod
    def _unpack_data(data):
        "Return unpacked data as a tuple (conditions, features, weights). Only weights can be None."
        if isinstance(data, tuple) and len(data) == 2:
            X, Y = data
            w = None
        elif isinstance(data, tuple) and len(data) == 3:
            X, Y, w = data
        else:
            X = tf.zeros((tf.shape(data)[0], 0))
            Y = data
            w = None

        return X, Y, w

    @staticmethod
    def _get_shapes(x, y):
        "Returns a tuple (n_entries, n_conditions, n_features) given condition and feature tensors"
        shape_x = tf.shape(x)
        shape_y = tf.shape(y)
        return shape_x[0], shape_x[1], shape_y[1]

    def _model(self, X, Y):
        """Describe the model for X conditions and Y features and returns a tuple (gaussianized, logDetJ, decoded).
        * gaussianized is the tensor of variables in the latent space
        * logDetJ is the log of the determinant of the Jacobian of the transform from the encoded to gaussianized vars
        * decoded is the tensor of variables undergoing the whole process that should match the features Y.
        """
        encoded = self.encoder(Y)

        with tf.GradientTape(watch_accessed_variables=False) as g_jacobi:
            g_jacobi.watch(encoded)
            Xencoded = tf.concat((X, encoded), axis=1)
            gaussianized = self.normflow(Xencoded)

        J = g_jacobi.batch_jacobian(gaussianized, encoded, experimental_use_pfor=False)
        logDetJ = tf.math.log(tf.abs(tf.linalg.det(J)))

        Xgaussianized = tf.concat((X, gaussianized), axis=1)
        decoded = self.decoder(Xgaussianized)

        return gaussianized, logDetJ, decoded

    @staticmethod
    def _get_loss_nf(gaussianized, logDetJ):
        "Negative log likelihood"
        return 0.5 * tf.reduce_sum(tf.square(gaussianized), axis=1) - logDetJ

    def train_step(self, data, *args, **kwargs):
        "Train step for the keras APIs"
        X, Y, w = self._unpack_data(data)
        n_entries, n_x, n_y = self._get_shapes(X, Y)

        with tf.GradientTape() as g_ae:
            with tf.GradientTape() as g_nf:
                gaussianized, logDetJ, decoded = self._model(X, Y)

                loss_ae = self.compiled_loss(Y, decoded)
                loss_nf = tf.reduce_mean(self._get_loss_nf(gaussianized, logDetJ))

        vars_e = self.encoder.trainable_weights
        vars_d = self.decoder.trainable_weights
        vars_nf = self.normflow.trainable_weights

        grads_ae = g_ae.gradient(loss_ae, vars_e + vars_d)
        grads_nf = g_nf.gradient(loss_nf, vars_nf)

        self.optimizer.apply_gradients(zip(grads_ae, vars_e + vars_d))
        self.optimizer.apply_gradients(zip(grads_nf, vars_nf))

        return dict(loss=loss_ae, loss_nf=loss_nf)


    def test_step(self, data, *args, **kwargs):
        "Test step for the keras APIs"
        X, Y, w = self._unpack_data(data)
        n_entries, n_x, n_y = self._get_shapes(X, Y)

        gaussianized, logDetJ, decoded = self._model(X, Y)
        loss_ae = self.compiled_loss(Y, decoded)
        loss_nf = tf.reduce_mean(self._get_loss_nf(gaussianized, logDetJ))

        return dict(loss=loss_ae, loss_nf=loss_nf)