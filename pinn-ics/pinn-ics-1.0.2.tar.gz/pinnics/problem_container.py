from .var_container import VarContainer
import tensorflow as tf


class Container:
    def __init__(self, variables, losses, 
            weights=[], epsilon=1e-2):
        self._var_container = VarContainer(variables)
        self._losses = losses
        self._weights = weights
        self._epsilon = epsilon
        self._loss_values = [0] * len(losses)
        self._first_run()

    @property
    def var_container(self):
        return self._var_container

    def _first_run(self):
        for loss_func in self._losses:
            loss_func(self._var_container)

    def cal_grads(self, model):
        for grad in self._var_container.iterate_grads():
            grad.cal_grad(model)

    def _cal_max(self, loss_index):
        loss_func = self._losses[loss_index]
        loss_val = tf.square(loss_func(self._var_container))
        index = tf.argmax(loss_val)

        mean_loss = tf.reduce_mean(loss_val) 

        if mean_loss < self._epsilon and mean_loss != self._loss_values[loss_index]:
            self._loss_values[loss_index] = mean_loss
            return index
        else:
            return None

    def _check_none(self, array):
        for data in array:
            if data != None:
                return False 

        return True

    def cal_update_index(self):
        indexes = []
        for index in range(len(self._losses)):
            indexes.append(self._cal_max(index))
        self._var_container.update(indexes)
        return self._check_none(indexes)

    def cal_loss(self):
        result = 0
        for index, loss_func in enumerate(self._losses):
            result += tf.reduce_mean(tf.square(loss_func(self._var_container)))
            self._loss_values[index] = result
        return result

    def reset_loss_val(self):
        self._loss_values = [0] * len(self._losses)
