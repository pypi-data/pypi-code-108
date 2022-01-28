import logging
import os
import shutil
import xml.etree.ElementTree as ET

from django.conf import settings
from isc_common import setAttr, Stack, StackElementNotExist
from isc_common.ws.webSocket import WebSocket
from react.models.page_fragments import Page_fragments

logger = logging.getLogger(__name__)


class AbstractGenerator:
    gen_variables = dict()
    gen_files = Stack()


class TypeScriptGenerator(AbstractGenerator):
    def _get_text(self, text):
        if isinstance(text, str):
            try:
                root = ET.fromstring(text=text)
            except ET.ParseError:
                return text
        else:
            root = text

        if len(list(root)) == 0:
            return root.text

        for child in root:
            res = self._get_text(child)
            if isinstance(res, str):
                return res

        raise Exception('Not found text.')

    def _rec_gen_files(self):
        for path_file, data_4_file in self.gen_files:
            pathes_file = path_file.split('/')
            _pathes_file = []
            for p in pathes_file:
                if '$' in p:
                    p_item = self.gen_variables.get(p.replace('$', ''))
                    if p_item is None:
                        raise Exception(f'Variable {p} not found.')

                    _pathes_file.append(p_item.get('value_text'))
                else:
                    _pathes_file.append(p)
            pathes_file = '/'.join(_pathes_file)
            dir, file = os.path.split(pathes_file)

            if os.path.exists(dir) and 'generated' in dir:
                shutil.rmtree(dir)
                os.mkdir(dir)

            if not os.path.exists(dir):
                os.mkdir(dir)

            if os.path.exists(pathes_file):
                os.remove(pathes_file)

            with open(pathes_file, 'w') as f:
                for line in data_4_file:
                    f.write(line.replace('&amp;', '&'))
                    f.write('\n')

        WebSocket.send_info_message(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{self.user.username}',
            message='Генерация выполнена',
            logger=logger
        )

    def _get_comment(self, text):
        if text is None:
            return None

        return f'//{self._get_text(text)}'

    def _set_file_text(self, data_4_file: list, fragment_param):
        if not isinstance(data_4_file, list):
            raise Exception(f'file must be list.')

        if 'SCSS' in fragment_param.type.code and 'VAR' in fragment_param.type.code and 'URL' in fragment_param.type.code:
            data_4_file.append(self._get_comment(fragment_param.description))
            data_4_file.append(f'${fragment_param.code} : "{self._get_text(fragment_param.value_text)}";')

        if fragment_param.type.code == 'TS_MODULE':
            data_4_file.append(self._get_comment(fragment_param.description))
            data_4_file.append(fragment_param.value_text)

    def generate(self, data, user):
        from react.models.pages import Pages
        from react.models.fragment_params import Fragment_params

        self.user = user
        for pages_id in data.get('pages_ids'):
            for page in Pages.tree_objects.get_descendants(id=pages_id, child_id='id', order_by_clause='order by level'):
                for page_fragment in Page_fragments.objects.filter(page=page):
                    for fragment_param in Fragment_params.objects.filter(fragment=page_fragment.fragment).order_by('num'):
                        if fragment_param.type.code == 'GEN_VAR':
                            if self.gen_variables.get(fragment_param.code) is None:
                                setAttr(self.gen_variables, fragment_param.code, dict(value_dec=fragment_param.value_dec, value_text=fragment_param.value_text))
                        elif fragment_param.props.use_generator.is_set is True:
                            try:
                                _, data_4_file = self.gen_files.find_one(lambda x: x[0] == fragment_param.path_file)
                                self._set_file_text(data_4_file=data_4_file, fragment_param=fragment_param)
                            except StackElementNotExist:
                                data_4_file = []
                                self._set_file_text(data_4_file=data_4_file, fragment_param=fragment_param)
                                self.gen_files.push((fragment_param.path_file, data_4_file))
        self._rec_gen_files()
