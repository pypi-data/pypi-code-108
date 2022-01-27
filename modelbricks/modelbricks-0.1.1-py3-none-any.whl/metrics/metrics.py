"""Create Custom Metrics."""
import tensorflow as tf

class F1Score(tf.keras.metrics.Metric):
    """Creates a F1 Score Metric."""
    def __init__(self, name='f1_score', **kwargs):
        """Creates a F1 Score Metric."""
        super().__init__(name=name, **kwargs)
        self.f1score = self.add_weight(name='f1', initializer='zeros')
        self.precision_fn = tf.keras.metrics.Precision(thresholds=0.5)
        self.recall_fn = tf.keras.metrics.Recall(thresholds=0.5)

    def update_state(self, y_true, y_pred, sample_weight=None):
        """Caculate F1Score from Precison and Recall, and Update the state.
        """
        if sample_weight is not None:
            precision = self.precision_fn(y_true, y_pred, sample_weight)
            recall = self.recall_fn(y_true, y_pred, sample_weight)
        else:
            precision = self.precision_fn(y_true, y_pred)
            recall = self.recall_fn(y_true, y_pred)
        # since f1 is a variable, we use assign
        self.f1score.assign(2 * ((precision * recall) / (precision + recall + 1e-6)))

    def result(self):
        """Get this metrics result
        """
        return self.f1score

    def reset_state(self):
        """Reset this metrics state
        """
        # we also need to reset the state of the precision and recall objects
        self.precision_fn.reset_state()
        self.recall_fn.reset_state()
        self.f1score.assign(0)
