class TestResults():
    def __init__(self,
                 name=None,
                 test=None,
                 statistic=None,
                 pvalue=None,
                 passed=None,
                 description=None,
                 ):
        self.name = name
        self.test = test
        self.statistic = statistic
        self.pvalue = pvalue
        self.passed = passed
        self.description = description

    def __str__(self):
        return (f'{self.description}')

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.name!r}, test={self.test!r}, statistic={self.statistic:1.2f}, pvalue={self.pvalue:1.4f}, passed={self.passed})')
