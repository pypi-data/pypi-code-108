from datetime import datetime, timedelta


class Timer:
    def __init__(self):
        self._nodes = []

    @property
    def is_running(self):
        return self._nodes and len(self._nodes[-1]) < 2

    @property
    def time_elapsed(self):
        result = timedelta(0)
        nodes_working = list(self._nodes)

        if self.is_running:
            result += datetime.now() - nodes_working.pop()[0]

        for start_stop_pair in nodes_working:
            result += start_stop_pair[1] - start_stop_pair[0]

        return result

    @property
    def elapsed_string(self):  # Ignores days
        current_elapsed = self.time_elapsed

        hours, rem = divmod(current_elapsed.seconds, 3600)
        mins, seconds = divmod(rem, 60)

        return "{0}:{1}:{2}".format(str(hours).zfill(2), str(mins).zfill(2), str(seconds).zfill(2))

    def reset(self):
        self._nodes = []

    def start(self):
        if self.is_running:
            return

        self._nodes.append([datetime.now()])

    def stop(self):
        if not self.is_running:
            return

        self._nodes[-1].append(datetime.now())
