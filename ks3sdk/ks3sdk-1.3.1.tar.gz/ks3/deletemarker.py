from ks3.user import User

class DeleteMarker(object):
    def __init__(self, bucket=None, name=None):
        self.bucket = bucket
        self.name = name
        self.version_id = None
        self.is_latest = False
        self.last_modified = None
        self.owner = None

    def startElement(self, name, attrs, connection):
        if name == 'Owner':
            self.owner = User(self)
            return self.owner
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'Key':
            self.name = value
        elif name == 'IsLatest':
            if value == 'true':
                self.is_latest = True
            else:
                self.is_latest = False
        elif name == 'LastModified':
            self.last_modified = value
        elif name == 'Owner':
            pass
        elif name == 'VersionId':
            self.version_id = value
        else:
            setattr(self, name, value)
