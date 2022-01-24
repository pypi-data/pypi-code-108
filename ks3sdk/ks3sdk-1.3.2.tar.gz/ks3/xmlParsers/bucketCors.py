class BucketCors(object):
    def __init__(self, rules=None):
        if rules is None:
            self.rules = []
        else:
            self.rules = rules

    def __repr__(self):
        return "rules: " + str(len(self.rules))

    def startElement(self, name, attrs, connection):
        if name == "CORSRule":
            self.rules.append(CORSRule())
            return self.rules[-1]
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def to_xml(self):
        # caller is responsible to encode to utf-8
        s = u'<CORSConfiguration xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        if self.rules:
            for rule in self.rules:
                s += rule.to_xml()
        s += '</CORSConfiguration>'
        return s


class CORSRule(object):
    def __init__(self, origins=None, methods=None, headers=None, max_age=None, exposed_headers=None):
        if origins is None:
            self.origins = []
        else:
            self.origins = origins
        if methods is None:
            self.methods = []
        else:
            self.methods = methods
        if headers is None:
            self.headers = []
        else:
            self.headers = headers
        if exposed_headers is None:
            self.exposed_headers = []
        else:
            self.exposed_headers = exposed_headers
        self.max_age = max_age

    def startElement(self, name, attrs, connection):
        return None

    def endElement(self, name, value, connection):
        if name == "AllowedOrigin":
            self.origins.append(value)
        if name == "AllowedMethod":
            self.methods.append(value)
        if name == "AllowedHeader":
            self.headers.append(value)
        if name == "ExposeHeader":
            self.exposed_headers.append(value)
        if name == 'MaxAgeSeconds':
            self.max_age = value
        else:
            setattr(self, name, value)

    def to_xml(self):
        s = '<CORSRule>'
        if self.origins is not None:
            for origin in self.origins:
                s += '<AllowedOrigin>%s</AllowedOrigin>' % origin
        if self.methods is not None:
            for method in self.methods:
                s += '<AllowedMethod>%s</AllowedMethod>' % method
        if self.headers is not None:
            for header in self.headers:
                s += '<AllowedHeader>%s</AllowedHeader>' % header
        if self.max_age is not None:
            s += '<MaxAgeSeconds>%s</MaxAgeSeconds>' % self.max_age
        if self.exposed_headers is not None:
            for exposed_header in self.exposed_headers:
                s += '<ExposeHeader>%s</ExposeHeader>' % exposed_header
        s += '</CORSRule>'
        return s