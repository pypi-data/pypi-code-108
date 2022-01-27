import random
import numpy as np


class LeaveNout(object):
    def __init__(self, n, n_repeats):
        r"""[Leave-N-Out](https://link.springer.com/referenceworkentry/10.1007%2F978-0-387-30164-8_469) Cross-Validation

        Args:
            n (int): \( n \) to leave out.
            n_repeats (int): Repetitions.
        """

        self.n = n
        self.n_repeats = n_repeats

    def split(self, X):
        n_samples = np.shape(X)[0]
        n = self.n
        n_splits = int(n_samples/n)
        result = []
        for i in range(self.n_repeats):
            indices = random.sample(range(n_samples), n_samples)
            for j in range(n_splits):
                testSet = indices[j*n:n*(j+1)]
                trainingSet = [k for k in indices if k not in testSet]
                result.append((trainingSet, testSet))
            n_remaining = n_samples % n
            if n_remaining != 0:
                testSet = indices[-n_remaining:]
                trainingSet = [k for k in indices if k not in testSet]
                result.append((trainingSet, testSet))
        return result
