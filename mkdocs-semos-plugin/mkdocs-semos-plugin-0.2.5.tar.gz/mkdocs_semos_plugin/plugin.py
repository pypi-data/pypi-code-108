import os
import re
import time
import json
import os.path
import logging
import tempfile
import subprocess
import wsgiref.simple_server

from pathlib import Path
from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin

class _LoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return time.strftime("[%H:%M:%S] == ") + f"{msg}", kwargs

log = _LoggerAdapter(logging.getLogger("mkdocs.semos"), {})

CONVERT_TOOL = os.getenv('CONVERT_TOOL', 'D:/Ceiba/pocs/markdown/bpmn-to-image-test/convert.bat')
CONVERT_MODE = os.getenv('CONVERT_MODE', 'DEBUG')

BPMN_ENDPOINT = '/bpmn-render'
SRC_PATH = 'documentacion/'

class SemosPlugin(BasePlugin):

    config_scheme = (
        ('param', config_options.Type(str, default='')),
    )

    def __init__(self):
        self.enabled = True
        self.total_time = 0

    def on_page_content(self, html, page, config, files):
        log.debug(f"({page.url})")
        
        img_regex = '<img(.*?)\/>'
        src_regex = 'src="(.*?)"'

        img = re.compile(img_regex)
        src = re.compile(src_regex)
        index = 0

        for item in img.finditer(html):
            src_match = src.search(item.group())

            if src_match:
                log.debug(item.group())
                index = index = 1
                
                # <img alt="Diagrama solucion!" src="imgs/aws.drawio.svg" title="Diagrama Solución" />
                # <object data="imgs/componentes.drawio.svg" type="image/svg+xml" id="svg" width="100%" height="100%"></object>
                image_file = src_match.group(1)
                html_class = 'doc-svg'

                if image_file.endswith('.bpmn'):
                    html_class = 'doc-svg-bpmn'
                    if CONVERT_MODE == 'DEBUG':
                        image_file = f"{BPMN_ENDPOINT}/?{page.url}{image_file}.svg"
                    else:
                        image_file = image_file + '.svg'

                html = html.replace(item.group(), f"<object data=\"{image_file}\" type=\"image/svg+xml\" class=\"{html_class}\" id=\"svg{index}\" width=\"100%\" height=\"100%\"></object>")

        return html

    def on_post_build(self, config):
        build_dir = config['site_dir']

        log.info('temp dir: ' + build_dir)

        for svg in Path(build_dir).rglob('*.svg'):
            if svg.suffix == '.svg':
                log.debug(f"{svg}")
        
                content = svg.read_text()
                svg.write_text(content.replace('<a xlink', '<a target="_parent" xlink'))

        if CONVERT_MODE != 'DEBUG':
            for bpmn in Path(build_dir).rglob('*.bpmn'):
                #if bpmn.suffix == '.bpmn':
                log.debug(bpmn)
            
                self.convert_bpmn_to_svg(bpmn, f"{bpmn}.svg")

        return

    def on_serve(self, server, config, builder):
        if CONVERT_MODE == 'DEBUG':
            log.info('onServe -- debug-mode')
            data = {}
            tmp_dir = tempfile.gettempdir().replace('\\', '/')
            db_path = f"{tmp_dir}/bpmn-converted-files"
            db_file = f"{db_path}/data.json"

            if not os.path.exists(db_path):
                os.mkdir(db_path)

            log.info(f"open database -- {db_file}")
            try:
                with open(db_file) as infile:
                    data = json.load(infile)
            except Exception:
                log.info(f"database not exist -- {db_file}")

            old_app = server.get_app()

            def new_app(environ, start_response):
                path = environ['PATH_INFO'].encode('latin-1').decode('utf-8', 'ignore')

                if path.startswith(BPMN_ENDPOINT):
                    log.info(path)
                    fixed_path = self.fix_path(environ['QUERY_STRING'])
                    file = (SRC_PATH + fixed_path).replace('.svg', '')
                    new_file = f"{db_path}/{file}.svg"

                    try:
                        new_path = Path(os.path.dirname(os.path.abspath(new_file)))
                        new_path.mkdir(parents=True)
                    except Exception:
                        None

                    self.update_database(file, new_file, data, db_file)

                    cached_file = data[file]

                    while not os.path.exists(cached_file['new_file']):
                        log.debug(f"wait => {cached_file['new_file']}")
                        time.sleep(0.100)
                    log.debug(f"exist => {cached_file['new_file']}")

                    rfile = open(cached_file['new_file'], "rb")

                    start_response("200 OK", [])
                    return wsgiref.util.FileWrapper(rfile)                    
                    #return []
                else:
                    return old_app(environ, start_response)
            
            server.set_app(new_app)

        return server

###########################################################
# OTHER FUNCTIONS
###########################################################

    def convert_bpmn_to_svg(self, file_in, file_out):
        subprocess.call([CONVERT_TOOL, file_in, file_out])

    def fix_path(self, file_path):
        parts = file_path.split('/')

        try:
            index = parts.index('..')

            if index >= 0:
                del parts[index-1:index+1]
                return '/'.join(parts)
        except Exception:
            None
        
        return file_path

    def update_database(self, file, new_file, data, db_file):
        last_modified = time.ctime(os.path.getmtime(file))
        save = True

        if not file in data:
            created = time.ctime(os.path.getctime(file))

            data[file] = { 
                'new_file': new_file,  
                'last_modified': last_modified,
                'created': created }        
        elif last_modified != data[file]['last_modified']:
            data[file]['last_modified'] = last_modified
        else:
            save = False

        if save:
            self.convert_bpmn_to_svg(file, new_file)
            
            json_data = json.dumps(data)
            f = open(db_file, 'w')
            f.write(json_data)
            f.close()
            log.info('bpmn database updated!')


#
#    def on_pre_build(self, config):
#        return
#
#    def on_files(self, files, config):
#        return files
#
#    def on_nav(self, nav, config, files):
#        return nav
#
#    def on_env(self, env, config, files):
#        return env
#    
#    def on_config(self, config):
#        return config
#
#    def on_pre_template(self, template, template_name, config):
#        return template
#
#    def on_template_context(self, context, template_name, config):
#        return context
#    
#    def on_post_template(self, output_content, template_name, config):
#        return output_content
#    
#    def on_pre_page(self, page, config, files):
#        return page
#
#    def on_page_read_source(self, page, config):
#        return ""
#
#    def on_page_markdown(self, markdown, page, config, files):
#        return markdown
#
#    def on_page_content(self, html, page, config, files):
#        return html 
#
#    def on_page_context(self, context, page, config, nav):
#        return context
#
#    def on_post_page(self, output_content, page, config):
#        return output_content

