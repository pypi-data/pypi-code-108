

from twisted import logger

from .spec import BasicTableSpec


class BasicTableEntry(object):
    def __init__(self, data):
        self._data = data
        self._parent = None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, value):
        self._parent = value

    @property
    def data(self):
        return self._data


class BasicTable(object):
    def __init__(self, node, spec):
        self._node = node
        self._log = None
        self._spec = spec
        self._entries = []

    def install(self):
        self._spec.install()

    @property
    def node(self):
        return self._node

    @property
    def log(self):
        if not self._log:
            self._log = logger.Logger(namespace="table.{0}".format(self._spec.name),
                                      source=self)
        return self._log

    @property
    def spec(self) -> BasicTableSpec:
        return self._spec

    def update(self, entries, incremental=False):
        if incremental:
            raise NotImplementedError

        self._entries = []
        enable_dedup = bool(self.spec.dedup_keys)
        dedup_record = []

        for entry in entries:
            if enable_dedup:
                tags = tuple([getattr(entry, x) for x in self.spec.dedup_keys])
                if tags in dedup_record:
                    continue
                dedup_record.append(tags)
            entry.parent = self
            self._entries.append(entry)
        self.log.info("Extracted {0} Entries from API response".format(len(self._entries)))
