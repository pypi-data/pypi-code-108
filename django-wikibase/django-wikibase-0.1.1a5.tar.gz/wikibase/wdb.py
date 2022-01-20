from binascii import hexlify
from functools import partial
from itertools import chain
from json import dumps, loads
from mimetypes import MimeTypes
from os import stat, urandom
from os.path import exists
from time import sleep
from typing import Any, ByteString, Dict, List, Tuple
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from django.db.models.fields.files import FieldFile, ImageFieldFile
from django.core.files import File

from .ir.cmd import Cmd
from .ir.django_model import DjangoModel
from .ir.django_property import DjangoProperty
from .loggable import Loggable

charset_map = dict()


class WbDatabase:
    SHRT_MIN = 1
    SHRT_MAX = 1
    INT_MIN = 1
    INT_MAX = 1
    LONG_MIN = 1
    LONG_MAX = 1

    ISOLATION_LEVEL_READ_COMMITED = 1

    _BASE_URL = '_base_url'
    _MEDIAWIKI_VERSION = '_mediawiki_version'
    _INSTANCE_OF = 'instance of'
    _SUBCLASS_OF = 'subclass of'
    _DJANGO_MODEL = 'django model'
    _DJANGO_NAMESPACE = 'django namespace'
    _DJANGO_APPLICATION = 'django application'
    _DJANGO_FIELD = 'django field'
    _DJANGO_SEQUENCE = 'django sequence'
    _DJANGO_NEXT_ID = 'django next id'
    _DJANGO_MODELS = '_django_models'
    _SPARQL_ENDPOINT = '_sparql_endpoint'
    _WIKIBASE_PROPERTIES = '_wikibase_properties'
    _WIKIBASE_CREDENTIALS = '_wikibase_credentials'

    class Error:
        ...

    class DatabaseError(BaseException):
        ...

    class IntegrityError(BaseException):
        ...

    class OperationalError(BaseException):
        ...

    class DataError(BaseException):
        ...

    class InternalError(BaseException):
        ...

    class NotSupportedError(BaseException):
        ...

    class InterfaceError(BaseException):
        ...

    class ProgrammingError(BaseException):
        ...

    @staticmethod
    def get_property_type_for_django_field(field: DjangoProperty) -> str:
        django_field_type = field['property_type']
        if django_field_type == 'CharField':
            return 'string'
        if django_field_type == 'AutoField':
            return 'quantity'
        if django_field_type == 'BigAutoField':
            return 'quantity'
        if django_field_type == 'ForeignKey':
            return 'wikibase-item'
        if django_field_type == 'DecimalField':
            return 'quantity'
        if django_field_type == 'IntegerField':
            return 'quantity'
        if django_field_type == 'PositiveSmallIntegerField':
            return 'quantity'
        if django_field_type == 'DateTimeField':
            return 'string'
        if django_field_type == 'DateField':
            return 'time'
        if django_field_type == 'FileField':
            return 'string'
        if django_field_type == 'ImageField':
            return 'string'
        if django_field_type == 'FloatField':
            return 'quantity'
        if django_field_type == 'BooleanField':
            # Mapping to snaks: novalue/somevalue
            return 'string'
        if django_field_type == 'EmailField':
            # Mapping to snaks: novalue/somevalue
            return 'string'
        if django_field_type == 'TextField':
            # Mapping to snaks: novalue/somevalue
            return 'string'
        raise WbDatabase.InternalError(
            f'Sorry I can\'t recognize type: {django_field_type} for field {field}.')

    @staticmethod
    def connect(charset: str = 'utf8', url: str = '',
                bot_username: str = '', bot_password: str = '',
                instance_of_property_id: int = None,
                subclass_of_property_id: int = None,
                django_model_item_id: int = None,
                wdqs_sparql_endpoint: str = None,
                django_namespace: str = None):
        return WbDatabaseConnection(charset, url,
                                    bot_username, bot_password,
                                    instance_of_property_id,
                                    subclass_of_property_id,
                                    django_model_item_id,
                                    wdqs_sparql_endpoint,
                                    django_namespace)


class WbCredentials(dict):

    def __init__(self, bot_username: str, bot_password: str):
        super().__init__(bot_username=bot_username, bot_password=bot_password)


class WbLink(dict):

    def __init__(self, id: int, entity_type: str, base_url: str):
        super().__init__(id=id, entity_type=entity_type,
                         url=f'{base_url}{self._entity_prefix(entity_type)}{id}')

    @staticmethod
    def _entity_prefix(entity_type: str) -> str:
        if not entity_type:
            return None
        first_letter = str(entity_type).upper()[:1]
        if first_letter == 'I':
            return 'Q'
        if first_letter == 'P':
            return 'P'
        raise WbDatabase.InternalError(
            f'Sorry I can\'t recognize entity type: {entity_type}')

    def get_entity_id(self) -> str:
        return f'{self._entity_prefix(self["entity_type"])}{self["id"]}'


_1X1_JPG = bytearray.fromhex('''
ffd8 ffe0 0010 4a46 4946 0001 0100 0001
0001 0000 ffdb 0043 0003 0202 0202 0203
0202 0203 0303 0304 0604 0404 0404 0806
0605 0609 080a 0a09 0809 090a 0c0f 0c0a
0b0e 0b09 090d 110d 0e0f 1010 1110 0a0c
1213 1210 130f 1010 10ff c000 0b08 0001
0001 0101 1100 ffc4 0014 0001 0000 0000
0000 0000 0000 0000 0000 0009 ffc4 0014
1001 0000 0000 0000 0000 0000 0000 0000
0000 ffda 0008 0101 0000 3f00 2a9f ffd9
''')


