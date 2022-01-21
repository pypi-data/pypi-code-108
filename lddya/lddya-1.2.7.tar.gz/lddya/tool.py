import datetime

class Clock():
    def __init__(self):
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = datetime.datetime.now()

    def end(self):
        self.end_time = datetime.datetime.now()
    
    def show(self):
        a = self.end_time - self.start_time
        print('The program runs for ',a,' microsecond')

