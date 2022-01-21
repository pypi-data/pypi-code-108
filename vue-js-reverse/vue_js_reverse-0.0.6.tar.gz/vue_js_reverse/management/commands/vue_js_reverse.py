import json
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.management.base import BaseCommand
from vue_js_reverse.core import generate_js
from vue_js_reverse.js_reverse_settings import JS_OUTPUT_PATH

try:
    from django.urls import get_resolver
except ImportError:
    from django.core.urlresolvers import get_resolver

REVERSE_FILE_NAME = 'reverse.js'


class Command(BaseCommand):
    @staticmethod
    def get_location():
        output_path = getattr(settings, 'JS_REVERSE_OUTPUT_PATH', JS_OUTPUT_PATH)

        if output_path:
            return output_path

        if not hasattr(settings, 'STATIC_ROOT') or not settings.STATIC_ROOT:
            raise ImproperlyConfigured(
                'The vue_js_reverse command needs settings.JS_REVERSE_OUTPUT_PATH or '
                'settings.STATIC_ROOT to be set.'
            )

        return os.path.join(settings.STATIC_ROOT, 'vue_js_reverse', 'js')

    help = "Generate vue functions for js reverse"

    def generate_js_reverse(self):
        location = self.get_location()

        fs = FileSystemStorage(location=location)

        if fs.exists(REVERSE_FILE_NAME):
            fs.delete(REVERSE_FILE_NAME)

        urlconf = getattr(settings, 'ROOT_URLCONF', None)
        default_url_resolver = get_resolver(urlconf)
        content = generate_js(default_url_resolver)

        fs.save(REVERSE_FILE_NAME, ContentFile(content))

        self.stdout.write('js-reverse file written to %s' % location)  # pragma: no cover

    def handle(self, *args, **options):
        self.generate_js_reverse()

        fs = FileSystemStorage(location=self.get_location())

        filename = os.path.join(self.get_location(), REVERSE_FILE_NAME)

        content = str(fs.open(filename).read())

        content = content[:content.index(';function factory(d)')]
        content = content[content.index('var data=') + 9:]

        urls = json.loads(content)

        vue_content = ''

        for url in urls['urls']:
            parameters = url[1][0]

            vue_content += '      ' + url[0].replace('-', '_').replace(':', '_') + ": "
            vue_content += '(' + ', '.join(parameters[1]) + ') => {'
            string = parameters[0].replace('%(', '${').replace(')s', '}')
            vue_content += ' return `/' + string + '` '
            vue_content += '},\n'

        vue_content = '    Vue.prototype.$urls = {\n' + vue_content + '    }\n'

        js = 'export default {\n'
        js += '  install(Vue, options) {\n'
        js += '    Vue.PLUGIN_VERSION = "0.0.1"\n'
        js += vue_content
        js += '  }\n'
        js += '}\n'

        if hasattr(settings, 'VUE_PLUGINS_DIR'):
            vue_plugins_dir = settings.VUE_PLUGIN_DIR
        else:
            vue_plugins_dir = os.path.join(settings.BASE_DIR, 'vue_frontend', 'src', 'plugins')

        if hasattr(settings, 'VUE_REVERSE_URL_PLUGIN'):
            vue_reverse_url_plugin = settings.VUE_REVERSE_URL_PLUGIN
        else:
            vue_reverse_url_plugin = 'Url.js'

        location = os.path.join(vue_plugins_dir, vue_reverse_url_plugin)

        file = open(location, 'w')
        file.write(js)
        file.close()

        self.stdout.write('Vue plugin file written to %s' % location)