class WbApi():

    def __init__(self, url: str, charset: str = 'utf-8', wdqs_sparql_endpoint: str = None):
        super().__init__()
        self.url = url
        self.charset = charset
        self.wdqs_sparql_endpoint = wdqs_sparql_endpoint if wdqs_sparql_endpoint else f'{url}/sparql'
        self.cookies = None
        self.session = None

    def _retry(self, countdown: int, request: Request) -> dict:
        search_result = {}
        for i in range(0, countdown):
            if self.session:
                request.headers['Cookie'] = self.session
            response = urlopen(request)
            search_result = loads(response.read().decode(self.charset))
            if 'error' in search_result and 'code' in search_result['error'] and \
                    (search_result['error']['code'] == 'failed-save' or search_result['error']['code'] == 'no-automatic-entity-id'):
                sleep(1.27 ** i)
                continue
            # Handle session
            if 'Set-Cookie' in response.headers:
                self.cookies = response.headers['Set-Cookie']
                if 'session' in response.headers['Set-Cookie']:
                    self.session = str(self.cookies).split(';')[0]
            return search_result
        raise WbDatabase.InternalError(
            f'Countdown exceeds limit {countdown}. The last search result is {search_result}.')

    def mediawiki_info(self):
        return loads(urlopen(
            f'{self.url}/api.php?action=query&meta=siteinfo&format=json').read().decode(self.charset))

    def search_items(self, query):
        if 'label' in query:
            label_search_string = query['label']
            search_result = loads(urlopen(
                f'{self.url}/api.php?action=wbsearchentities&search={quote_plus(label_search_string)}&language=en&type=item&format=json').read().decode(self.charset))
            return search_result['search']
        raise WbDatabase.InternalError('Only search by label implemented')

    def search_properties(self, query):
        if 'label' in query:
            label_search_string = query['label']
            search_result = loads(urlopen(
                f'{self.url}/api.php?action=wbsearchentities&search={quote_plus(label_search_string)}&language=en&type=property&format=json').read().decode(self.charset))
            return search_result['search']
        raise WbDatabase.InternalError('Only search by label implemented')

    def new_item(self, data):
        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']
        post_request_body = f'token={quote_plus(csrf_token)}'
        search_result = self._retry(20, Request(
            f'{self.url}/api.php?action=wbeditentity&new=item&data={quote_plus(dumps(data))}&format=json', method='POST', data=post_request_body.encode('utf-8')))
        return search_result['entity']

    def new_property(self, data):
        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']
        post_request_body = f'token={quote_plus(csrf_token)}'
        search_result = self._retry(20, Request(
            f'{self.url}/api.php?action=wbeditentity&new=property&data={quote_plus(dumps(data))}&format=json', method='POST', data=post_request_body.encode('utf-8')))
        return search_result['entity']

    def get_item_claims(self, numeric_entity_id: int, numeric_property_id: int = None):
        response = urlopen(Request(
            f'{self.url}/api.php?action=wbgetclaims&entity=Q{numeric_entity_id}&format=json' +
            (f'&poperty=P{numeric_property_id}' if numeric_property_id else ''),
            method='GET'))
        search_result = loads(response.read().decode(self.charset))
        return search_result['claims']

    def get_entities(self, wb_links: List[WbLink]) -> List[dict]:
        if not wb_links:
            return []
        entities_ids = '|'.join([wb_link.get_entity_id()
                                for wb_link in wb_links])
        response = urlopen(Request(
            f'{self.url}/api.php?action=wbgetentities&ids={entities_ids}&format=json',
            method='GET'))
        search_result = loads(response.read().decode(self.charset))
        return search_result['entities'].values()

    def new_claim(self, entity_type: str, entity_id: int, property_id: int, value: Any) -> dict:
        entity_id = f'{WbLink._entity_prefix(entity_type)}{entity_id}'
        snak_type = 'value' if value else 'novalue'

        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']
        post_request_body = f'token={quote_plus(csrf_token)}'
        search_result = self._retry(20, Request(
            f'{self.url}/api.php?action=wbcreateclaim&entity={entity_id}&property=P{property_id}&snaktype={snak_type}&format=json' +
            (f'&value={quote_plus(dumps(value))}' if value else ''), method='POST', data=post_request_body.encode('utf-8')))
        return search_result['claim']

    def get_and_increase_value(self, claim_id: str, increase_step: int) -> int:
        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']

        response = urlopen(Request(
            f'{self.url}/api.php?action=wbgetclaims&claim={claim_id}&format=json',
            method='GET'))
        search_result = loads(response.read().decode(self.charset))
        for claims in search_result['claims'].values():
            value = claims[0]['mainsnak']['datavalue']['value']
            result = int(value['amount'])
            value['amount'] = result + increase_step
            post_request_body = f'token={quote_plus(csrf_token)}'
            self._retry(20, Request(
                f'{self.url}/api.php?action=wbsetclaimvalue&claim={claim_id}&snaktype=value&&value={quote_plus(dumps(value))}&format=json', method='POST', data=post_request_body.encode('utf-8')))

            return result

        raise WbDatabase.InternalError(
            f'Sorry, I can\'t found claim {claim_id} value')

    def set_integer_value_if_less_then_current_value(self, claim_id: str, value: int) -> int:
        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']

        response = urlopen(Request(
            f'{self.url}/api.php?action=wbgetclaims&claim={claim_id}&format=json',
            method='GET'))
        search_result = loads(response.read().decode(self.charset))
        for claims in search_result['claims'].values():
            datavalue = claims[0]['mainsnak']['datavalue']['value']
            if int(datavalue['amount']) >= value:
                return int(datavalue['amount'])
            datavalue['amount'] = value
            post_request_body = f'token={quote_plus(csrf_token)}'
            self._retry(20, Request(
                f'{self.url}/api.php?action=wbsetclaimvalue&claim={claim_id}&snaktype=value&&value={quote_plus(dumps(datavalue))}&format=json', method='POST', data=post_request_body.encode('utf-8')))

            return value

        raise WbDatabase.InternalError(
            f'Sorry, I can\'t found claim {claim_id} value')

    def get_claim_value(self, claim_id: str) -> Dict:
        response = urlopen(Request(
            f'{self.url}/api.php?action=wbgetclaims&claim={claim_id}&format=json',
            method='GET'))
        search_result = loads(response.read().decode(self.charset))
        for claims in search_result['claims'].values():
            return claims[0]['mainsnak']['datavalue']['value']

        raise WbDatabase.InternalError(
            f'Sorry, I can\'t found claim {claim_id} value')

    @staticmethod
    def empty_content(guessed_mime_types: Tuple) -> ByteString:
        if guessed_mime_types[0] == 'text/plain':
            return b'\x20'
        if guessed_mime_types[0] == 'image/jpeg':
            return _1X1_JPG
        raise WbDatabase.InternalError(
            f'Sorry, I can\'t generate empty content for the {guessed_mime_types}')

    def read_chunks(self, file_object, chunk_size):
        '''Return the next chunk of the file'''

        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    @staticmethod
    def _build_part(item, sep_boundary):
        key, values = item
        title = '\nContent-Disposition: form-data; name="%s"' % key
        # handle multiple entries for the same name
        if not isinstance(values, list):
            values = [values]
        for value in values:
            if isinstance(value, tuple):
                title += '; filename="%s"' % value[0]
                value = value[1]
            else:
                value = str(value).encode('utf-8', 'surrogateescape')
            yield sep_boundary
            yield title.encode('utf-8', 'surrogateescape')
            yield b"\n\n"
            yield value
            if value and value[-1:] == b'\r':
                yield b'\n'  # write an extra newline (lurve Macs)

    @classmethod
    def encode_multipart_formdata(cls, data):
        '''
        Build up the MIME payload for the POST data
        '''
        boundary = f'--------{hexlify(urandom(16)).decode("ascii")}'
        sep_boundary = b'\n--' + boundary.encode('ascii')
        end_boundary = sep_boundary + b'--'
        end_items = end_boundary, b"\n",
        builder = partial(
            cls._build_part,
            sep_boundary=sep_boundary,
        )
        part_groups = map(builder, data.items())
        parts = chain.from_iterable(part_groups)
        body_items = chain(parts, end_items)
        content_type = 'multipart/form-data; boundary=%s' % boundary
        return b''.join(body_items), content_type

    def login(self, credentials: WbCredentials) -> Dict:
        login_token_response = self._retry(20,
                                           Request(
                                               f'{self.url}/api.php?action=query&meta=tokens&type=login&format=json',
                                               method='GET'))
        data, content_type = self.encode_multipart_formdata({
            'action': 'login',
            'lgname':  credentials['bot_username'],
            'lgpassword': credentials['bot_password'],
            'format': 'json',
            'lgtoken': login_token_response['query']['tokens']['logintoken']
        })
        login_response = self._retry(20,
                                     Request(
                                         f'{self.url}/api.php',
                                         method='POST',
                                         data=data,
                                         headers={'Content-Type': content_type}))
        if not ('login' in login_response) or login_response['login']['result'] != 'Success':
            raise WbDatabase.InternalError(
                f'Sorry, I can\'t login as {credentials["bot_username"]}')
        return login_response

    def upload_file_in_chunks(self, csrf_token: str, file_name: str,
                              file_object, file_size: int,
                              file_comment: str = None, chunk_size: int = 65535):
        '''Send multiple post requests to upload a file in chunks using `stash` mode.
        Stash mode is used to build a file up in pieces and then commit it at the end
        '''

        # from mimetypes import MimeTypes
        # guessed_mime_type = MimeTypes().guess_type(file_path)

        if file_size == 0:
            # Empty file is not upload to the mediawiki
            return

        chunks = self.read_chunks(file_object, chunk_size)
        chunk = next(chunks)

        index = 0
        # Parameters for the first chunk
        params = {
            'action': 'upload',
            'stash': 1,
            'filename': file_name,
            'filesize': file_size,
            'offset': 0,
            'format': 'json',
            'token': csrf_token,
            'ignorewarnings': 1,
            'chunk': ('{}.jpg'.format(index), chunk, 'multipart/form-data')
        }
        data, content_type = self.encode_multipart_formdata(params)
        chunk_upload_result = self._retry(20,
                                          Request(
                                              f'{self.url}/api.php',
                                              method='POST',
                                              data=data,
                                              headers={'Content-Type': content_type, 'Content-Disposition': '{}.jpg'.format(index)}))
        index += 1

        # Pass the filekey parameter for second and further chunks
        for chunk in chunks:
            params = {
                'action': 'upload',
                'stash': 1,
                'offset': chunk_upload_result['upload']['offset'],
                'filename': file_name,
                'filesize': file_size,
                'filekey': chunk_upload_result['upload']['filekey'],
                'format': 'json',
                'token': csrf_token,
                'ignorewarnings': 1,
                'chunk': ('{}.jpg'.format(index), chunk, 'multipart/form-data')
            }
            data, content_type = self.encode_multipart_formdata(params)
            chunk_upload_result = self._retry(20,
                                              Request(
                                                  f'{self.url}/api.php',
                                                  method='POST',
                                                  data=data,
                                                  headers={'Content-Type': content_type}))
            index += 1

        # Final upload using the filekey to commit the upload out of the stash area
        params = {
            'action': 'upload',
            'filename': file_name,
            'filekey': chunk_upload_result['upload']['filekey'],
            'format': 'json',
            'comment': file_comment,
            'token': csrf_token,
        }

        data, content_type = self.encode_multipart_formdata(params)
        chunk_upload_result = self._retry(20,
                                          Request(
                                              f'{self.url}/api.php',
                                              method='POST',
                                              data=data,
                                              headers={'Content-Type': content_type}))
        return chunk_upload_result

    def upload_file(self, name: str, file_path: str,
                    credentials: WbCredentials) -> Dict:

        self.login(credentials)

        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']
        # post_request_body = f'token={quote_plus(csrf_token)}'

        file_size = stat(file_path).st_size
        with open(file_path, 'rb') as file_object:
            return self.upload_file_in_chunks(csrf_token, name, file_object, file_size)

    def upload_file(self, name: str, django_file: File,
                    credentials: WbCredentials) -> Dict:

        self.login(credentials)

        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']
        # post_request_body = f'token={quote_plus(csrf_token)}'

        with django_file:
            return self.upload_file_in_chunks(csrf_token, name, django_file, django_file.size)

    def upload_empty_file(self, name: str,
                          credentials: WbCredentials) -> Dict:

        guessed_mime_type = MimeTypes().guess_type(name)

        self.login(credentials)

        retrieve_csrf_token = self._retry(20, Request(
            f'{self.url}/api.php?action=query&meta=tokens&format=json'))
        csrf_token = retrieve_csrf_token['query']['tokens']['csrftoken']
        data, content_type = self.encode_multipart_formdata({
            'action': 'upload',
            'filename': name,
            'format': 'json',
            'token': csrf_token,
            'ignorewarnings': 1,
            'file': (name, self.empty_content(guessed_mime_type), 'multipart/form-data')
        })

        upload_result = self._retry(20,
                                    Request(
                                        f'{self.url}/api.php',
                                        method='POST',
                                        data=data,
                                        headers={'Content-Type': content_type}))

        return upload_result

    def execute_sparql_query(self, sparql_query: str) -> Dict:
        execute_result = self._retry(20,
                                     Request(
                                         f'{self.wdqs_sparql_endpoint}?format=json',
                                         method='POST',
                                         data=sparql_query.encode('utf-8'),
                                         headers={
                                             'Content-Type': 'application/sparql-query',
                                             'Accept': 'application/sparql-results+json'
                                         }))

        return execute_result


