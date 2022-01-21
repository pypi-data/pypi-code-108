from setuptools import setup

descricao_longa = """
    # EcotrustAPI - Python3
Biblioteca que interage com a api do Ecotrust e normaliza alguns retornos da plataforma.


# Ações possíveis pela lib

 - Criar scan parametrizado e executá-lo
 - Cadastrar ativo
 - Obter detalhes do ativo

## Exemplo de uso

```py
from ecotrust_api import EcotrustAPI  

  
def test_criar_ativo(api_control):  
	  \"\"\"  
		 Cria um ativo na instância com os payloads abaixo, o 				padrão para cada chamada de api é retornar um booleano err e uma mensagem que pode ser vazia ou populada com o retorno padrão da 	API.  
		 Caso o ativo já exista, é retornado False e o endpoint 			retorna 500.  
		
	 \"\"\"  
	 err, msg = api_control.criar_ativo({  
		  'name': 'Teste ativo criado pela API',  
		  'value': 'ecoit.com.br',  
		  'type': 'fqdn',  
		  'criticity': 'high',  
		  'financeiro': 900000000,  
		  'description': 'Ativo criado via API',  
		  'tags': 'Ativo Externo'  
	 })  

  def testar_criar_scan_parametrizado(api_control):  
		 \"\"\"  
		 Cria um scan parametrizado no Ecotrust Obs: Os ativos 		especificados devem estar previamente cadastrados no Ecotrust  
		 !! Anteção, os ativos devem ser do tipo: fqdn/url/domain... e não devem conter espaços !!  
		 Para criar e já iniciar um scan pontual, configure o campo start_scan com "now" ou executar imediamente após a criação do scan parametrizado.
		 \"\"\"  
		 err, msg = api_control.criar_scan_parametrizado({  
			  'title': 'Scan parametrizdo - API 4',  
			  'description': 'Scan parametrizado 23 via API',  
			  'sensor_nome': 'NET-SCAN',  
			  'sensor_politica': 'Descoberta Portas Abertas (TCP/53,56,80,443,8080)',  
			  'ativos': [  
			  'teste.api.com.br',  
			  'ecoit.com.br',  
			 ],  
			  'start_scan': 'now',  
			  'scan_type': 'single'  
		 })  
  
  
if __name__ == '__main__':  
	 instancia = "https://instancia.ecotrust.io"  
	 api_control = EcotrustAPI("<token>", instancia)
	 testar_criar_scan_parametrizado(api_control)
```
"""

setup(
    name="EcotrustAPI",
    version="1.0.1",
    install_requires=[
        'requests', 'urllib3'
    ],
    description="Biblioteca para interação com API do EcotrustET",
    long_description=descricao_longa,
    long_description_content_type='text/markdown',
    author="EcoIT - Dev Team",
    author_email="pablo.viana@ecoit.com.br",
    py_modules=['ecotrust_api'],
    python_requires='>=3.9',
)