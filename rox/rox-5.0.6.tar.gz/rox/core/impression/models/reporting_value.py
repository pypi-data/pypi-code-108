class ReportingValue(object):
    def __init__(self, name, value, targeting):
        self.name = name
        self.value = value
        self.targeting = targeting

    def __str__(self):
        return '%s - %s %s %s' % (super(ReportingValue, self).__str__(), self.name, self.value, self.targeting)
