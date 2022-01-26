class Coding(object):
    pass


class Action(object):

    def __init__(self, title, type, content):
        self.title = title
        self.type = type
        self.content = content

    def to_json(self):
        pass
