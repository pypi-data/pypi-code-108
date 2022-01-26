__current_app = None  # type: metasdk.MetaApp


def set_current_app(app):
    global current_app
    current_app = app


def get_current_app():
    global current_app
    return current_app
