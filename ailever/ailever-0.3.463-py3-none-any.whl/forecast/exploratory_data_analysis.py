from .utils import directory

class UnivariateEDA:
    def __init__(self, time_series):
        self.data = time_series
        self.name = 'UnivariateEDA'
        directory(self.name)
        self.pairplot()

    def pairplot(self):
        sns.displot(data=self.data)

        pass
    

class MultivariteEDA:
    def __init__(self, time_series):
        self.data = time_series
        self.name = 'MultivariateEDA'
        directory(self.name)


