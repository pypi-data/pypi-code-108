# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without
#  the express permission of Comet ML Inc.
# *******************************************************

import six
import tensorflow as tf
from tensorflow.python.training.basic_session_run_hooks import _as_graph_element


class TensorflowPredictorStopHook(tf.train.SessionRunHook):
    def __init__(self, predictor):
        self.predictor = predictor
        self.monitor = predictor.loss_name
        self._timer = tf.train.SecondOrStepTimer(every_steps=self.predictor.interval)

        self._global_step_tensor = None

    def begin(self):
        if isinstance(self.monitor, six.string_types):
            self.monitor = _as_graph_element(self.monitor)
        else:
            self.monitor = _as_graph_element(self.monitor.name)

        self._global_step_tensor = tf.train.get_global_step()

    def before_run(self, run_context):
        del run_context
        return tf.train.SessionRunArgs([self._global_step_tensor, self.monitor])

    def after_run(self, run_context, run_values):
        global_step, loss = run_values.results

        if self._timer.should_trigger_for_step(global_step):
            self._timer.update_last_triggered_step(global_step)
            self.predictor.report_loss(loss)

            if self.predictor.stop_early(epoch=global_step):
                tf.logging.info(
                    "Requesting early stopping at global step %d", global_step
                )
                run_context.request_stop()
