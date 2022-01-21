from __future__ import annotations
from requests import Session
from urllib3 import Retry
from requests.adapters import HTTPAdapter
from typing import Tuple, Final
from http import HTTPStatus
import json
from json.decoder import JSONDecodeError
# Import base exception


class EcoTrustAPIException(Exception):
    """Base exception for the EcoTrust API"""
    pass


# Post/Put exceptions
class BodyInvalido(EcoTrustAPIException):
    pass


class PayloadInvalido(EcoTrustAPIException):
    pass


class NenhumScanRodando(EcoTrustAPIException):
    pass


class APIError(EcoTrustAPIException):
    pass


# Sensor lookup
class SensorNaoEncontrado(EcoTrustAPIException):
    pass


class PoliticaNaoEncontrada(EcoTrustAPIException):
    pass


class ScanExecutando:
    def __init__(self, titulo: str, et_api: EcotrustAPI):
        self.titulo = titulo
        self.et_api = et_api

    def aguardar_termino(self) -> Tuple[bool, dict]:
        ok, scns = self.et_api.obter_scan({
            "_status": "started",
            "_status_cond": "exact",
            "_title": self.titulo,
            "_title_cond": "exact",
            "limit": 10
        })

        try:
            scns = json.loads(scns)
        except JSONDecodeError:
            raise APIError("Erro ao decodificar resposta da API")

        if not ok or len(scns) == 0:
            raise NenhumScanRodando("Não há nenhum scan em execução nesse momento, verifique se o scan não falhou.")

        scn = sorted(scns, key=lambda x: x["created_at"], reverse=True)[0]