class WbCursor(Loggable):

    def __init__(self, django_namespace: str, wikibase_info: dict, api: WbApi):
        super().__init__()
        self.wikibase_info = wikibase_info
        self.django_namespace = django_namespace
        self.api = api
        self.result = []
        self._position = 0

    def close(self):
        print('close')

    def _get_models(self, cmd: Cmd):
        if cmd['cmd'] == 'add_property':
            return (cmd['data']['model'], ) if not cmd['data']['property']['related_models'] else (cmd['data']['model'], cmd['data']['property']['related_models'][0])
        if cmd['cmd'] == 'add_items':
            return (cmd['data']['model'], )
        return None

    def get_or_create_item_if_not_found_by_name(self, item_name: str, data: dict = None) -> Dict:
        entities = self.api.search_items({'label': item_name})
        if len(entities) == 1:
            return entities[0]
        labels_data = {'labels': {
            'en': {'language': 'en', 'value': item_name}}}
        entity_data = labels_data if not data else {**labels_data, **data}
        if len(entities) == 0:
            entity = self.api.new_item(entity_data)
            return entity
        raise WbDatabase.InternalError(
            f'The entity {item_name} has another one (i.e. not unique)')

    def get_or_create_property_if_not_found_by_name(self, property_name: str, data_type_name: str) -> Dict:
        # TODO: add claims if we'll create the new property
        entities = self.api.search_properties({'label': property_name})
        if len(entities) == 1:
            return entities[0]
        if len(entities) == 0:
            entity = self.api.new_property(
                {'labels': {'en': {'language': 'en', 'value': property_name}}, 'datatype': data_type_name})
            return entity
        raise WbDatabase.InternalError(
            f'The property {property_name} has another one (i.e. not unique)')

    def _wb_link(self, snak: dict) -> DjangoProperty:
        return WbLink(
            snak['mainsnak']['datavalue']['value']['numeric-id'],
            snak['mainsnak']['datavalue']['value']['entity-type'],
            self.wikibase_info[WbDatabase._BASE_URL])

    def _general_model_label(self, model: DjangoModel):
        application = model['application']
        return f'{application}{" for " + self.django_namespace if self.django_namespace else ""}'

    def _model_label(self, model: DjangoModel):
        model_name = model['type'].split('.')[-1]
        return f'{model_name} in {self._general_model_label(model)}'

    def _instance_of_model_label(self, model: DjangoModel, id: int):
        model_name = model['type'].split('.')[-1]
        return f'{model_name}:{id} in {self._general_model_label(model)}'

    def _wikibase_property(self, wikibase_property_id: int) -> Dict:
        cached_wikibase_property = self.wikibase_info[WbDatabase._WIKIBASE_PROPERTIES].get(
            wikibase_property_id)
        if cached_wikibase_property:
            return cached_wikibase_property
        for wikibase_property in self.api.get_entities(
                [WbLink(wikibase_property_id, 'property', self.wikibase_info[WbDatabase._BASE_URL])]):
            self.wikibase_info[WbDatabase._WIKIBASE_PROPERTIES][wikibase_property_id] = wikibase_property
            return wikibase_property
        raise WbDatabase.InternalError(
            f'Sorry, I can\'t find wikibase_property  by id {wikibase_property_id}')

    def _claim_item_value(self, numeric_property_id: int, item: Dict = None, numeric_item_id: int = None) -> Dict:
        if item is None and numeric_item_id is None:
            return {
                'mainsnak': {
                    'snaktype': 'novalue',
                    'property': f'P{numeric_property_id}',
                },
                'type': 'statement',
                'rank': 'normal'
            }

        return {
            'mainsnak': {
                'snaktype': 'value',
                'property': f'P{numeric_property_id}',
                'datavalue': {
                            'value': {
                                'entity-type': 'item',
                                'numeric-id': int(item['id'][1:]) if item else numeric_item_id},
                            'type': 'wikibase-entityid'}
            },
            'type': 'statement',
            'rank': 'normal'
        }

    def _claim_string_value(self, numeric_property_id: int, value: str = None) -> Dict:
        if value is None or value == '':
            return {
                'mainsnak': {
                    'snaktype': 'novalue',
                    'property': f'P{numeric_property_id}',
                },
                'type': 'statement',
                'rank': 'normal'
            }

        return {
            'mainsnak': {
                'snaktype': 'value',
                'property': f'P{numeric_property_id}',
                'datavalue': {
                            'value': value,
                            'type': 'string'}
            },
            'type': 'statement',
            'rank': 'normal'
        }

    def _claim_quantity_value(self, numeric_property_id: int, value: None) -> Dict:
        if value is None or value == '':
            return {
                'mainsnak': {
                    'snaktype': 'novalue',
                    'property': f'P{numeric_property_id}',
                },
                'type': 'statement',
                'rank': 'normal'
            }

        return {
            'mainsnak': {
                'snaktype': 'value',
                'property': f'P{numeric_property_id}',
                'datavalue': {
                            'value': {
                                'amount': value,
                                'unit': '1'
                            },
                    'type': 'quantity'}
            },
            'type': 'statement',
            'rank': 'normal'
        }

    def _check_or_create_model(self, model: DjangoModel):

        # Check general model
        general_model_label = self._general_model_label(model)
        if not(general_model_label in self.wikibase_info):
            # get application django model it contains general info
            application_model = self.get_or_create_item_if_not_found_by_name(
                general_model_label,
                data={'claims': [
                    self._claim_item_value(
                        self.wikibase_info[WbDatabase._SUBCLASS_OF]['id'],
                        numeric_item_id=self.wikibase_info[WbDatabase._DJANGO_MODEL]['id']),
                    # self._claim_value(
                    #     self.wikibase_info[WbDatabase._DJANGO_SEQUENCE]['id'],
                    #     numeric_item_id=...),
                    self._claim_string_value(
                        self.wikibase_info[WbDatabase._DJANGO_APPLICATION]['id'],
                        model['application']),
                    self._claim_string_value(
                        self.wikibase_info[WbDatabase._DJANGO_NAMESPACE]['id'],
                        self.django_namespace),
                ]})

            application_model_claims = self.api.get_item_claims(
                int(application_model['id'][1:]))

            django_sequence_property_id = self.wikibase_info[WbDatabase._DJANGO_SEQUENCE]['id']
            if not (f'P{django_sequence_property_id}' in application_model_claims):
                application_model_claims[f'P{django_sequence_property_id}'] = [
                ]
            application_model_sequences = [self._wb_link(property_value) for property_value in application_model_claims[f'P{django_sequence_property_id}']] \
                if f'P{django_sequence_property_id}' in application_model_claims else []

            application_model['claims'] = application_model_claims
            self.wikibase_info[general_model_label] = application_model

        # Check concrete model
        concrete_model_label = self._model_label(model)
        if not(concrete_model_label in self.wikibase_info):

            concrete_model = self.get_or_create_item_if_not_found_by_name(
                concrete_model_label,
                data={'claims': [
                    self._claim_item_value(
                        self.wikibase_info[WbDatabase._SUBCLASS_OF]['id'],
                        self.wikibase_info[general_model_label]),
                    # self._claim_value(
                    #     self.wikibase_info[WbDatabase._DJANGO_SEQUENCE]['id'],
                    #     numeric_item_id=...),
                    self._claim_string_value(
                        self.wikibase_info[WbDatabase._DJANGO_APPLICATION]['id'],
                        model['application']),
                    self._claim_string_value(
                        self.wikibase_info[WbDatabase._DJANGO_NAMESPACE]['id'],
                        self.django_namespace),
                ]})
            concrete_model_id = int(concrete_model['id'][1:])

            django_field_property_id = self.wikibase_info[WbDatabase._DJANGO_FIELD]['id']
            # below is the request existed claims or add a placeholder for them
            concrete_model_claims = self.api.get_item_claims(concrete_model_id)
            if not (f'P{django_field_property_id}' in concrete_model_claims):
                concrete_model_claims[f'P{django_field_property_id}'] = []
            concrete_model_properties = [self._wb_link(property_value) for property_value in concrete_model_claims[f'P{django_field_property_id}']] \
                if f'P{django_field_property_id}' in concrete_model_claims else []

            concrete_model_fields = {
                p['labels']['en']['value'] for p in self.api.get_entities(concrete_model_properties)}

            # Create/Update properties
            for field in model['fields']:
                related_model_label = self._model_label(
                    field['related_models'][0]) if field['related_models'] else None
                related_models = f' to {related_model_label}' if related_model_label else ''
                property_type_name = f'{field["property_type"]}{related_models}'
                property_name = f'{field["property_name"]} type {property_type_name}'

                if property_name in concrete_model_fields:
                    continue

                # Create claim cause missed
                wikibase_property = self.get_or_create_property_if_not_found_by_name(
                    property_name, WbDatabase.get_property_type_for_django_field(field))
                wikibase_property_id = int(wikibase_property['id'][1:])
                self.wikibase_info[WbDatabase._WIKIBASE_PROPERTIES][wikibase_property_id] = wikibase_property

                claim = self.api.new_claim('item', concrete_model_id, django_field_property_id, {
                                           'entity-type': 'property', 'numeric-id': wikibase_property_id})
                concrete_model_claims[f'P{django_field_property_id}'].append(
                    claim)

            # default sequence for the concrete model
            django_next_id_property_id = self.wikibase_info[WbDatabase._DJANGO_NEXT_ID]['id']
            if not (f'P{django_next_id_property_id}' in concrete_model_claims):
                claim = self.api.new_claim('item', concrete_model_id, django_next_id_property_id, {
                                           'amount': 1, 'unit': '1'})
                concrete_model_claims[f'P{django_next_id_property_id}'] = [
                    claim]

            concrete_model['claims'] = concrete_model_claims
            self.wikibase_info[concrete_model_label] = concrete_model
            # Store table link
            self.wikibase_info[WbDatabase._DJANGO_MODELS][model['table_name']] = model

            return concrete_model

        return self.wikibase_info[concrete_model_label]

    def _django_field_name_from_wikibase_property_name(self, wikibase_property_name: str) -> str:
        result = wikibase_property_name.strip()
        return result[:result.index(' ')]

    def _convert_to_snak_and_handle_value(self, wikibase_property_id, wikibase_datatype: str, django_field_value: Any) -> Dict:
        # Snak template
        if django_field_value is None or \
                str(django_field_value) == '':
            return {
                'snaktype': 'novalue',
                'property': f'P{wikibase_property_id}'
            }
        result = {
            'snaktype': 'value',
            'property': f'P{wikibase_property_id}',
            'datavalue': {
                'value': None,
                'type': self._replace_unsupported_types(wikibase_datatype)}
        }

        # Handle value
        if wikibase_datatype == 'string':
            if isinstance(django_field_value, FieldFile):  # FileField
                field_value: FieldFile = django_field_value
                # Upload file to the mediawiki storage
                try:
                    self.api.upload_file(field_value.name, field_value.file,
                                         self.wikibase_info[WbDatabase._WIKIBASE_CREDENTIALS])
                except FileNotFoundError as e:
                    self.error(e)
            if isinstance(django_field_value, ImageFieldFile):  # ImageField
                field_value: ImageFieldFile = django_field_value
                # Upload file to the mediawiki storage
                try:
                    self.api.upload_file(field_value.name, field_value.file,
                                         self.wikibase_info[WbDatabase._WIKIBASE_CREDENTIALS])
                except FileNotFoundError as e:
                    self.error(e)
            result['datavalue']['value'] = str(django_field_value)
        elif wikibase_datatype == 'commonsMedia':
            # TODO: upload to the https://commons.wikipedia.org
            result['datavalue']['value'] = django_field_value.name
        elif wikibase_datatype == 'quantity':
            result['datavalue']['value'] = {
                'amount': float(django_field_value),
                'unit': '1'
            }
        elif wikibase_datatype == 'wikibase-item':
            result['datavalue']['value'] = {
                'numeric-id': int(django_field_value),
                'entity-type': 'item'
            }
        elif wikibase_datatype == 'time':
            result['datavalue']['value'] = {
                'time': '+' + django_field_value.replace(tzinfo=None, hour=0, minute=0, second=0).isoformat('T', 'seconds') + 'Z',
                'timezone': 0,
                'before': 0,
                'after': 0,
                'precision': 11,
                'calendarmodel': 'http://www.wikidata.org/entity/Q1985727'
            }
        else:
            raise WbDatabase.InternalError(
                f'Sorry, I can\'t convert django_field_value {django_field_value} to wikibase_datatype {wikibase_datatype}')

        return result

    def _replace_unsupported_types(self, wikibase_type: str) -> str:
        if wikibase_type == 'commonsMedia':
            return 'string'
        if wikibase_type == 'wikibase-item':
            return 'wikibase-entityid'
        return wikibase_type

    def _claims_make(self, claims: List, value: Dict) -> List:
        result = []
        for claim in claims:
            wikibase_property_id = claim['mainsnak']['datavalue']['value']['numeric-id']
            wikibase_property = self._wikibase_property(wikibase_property_id)
            wikibase_property_name = wikibase_property[
                'label'] if 'label' in wikibase_property else wikibase_property['labels']['en']['value']
            django_field_name = self._django_field_name_from_wikibase_property_name(
                wikibase_property_name)
            if django_field_name in value:
                result.append({
                    'mainsnak': self._convert_to_snak_and_handle_value(wikibase_property_id, wikibase_property['datatype'], value[django_field_name]),
                    'type': 'statement',
                    'rank': 'normal'
                })
        return result

    def _get_autofield_numeric_property_id_and_django_autofield_name_or_none(self, model: DjangoModel, concrete_model: Dict) -> int:
        django_field_property_id = self.wikibase_info[WbDatabase._DJANGO_FIELD]['id']
        for field in model['fields']:
            if field['property_type'] in {'AutoField', 'BigAutoField'}:
                for claim in concrete_model['claims'][f'P{django_field_property_id}']:
                    wikibase_property_id = claim['mainsnak']['datavalue']['value']['numeric-id']
                    wikibase_property = self._wikibase_property(
                        wikibase_property_id)
                    wikibase_property_name = wikibase_property[
                        'label'] if 'label' in wikibase_property else wikibase_property['labels']['en']['value']
                    django_field_name = self._django_field_name_from_wikibase_property_name(
                        wikibase_property_name)
                    if django_field_name == field['attribute_name']:
                        return wikibase_property_id, django_field_name
        return None, None

    def _get_wikibase_numeric_property_id_or_none(self, model: DjangoModel, property_name: str) -> int:
        concrete_model = self._check_or_create_model(model)
        django_field_property_id = self.wikibase_info[WbDatabase._DJANGO_FIELD]['id']
        for field in model['fields']:
            if field['property_name'] == property_name:
                for claim in concrete_model['claims'][f'P{django_field_property_id}']:
                    wikibase_property_id = claim['mainsnak']['datavalue']['value']['numeric-id']
                    wikibase_property = self._wikibase_property(
                        wikibase_property_id)
                    wikibase_property_name = wikibase_property[
                        'label'] if 'label' in wikibase_property else wikibase_property['labels']['en']['value']
                    django_field_name = self._django_field_name_from_wikibase_property_name(
                        wikibase_property_name)
                    if django_field_name == field['attribute_name']:
                        return wikibase_property_id
        return None

    def _convert_values(self, values_map: dict, keys: list) -> Tuple:
        return tuple([values_map[key]['value'] for key in keys])

    def _tuples(self, vars: list, bindings: list) -> List[Tuple]:
        return [self._convert_values(t, vars) for t in bindings]

    def _add_property(self, cmd: Cmd, params: list):
        self.debug('_add_property %s with %s', cmd, params)

    def _alter_property(self, cmd: Cmd, params: list):
        self.debug('_alter_property %s with %s', cmd, params)

    def _add_constraints(self, cmd: Cmd, params: list):
        self.debug('_add_constraints %s with %s', cmd, params)

    def _field_indexes(self, cmd: Cmd, params: list):
        self.debug('_field_indexes %s with %s', cmd, params)

    def _create_foreignkey_constraint(self, cmd: Cmd, params: list):
        self.debug('_create_foreignkey_constraint %s with %s', cmd, params)

    def _show_all_models(self, cmd: Cmd, params: list):
        self.debug('_show_all_models %s with %s', cmd, params)

    def _remove_property(self, cmd: Cmd, params: list):
        self.debug('_remove_property %s with %s', cmd, params)

    def _savepoint_create(self, cmd: Cmd, params: list):
        # self.debug('_savepoint_create %s with %s', cmd, params)
        ...

    def _savepoint_rollback(self, cmd: Cmd, params: list):
        # self.debug('_savepoint_rollback %s with %s', cmd, params)
        ...

    def _savepoint_commit(self, cmd: Cmd, params: list):
        # self.debug('_savepoint_commit %s with %s', cmd, params)
        ...

    def _add_items(self, cmd: Cmd, values: list):
        self.debug('_add_items %s with %s', cmd, values)
        model = cmd['data']['model']
        concrete_model = self._check_or_create_model(model)

        instance_of_property_id = self.wikibase_info[WbDatabase._INSTANCE_OF]['id']
        django_field_property_id = self.wikibase_info[WbDatabase._DJANGO_FIELD]['id']
        django_next_id_property_id = self.wikibase_info[WbDatabase._DJANGO_NEXT_ID]['id']

        for value in values:
            next_id = self.api.get_and_increase_value(
                concrete_model['claims'][f'P{django_next_id_property_id}'][0]['id'], 1)

            instance_of_model_label = self._instance_of_model_label(
                model, next_id)
            claims = self._claims_make(
                concrete_model['claims'][f'P{django_field_property_id}'], value)
            claims.append(self._claim_item_value(
                instance_of_property_id, concrete_model))
            autofield_property_id, _ = self._get_autofield_numeric_property_id_and_django_autofield_name_or_none(
                model, concrete_model)
            if autofield_property_id:
                claims.append(self._claim_quantity_value(
                    autofield_property_id, next_id))
            self.get_or_create_item_if_not_found_by_name(
                instance_of_model_label,
                data={'claims': claims})

    def _last_insert_id(self, cmd: Cmd, params: list):
        self.debug('_last_insert_id %s with %s', cmd, params)
        model = self.wikibase_info[WbDatabase._DJANGO_MODELS][cmd['data']['table']]
        concrete_model = self._check_or_create_model(model)

        django_next_id_property_id = self.wikibase_info[WbDatabase._DJANGO_NEXT_ID]['id']
        claim_value = self.api.get_claim_value(
            concrete_model['claims'][f'P{django_next_id_property_id}'][0]['id'])
        self.result = [[int(claim_value['amount']) - 1]]
        self._position = 0

    def _set_items(self, cmd: Cmd, values: list):
        self.debug('_set_items %s with %s', cmd, values)
        model = cmd['data']['model']
        concrete_model = self._check_or_create_model(model)

        # TODO: select claims for update

        instance_of_property_id = self.wikibase_info[WbDatabase._INSTANCE_OF]['id']
        django_field_property_id = self.wikibase_info[WbDatabase._DJANGO_FIELD]['id']
        django_next_id_property_id = self.wikibase_info[WbDatabase._DJANGO_NEXT_ID]['id']

        autofield_property_id, django_autofield_name = self._get_autofield_numeric_property_id_and_django_autofield_name_or_none(
            model, concrete_model)
        if autofield_property_id is None:
            # TODO: We need to think, how implement primary keys without autofields
            raise WbDatabase.InternalError(
                'Sorry, I can\'t find autofield property')

        for value in values:
            if not(django_autofield_name in value):
                # TODO: We need to think, how implement primary keys without autofields
                raise WbDatabase.InternalError(
                    'Sorry, I can\'t find autofield property')
            determined_id = int(value[django_autofield_name])

            self.api.set_integer_value_if_less_then_current_value(
                concrete_model['claims'][f'P{django_next_id_property_id}'][0]['id'],
                determined_id + 1)

            instance_of_model_label = self._instance_of_model_label(
                model, determined_id)
            claims = self._claims_make(
                concrete_model['claims'][f'P{django_field_property_id}'], value)
            claims.append(self._claim_item_value(
                instance_of_property_id, concrete_model))
            claims.append(self._claim_quantity_value(
                autofield_property_id, determined_id))
            self.get_or_create_item_if_not_found_by_name(
                instance_of_model_label,
                data={'claims': claims})

    def _create_model(self, cmd: Cmd, params: list):
        self.debug('_create_model %s with %s', cmd, params)
        self._check_or_create_model(cmd['data']['model'])

    def _alter_model(self, cmd: Cmd, params: list):
        self.debug('_alter_model %s with %s', cmd, params)
        if cmd['data']['model']:
            self._check_or_create_model(cmd['data']['model'])

    def _field_has_default(self, cmd: Cmd, params: list):
        self.debug('_field_has_default %s with %s', cmd, params)
        self.result = [[None]]

    def _table_exists(self, cmd: Cmd, params: list):
        self.debug('_table_exists %s with %s', cmd, params)

    def _enable_constraints(self, cmd: Cmd, params: list):
        self.debug('_enable_constraints %s with %s', cmd, params)

    def _disable_constraints(self, cmd: Cmd, params: list):
        self.debug('_disable_constraints %s with %s', cmd, params)

    def _create_index(self, cmd: Cmd, params: list):
        self.debug('_create_index %s with %s', cmd, params)

    def _get_constraints(self, cmd: Cmd, params: list):
        self.debug('_get_constraints %s with %s', cmd, params)

    def _select(self, cmd: Cmd, params: list):
        self.debug('_select %s with %s', cmd, params)
        for model in cmd['data']['models']:
            self._check_or_create_model(model)
        # ...
        answer = self.api.execute_sparql_query(cmd['data']['sparql'])
        self.result = self._tuples(
            answer['head']['vars'], answer['results']['bindings'])
        self._position = 0

    def execute(self, cmd, params) -> Any:
        if not isinstance(cmd, Cmd):
            # TODO: transform SQL-92 into commands
            raise WbDatabase.InternalError(f'Wrong command: {cmd}')
        models = self._get_models(cmd)
        if models:
            for model in models:
                self._check_or_create_model(model)
        if cmd['cmd'] == 'add_property':
            return self._add_property(cmd, params)
        if cmd['cmd'] == 'alter_property':
            return self._alter_property(cmd, params)
        if cmd['cmd'] == 'add_constraints':
            return self._add_constraints(cmd, params)
        if cmd['cmd'] == 'field_indexes':
            return self._field_indexes(cmd, params)
        if cmd['cmd'] == 'create_foreignkey_constraint':
            return self._create_foreignkey_constraint(cmd, params)
        if cmd['cmd'] == 'show_all_models':
            return self._show_all_models(cmd, params)
        if cmd['cmd'] == 'remove_property':
            return self._remove_property(cmd, params)
        if cmd['cmd'] == 'savepoint_create':
            return self._savepoint_create(cmd, params)
        if cmd['cmd'] == 'savepoint_rollback':
            return self._savepoint_rollback(cmd, params)
        if cmd['cmd'] == 'savepoint_commit':
            return self._savepoint_commit(cmd, params)
        if cmd['cmd'] == 'add_items':
            model = cmd['data']['model']
            concrete_model = self._check_or_create_model(model)

            _, django_autofield_name = self._get_autofield_numeric_property_id_and_django_autofield_name_or_none(
                model, concrete_model)

            # split to the two groups (determined autofield values and not determined)
            determined_auto_field_values = [
                p for p in params if django_autofield_name in p and p[django_autofield_name]]
            undetermined_auto_field_values = [p for p in params if not(
                django_autofield_name in p) or not(p[django_autofield_name])]
            if undetermined_auto_field_values:
                return self._add_items(cmd, undetermined_auto_field_values)
            if determined_auto_field_values:
                return self._set_items(cmd, determined_auto_field_values)
        if cmd['cmd'] == 'last_insert_id':
            return self._last_insert_id(cmd, params)
        if cmd['cmd'] == 'set_items':
            return self._set_items(cmd, params)
        if cmd['cmd'] == 'create_model':
            return self._create_model(cmd, params)
        if cmd['cmd'] == 'alter_model':
            return self._alter_model(cmd, params)
        if cmd['cmd'] == 'field_has_default':
            return self._field_has_default(cmd, params)
        if cmd['cmd'] == 'create_model':
            return self._create_model(cmd, params)
        if cmd['cmd'] == 'table_exists':
            return self._table_exists(cmd, params)
        if cmd['cmd'] == 'enable_constraints':
            return self._enable_constraints(cmd, params)
        if cmd['cmd'] == 'disable_constraints':
            return self._disable_constraints(cmd, params)
        if cmd['cmd'] == 'create_index':
            return self._create_index(cmd, params)
        if cmd['cmd'] == 'get_constraints':
            return self._get_constraints(cmd, params)
        if cmd['cmd'] == 'select':
            return self._select(cmd, params)

        raise WbDatabase.InternalError(
            f'Sorry, but that command {cmd} can\'t execute')

    def fetchall(self):
        '''Fetch rows from the wikibase

        Returns:
            List[Tuple]: List of rows from the wikibase
        '''
        return self.result

    def fetchmany(self, limit: int):
        '''Fetch rows from the wikibase

        Returns:
            List[Tuple]: List of rows from the wikibase
        '''
        self._position += limit
        result = self.result[:limit]
        self.result = self.result[limit:]
        return result

    def fetchone(self):
        '''Fetch single row from the wikibase

        Returns:
            Tuple: the row from the wikibase
        '''
        return self.result[0]

    def rowcount(self):
        return len(self.result)


