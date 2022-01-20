from flask import current_app, _app_ctx_stack

class ChartJS(object):
    def __init(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        app.teardown_appcontext(self.teardown)
        
    def teardown(self, exception):
        ctx = _app_ctx_stack.top
    
    