class EcotrustAPI:

    def __init__(self, token: str, instancia_url: str):
        # Três minutos de timeout padrão
        self.TIMEOUT: Final = 60 * 3

        self.sess = Session()
        self.endpoints = {}
        self.instancia_base_url = instancia_url[:-1] if instancia_url[-1] == '/' else instancia_url

        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[502, 503, 504])

        self.sess.mount('https://', HTTPAdapter(max_retries=retries))
        self.sess.headers.update({
            'Authorization': 'Token {}'.format(token)
        })

        # Adiciona os endpoints da API
        self.\
            __add_endpoint('/assets/api/v1/add', 'add-ativo').\
            __add_endpoint('/assets/api/v1/details/{}', 'detalhe-ativo').\
            __add_endpoint('/scans/api/v1/defs/add', 'add-scan-parametrizado').\
            __add_endpoint('/scans/api/v1/list', 'listar-scans').\
            __add_endpoint('/scans/api/v1/listbydate', 'listar-por-data').\
            __add_endpoint('/engines/api/v1/instances/list', 'listar-engines').\
            __add_endpoint('/engines/api/v1/policies/list', 'listar-politicas')

    def __add_endpoint(self, endpoint: str, apelido: str) -> EcotrustAPI:
        self.endpoints[apelido] = f"{self.instancia_base_url}{endpoint}"
        return self

    def __listar_engines(self):
        req = self.sess.get(self.endpoints['listar-engines'], timeout=self.TIMEOUT)
        return req.status_code == HTTPStatus.OK, req.text

    def __listar_politicas(self) -> Tuple[bool, str]:
        req = self.sess.get(self.endpoints['listar-politicas'], timeout=self.TIMEOUT)

        return req.status_code == HTTPStatus.OK, req.text

    def obter_scan(self, filtro: dict) -> Tuple[bool, str]:
        req = self.sess.get(self.endpoints['listar-scans'], timeout=self.TIMEOUT, params=filtro)
        return req.status_code == HTTPStatus.OK, req.text

    # Obs: Valor não se refere ao valor financeiro e sim ao valor de endereço do ativo
    # Ex: 10.10.10.10, www.testphp.com.br etc...
    def obter_detalhes_de_ativo(self, ativo_valor: str) -> Tuple[bool, str]:
        req = self.sess.get(self.endpoints['detalhe-ativo'].format(ativo_valor), timeout=self.TIMEOUT)
        return req.status_code == HTTPStatus.OK, req.text

    """
        Cadastra um ativo na base da instância 
    
        :param Ativo: Dictionary com os dados do ativo
        :return Tuple: (err Houve um erro na solicitação, msg Mensagem de sucesso/erro)
    """
    def criar_ativo(self, ativo: dict) -> Tuple[bool, str]:

        # Verifica se o ativo é válido e contém todos os campos (body) necessários
        payloads = ['name', 'value', 'type', 'criticity', 'financeiro', 'description', 'tags']
        if not all(campo in ativo for campo in payloads):
            raise BodyInvalido('O ativo não possui todos os campos necessários: {}'.format(payloads))

        # Verificações de conformidade com os campos
        if ativo['type'] not in (tipos := ['fqdn', 'url', 'ip', 'domain']):
            raise PayloadInvalido('O ativo não possui um tipo válido, tipos válidos: {}'.format(tipos))

        if ativo['criticity'] not in (crts := ['high', 'medium', 'low']):
            raise PayloadInvalido('A criticidade do ativo não é válida, criticidades válidas: {}'.format(crts))

        if ativo['tags'] not in (tgs := ['Ativo Externo', 'Ativo Interno', 'Custom', 'External Network']):
            raise PayloadInvalido('A tag do ativo não é válida, tags válidas: {}'.format(tgs))

        criar_ativo_req = self.sess.put(self.endpoints['add-ativo'], data=ativo, timeout=self.TIMEOUT)
        return criar_ativo_req.status_code != HTTPStatus.OK, criar_ativo_req.text



    def criar_scan_parametrizado(self, scan_parametrizado: dict) -> Tuple[bool, int | str]:
        payloads = [
            'title', 'description', 'sensor_nome',
            'sensor_politica', 'ativos',
            'start_scan', 'scan_type'
        ]

        # Check if all the fields are present
        if not all(campo in scan_parametrizado for campo in payloads):
            raise BodyInvalido('O dict de scan parametrizado não possui todos os campos necessários: {}'.format(payloads))

        # Verificações de conformidade com os campos
        if scan_parametrizado['start_scan'] not in ['now', 'later']:
            raise PayloadInvalido('O start_scan não é válido, start_scan válidos: later ou now.')

        if scan_parametrizado['scan_type'] not in ['single', 'periodic']:
            raise PayloadInvalido('O scan_type não é válido, scan_type válidos: single ou periodic.')

        # Procura pelo ID do sensor com base no nome
        ok, engines = self.__listar_engines()
        if not ok:
            raise APIError('Não foi possível listar os engines da instância, erro: {}'.format(engines))

        engines = json.loads(engines)['engines']
        engines_encontradas = list(
            filter(lambda e: e['name'] == scan_parametrizado['sensor_nome'], engines)
        )

        if len(engines_encontradas) == 0:
            raise SensorNaoEncontrado('O sensor {} não foi encontrado na instância.'.format(scan_parametrizado['sensor_nome']))
        elif len(engines_encontradas) > 1:
            raise APIError("Foi encontrado mais de um sensor com o mesmo nome, verifique o nome novamente "
                           "antes de continuar.")

        # Procura pelo ID da política com base no nome
        ok, policies = self.__listar_politicas()
        if not ok:
            raise APIError('Não foi possível listar as políticas da instância, erro: {}'.format(policies))

        politicas = json.loads(policies)
        politicas_encontradas = list(
            filter(lambda p: p['name'] == scan_parametrizado['sensor_politica'], politicas)
        )

        if len(politicas_encontradas) == 0:
            raise PoliticaNaoEncontrada('A política {} não foi encontrada na instância.'.format(scan_parametrizado['sensor_politica']))
        elif len(politicas_encontradas) > 1:
            raise APIError("Foi encontrado mais de uma política com o mesmo nome, verifique o nome novamente")

        try:
            engine_id = engines_encontradas[0]['id']
            politica_id = politicas_encontradas[0]['id']
        except (KeyError, IndexError, TypeError) as ex:
            raise APIError("Não foi possível encontrar o ID do sensor ou da política. Erro: \'{}\'".format(ex))

        # Cria uma lista com ID's os ativos pelo endereço do ativo especificado (e.g fqdn/domain/url)
        ativos_ids = []
        for ativo in scan_parametrizado['ativos']:
            ok, detalhe = self.obter_detalhes_de_ativo(ativo)
            if not ok:
                raise APIError("Não foi possível obter detalhes do ativo {}. Erro: \'{}\'".format(ativo, detalhe))

            try:
                ativos_ids.append(json.loads(detalhe)['id'])
            except (KeyError, JSONDecodeError, TypeError) as ex:
                raise APIError("Não foi possível converter para JSON, Erro: \'{}\'".format(ex))

        # Renomeia alguns campos do dict para seu respectivo nome no payload
        scan_parametrizado['assets'] = ativos_ids
        scan_parametrizado['assetgroups'] = []
        scan_parametrizado['engine_id'] = engine_id
        scan_parametrizado['engine_policy'] = politica_id

        scan_parametrizado.pop('sensor_nome')
        scan_parametrizado.pop('sensor_politica')

        req = self.sess.post(self.endpoints['add-scan-parametrizado'], data=scan_parametrizado, timeout=self.TIMEOUT)
        if req.status_code == HTTPStatus.NO_CONTENT:
            return True, json.loads(req.text)['scan_def_id']
        else:
            return False, req.text


