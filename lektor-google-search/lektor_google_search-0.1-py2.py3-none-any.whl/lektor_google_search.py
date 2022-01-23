# -*- coding: utf-8 -*-
from lektor.pluginsystem import Plugin
from markupsafe import Markup

SCRIPT ='''
<script async src="https://cse.google.com/cse.js?cx=%(SEARCH_ENGINE_ID)s"></script>
<div class="gcse-search"></div>
'''

class GoogleSearchPlugin(Plugin):
    name = 'google-search'
    description = u'Lektor plugin to add google seach to a website'

    def on_setup_env(self, **extra):
        search_engine_id = self.get_config().get('SEARCH_ENGINE_ID')

        if search_engine_id is None:
            raise RuntimeError('SEARCH_ENGINE_ID is not configured.'
                                'Please configure it in '
                                '`./configs/google-search.ini` file')

        def render_google_search():
            return Markup(SCRIPT % {'SEARCH_ENGINE_ID':search_engine_id})

        self.env.jinja_env.globals['render_google_search'] = render_google_search
