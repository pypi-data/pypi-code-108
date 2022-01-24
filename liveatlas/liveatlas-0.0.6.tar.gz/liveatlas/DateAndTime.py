from datetime import datetime


class DateAndTime:
    def __init__(self, timestamp, game_time):
        date_and_time = datetime.fromtimestamp(timestamp / 1000)
        self.timestamp = timestamp
        self.game_time = game_time
        self.time_24hr = date_and_time.time()
        self.date = date_and_time.date()
        self.is_day = True if game_time < 13000 else False

