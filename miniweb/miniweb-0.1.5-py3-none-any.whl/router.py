
class Router(object):

    def __init__(self):
        self.urls = {}

    def add_route(self, path, handler):
        if isinstance(handler, Router):
            for subpath, handler in handler.urls.items():
                final_path = path + "/" + subpath
                final_path = final_path.replace("/////", "/").replace("////", "/").replace("///", "/").replace("//", "/")
                self.urls[final_path] = handler
        else:
            self.urls[path] = handler

    def dispatch(self, path):
        return self.urls.get(path, None)
