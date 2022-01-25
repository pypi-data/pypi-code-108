from pytz import timezone
from time import sleep
from datetime import datetime
from requests.exceptions import ConnectionError, ConnectTimeout, ReadTimeout
from .request_base import mindset_request

def aguarda_api_subir():
    api_online = False
    while not api_online:
        agora = datetime.now(timezone('America/Sao_Paulo'))
        try:
            api_online = mindset_request('GET', '').ok
        except (ConnectionError, ConnectTimeout, ReadTimeout):
            print((
                f'{agora}: Não foi possível conectar com a API MINDSET. '
                'Uma nova tentativa será efeuada em 5 segundos.'
            ))
            sleep(5)
    print(f'{agora}: Conexão estabelecida. Continuando execução...')

def response_logger(response, msg_alternativa=''):
    agora = datetime.now(tz=timezone('America/Sao_Paulo'))
    log_erro = '{agora}: A requisição para {url} falhou. Status {status_code}.'
    if not response.ok:
        print(log_erro.format(**{**locals(), **response.__dict__}))
    elif response.ok and msg_alternativa:
        print(f'{agora}: {msg_alternativa}')


def format_datetime(data: str):
    if data and len(data) == 19:
        data += '.0'
    return datetime.strptime(data, '%Y-%m-%dT%H:%M:%S.%f')
