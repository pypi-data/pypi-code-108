import numpy as np


class Population:

    def __init__(self, number, n_hip):
        self.number = number
        self.n_hip = n_hip
        self.h = list(range(n_hip + 1))
        self.h[0] = ['nr:', list(range(1, number + 1))]
        self.stored = np.zeros((0, n_hip + 2))
        self.initialized = np.zeros((self.number, self.n_hip + 2))
        self.it = 0
        self.cross_position = 0

    def define_feature(self, place, name, le):
        # print(self.f)
        self.h[place] = [name, le]
        # print(self.f)

    def initialize(self):
        """Initialization (by randomization) of initial values"""
        self.initialized = np.zeros((self.number, self.n_hip + 2))
        self.initialized[:, 0] = range(1, self.number + 1)
        for i in range(1, self.n_hip + 1):
            self.initialized[:, i] = np.random.randint(0, len(self.h[i][1]), self.number)
        print(self.initialized)
        self.it = 0

    def read(self, hiper):
        place = self.initialized[self.it, hiper]
        out = self.h[hiper][1][round(place)]
        return out

    def is_finished(self):
        return self.it < self.number

    def nextind(self):
        self.it += 1

    def indbeg(self):
        self.it = 0

    def read_metric(self, value):
        """Rewrite the value of the metric into the individual"""
        self.initialized[self.it, self.n_hip + 1] = value

    def store(self):  # Storage of the results of previous evaluations
        self.stored = np.append(self.stored, self.initialized, axis=0)

    def save(self):
        """Saving the data of current individuals in a file named "DataCurrent.csv"
        and of past individuals in "Datastored.csv"."""
        np.savetxt('DataStored.csv', self.stored, type=np.ndarray)
        np.savetxt('DataCurrent.csv', self.initialized, type=np.ndarray)

    def load(self, stored_datafile, current_datafiled):
        self.stored = np.loadtxt(stored_datafile)
        self.initialized = np.loadtxt(current_datafiled)

    def sorting(self):
        self.initialized = self.initialized[self.initialized[:, -1].argsort()]

    def selection(self):
        self.initialized[:-2, :] = self.initialized[1:-1, :]
        self.initialized[-2, :] = self.initialized[-1, :]

    def crossing(self):
        self.cross_position = np.random.randint(2, 1 + self.n_hip)
        self.initialized[:2, self.cross_position:] = self.initialized[1::-1, self.cross_position:]

        self.cross_position = np.random.randint(2, 1 + self.n_hip)
        self.initialized[2:4, self.cross_position:] = self.initialized[3:1:-1, self.cross_position:]

    def mutation(self, m_rate):
        self.initialized[:, 0] = range(1, self.number + 1)
        self.initialized[:, -1] = [0]
        n_mutations = int(np.ceil(m_rate * self.n_hip * self.number))  # Policzenie ilości dokonywanych mutacji
        for i in range(n_mutations):
            x = np.random.randint(1, self.n_hip + 1)
            y = np.random.randint(self.number)
            # print(x +str(" ")+y)
            self.initialized[y, x] = np.random.randint(0, len(self.h[x][1]))

    def check(self):
        for y in range(len(self.stored)):
            for yi in range(len(self.initialized)):
                if np.array_equal(self.initialized[yi, 1:-1], self.stored[y, 1:-1]):
                    self.initialized[yi, -1] = self.stored[y, -1]

    def check_is_metric_wrote(self):
        return self.initialized[self.it, self.n_hip + 1] != 0
