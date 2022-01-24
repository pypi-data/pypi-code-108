import requests
import logging

logger = logging.getLogger()


def registerWarn(message):
    logger.warning(message)
    post_message(message)


def registerErro(erro):
    logger.error(erro)
    post_message(erro)


def post_message(message):
    dct_body = {
        'text': message,
        'channel': '#src'
    }

    url = 'https://hooks.slack.com/services/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'

    try:
        headers = {'Content-type': 'application/json',
                   'Accept': 'text/html'
                   }
        response = requests.post(url, json=dct_body, headers=headers)

        if response.status_code >= 200 and response.status_code <= 299:
            logger.info('Envio de mensagem para o slack')
        else:
            msg = 'Erro ao enviar slack ' + \
                response.status_code + ' ' + dct_body
            logger.error(msg)
            response.raise_for_status()

    except Exception as ex:
        logger.error(str(ex), exc_info=True)
