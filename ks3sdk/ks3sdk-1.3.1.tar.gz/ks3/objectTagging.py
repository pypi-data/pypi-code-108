class ObjectTagging(object):
    def __init__(self, taggingSet=None):
        if taggingSet is None:
            self.taggingSet = []
        else:
            self.taggingSet = taggingSet

    def __repr__(self):
        s = "tagging "
        for tag in self.taggingSet:
            s += tag.key + ':' + (lambda x: ['', tag.value][tag.value is not None])(tag.value) + ' '
        return s

    def startElement(self, name, attrs, connection):
        if name == 'Tag':
            self.taggingSet.append(Tag())
            return self.taggingSet[-1]
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        s = '<?xml version="1.0" encoding="UTF-8"?>'
        s += '<Tagging>'
        if self.taggingSet is not None:
            s += '<TagSet>'
            for tag in self.taggingSet:
                s += tag.to_xml()
            s += '</TagSet>'
        s += '</Tagging>'
        return s


class Tag(object):
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == 'Key':
            self.key = value
        elif name == 'Value':
            self.value = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<Tag>'
        if self.key is not None:
            s += '<Key>%s</Key>' % self.key
        if self.value is not None:
            s += '<Value>%s</Value>' % self.value
        s += '</Tag>'
        return s
