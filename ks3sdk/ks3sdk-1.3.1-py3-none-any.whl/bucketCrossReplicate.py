class BucketCrossReplicate(object):
    def __init__(self, targetBucket=None, deleteMarkerStatus=None, prefix=None, region=None):
        self.targetBucket = targetBucket
        self.deleteMarkerStatus = deleteMarkerStatus
        self.prefix = prefix
        self.region = region

    def __repr__(self):
        list_prefix = ''
        if self.prefix is not None:
            for x in self.prefix:
                list_prefix += x
        return "targetBucket " + self.targetBucket \
               + " deleteMarkerStatus " + self.deleteMarkerStatus \
               + " prefix " + list_prefix \
               + " region " + self.region

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'targetBucket':
            self.targetBucket = value
        elif name == 'DeleteMarkerStatus':
            self.deleteMarkerStatus = value
        elif name == 'prefix':
            if self.prefix is None:
                self.prefix = []
            self.prefix.append(value)
        elif name == 'region':
            self.region = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = u'<?xml version="1.0" encoding="UTF-8"?>'
        s += u'<Replication xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        # s += '<BucketLoggingStatus xmlns="http://ks3.ksyun.com">'
        if self.targetBucket is not None:
            s += '<targetBucket>%s</targetBucket>' % self.targetBucket
        if self.deleteMarkerStatus is not None:
            s += '<DeleteMarkerStatus>%s</DeleteMarkerStatus>' % self.deleteMarkerStatus
        if self.region is not None:
            s += '<region>%s</region>' % self.region
        if self.prefix is not None and len(self.prefix) > 0:
            for x in self.prefix:
                s += '<prefix>%s</prefix>' % x
        s += '</Replication>'
        return s
