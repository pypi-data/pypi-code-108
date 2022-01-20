# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fast_auth', 'fast_auth.auth']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.30,<2.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'fastapi>=0.72.0,<0.73.0',
 'isort>=5.10.1,<6.0.0',
 'passlib>=1.7.4,<2.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'python-jose>=3.3.0,<4.0.0']

entry_points = \
{'console_scripts': ['create_user = fast_auth.auth.auth:create_user_cli',
                     'migrate = fast_auth.migration:create_auth_tables_cli']}

setup_kwargs = {
    'name': 'fast-auth',
    'version': '0.1.3',
    'description': 'Simple implementation of authentication in projects using FastAPI',
    'long_description': "Fast Auth\n===================\n\n\nFacilita implementação de um sistema de autenticação básico e uso de uma\nsessão de banco de dados em projetos com tFastAPi.\n\n\nInstalação e configuração\n=========================\n\nInstale usando pip ou seu o gerenciador de ambiente da sua preferencia:\n\n    pip install fast-auth\n\nAs configurações desta lib são feitas a partir de variáveis de ambiente.\nPara facilitar a leitura dessas informações o fast_auth\nprocura no diretório inicial(pasta onde o uvicorn ou gunicorn é chamado\niniciando o serviço web) o arquivo .env e faz a leitura dele.\n\nAbaixo temos todas as variáveis de ambiente necessárias e em seguida a explição de cada uma:\n\n    CONNECTION_STRING=postgresql+asyncpg://postgres:12345678@localhost:5432/fastapi \n\n    SECRET_KEY=1155072ced40aeb1865533335aaec0d88bbc47a996cafb8014336bdd2e719376\n    \n    TTL_JWT=60\n\n- CONNECTION_STRING: Necessário para a conexão com o banco de dados. Gerealmente seguem o formato\n  dialect+driver://username:password@host:port/database. O driver deve ser um que suporte execuções\n  assíncronas como asyncpg para PostgreSQL, asyncmy para MySQL, para o SQLite o fast_auth\n  já trás o aiosqlite.\n\n- SECRET_KEY: Para gerar e decodificar o token JWT é preciso ter uma chave secreta, que como o nome\n  diz não deve ser pública. Para gerar essa chave pode ser utilizado o seguinte comando:\n\n    openssl rand -hex 32\n\n- TTL_JWT: O token JWT deve ter um tempo de vida o qual é especificado por essa variável. Este deve \n  ser um valor inteiro que ira representar o tempo de vida dos token em minutos. Caso não seja\n  definido será utilizado o valor 1440 o equivalente a 24 horas.\n\n\nPrimeiros passos\n================\n\nApós a instalação e especificação da CONNECTION_STRING as tabelas podem ser criada no banco de dados\nutilizando o seguinte comando no terminal:\n\n    migrate\n\nEste comando irá criar 3 tabelas, auth_users, auth_groups e auth_users_groups.\nTendo criado as tabelas, já será possível criar usuários pela linha de comando:\n\n    create_user\n\nAo executar o comando será solicitado o username e password.\n\nComo utilizar\n=============\n\nToda a forma de uso foi construida seguindo o que consta na documentação do FastAPI\n\nConexao com banco de dados\n--------------------------\n\nTendo a CONNECTION_STRING devidamente especificada, para ter acesso a uma sessão do banco de dados\na partir de uma path operation basta seguir o exemplo abaixo::\n\n    from fastapi import FastAPI, Depends\n    from sqlalchemy.ext.asyncio import AsyncSession\n    from fast_auth import connection_database, get_db\n\n    connection_database()\n\n    app = FastAPI()\n\n\n    @app.get('/get_users')\n    async def get_users(db: AsyncSession = Depends(get_db)):\n        result = await db.execute('select * from auth_users')\n        return [dict(user) for user in result]\n\nExplicando o que foi feito acima, a função connection_database estabelece conexão com o banco de dados\npassando a CONNECTION_STRING para o SQLAlchemy, mais especificamente para a função\ncreate_async_engine.\nNo path operation passamos a função get_db como dependencia, sendo ele um generator que retorna\numa sessão assincrona já instanciada, basta utilizar conforme necessário e o fast_auth mais o\nprório fastapi ficam responsáveis por encerrar a sessão depois que a requisição é retornada.\n\n\nAutenticação - Efetuando login\n------------------------------\n\nAbaixo um exemplo de rota para authenticação::\n\n    from fastapi import FastAPI, Depends\n    from pydantic import BaseModel\n    from sqlalchemy.ext.asyncio import AsyncSession\n    from fast_auth import connection_database, authenticate, create_token_jwt\n\n    connection_database()\n\n    app = FastAPI()\n\n\n    class SchemaLogin(BaseModel):\n        username: str\n        password: str\n\n\n    @app.post('/login'):\n    async def login(credentials: SchemaLogin):\n        user = await authenticate(credentials.username, credentials.password)\n        if user:\n            token = create_token_jwt(user)\n            return {'access': token}\n\nA função authenticate é responsável por buscar no banco de dados o usuário informado\ne checar se a senha confere, se estiver correto o usuário(objeto do tipo User que está\nem fast_auth.models) é retornado o qual deve ser passado como parâmetro para a \nfunção create_token_jwt que gera e retorna o token. No token fica salvo por padrão o id \ne o username do usuário, caso necessário, pode ser passado um dict como parametro com\ninformações adicionais para serem empacotadas junto.\n\n\nAutenticação - requisição autenticada\n-------------------------------------\n\nO exemplo a seguir demonstra uma rota que só pode ser acessada por um usuário autenticado::\n\n    from fastapi import FastAPI, Depends\n    from pydantic import BaseModel\n    from sqlalchemy.ext.asyncio import AsyncSession\n    from fast_auth import connection_database, require_auth\n\n    connection_database()\n\n    app = FastAPI()\n\n\n    @app.get('/authenticated')\n    def authenticated(payload: dict = Depends(require_auth)):\n        #faz alguma coisa\n        return {}\n\n\nPara garantir que uma path operation seja executada apenas por usuários autenticados basta \nimportar e passar ccomo dependência a função require_auth. Ela irá retornar os dados\nque foram empacotados no token JWT.\n",
    'author': 'Douglas de Oliveira Braga',
    'author_email': 'douglasob94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/douglasob/fast-auth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
