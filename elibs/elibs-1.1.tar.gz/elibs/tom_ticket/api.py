import aiohttp
from elibs.utils import dict_to_prop


class TomTicket:
    def __init__(self, token):
        self.token = token
        self.url = 'http://api.tomticket.com'
        self.headers = {'content-type': 'application/x-www-form-urlencoded'}

    async def get_chamados(self, page=1):
        url = f"{self.url}/chamados/{self.token}/{page}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def get_chamado(self, chamado):
        url = f"{self.url}/chamado/{self.token}/{chamado}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def get_clientes(self, page=1):
        url = f"{self.url}/clientes/{self.token}/{page}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def get_custom_fields(self):
        url = f"{self.url}/custom_fields/{self.token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def get_organizations(self, page=1):
        url = f"{self.url}/organizacoes/{self.token}/{page}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def get_cliente(self, identificador, tipo_identificador='E'):
        url = f"{self.url}/cliente/detalhes/{self.token}/{identificador}/{tipo_identificador}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def create_cliente(self, cliente):
        url = f"{self.url}/criar_cliente/{self.token}/"
        data = {
            "identificador": cliente.grid,
            "nome": cliente.name,
            "email": cliente.email,
            "criarchamados": cliente.can_create_order,
            "telefone": cliente.telephone,
            "id_organizacao": cliente.organization_id,
            "campos": cliente.fields
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def search_wiki(self, text):
        url = f"{self.url}/kb/busca/{self.token}/{text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def create_client_quick_access(self, cliente, tipo='E'):
        url = f"{self.url}/criar_acesso_cliente/{self.token}"

        data = {
            "identificador": cliente,
            "tipo_identificacao": tipo
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def update_cliente(self, identificador, cliente, tipo_identificador='E'):
        url = f"{self.url}/update_cliente/{self.token}/{identificador}/{tipo_identificador}"
        data = {
            "id_interno": cliente.grid,
            "nome": cliente.name,
            "email": cliente.email,
            "criarchamados": cliente.can_create_order,
            "telefone": cliente.telephone,
            "id_organizacao": cliente.organization_id,
            "campos": cliente.fields,

        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def inactive_cliente(self, identificador, tipo_identificador='E', active=False):
        url = f"{self.url}/customer/status/{self.token}/{identificador}/{tipo_identificador}"
        data = {
            "active": active

        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def start_chamado_status(self, ticket_id, status_id, comment):
        url = f"{self.url}/ticket/status/open/{self.token}"
        data = {
            "comment": comment,
            "ticket_id": ticket_id,
            "status_id": status_id

        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def close_chamado(self, ticket_id):
        url = f"{self.url}/ticket/status/close/{self.token}"
        data = {
            "ticket_id": ticket_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def insert_comment(self, comment, ticket_id, attachment=None):
        url = f"{self.url}/ticket/comment/{self.token}"
        data = {
            "ticket_id": ticket_id,
            "comment": comment
        }
        if attachment is not None:
            data["attachment"] = attachment
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def get_departaments(self):
        url = f"{self.url}/departamentos/{self.token}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def criar_chamado(self, identificador, chamado):
        url = f"{self.url}/criar_chamado/{self.token}/{identificador}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=chamado, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def responder_chamado(self, chamado, mensagem, anexos=None):
        if anexos is None:
            anexos = []
        url = f"{self.url}/chamado/{self.token}/{chamado}/responder"
        data = {
            "mensagem": mensagem,
            "anexos": anexos
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def bloquear_clientes_abertura_chamados(self, cliente, bloquear=True):
        url = f"{self.url}/bloqueio_criacao_chamado/{self.token}/{cliente}"
        data = {
            "criarchamados": bloquear
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def check_blacklist(self, endereco_email):
        url = f"{self.url}/blacklist/{self.token}/{endereco_email}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def criar_organizacao(self, nome, email='', telefone='', criar_chamados=False, chamadosgerente=False,
                          chamadosmembros=False, limitechamadosmensal=0):
        url = f"{self.url}/criar_organizacao/{self.token}"
        data = {
            "nome": nome,
            "email": email,
            "telefone": telefone,
            "criar_chamados": criar_chamados,
            "chamadosgerente": chamadosgerente,
            "chamadosmembros": chamadosmembros,
            "limitechamadosmensal": limitechamadosmensal

        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)

    async def check_cliente(self, cliente, identificador='E'):
        url = f"{self.url}/cliente/{self.token}/{cliente}"
        data = {
            "tipo_identificador": identificador

        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, data=data, headers=self.headers) as resp:
                json = await resp.json()
                return dict_to_prop(json)
