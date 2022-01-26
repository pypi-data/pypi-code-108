from datetime import date

class Today(object):
    def __init__(self):
        self.today = date.today()

    def __call__(self, strftime: str):
        return self.today.strftime(strftime)


today = Today()

