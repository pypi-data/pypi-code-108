class BucketQuota(object):
    def __init__(self, quota=None):
        self.quota = quota

    def __repr__(self):
        return "quota "+self.quota

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'StorageQuota':
            self.quota = value
        else:
            setattr(self, name, value)


    def to_xml(self):
        s = '<?xml version="1.0" encoding="UTF-8"?>'
        s += '<Quota>'
        if self.quota is not None:
            s += '<StorageQuota>%s</StorageQuota>' % self.quota
        s += '</Quota>'
        return s
