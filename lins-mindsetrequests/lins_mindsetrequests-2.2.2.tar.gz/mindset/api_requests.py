from os import environ
from .utils.request_base import mindset_request
from .utils.date_utils import make_aware
from datetime import datetime


class Servico:

    def __init__(self, nome_servico):
        self.nome_servico = nome_servico
        self.id = None

    def get_or_create(self, service_params={}):
        response = mindset_request('GET', '/servicos', query_params={'servico': self.nome_servico})
        if not response.ok:
            return response, {}
        if not response.json():
            response = mindset_request('POST', '/servicos', json=service_params)
            self.id = response.json()['_id']
            return (response, response.json()) if response.ok else (response, {})
        self.id = response.json()[0]['_id']
        return (response, response.json()[0])

    def ativo(self):
        response = mindset_request('GET', '/servicos', query_params={'servico': self.nome_servico})
        if response.ok and response.json():
            return response.json()[0]['ativo']

    @staticmethod
    def filtrar(filter_params={}):
        return mindset_request('GET', '/servicos', query_params=filter_params)

    def forcar_execucao(self):
        response = mindset_request('GET', '/servicos', query_params={'servico': self.nome_servico})
        if not response.ok:
            raise ConnectionError(f'Status code {response.status_code} em "{response.url}"')
        return response.json()[0]['forcar_execucao']

    def get_id(self):
        response = mindset_request('GET', '/servicos', query_params={'servico': self.nome_servico})
        if response.ok and response.json():
            self.id = response.json()[0]['_id']
            return self.id

    def inicia_integracao(self):
        return mindset_request('POST', f'/servicos/{self.id}/inicia_integracao')

    def sucesso_integracao(self):
        return mindset_request('POST', f'/servicos/{self.id}/sucesso_integracao')

    def falha_integracao(self):
        return mindset_request('POST', f'/servicos/{self.id}/falha_integracao')

    def get_data_ultima_integracao(self, filter_params={}):
        query_params = {
            '_id_servico': self.id,
            'status': 'S',
            'fields': 'inicio_execucao',
            'sort': '-inicio_execucao',
            'per_page': 1,
        }
        query_params.update(filter_params)
        valor_padrao = {'inicio_execucao': environ.get('DATA_PADRAO_INTEGRACAO')}
        response = Status.get(query_params)
        data = response.json()[0] if response.ok and response.json() else valor_padrao
        data = make_aware(self.format_datetime(data.get('inicio_execucao')))
        return datetime.strftime(data, '%Y-%m-%dT%H:%M:%S')

    def delete(self):
        return mindset_request('DELETE', f'/servicos/{self.id}')

    def update(self, json):
        return mindset_request('PATCH', f'/servicos/{self.id}', json=json)

    def status(self):
        return mindset_request('GET', f'/servicos/{self.id}/status')

    def em_execucao(self):
        response = self.status()
        if response.ok and response.json():
            return "E" == response.json()[0].get('status', False)
        if response.ok and not response.json():
            return False
        return True

    def executado(self):
        response = Controle.get({'servico': self.id})
        if response.ok and not response.json():
            return False
        if response.ok and response.json():
            return response.json()[0]['executado']

    @staticmethod
    def format_datetime(data: str) -> datetime:
        if data and len(data) == 19:
            data += '.0'
        return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%f')

    def pode_integrar(self):
        servico = mindset_request('GET', f'/servicos/{self.id}').json()
        response = self.status()
        if not response.json() and self.ativo():
            return True
        if self.em_execucao():
            return False
        if self.forcar_execucao():
            return True
        hoje, json = datetime.now(), response.json()[0]
        fim_execucao = {19: f'{json["fim_execucao"]}.0'}.get(
            len(str(json['fim_execucao'])),
            json['fim_execucao'],
        )
        no_horario = hoje.time() >= datetime.strptime(
            servico.get('hora_agendamento', '01:00:00'),
            '%H:%M:%S',
        ).time()
        executou_hoje = all([
            json.get('status') == 'S',
            fim_execucao,
            datetime.strptime(
                fim_execucao,
                '%Y-%m-%dT%H:%M:%S.%f',
            ).date() == hoje.date() if fim_execucao else False,
        ])
        return all([self.ativo(), not self.executado(), no_horario, not executou_hoje])

    def limpar_controle(self):
        return Controle.limpar({'_id_servico': self.id})


class Controle:

    @staticmethod
    def get(filter_params={}):
        return mindset_request('GET', '/controle', query_params=filter_params)

    @staticmethod
    def limpar(json={}):
        return mindset_request('POST', '/controle/limpar_controles', json=json)


class Status:

    @staticmethod
    def get(filter_params={}):
        return mindset_request('GET', '/status', query_params=filter_params)

    @staticmethod
    def atuais():
        return mindset_request('GET', '/status/atual')
