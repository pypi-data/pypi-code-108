class TimeCostResult:
    def __init__(self):
        self.start = 0
        self.end = 0
        self.period = 0

    def __str__(self):
        return f"PERIOD {self.period} seconds FROM {self.start} TO {self.end}"
