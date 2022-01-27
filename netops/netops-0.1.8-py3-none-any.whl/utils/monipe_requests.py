import json

from .template_rendering import J2Template


def get_api_request_data(infra, request_template_path):
    """ TODO: write docstrings
    
    Obtem as configuracoes a serem executadas nos dispositivos baseado nos templates de configuracao.
    
    Recebe:
            infra = Dicionario que contem as informacoes relativas a infraestrutura para ativacao do novo circuito
            request_template_path = Path do template de request a API do MONIPE
    Retorna:
            request_data = Dados do request a API do MONIPE"""
    template_request = J2Template(request_template_path, 'json')
    request_data = json.loads(
        template_request.template.render(**infra)
    )
        
    return request_data