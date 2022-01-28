import jinja2
import os
import json

class J2Template():
    """ TODO: translate to English

    Classe utilizada para carregar o template Jinja2 a ser renderizado.
    
    Argumentos:
                template_relative_path: caminho do arquivo de template
                jtype: tipo do template (yaml, json)"""
    
    def __init__(self, template_relative_path, jtype=None) -> None:
        template_dir = os.path.dirname(os.path.realpath(template_relative_path))
        #print("Template dir:", template_dir)
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath=template_dir)
        )
        if jtype == 'json':
            env.filters['jsonify'] = json.dumps

        template_file_name = template_relative_path.split('/')[-1]
        
        self.template = env.get_template(template_file_name)