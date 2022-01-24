class BucketVersioningConfig(object):
    def __init__(self, status=None):
        self.status = status

    def __repr__(self):
        return "status " + self.status

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Status':
            self.status = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<?xml version="1.0" encoding="UTF-8"?>'
        s += '<VersioningConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        if self.status is not None:
            s += '<Status>%s</Status>' % self.status
        s += '</VersioningConfiguration>'
        return s
