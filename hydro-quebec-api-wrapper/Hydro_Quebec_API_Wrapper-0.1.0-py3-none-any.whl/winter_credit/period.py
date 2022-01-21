"""Class describing a period."""


class Period:
    """This class describe a period object."""

    def __init__(self, config, date, start, end, critical=False):
        """Period constructor."""
        self.config = config
        self.date_dt = date
        self.start_dt = start
        self.end_dt = end
        self.critical = critical

    @property
    def date(self):
        """Give period date."""
        return self.date_dt.strftime("%Y-%m-%d")

    @property
    def start(self):
        """Give period start time as hour (without date)."""
        return self.start_dt.strftime(self.config.datetime_format)

    @property
    def end(self):
        """Give period end time as hour (without date)."""
        return self.end_dt.strftime(self.config.datetime_format)

    @property
    def start_ts(self):
        """Give period start time as timestamp."""
        return self.start_dt.timestamp()

    @property
    def end_ts(self):
        """Give period end time as timestamp."""
        return self.end_dt.timestamp()

    def to_dict(self):
        """Return the current object attributes as a dict."""
        return {
            "date": self.date,
            "start": self.start,
            "end": self.end,
            "start_ts": self.start_ts,
            "end_ts": self.end_ts,
            "critical": self.critical,
        }
