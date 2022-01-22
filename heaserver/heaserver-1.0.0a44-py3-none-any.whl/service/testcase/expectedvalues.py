"""
Functions for automatically generating expected values for unit and integration tests of HEA services.
"""
import copy
import logging
from typing import Dict, Any, List, Optional, cast
from heaserver.service import wstl
from yarl import URL
from dataclasses import dataclass
import uritemplate
from enum import Enum
from heaobject.root import is_primitive, is_primitive_list, is_heaobject_dict_list, is_heaobject_dict, HEAObjectDict, Primitive, HEAObjectDictValue, MemberObjectDict, Union
from datetime import date, time


@dataclass
class ActionSpec:
    name: str
    rel: Optional[List[str]] = None
    url: Optional[str] = None


@dataclass
class LinkSpec:
    url: str
    rel: Optional[List[str]]


def body_post(fixtures: Dict[str, List[HEAObjectDict]], coll: str) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Create a Collection+JSON template from a data test fixture.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :return: a Collection+JSON template as a dict using the first object in the given mongodb collection. Replaces the
    object's name and display_name attribute values with 'tritimus' and 'Tritimus', respectively.
    """
    return _create_template({**fixtures[coll][0], **{'name': 'tritimus', 'display_name': 'Tritimus'}})


def body_put(fixtures: Dict[str, List[HEAObjectDict]], coll: str) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Create a Collection+JSON template from a data test fixture.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :return: a Collection+JSON template as a dict using the first object in the given mongodb collection. Replaces the
    object's description attribute value with 'A description'.
    """
    logger_ = logging.getLogger(__name__)
    data = fixtures[coll][1]
    logger_.debug('Transforming into template %s', data)
    return _create_template({**data, **{'description': 'A description'}}, exclude=None)


def expected_one_wstl(fixtures: Dict[str, List[HEAObjectDict]],
                      coll: str,
                      wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                      include_root=False,
                      get_actions: Optional[List[ActionSpec]] = None) -> List[Dict[str, Any]]:
    """
    Create a run-time WeSTL document from a data test fixture. The document will contain the first HEAObject dict in
    the given collection, and will contain a single action.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param include_root: whether to use absolute URLs or just paths.
    :param get_actions: the actions to include in the body of GET calls.
    :return: a run-time WeSTL document as a dict.
    """
    if get_actions is None:
        get_actions = []
    actions = []
    href_ = wstl_builder.href if wstl_builder.href else ''
    for action, action_name, action_rel, action_url in ((wstl_builder.find_action(a.name), a.name, a.rel, a.url) for a
                                                        in get_actions):
        if action is None:
            raise ValueError(f'Action {action_name} does not exist')
        action = {**action,
                  'href': action_url if action_url else '#',
                  'rel': action_rel if action_rel else []}
        actions.append(action)
    return [{
        'wstl': {
            'data': [_wstl_data_transform(fixtures[coll][0])],
            'hea': {'href': str(URL(href_) / str(fixtures[coll][0]['id']))},
            'actions': actions,
            'title': wstl_builder.design_time_document['wstl']['title']}}]


