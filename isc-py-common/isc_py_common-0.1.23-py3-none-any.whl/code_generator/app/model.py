import inspect
import logging
import os
import re
from shutil import copyfile, rmtree

from code_generator.app.icons import Icons
from code_generator.core.writer import Writer

logger = logging.getLogger(__name__)


class Tag(Writer):
    params = []
    value = []
    pos = None
    raw_tag = None
    absolute_position = None
    unquoted = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pos = kwargs.get('pos')
        if self.pos is None:
            raise Exception(f'Не определен pos.')

        self.raw_tag = kwargs.get('raw_tag')
        if self.raw_tag is not None and self.raw_tag != '':
            if self.raw_tag is None:
                raise Exception(f'Не определен raw_tag.')

            self.code_type = kwargs.get('code_type')
            if self.code_type is None:
                raise Exception(f'Не определен code_type.')

            self.value = kwargs.get('value')
            if self.value is None:
                raise Exception(f'Не определен value.')

            if not isinstance(self.value, list):
                self.value = [self.value]

            self.value_len = max([len(str(item)) for item in self.value])

            lst = self.raw_tag.replace('${', '').replace('}', '').split(':')
            self.params = lst[1:]

            self.unquoted = self.get_param('unquoted')  # Строковый параметр не заквочивается
            self.absolute_position = self.get_param('absolute_position')  # Праметр заменяется непосредственно в месте нахождения.
            # если замена многострочная, то остальные строки подтягиваются на уровень вставки первой строки

    def get_param(self, param_name):
        res = [item for item in self.params if item == param_name]
        return len(res) > 0

    def get_str(self):
        step = 1
        new_pos = 0
        res = ''
        if self.raw_tag is not None and self.raw_tag != '':
            for _value in self.value:
                if isinstance(_value, str):
                    if not self.unquoted:
                        _value = self.dbl_qutes_str(_value)

                if isinstance(_value, bool):
                    if self.code_type == 'ts':
                        _value = self.uncapitalize(str(_value))

                if step == 1:
                    if self.absolute_position:
                        res = _value
                    else:
                        res = self.fill_space(self.pos) + _value

                    new_pos = self.pos + self.value_len
                    step += 1
                else:
                    res += self.fill_space(self.pos) + _value

            self.pos = new_pos
        return str(res)


class Model(Writer):
    image_dir_name = 'common-webapp'
    template_name = None
    output_file_name = None
    class_name = None

    name_app = None
    code_app = None
    path_app = None

    def get_model_attributes(self):
        members = [m for m in inspect.getmembers(self) if not (m[0].startswith('__') and m[0].endswith('__')) and m[1] is not None and not inspect.ismethod(m[1])]
        return members

    def write_bool(self, value):
        if self.code_type == 'ts':
            return self.uncapitalize(value)
        elif self.code_type == 'py':
            return self.capitalize(value)
        else:
            raise Exception(f'Unknowm code_type.')

    check_patern = re.compile('(.+?)(\$?\{.*?\})|(.*)')

    def check_line(self, line):
        for tag in self.check_patern.findall(line):
            if tag[1] is None or tag[1] == '':
                return True
            else:
                return False

    def check_line1(self, line):
        for tag in self.check_patern.findall(line):
            if tag[1] is None or tag[1] == '':
                return True, ''
            else:
                return False, tag[1]

    def check_releases_template(self, lines):
        messages = []

        for line in lines:
            check, tag = self.check_line1(line)
            if not check:
                if len(messages) == 0:
                    messages.append(f'В шаблоне {self.template_name} не замещены следуюжие теги:')
                messages.append(self.fill_space(4) + tag)

        if len(messages) > 0:
            raise Exception('\n'.join(messages))

    def mod_emtity(self, value, results_finded):
        pos = 0
        if isinstance(results_finded, list):
            str = ''
            for _tuple in results_finded:
                if isinstance(_tuple, tuple):
                    str += _tuple[0]
                    pos += len(_tuple[0])
                    tag = Tag(raw_tag=_tuple[1], value=value, pos=pos, code_type=self.code_type)
                    str += tag.get_str()
                    pos += tag.pos
                    str += _tuple[2]
                    pos += len(_tuple[2])
                else:
                    raise Exception(f'{results_finded} in not tuple')
            return str
        else:
            raise Exception(f'{results_finded} in not list')

    def write_entity(self, replace_map=None):
        from code_generator.app.app_codeblock import ModelCodeBlock

        template_path = f'{self.template_path}{os.sep}{self.template_name}'

        self.check_path(self.template_path)

        out_path1 = f'{self.path_output}{os.sep}{self.path_app}'
        out_path = f'{self.path_output}{os.sep}{self.path_app}{os.sep}ts{os.sep}generated'
        if os.path.exists(out_path1):
            rmtree(out_path1)
        os.makedirs(out_path)
        copyfile(self.check_path(f'{self.template_path}{os.sep}__init__.pmd'), f'{out_path1}{os.sep}__init__.py')

        out_path = f'{out_path}{os.sep}{self.output_file_name}'

        out_file = open(out_path, "w+")  # open for append
        lines = []

        for line in open(template_path):
            self.print_dict(**dict(self.get_model_attributes()))
            for key, value in self.get_model_attributes():
                if isinstance(value, bool) or isinstance(value, str) or isinstance(value, int):
                    pattern = self.get_pattern(key)
                    result = pattern.findall(line)
                    line = self.mod_emtity(value, result)
                    if line == '' or self.check_line(line):
                        break

                elif isinstance(value, ModelCodeBlock):

                    pattern = self.get_pattern(key)
                    result = pattern.findall(line)
                    line = self.mod_emtity(value.code, result)
                    if line == '' or self.check_line(line):
                        break

            if line != '':
                lines.append(line)

        self.check_releases_template(lines)
        for line in lines:
            out_file.write(f'{line}\n')
        out_file.close()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from projectsettings import STATICFILES_DIRS

        icons_path = [path for key, path in STATICFILES_DIRS if key == self.image_dir_name]
        if len(icons_path) != 1 or not os.path.exists(icons_path[0]):
            raise Exception(f'Не найден путь {icons_path}')
        self.icons = Icons(icons_path[0])

        if kwargs is not None:
            for key, value in kwargs.items():
                if isinstance(value, (list, tuple)):
                    setattr(self, key, [Model(x) if isinstance(x, dict) else x for x in value])
                else:
                    setattr(self, key, Model(key=value) if isinstance(value, dict) else value)
