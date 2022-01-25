from .config import Option

def set_samstatic_default_parm(app):
    app.config.setdefault('SAMSTATIC_ENDPOINTS', Option.ALL)
    app.config.setdefault('SAMSTATIC_ENDPOINTS_USE_CACHE', True)
    app._samstatic_endpoints_caches = {'config': None, 'all': None}