import time
import requests
import platform
import yaml


def write_result(path: str, result, type_w: str = 'a', errors: int = 0):
    while errors < 3:
        try:
            with open(path, type_w, encoding='utf-8') as f:
                if type_w == 'a':
                    f.write(f'{result}\n')
                else:
                    f.write(f'{result}')
                return None

        except Exception:
            errors += 1
            time.sleep(1)
            continue


def update_monitoring(crawler: str, reply: str, status: int = 1, host: str = 'localhost'):
    try:
        _node = platform.node()

        if _node in 'vm-additional-services02p.tcsbank.ru':
            host = 'localhost:8100'
        elif _node in 'm1-crawlig-portal-1.tcsbank.ru':
            host = 'localhost'

        requests.get(f'http://{host}/api/v1/crawlers/reply?'
                     f'crawler_name={crawler}&status={status}&reply={reply}', timeout=0.1)
    except Exception:
        pass


def strip(text):
    return text.replace('\n', '').strip().replace(u'\xa0', ' ').replace('  ', '')


def find(text, start, end):
    start_idx = text.find(start)
    if start_idx < 1:
        return ''

    text = text[start_idx + len(start):]
    end_idx = text.find(end)
    if end_idx < 1:
        return ''

    text = text[:end_idx]
    return text


phone_codes = [
    '388', '385', '416', '814', '818', '851', '472', '483', '302', '492', '844', '817', '820', '844', '473', '426',
    '493', '395', '866', '401', '484', '415', '878', '384', '833', '494', '861', '862', '391', '352', '471', '812',
    '813', '474', '413', '495', '495', '496', '815', '818', '831', '816', '383', '381', '353', '486', '841', '342',
    '423', '811', '877', '347', '301', '872', '873', '847', '814', '821', '836', '834', '867', '843', '855', '394',
    '341', '390', '835', '411', '863', '491', '846', '848', '845', '424', '343', '481', '863', '865', '879', '475',
    '482', '382', '487', '345', '346', '842', '421', '351', '871', '302', '427', '349'
]


def format_phone(phone: str) -> int:
    phone = ''.join([d for d in phone if d.isdigit()])
    if len(phone) == 11:
        if phone.startswith('8'):
            formatted_phone = int(f'7{phone[1:]}')
        elif phone.startswith('7'):
            formatted_phone = int(phone)
        else:
            formatted_phone = 0
    elif len(phone) == 10:
        if phone.startswith('9'):
            formatted_phone = int(f'7{phone}')
        elif any([phone.startswith(_code) for _code in phone_codes]):
            formatted_phone = int(f'7{phone}')
        else:
            formatted_phone = ''
    else:
        formatted_phone = ''
    if formatted_phone != '':
        return int(formatted_phone)
    else:
        return 0


def read_config(path: str, method: str = None, key: str = None) -> dict:
    try:
        with open(path, 'r') as yml_file:
            _config = yaml.load(yml_file)
            print('_config', _config)
            if method is not None:
                if method in _config:
                    if key is None:
                        return _config[method]
                    else:
                        return _config[method][key] if key in _config[method] else None
            else:
                return _config

    except Exception as ex:
        print(ex)

    return dict()
