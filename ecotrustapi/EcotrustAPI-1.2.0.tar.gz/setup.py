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
  success, msg = api_control.criar_ativo({  
		'name': 'Teste ativo criado pela API',  
		'value': 'testphp.com.br',  
		'type': 'fqdn',  
		'criticity': 'high',  
		'financeiro': 900000000,  
		'description': 'Ativo criado via API',  
		'tags': 'Ativo Externo'  
 })  
 return success, msg  

def testar_criar_scan_parametrizado(api_control):  
	\"\"\"  
		Cria um scan parametrizado no Ecotrust Obs: Os ativos 		especificados devem estar previamente cadastrados no Ecotrust  
		!! Anteção, os ativos devem ser do tipo: fqdn/url/domain... e não devem conter espaços !!  
		Para criar e já iniciar um scan pontual, configure o campo start_scan com "now" ou executar imediamente após a criação do scan parametrizado.
    \"\"\"  
	success, msg = api_control.criar_scan_parametrizado({  
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
	return success
  
def teste_aguardar_relatorio(api_control, scan_parametrizado_titulo):  
    while True:
        success, ret = self.api_control.obter_reporte_se_disponivel(scan_parametrizado_titulo)
        if not success and ret != '':
            print(f"Erro ao obter relatório: {ret}")
        elif success:
            print(f"Relatório obtido!")
            break
        elif not success and ret == '':
            print(f"Relatório não está disponível ainda.")

        time.sleep(5)
  
if __name__ == '__main__':  
	 instancia = "https://instancia.ecotrust.io"  
	 api_control = EcotrustAPI("<token>", instancia)
	 
	 
	 testar_criar_scan_parametrizado(api_control)
	 teste_aguardar_relatorio(api_control, 'Scan parametrizdo - API 4')
```
"""

setup(
    name="EcotrustAPI",
    version="1.2.0",
    install_requires=[
        'requests', 'urllib3', 'rand-string'
    ],
    description="Biblioteca para interação com API do EcotrustET",
    long_description=descricao_longa,
    long_description_content_type='text/markdown',
    author="EcoIT - Dev Team",
    author_email="pablo.viana@ecoit.com.br",
    py_modules=['ecotrust_api'],
    python_requires='>=3.9',
)