class WbDatabaseConnection(Loggable):

    def __init__(self, charset: str, url: str,
                 user: str, password: str,
                 instance_of_property_id: int,
                 subclass_of_property_id: int,
                 django_model_item_id: int,
                 wdqs_sparql_endpoint: str,
                 django_namespace: str):
        super().__init__()
        self.charset = charset
        self.api = WbApi(url, charset, wdqs_sparql_endpoint)
        self.user = user
        self.password = password  # TODO: hash instead plain
        self.django_namespace = django_namespace

        if not django_model_item_id:
            # algo: 1. select django model by name 'django model'
            #       2. if not found create the item
            #       3. if found just get the identity
            django_model_item_id = self.create_item_if_not_found_by_name_and_get_id_without_prefix(
                WbDatabase._DJANGO_MODEL)
        django_namespace_property_id = self.create_property_if_not_found_by_name_and_get_id_without_prefix(
            WbDatabase._DJANGO_NAMESPACE, 'string')
        django_application_property_id = self.create_property_if_not_found_by_name_and_get_id_without_prefix(
            WbDatabase._DJANGO_APPLICATION, 'string')
        django_field_property_id = self.create_property_if_not_found_by_name_and_get_id_without_prefix(
            WbDatabase._DJANGO_FIELD, 'wikibase-property')
        django_sequence_property_id = self.create_property_if_not_found_by_name_and_get_id_without_prefix(
            WbDatabase._DJANGO_SEQUENCE, 'wikibase-property')
        django_next_id_property_id = self.create_property_if_not_found_by_name_and_get_id_without_prefix(
            WbDatabase._DJANGO_NEXT_ID, 'quantity')

        mediawiki_info = self.api.mediawiki_info()
        server = mediawiki_info['query']['general']['server']
        # https://avangard.testo.click/api.php?action=query&meta=siteinfo&siprop=extensions&format=json
        self.wikibase_info = {
            WbDatabase._BASE_URL: server,
            WbDatabase._MEDIAWIKI_VERSION: mediawiki_info['query']['general']['generator'],
            WbDatabase._INSTANCE_OF: WbLink(instance_of_property_id, 'property', server),
            WbDatabase._SUBCLASS_OF: WbLink(subclass_of_property_id, 'property', server),
            WbDatabase._DJANGO_MODEL: WbLink(django_model_item_id, 'item', server),
            WbDatabase._DJANGO_NAMESPACE: WbLink(django_namespace_property_id, 'property', server),
            WbDatabase._DJANGO_APPLICATION: WbLink(django_application_property_id, 'property', server),
            WbDatabase._DJANGO_FIELD: WbLink(django_field_property_id, 'property', server),
            WbDatabase._DJANGO_SEQUENCE: WbLink(django_sequence_property_id, 'property', server),
            WbDatabase._DJANGO_NEXT_ID: WbLink(django_next_id_property_id, 'property', server),
            WbDatabase._DJANGO_MODELS: dict(),
            WbDatabase._SPARQL_ENDPOINT: wdqs_sparql_endpoint if wdqs_sparql_endpoint else f'{url}/sparql',
            WbDatabase._WIKIBASE_PROPERTIES: dict(),
            WbDatabase._WIKIBASE_CREDENTIALS: WbCredentials(user, password)
        }
        self.transactions = []
        self._test_django_application_models()

    def prefixes(self) -> List[str]:
        return [
            'PREFIX bd: <http://www.bigdata.com/rdf#>',
            'PREFIX wikibase: <http://wikiba.se/ontology#>',
            'PREFIX e: <%s/entity/>' % (
                self.wikibase_info[WbDatabase._BASE_URL], ),
            'PREFIX pd: <%s/prop/direct/>' % (
                self.wikibase_info[WbDatabase._BASE_URL], )
        ]

    def _test_django_application_models(self):
        test_result = self.api.execute_sparql_query('''
            # Instance of (Document)
            PREFIX bd: <http://www.bigdata.com/rdf#>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX e: <%s/entity/>
            PREFIX pd: <%s/prop/direct/>

            SELECT ?item ?itemLabel
            WHERE
            {
                ?item pd:P%s e:Q%s.
                SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
            }

            LIMIT 100
        ''' % (
            self.wikibase_info[WbDatabase._BASE_URL],
            self.wikibase_info[WbDatabase._BASE_URL],
            self.wikibase_info[WbDatabase._SUBCLASS_OF]['id'],
            self.wikibase_info[WbDatabase._DJANGO_MODEL]['id']
        ))
        # TODO: process all django applications
        self.debug(dumps(test_result))

    def create_item_if_not_found_by_name_and_get_id_without_prefix(self, item_name: str) -> int:
        entities = self.api.search_items({'label': item_name})
        if len(entities) == 1:
            return int(entities[0]['id'][1:])
        if len(entities) == 0:
            entity = self.api.new_item(
                {'labels': {'en': {'language': 'en', 'value': item_name}}})
            return int(entity['id'][1:])
        # Exact matching
        for entity in entities:
            if entity['label'] == item_name:
                return int(entity['id'][1:])
        raise WbDatabase.InternalError(
            f'The entity {item_name} has another one (i.e. not unique)')

    def create_property_if_not_found_by_name_and_get_id_without_prefix(self, property_name: str, data_type_name: str):
        entities = self.api.search_properties({'label': property_name})
        if len(entities) == 1:
            return int(entities[0]['id'][1:])
        if len(entities) == 0:
            entity = self.api.new_property(
                {'labels': {'en': {'language': 'en', 'value': property_name}}, 'datatype': data_type_name})
            return int(entity['id'][1:])
        # Exact matching
        for entity in entities:
            if entity['label'] == property_name:
                return int(entity['id'][1:])
        raise WbDatabase.InternalError(
            f'The entity {property_name} has another one (i.e. not unique)')

    def django_model(self, django_table_name: str):
        for table_name, model in self.wikibase_info[WbDatabase._DJANGO_MODELS].items():
            if table_name == django_table_name:
                return model
        raise WbDatabase.InternalError(
            f'Sorry, I can\'t find django model for {django_table_name} in cache {WbDatabase._DJANGO_MODELS}.')

    def expression_instance_of(self, django_table_name: str) -> str:
        concrete_model = self.cursor()._check_or_create_model(
            self.django_model(django_table_name))
        return f'?{django_table_name} pd:P{self.wikibase_info[WbDatabase._INSTANCE_OF]["id"]} e:Q{int(concrete_model["id"][1:])}'

    def expression_has_property(self, django_table_name: str, property_name: str) -> str:
        wikibase_property_id = self.cursor()._get_wikibase_numeric_property_id_or_none(
            self.django_model(django_table_name), property_name)
        return f'?{django_table_name} pd:P{wikibase_property_id} ?{property_name}'

    def sparql_parameter_value(self, built_in_type_value):
        if isinstance(built_in_type_value, str):
            return "'" + built_in_type_value.replace("'", "\\'") + "'"
        return str(built_in_type_value)

    def db_info(self, key):
        return self.wikibase_info.get(key)

    def cursor(self):
        return WbCursor(self.django_namespace, self.wikibase_info, self.api)

    def rollback(self):
        ...

    def commit(self):
        ...

    def close(self):
        ...

    def trans(self) -> List:
        return self


class TransactionContext:

    def __init__(self, connection: WbDatabaseConnection):
        self.connection = connection

    def __enter__(self):
        # make a database connection and return it
        ...
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        # make sure the dbconnection gets closed
        self.connection.close()
        ...
