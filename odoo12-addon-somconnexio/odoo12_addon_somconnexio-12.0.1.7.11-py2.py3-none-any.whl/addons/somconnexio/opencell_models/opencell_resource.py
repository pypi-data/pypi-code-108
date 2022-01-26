class OpenCellResource(object):
    def to_dict(self):
        return {key: getattr(self, key) for key in self.white_list}
