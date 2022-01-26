# from tensorflow.compat.v1.keras import backend as K
# from tensorflow.compat.v1.keras.legacy import interfaces

# from tensorflow.compat.v1.keras.optimizers import Optimizer


# TODO: migrate to tensorflow 2.0, it does not have legacy
# class AdamWeightDecay(Optimizer):
#     """Adam optimizer with weight decay.

#     Default parameters follow those provided in the original paper.

#     # Arguments
#         lr: float >= 0. Learning rate. Defaults to 1.0. Here it is different than in usual Adam implementations.
#             It is used to allow step size scheduling while preserving decoupling of alpha and weight decay parameters.
#         alpha: float >=0. In other Adam implementations it is called learning rate.
#             Corresponds to 'alpha' from the original paper.
#         beta_1: float, 0 < beta < 1. Generally close to 1.
#         beta_2: float, 0 < beta < 1. Generally close to 1.
#         epsilon: float >= 0. Fuzz factor. If `None`, defaults to `K.epsilon()`.
#         decay: float >= 0. Learning rate decay over each update.
#         weight_decay: float >= 0. Weight decay, equivalent to L2 penalty. Defaults to 0.001.
#         batch_size: integer >= 1. Batch size used during training.
#         samples_per_epoch: integer >= 1. Number of training examples per epoch.
#         epochs: integer >= 1. Number of epochs for training.

#     # References
#         - [Adam - A Method for Stochastic Optimization](http://arxiv.org/abs/1412.6980v8)
#         - [Fixing Weight Decay Regularization in Adam](https://arxiv.org/abs/1711.05101)
#     """

#     def __init__(self, lr=1.0, alpha=0.001, beta_1=0.9, beta_2=0.999,
#                  epsilon=None, decay=0., weight_decay=0.001,
#                  batch_size=1, samples_per_epoch=1,
#                  epochs=1, **kwargs):
#         super().__init__(**kwargs)
#         with K.name_scope(self.__class__.__name__):
#             self.iterations = K.variable(0, dtype='int64', name='iterations')
#             self.learning_rate = K.variable(lr, name='lr')
#             self.alpha = K.variable(alpha, name='alpha')
#             self.beta_1 = K.variable(beta_1, name='beta_1')
#             self.beta_2 = K.variable(beta_2, name='beta_2')
#             self.decay = K.variable(decay, name='decay')
#             self.weight_decay = K.variable(weight_decay, name='weight_decay')
#             self.batch_size = K.variable(batch_size, name='batch_size')
#             self.samples_per_epoch = K.variable(samples_per_epoch, name='samples_per_epoch')
#             self.epochs = K.variable(epochs, name='epochs')
#         if epsilon is None:
#             epsilon = K.epsilon()
#         self.epsilon = epsilon
#         self.initial_decay = decay

#     @interfaces.legacy_get_updates_support
#     def get_updates(self, loss, params):
#         grads = self.get_gradients(loss, params)
#         self.updates = [K.update_add(self.iterations, 1)]

#         lr = self.lr
#         if self.initial_decay > 0:
#             lr = lr * (1. / (1. + self.decay * K.cast(self.iterations,
#                                                       K.dtype(self.decay))))

#         # Scaling corresponding to lines 9-10 of the original AdamW paper (page 2, Algorithm 2)
#         t = K.cast(self.iterations, K.floatx()) + 1
#         hat_t = self.alpha * (K.sqrt(1. - K.pow(self.beta_2, t)) /
#                               (1. - K.pow(self.beta_1, t)))

#         ms = [K.zeros(K.int_shape(p), dtype=K.dtype(p)) for p in params]
#         vs = [K.zeros(K.int_shape(p), dtype=K.dtype(p)) for p in params]
#         self.weights = [self.iterations] + ms + vs

#         for p, g, m, v in zip(params, grads, ms, vs):
#             m_t = (self.beta_1 * m) + (1. - self.beta_1) * g
#             v_t = (self.beta_2 * v) + (1. - self.beta_2) * K.square(g)
#             p_t = p - lr * (hat_t * m_t / (K.sqrt(v_t) + self.epsilon) + self.weight_decay * p)

#             self.updates.append(K.update(m, m_t))
#             self.updates.append(K.update(v, v_t))
#             new_p = p_t

#             # Apply constraints.
#             if getattr(p, 'constraint', None) is not None:
#                 new_p = p.constraint(new_p)

#             self.updates.append(K.update(p, new_p))
#         return self.updates

#     def get_config(self):
#         config = {'lr': float(K.get_value(self.lr)),
#                   'alpha': float(K.get_value(self.alpha)),
#                   'beta_1': float(K.get_value(self.beta_1)),
#                   'beta_2': float(K.get_value(self.beta_2)),
#                   'decay': float(K.get_value(self.decay)),
#                   'epsilon': self.epsilon,
#                   'weight_decay': self.weight_decay,
#                   'batch_size': self.batch_size,
#                   'samples_per_epoch': self.samples_per_epoch,
#                   'epochs': self.epochs}
#         base_config = super(AdamWeightDecay, self).get_config()
#         return dict(list(base_config.items()) + list(config.items()))
