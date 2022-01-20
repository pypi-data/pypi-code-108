def tags(*object_tags):
    def wrap(func):
        func.tags = object_tags
        return func

    return wrap


def executable(func):
    func.executable = True
    return func
