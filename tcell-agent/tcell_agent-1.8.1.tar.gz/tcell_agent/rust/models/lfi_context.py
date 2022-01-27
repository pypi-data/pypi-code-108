class LFIContext(dict):
    def __init__(self, file_path, mode, opener_class, tcell_context=None):
        dict.__init__(self)

        self['file_path'] = file_path
        self['mode'] = mode
        self['opener_class'] = opener_class
        self['dir_classification'] = 'Unknown'
        if tcell_context:
            self['remote_address'] = tcell_context.remote_address
            self['full_uri'] = tcell_context.uri
            self['request_path'] = tcell_context.path
            self['method'] = tcell_context.method
            self['route_id'] = tcell_context.route_id
            self['user_id'] = tcell_context.user_id
            self['session_id'] = tcell_context.session_id
            self["reverse_proxy_header_value"] = tcell_context.reverse_proxy_header_value