def expected_one(fixtures: Dict[str, List[HEAObjectDict]], coll: str, wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                 include_root=False,
                 get_actions: Optional[List[ActionSpec]] = None) -> List[Dict[str, Dict[str, Any]]]:
    """
    Create a Collection+JSON document with the first HEAObject from a mongodb collection in the given data test fixture.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param include_root: whether to use absolute URLs or just paths.
    :param get_actions: the actions to include in the body of GET calls.
    :return: a list containing Collection+JSON template as a dict using the first object in the given mongodb collection.
    Replaces the object's description attribute value with 'A description'.
    """
    obj = fixtures[coll][0]
    id_ = str(obj['id'])
    href = URL(wstl_builder.href if wstl_builder.href else '') / id_
    get_actions_ = get_actions or []

    def item_links() -> List[Dict[str, Any]]:
        links = []
        for action, action_name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                              get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name}')
            targets = action.get('target', '').split()
            if 'item' in targets and 'read' in targets and 'cj' in targets:
                links.append({
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {'id': id_}) if url else str(href),
                    'rel': ' '.join(rel)
                })
        return links

    def item_link() -> Dict[str, Any]:
        for action, action_name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                              get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name}')
            targets = action.get('target', '').split()
            if 'item' in targets and 'href' in targets and 'cj' in targets:
                return {
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {'id': id_}) if url else (
                        str(href) if include_root else str(href.path)),
                    'rel': ' '.join(rel),
                    'readOnly': 'true'
                }
        return {}

    def top_level_links() -> List[Dict[str, Any]]:
        links = []
        for action, action_name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in
                                              get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name} in get_actions')
            targets = action.get('target', '').split()
            if action['type'] == 'safe' and 'app' in targets and 'cj' in targets and (
                'inputs' not in action or not action['inputs']):
                links.append({
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {'id': id_}) if url else (
                        str(href) if include_root else str(href.path)),
                    'rel': ' '.join(rel)
                })
        return links

    def queries() -> List[Dict[str, Any]]:
        queries = []
        for action, action_name, rel in ((wstl_builder.find_action(a.name), a.name, a.rel) for a in get_actions_):
            if action is None:
                raise ValueError(f'Invalid action name {action_name} in get_actions')
            targets = action.get('target', '').split()
            if 'inputs' in action and action['type'] == 'safe' and 'list' in targets and 'cj' in targets:
                q = {'rel': ' '.join(action['rel']),
                     'href': action['href'],
                     'prompt': action.get('prompt', ''),
                     'data': []}
                inputs_ = action['inputs']
                for i in range(len(inputs_)):
                    d = inputs_[i]
                    nm = d.get('name', 'input' + str(i))
                    q['data'].append({
                        'name': nm,
                        'value': d.get('value', None),
                        'prompt': d.get('prompt', nm),
                        'required': d.get('required', False),
                        'readOnly': d.get('readOnly', False),
                        'pattern': d.get('pattern', '')
                    })
                queries.append(q)
        return queries

    item_link_ = item_link()

    data_: List[Dict[str, Any]] = []
    for x, y in obj.items():
        _data_append(data_, x, y)
    collection: Dict[str, Any] = {
        'collection': {
            'href': str(href),
            'items': [{'data': data_,
                       'links': item_links()}],
            'version': '1.0'}}
    if item_link_:
        if 'rel' in item_link_:
            collection['collection']['items'][0]['rel'] = item_link_['rel']
        collection['collection']['items'][0]['href'] = item_link_['href']
    top_level_links_ = top_level_links()
    if top_level_links_:
        collection['collection']['links'] = top_level_links_
    queries_ = queries()
    if queries_:
        collection['collection']['queries'] = queries_
    for action, action_name, rel in ((wstl_builder.find_action(a.name), a.name, a.rel) for a in get_actions_):
        if action is None:
            raise ValueError(f'Invalid action name in get_all_actions {action_name}')
        _set_collection_template(action, collection, obj, 1, rel)
    return [collection]


