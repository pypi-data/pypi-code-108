import urwid
import json
import copy
import re
from collections import OrderedDict
from distutils.util import strtobool
from cerberus_kind.utils import parse_error, kind_schema
from cerberus_document_editor import yaml_parser
from .validator import Validator
from .widget import Widget, FlatButton
from .page import ListPage, PopupPage
from .debug import log

def BOOLEAN(x):
    return bool(strtobool(x))

# Helper functions
def ellipsis(text, max_w=60, max_h=10):
    def cols(rows):
        output = []
        for row in rows:
            if len(row) > max_w:
                output.append(row[:max_w-3]+'...')
            else:
                output.append(row)
        return output
    rows = text.strip('\n').split('\n')
    if len(rows) > max_h:
        return '\n'.join(cols(rows[:max_h-1]+['...']))
    else:
        return '\n'.join(cols(rows))

def callback_generator(ctx, name, schema, doc):
    def callback(key):
        page = EditorPage(
            name, 
            schema, # copy.deepcopy(schema),
            doc,
            #doc if isinstance(doc, list) else dict(filter(lambda x: x[0] != 'kind', doc.items())),
            True,
        )
        ctx.next(page)
    return callback

class EditorPage(ListPage):
    def __init__(self, name, schema, document, sub_page=False):
        super().__init__(name, sub_page=sub_page)
        self.widget_map = {}
        log(f'Schema: {schema}')
        log(f'Document: ', document)

        self.validator = Validator(schema, purge_unknown=True)
        self.json = {
            'document': self.validator.normalized(document, ordered=True) or document,
            'schema': schema
        }
        if document != self.json['document']:
            self.modified()
        self._config = {}

    def __repr__(self):
        return json.dumps(self.json.get('document', {}))

    @property
    def root_schema(self):
        return self._config.get("root_schema")

    @property
    def is_list(self):
        return self._config.get("root_type") == 'list'

    @property
    def is_selector(self):
        return self._config.get("root_type") == 'selector'

    @property
    def is_valuesrules(self):
        return self._config.get("root_type") == 'valuesrules'

    @property
    def is_oneof(self):
        return self._config.get('root_type') == 'oneof'

    def warning(self, message=None, high_priority=False):
        super(ListPage, self).warning(message, high_priority)

    def on_change_focus(self):
        self.update_indicator()

    def on_page_result(self, page):
        if page.json:
            if 'popup' in page.json:
                key = page.json.get('popup')
                if key:
                    body = self.json
                    if key in body['document']:
                        self.warning('Already exist key.')
                    else:
                        body['document'][key] = None
                        self.json = body
                        self.modified()
                        self.render()
            elif 'rename' in page.json:
                if hasattr(self, '_last_key'):
                    last_key = getattr(self, '_last_key')
                    new_key = page.json.get('rename')
                    if new_key:
                        body = self.json
                        if new_key in body['document']:
                            self.warning("Already exist key.")
                        else:
                            body['document'] = OrderedDict(
                                [(new_key, v) if k == last_key else (k, v) for k, v in body['document'].items()]
                            )
                            self.json = body
                            self.modified()
                            self.render()
            elif 'exit' in page.json:
                key = page.json.get('exit')
                if key.lower() == 'yes':
                    self.hwnd.destroy()
                elif key.lower() == 'no':
                    self.hwnd.destroy(False)
                elif key.lower() == 'cancel':
                    ...
                self.render()
            else:
                data = self.json
                document = data['document']
                if isinstance(page.json['document'], list):
                    document[page.name] = list(filter(None, page.json['document']))
                elif isinstance(page.json['document'], dict):
                    document[page.name] = dict(filter(lambda x: x[1] is not None, page.json['document'].items()))
                else:
                    document[page.name] = page.json['document']
                if self.json != data:
                    self.json = data
                    self.modified()
                self.render()

    def on_change(self, widget, new_value):
        def casting(value):
            if isinstance(widget, urwid.IntEdit):
                return int(f"0{value}")
            if isinstance(widget, urwid.numedit.FloatEdit):
                return float(f"0{value}")
            return value
        new_value = casting(new_value)

        key = self.widget_map.get(hash(widget))
        pattern = re.compile(r'^__(.*)__$')
        matched = pattern.match(str(key))
        if matched:
            key = matched.group(1)
            if key in ['kind']:
                data = self.json
                document = data['document']
                document[key] = new_value
                document = self.validator.normalized(document, data['schema'], ordered=True)
                if self.json['document'] != document:
                    self.json = {'document': document}
                    self.modified()
                self.render()
        else:
            type_pattern = re.compile(r'^T__([A-Z]+)_(.*)__$')
            matched = type_pattern.match(str(key))
            if matched:
                cast_type = matched.group(1)
                try:
                    cast_func = eval(f"lambda x: {cast_type}(x)")
                    new_value = cast_func(new_value)
                except:
                    ...
                key = matched.group(2)

            data = self.json
            document = data['document']
            schema = data['schema']

            document[key] = new_value
            if self.json['document'] != document:
                self.json = {"document": document}
                self.modified()
            self.render()

            # Update indicator for focusing item.
            if '__root__' in schema:
                schema = schema['__root__']
                if schema.get('selector'):
                    schema = schema['selector'][document['kind'].lower()]
                elif schema.get('valuesrules'):
                    schema = {key: schema['valuesrules'] for key in document}
                elif schema.get('oneof'):
                    schema = {k: v for _ in schema.get('oneof') for k, v in _.get('schema', {}).items()}
                else:
                    schema = schema['schema']
            
            item_schema = schema.get(key)
            if item_schema:
                if not self.validator.validate({key: new_value}, {key: item_schema}, update=True, normalize=False):
                    self.warning(parse_error(self.validator.errors, with_path=False), True)
                else:
                    self.warning()

    def on_update(self):
        doc = self.json['document']
        schema = self.json['schema']

        log('----------------------------------------------')

        # Prepare Root schema
        if '__root__' in schema:
            schema = schema.get('__root__')
            self._config['root_schema'] = schema
            self._config['root_type'] = schema.get('type', 'unknown')
            if schema.get('selector'):
                # Selector 일 경우
                self._config['root_type'] = 'selector'
                allowed = [_.title() for _ in schema['selector']]
                kind = doc.get('kind', "").lower()
                if not kind in schema['selector']:
                    allowed += [kind.title()]
                    kind = allowed[0].lower()
                schema = schema['selector'].get(kind)
                schema['kind'] = kind_schema(kind, allowed)
                log("** KIND ", schema['kind'])
            elif schema.get('oneof'):
                # -of-rules 일 경우
                self._config['root_type'] = 'oneof'
                schema = {k: v for _ in schema.get('oneof') for k, v in _.get('schema', {}).items()}
            elif schema.get('valuesrules'):
                # 동적 key 일 경우
                self._config['root_type'] = 'valuesrules'
                schema = {key: schema['valuesrules'] for key in doc}
            else:
                # 그 외 일반 schema 일경우
                schema = schema.get('schema', {})
                # 타입이 리스트일 경우
                if schema.get('type') == 'list':
                    self._config['root_type'] = 'list'

        log('root schema:', list(self._config['root_schema'].keys()))
        log('root type:', self._config['root_type'])

        # Prepare appendable items with hotkey
        if self.is_valuesrules:
            # 동적 key 생성 가능할 때
            def add_new_item(self):
                schema = {
                    'value': self.root_schema.get('keysrules', {'type': 'string'})
                }
                self.next(PopupPage("Add new item", background=self.on_draw(), schema=schema))
            self.register_keymap('ctrl n', 'Add new item', add_new_item)
            def rename_item(self):
                schema = {
                    'value': self.root_schema.get('keysrules', {'type': 'string'})
                }
                self._last_key = self.widget_map[hash(Widget.unwrap_widget(self.get_focus_widget()))]
                self.next(PopupPage("Rename item", background=self.on_draw(), schema=schema, return_key='rename'))
            self.register_keymap('ctrl r', 'Rename item', rename_item)
        elif self.is_list:
            # 배열일 때
            def add_new_item(self):
                doc = self.json.get('document', [])
                sub_type = schema.get('type', 'string')
                if sub_type in ['string']:
                    doc.append("")
                elif sub_type in ['integer']:
                    doc.append(0)
                elif sub_type in ['float', 'number']:
                    doc.append(.0)
                elif sub_type in ['list']:
                    doc.append(self.validator.normalized([], {'__root__': schema}, ordered=True))
                elif sub_type in ['dict']:
                    doc.append(self.validator.normalized({}, {'__root__': schema}, ordered=True))
                self.json = {'document': doc}
                self.render()
            self.register_keymap('ctrl n', 'Add new item', add_new_item)
            def move_to_up(self):
                doc = self.json.get('document', [])
                widget = self.get_focus_widget()
                int_key = int(self.widget_map[hash(Widget.unwrap_widget(widget))])
                doc.insert(max(0, int_key-1), doc.pop(int_key))
                self.json = {'document': doc}
                self.prev_focus()
                self.render()
            self.register_keymap('ctrl up', 'Move to up', move_to_up)
            def move_to_down(self):
                doc = self.json.get('document', [])
                widget = self.get_focus_widget()
                int_key = int(self.widget_map[hash(Widget.unwrap_widget(widget))])
                doc.insert(min(len(doc)-1, int_key+1), doc.pop(int_key))
                self.json = {'document': doc}
                self.next_focus()
                self.render()
            self.register_keymap('ctrl down', 'Move to down', move_to_down)
        else:
            # 일반 스키마일 때
            appendable_items = {k: v.get('description') for k, v in schema.items() if not k in doc}
            if appendable_items:
                def add_new_item(self):
                    self.next(PopupPage("Add new item", background=self.on_draw(), ptype='select', items=appendable_items))
                self.register_keymap('ctrl n', 'Add new item', add_new_item)
            else:
                self.unregister_keymap('ctrl n')

        # Prepare deletable items with hotkey
        if len(doc):
            if self.is_list:
                def delete_callback(self):
                    widget = self.get_focus_widget()
                    key = self.widget_map[hash(Widget.unwrap_widget(widget))]
                    doc.pop(int(key))
                    self.json = {'document': doc}
                    self.render()
            else:
                immutable_items = [k for k, v in schema.items() if v.get('required', False)]
                def delete_callback(self):
                    widget = self.get_focus_widget()
                    key = self.widget_map[hash(Widget.unwrap_widget(widget))]
                    for _ in [re.compile(r'^__(?P<key>.*)__$'), re.compile(r'^T__([A-Z]+)_(?P<key>.*)__$')]:
                        matched = _.match(str(key))
                        if matched:
                            key = matched.group('key')
                            break
                    if not key in immutable_items:
                        del doc[key]
                        self.json = {'document': doc}
                        self.modified()
                        self.render()
                    else:
                        self.warning("Cannot remove required item(required).")
            self.register_keymap('ctrl d', 'Delete item', delete_callback)
        else:
            self.register_keymap('ctrl d', 'Delete item', lambda x: None, enabled=False)

        # Re-construct widgets
        log('current schema:', list(schema.keys()))
        self.clear_items()
        for key, value in (enumerate(doc) if self.is_list else OrderedDict(doc).items()):
            log('key is', key)
            try:
                if self.is_list:
                    sub_schema = schema
                else:
                    sub_schema = schema.get(key, {})

                log('  sub schema:', list(sub_schema.keys()))

                dtype = sub_schema.get('type', 'string')
                dtype = dtype[0] if isinstance(dtype, list) else dtype
                desc = sub_schema.get('description', None)

                log('  data type:', dtype)
                log('  description:', desc)

                if key == 'kind' and schema.get('kind'):
                    log(  'allowed:', schema['kind']['allowed'], '/', doc['kind'])
                    widget = self.add_column_dropdown(key, desc, 
                        schema['kind']['allowed'],
                        doc['kind']
                    )
                    self.widget_map[hash(widget)] = f'__{key}__'
                elif sub_schema.get('allowed'):
                    allowed_list = sub_schema.get('allowed')
                    widget = self.add_column_dropdown(key, desc, 
                        allowed_list + ([doc[key]] if not doc[key] in allowed_list else []),
                        doc[key]# if doc[key] in allowed_list else len(allowed_list)-1
                    )
                    self.widget_map[hash(widget)] = key
                elif dtype in ['float', 'number']:       # float
                    value = value or .0
                    widget = self.add_column_number(key, desc, value)
                    self.widget_map[hash(widget)] = key
                elif dtype in ['integer']:             # integer
                    value = value or 0
                    widget = self.add_column_integer(key, desc, value)
                    self.widget_map[hash(widget)] = key
                elif dtype in ['string']:
                    value = value or ""
                    widget = self.add_column_str(key, desc, value, sub_schema.get('multiline', False))
                    self.widget_map[hash(widget)] = key
                elif dtype in ['boolean']:
                    allowed_list = [True, False]
                    widget = self.add_column_dropdown(key, desc, 
                        allowed_list,
                        doc[key] if doc[key] in allowed_list else allowed_list[0]
                    )
                    self.widget_map[hash(widget)] = f'T__BOOLEAN_{key}__'
                elif dtype in ['list']:
                    value = value or []
                    widget = self.add_column_object(key, desc, text=ellipsis(yaml_parser.dump(value)),
                        callback=callback_generator(
                            self, 
                            key,
                            {'__root__': sub_schema},
                            value
                        )
                    )
                    self.widget_map[hash(widget)] = key
                elif dtype in ['dict']:                 # Object
                    value = value or {}
                    if 'schema' in sub_schema:
                        widget = self.add_column_object(key, desc, text=ellipsis(yaml_parser.dump(value)), 
                            callback=callback_generator(
                                self, 
                                key,
                                sub_schema['schema'], 
                                value
                            )
                        )
                    else:
                        widget = self.add_column_object(key, desc, text=ellipsis(yaml_parser.dump(value)),
                            callback=callback_generator(
                                self, 
                                key,
                                {'__root__': sub_schema},
                                value
                            )
                        )
                    self.widget_map[hash(widget)] = key
            except Exception as e:
                raise e

        self.update_indicator()
    
    def update_indicator(self):
        doc = self.json.get('document')
        schema = self.json.get('schema')
        if not self.validator.validate(doc, schema, update=False, normalize=False):
            self.warning(parse_error(self.validator.errors, with_path=True))
        else:
            self.warning()

    def on_close(self):
        self.next(PopupPage("Exit with Save", return_key='exit', background=self.on_draw(), ptype='select', items=['Yes', 'No', 'Cancel']))
        return True
