import time

from nehushtan.helper.timer.TimeCostResult import TimeCostResult


class TimeCostHelper:
    def __init__(self, result: TimeCostResult):
        self.result = result

    def __enter__(self):
        self.result.start = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.result.end = time.time()
        self.result.period = self.result.end - self.result.start


if __name__ == '__main__':
    """
    This is an example
    """

    tcr = TimeCostResult()
    with TimeCostHelper(tcr):
        time.sleep(2)
    print(tcr)
