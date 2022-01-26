OFFSET_ZEROBASED_INDEX = 1

class Task:

    def __init__(self, id, name, effort, progress = 0.0):
        self._id = id
        self._name = name
        self._effort = effort
        self._pre = []
        self._post = []

        self._progress = progress

        self._es = None
        self._lf = None

    def __str__(self):
        return self._name

    def __effort_offset(self):
        return max(self.effort_numerical() - OFFSET_ZEROBASED_INDEX, 0)

    def id(self):
        return self._id

    def name(self):
        return self._name

    def effort(self):
        return self._effort

    def effort_numerical(self):
        if not isinstance(self._effort, int):
            return 0
        return self._effort

    def progress(self):
        return self._progress

    def earliest_start(self):
        if not self._es:
            if not self._pre:
                self._es = 0
                return self._es

            self._es = max([
                predecessor.earliest_start() + predecessor.effort_numerical()
                for predecessor in self._pre
            ])
        return self._es

    def latest_finish(self):
        if not self._lf:
            if not self._post:
                self._lf = self.earliest_start() + self.__effort_offset()
                return self._lf
            
            self._lf = min([
                successor.latest_finish() - successor.effort_numerical()
                for successor in self._post
            ])
        return self._lf

    def start(self):
        return self.earliest_start()

    def end(self):
        return self.start() + self.__effort_offset()

    def successors(self):
        return self._post

    def predecessors(self):
        return self._pre
        