def expected_opener_body(fixtures: Dict[str, List[HEAObjectDict]], coll: str,
                         wstl_builder: wstl.RuntimeWeSTLDocumentBuilder, include_root=False,
                         get_actions: Optional[List[ActionSpec]] = None,
                         opener_link: Optional[LinkSpec] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Create a Collection+JSON document with the first HEAObject from a mongodb collection in the given data test fixture,
    including an opener link.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param include_root: whether to use absolute URLs or just paths.
    :param get_actions: the actions to include in the body of GET calls.
    :param opener_link: link for an opener choice. If None or omitted, this function will return None.
    :return: a list containing the first object in the fixture and mongodb collection as a Collection+JSON template as
    a dict, or None if no opener link was passed in.
    """
    if opener_link:
        body = expected_one(fixtures, coll, wstl_builder, include_root, get_actions)
        coll_ = body[0]['collection']
        coll_.pop('template', None)
        coll_['href'] = coll_['href'] + '/opener'
        coll_['items'][0]['links'] = [{'prompt': 'Open', 'href': opener_link.url, 'rel': ' '.join(opener_link.rel or [])}]
        logging.getLogger(__name__).debug('Expected opener body is %s', body)
        return body
    else:
        logging.getLogger(__name__).debug('No opener body')
        return None


def expected_one_duplicate_form(fixtures: Dict[str, List[HEAObjectDict]],
                                coll: str,
                                wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                                duplicate_action_name: str,
                                duplicate_action_rel: Optional[List[str]] = None,
                                include_root=False) -> List[Dict[str, Any]]:
    """
    Create a Collection+JSON document with the first HEAObject from the given mongodb collection in the given data test
    fixture. The returned Collection+JSON document will contain the HEAObject in the data section and a template
    for duplicating the HEAObject.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param duplicate_action_name: the name of the service's duplicator action. Required.
    :param duplicate_action_rel: list of rel strings for the action. Optional.
    :param include_root: whether to use absolute URLs or just paths.
    :return: a list of Collection+JSON templates as dicts.
    """
    return _expected_one_form(fixtures, coll, wstl_builder, duplicate_action_name,
                              duplicate_action_rel, include_root, suffix='/duplicator')


def expected_all_wstl(fixtures: Dict[str, List[HEAObjectDict]],
                      coll: str,
                      wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                      include_root: bool = False,
                      get_all_actions: Optional[List[ActionSpec]] = None) -> List[Dict[str, Dict[str, Any]]]:
    """
    Create a run-time WeSTL document from a data test fixture. The document will contain all HEAObject dicts in
    the given collection, and it will contain a single action.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param include_root: whether to use absolute URLs or just paths.
    :param get_all_actions: the actions to include in the body of GET-all calls.
    :return: a run-time WeSTL document as a dict.
    """
    if get_all_actions is None:
        get_all_actions = []

    href_ = wstl_builder.href if wstl_builder.href else ''

    def runtime_actions():
        result = []
        for action, action_name, action_rel, action_url in ((wstl_builder.find_action(a.name), a.name, a.rel, a.url) for
                                                            a in get_all_actions):
            if action is None:
                raise ValueError(f'Action {action_name} does not exist')
            targets = action.get('target', '').split()
            if 'item' in targets:
                href = action_url if action_url else '#'
            else:
                href = action_url if action_url else (
                    str(URL(href_) / '') if include_root else (URL(href_) / '').path)
            action['href'] = href
            action['rel'] = action_rel if action_rel else []
            result.append(action)
        return result

    return [{
        'wstl': {
            'data': _wstl_data_transform(fixtures[coll]),
            'actions': runtime_actions(),
            'title': wstl_builder.design_time_document['wstl']['title'],
            'hea': {'href': href_ if href_ else '#'}
        }
    }]


def expected_all(fixtures: Dict[str, List[HEAObjectDict]], coll: str, wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                 include_root=False, get_all_actions: Optional[List[ActionSpec]] = None) -> List[Dict[str, Any]]:
    """
    Create a list of Collection+JSON documents with all HEAObjects from a mongodb collection in the given data test fixture.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param include_root: whether to use absolute URLs or just paths.
    :param get_all_actions: the actions to include in the body of GET-all calls.
    :return: a list of Collection+JSON dicts.
    """
    if get_all_actions is None:
        get_all_actions = []

    href_ = wstl_builder.href if wstl_builder.href else ''

    def item_links(id_):
        links = []
        for action, rel, url in ((wstl_builder.find_action(a.name), a.rel or [], a.url) for a in get_all_actions):
            targets = action.get('target', '').split()
            if 'item' in targets and 'read' in targets and 'cj' in targets:
                links.append({
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {'id': id_}) if url else (
                        str(URL(href_) / id_) if include_root else str((URL(href_) / id_).path)),
                    'rel': ' '.join(rel)
                })
        return links

    def item_link(id_):
        for action, name, rel, url in ((wstl_builder.find_action(a.name), a.name, a.rel or [], a.url) for a in get_all_actions):
            if action is None:
                raise KeyError(f'No action found with name {name}')
            targets = action.get('target', '').split()
            if 'item' in targets and 'href' in targets and 'cj' in targets:
                return {
                    'prompt': action['prompt'],
                    'href': uritemplate.expand(url, {'id': id_}) if url else (
                        str(URL(href_) / id_) if include_root else str((URL(href_) / id_).path)),
                    'rel': ' '.join(rel),
                    'readOnly': 'true'
                }
        return {}

    def top_level_links():
        links = []
        for action, rel, url in ((wstl_builder.find_action(a.name), a.rel or [], a.url) for a in get_all_actions):
            targets = action.get('target', '').split()
            if action['type'] == 'safe' and 'app' in targets and 'cj' in targets and (
                'inputs' not in action or not action['inputs']):
                links.append({
                    'prompt': action['prompt'],
                    'href': url if url else (
                        str(URL(href_) / '') if include_root else str((URL(href_) / '').path)),
                    'rel': ' '.join(rel)
                })
        return links

    items = []
    for f in fixtures[coll]:
        data_: List[Dict[str, Any]] = []
        id_ = f['id']
        item_link_ = item_link(id_)
        for x, y in f.items():
            _data_append(data_, x, y)
        item = {'data': data_,
                'links': item_links(id_)}
        if item_link_:
            if 'rel' in item_link_:
                item['rel'] = item_link_['rel']
            item['href'] = item_link_['href']
        items.append(item)

    collection_doc = {'collection': {'href': str(wstl_builder.href if wstl_builder.href else '#'),
                                     'items': items,
                                     'version': '1.0'}}
    for action, action_name, rel in ((wstl_builder.find_action(a.name), a.name, a.rel) for a in get_all_actions):
        if action is None:
            raise ValueError(f'Invalid action name in get_all_actions {action_name}')
        _set_collection_template(action, collection_doc, f, len(fixtures[coll]), rel)
    top_level_links_ = top_level_links()
    if top_level_links_:
        collection_doc['collection']['links'] = top_level_links_
    return [collection_doc]


def expected_values(fixtures: Dict[str, List[HEAObjectDict]],
                    coll: str,
                    wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                    duplicate_action_name: str,
                    href: str,
                    include_root=False,
                    get_actions: Optional[List[ActionSpec]] = None,
                    get_all_actions: Optional[List[ActionSpec]] = None,
                    opener_link: Optional[LinkSpec] = None) -> Dict[str, Any]:
    """
    Generate a dict of all of the expected values for passing into the mongotestcase and mockmongotestcase
    get_test_case_cls function.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param duplicate_action_name: the name of the service's duplicator action. Required.
    :param href: the resource's URL. Required. If None, then /{coll} is used as the resource_path.
    :param include_root: whether to use absolute URLs or just paths.
    :param get_actions: optional list of actions for GET calls.
    :param get_all_actions: optional list of actions for GET-all calls.
    :param opener_link: optional link representing a choice for opening the HEA object.
    :return: a dict of keyword argument name -> Collection+JSON dict or WeSTL document dict, where the keyword arguments
    match those of the mongotestcase and mockmongotestcase get_test_case_cls functions.
    """
    wstl_builder_ = copy.deepcopy(wstl_builder)
    wstl_builder_.href = str(href)
    return {
        'body_post': body_post(fixtures, coll),
        'body_put': body_put(fixtures, coll),
        'expected_one_wstl': expected_one_wstl(fixtures, coll, wstl_builder_, get_actions=get_actions,
                                               include_root=include_root),
        'expected_one': expected_one(fixtures, coll, wstl_builder_,
                                     include_root=include_root, get_actions=get_actions),
        'expected_one_duplicate_form': expected_one_duplicate_form(fixtures, coll, wstl_builder_,
                                                                   duplicate_action_name,
                                                                   include_root=include_root),
        'expected_all_wstl': expected_all_wstl(fixtures, coll, wstl_builder_, get_all_actions=get_all_actions,
                                               include_root=include_root),
        'expected_all': expected_all(fixtures, coll, wstl_builder_,
                                     include_root=include_root, get_all_actions=get_all_actions),
        'expected_opener': opener_link.url if opener_link is not None else None,
        'expected_opener_body': expected_opener_body(fixtures, coll, wstl_builder_,
                                                     include_root=include_root, get_actions=get_actions,
                                                     opener_link=opener_link)
    }


def _create_template(d: HEAObjectDict, exclude=('id',)) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    return {'template': {'data': [z for x, y in d.items() if (not exclude or x in exclude) for z in _nvpjson_property_to_cj_part_generator(x, y)]}}


def _set_collection_template(action, collection_doc, fixture, len_fixtures, rel):
    """
    Adds a template object to the provided Collection+JSON document.

    :param action:
    :param collection_doc:
    :param fixture:
    :param len_fixtures:
    :param rel:
    """
    def template_data_generator():
        for i in action['inputs']:
            if 'add' in targets:
                yield {'name': i['name'],
                       'value': _value_append(i['value']),
                       'prompt': i.get('prompt', ''),
                       'required': i.get('required', False),
                       'pattern': i.get('pattern', ''),
                       'readOnly': i.get('readOnly', False)}
            elif len_fixtures == 1:
                nm = i['name']
                val = fixture.get(i['section'], None) if 'section' in i else fixture.get(nm)
                if isinstance(val, list) and len(val) > 0:
                    if 'section' in i:
                        for i_, v in enumerate(val):
                            if nm not in ('meta', 'type'):
                                yield {'name': nm,
                                       'value': _value_append(v[nm]),
                                       'prompt': i.get('prompt', ''),
                                       'required': i.get('required', False),
                                       'pattern': i.get('pattern', ''),
                                       'readOnly': i.get('readOnly', False),
                                       'index': i_,
                                       'section': i['section']}
                    else:
                        if i['name'] not in ('meta', 'type'):
                            yield {'name': nm,
                                   'value': _value_append(val),
                                   'prompt': i.get('prompt', ''),
                                   'required': i.get('required', False),
                                   'pattern': i.get('pattern', ''),
                                   'readOnly': i.get('readOnly', False)}
                elif isinstance(val, dict) and len(val) > 0:
                    if nm not in ('meta', 'type'):
                        yield {'name': nm,
                               'value': _value_append(val[nm]),
                               'prompt': i.get('prompt', ''),
                               'required': i.get('required', False),
                               'pattern': i.get('pattern', ''),
                               'readOnly': i.get('readOnly', False),
                               'section': i['section']}
                elif i['name'] not in ('meta', 'type'):
                    yield {'name': i['name'],
                           'value': _value_append(val),
                           'prompt': i.get('prompt', ''),
                           'required': i.get('required', False),
                           'pattern': i.get('pattern', ''),
                           'readOnly': i.get('readOnly', False)}
            else:
                yield {'name': i['name'],
                       'value': None,
                       'prompt': i.get('prompt', ''),
                       'required': i.get('required', False),
                       'pattern': i.get('pattern', ''),
                       'readOnly': i.get('readOnly', False)}
    targets = action['target'].split()
    if 'cj-template' in targets:
        template = {'data': [d for d in template_data_generator()],
                    'prompt': action.get('prompt', action['name']),
                    'rel': ' '.join(rel) if rel is not None else ''}
        collection_doc['collection']['template'] = template


def _expected_one_form(fixtures: Dict[str, List[HEAObjectDict]],
                       coll: str,
                       wstl_builder: wstl.RuntimeWeSTLDocumentBuilder,
                       action_name: str,
                       action_rel: Optional[List[str]] = None,
                       include_root: bool = False,
                       suffix: str = None) -> List[Dict[str, Any]]:
    """
    Create a Collection+JSON document with the first HEAObject from the given mongodb collection in the given data test
    fixture. The returned Collection+JSON document will contain the HEAObject in the data section and a template
    containing that HEAObject's values.

    :param fixtures: mongodb collection name -> list of HEAObject dicts. Required.
    :param coll: the mongodb collection name to use. Required.
    :param wstl_builder: a runtime WeSTL document builder object. Required.
    :param action_name: the name of the action that causes creation of the template. Required.
    :param action_rel: list of rel strings for the action. Optional.
    :param include_root: whether to use absolute URLs or just paths.
    :return: a list of Collection+JSON templates as dicts.
    """
    action = wstl_builder.find_action(action_name)
    if action is None:
        raise ValueError(f'Action {action_name} does not exist')
    id_ = str(fixtures[coll][0]['id'])
    href = URL(wstl_builder.href if wstl_builder.href else '') / (id_ + (suffix if suffix else ''))
    data_: List[Dict[str, Any]] = []
    for x, y in fixtures[coll][0].items():
        _data_append(data_, x, y)
    return [{
        'collection': {
            'version': '1.0',
            'href': str(href),
            'items': [
                {
                    'data': data_,
                    'links': []}],
            'template': {
                'prompt': action.get('prompt', None),
                'rel': ' '.join(action_rel if action_rel else []),
                'data': _action_to_template_data(action, fixtures[coll][0])}
        }}]


def _wstl_data_transform(data: HEAObjectDictValue) -> HEAObjectDictValue:
    """
    Recursively goes through HEA object dicts, lists of HEA object dicts, primitive lists, and primitives, and replaces
    any enums and dates with strings as if the dicts had been serialized to JSON and deserialized back to dicts.

    :param data: HEA object dict, list of HEA object dicts, primitive list, or primitive.
    :return: a deep copy of the same data except with enums and dates replaced with strings.
    """
    if is_heaobject_dict_list(data):
        return [cast(MemberObjectDict, _wstl_data_transform(elt)) for elt in cast(List[MemberObjectDict], data)]
    elif is_heaobject_dict(data):
        return {x: cast(Union[Primitive, List[Primitive]], _wstl_data_transform(y)) for x, y in cast(MemberObjectDict, data).items()}
    elif is_primitive_list(data):
        return [cast(Primitive, _wstl_data_transform(d)) for d in cast(List[Primitive], data)]
    elif is_primitive(data):
        if isinstance(data, Enum):
            return str(data)
        elif isinstance(data, date):
            return data.isoformat()
        else:
            return data
    else:
        raise ValueError(str(data))


def _data_append(data: List[Dict[str, Any]], x: str, y: HEAObjectDictValue):
    if x != 'type':
        if is_heaobject_dict(y):
            for xprime, yprime in cast(HEAObjectDict, y).items():
                if xprime != 'type':
                    _data_append_part(data, xprime, yprime, {'section': x})
        elif is_heaobject_dict_list(y):
            for i, yprime_ in enumerate(cast(List[HEAObjectDict], y)):
                for xprimeprime, yprimeprime in yprime_.items():
                    if xprimeprime != 'type':
                        _data_append_part(data, xprimeprime, yprimeprime, {'section': x, 'index': i})
        elif is_primitive(y) or is_primitive_list(y):
            _data_append_part(data, x, y)
        else:
            raise ValueError(f'{x}.{y}')


def _value_append(yy: HEAObjectDictValue) -> HEAObjectDictValue:
    if isinstance(yy, Enum):
        return str(yy)
    elif isinstance(yy, (date, time)):
        return yy.isoformat()
    else:
        return yy


def _data_append_part(data_: List[Dict[str, Any]], x: str, y: HEAObjectDictValue, extra: Optional[Dict[str, Any]] = None):
    if isinstance(y, list):
        y_: Any = [_value_append(yy) for yy in y]
    else:
        y_ = _value_append(y)
    if not extra:
        extra = {}
    data_.append({
        'display': False if x == 'id' else True,
        'name': x,
        'prompt': x,
        'value': y_,
        **extra
    })


def _action_to_template_data(action, f):
    return [{'name': d['name'],
         'pattern': d.get('pattern', ''),
         'prompt': d.get('prompt', None),
         'readOnly': d.get('readOnly', False),
         'required': d.get('required', False),
         'value': _value_append(f.get(d['name'], None))} for d in action['inputs']]


def _nvpjson_property_to_cj_part_generator(section_or_name, value):
    if is_heaobject_dict(value):
        for xprime, yprime in value.items():
            yield {'name': xprime, 'value': yprime, 'section': section_or_name}
    elif is_primitive(value) or is_primitive_list(value):
        yield {'name': section_or_name, 'value': value}
    elif is_heaobject_dict_list(value):
        for i, yprime in enumerate(value):
            for xprimeprime, yprimeprime in yprime.items():
                yield {'name': xprimeprime, 'value': yprimeprime, 'section': section_or_name, 'index': i}
    else:
        raise ValueError(f'{section_or_name}.{value}')

