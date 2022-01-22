"""
Collection+JSON representor. It converts a WeSTL document into Collection+JSON form. The Collection+JSON spec is at
http://amundsen.com/media-types/collection/. HEA implements the spec with the following exceptions:
* Data array:
** A section property. When going to/from nvpjson, the nvpjson object will have properties for each section,
each of which will have a nested object with the properties in that section.
** A sectionPrompt property for displaying a section name.
** Periods are reserved and should not be used in name property values.
"""

import uritemplate
import logging
import operator
from itertools import groupby
from heaobject import root
from heaobject.root import is_heaobject_dict, is_heaobject_dict_list, is_primitive_list, is_primitive
from json.decoder import JSONDecodeError
from .error import ParseException, FormatException
from .. import jsonschemavalidator
from aiohttp.web import Request
from typing import Any, Union, Dict, List, Optional, Type, Tuple, Generator, Callable
from .representor import Representor, Link


MIME_TYPE = 'application/vnd.collection+json'


class CJ(Representor):
    MIME_TYPE = MIME_TYPE

    @classmethod
    def supports_links(cls) -> bool:
        """
        The CJ representor supports links.

        :return: True
        """
        return True

    async def formats(self, request: Request,
                      wstl_obj: Union[List[Dict[str, Any]], Dict[str, Any]],
                      dumps=root.json_dumps,
                      link_callback: Callable[[int, Link], None] = None) -> bytes:
        """
        Formats a run-time WeSTL document as a Collection+JSON document.

        :param request: the HTTP request.
        :param wstl_obj: dict with run-time WeSTL JSON, or a list of run-time WeSTL JSON dicts.
        :param dumps: any callable that accepts dict with JSON and outputs str. Cannot be None. By default, it uses
        the heaobject.root.json_dumps function, which dumps HEAObjects and their attributes to JSON objects. Cannot
        be None.
        :param link_callback: a callable that will be invoked whenever a link is created. Links can be
        specific to a data item in the wstl_obj's data list or "global" to the entire data list. The
        first parameter contains the index of the data item, or None if the link is global. The second
        parameter contains the link as a heaserver.service.representor.Link object. The purpose of this
        callback is to access parameterized links after their parameters have been filled in.
        :return: str containing Collection+JSON collection JSON.
        :raises FormatException: if an error occurs formatting the WeSTL document as Collection+JSON.
        """
        def cj_generator() -> Generator:
            for w in (wstl_obj if isinstance(wstl_obj, list) else [wstl_obj]):
                yield self.__format(request, w, link_callback)
        return dumps(list(c for c in cj_generator())).encode('utf-8')

    async def parse(self, request: Request) -> Dict[str, Any]:
        """
        Parses an HTTP request containing a Collection+JSON template JSON document body into a dict-like object.

        :param request: the HTTP request. Cannot be None.
        :return: the data section of the Collection+JSON document transformed into a dict.
        :raises ParseException: if an error occurs parsing Collection+JSON into a dict-like object.
        """
        try:
            return to_nvpjson(await request.json())
        except (JSONDecodeError, jsonschemavalidator.ValidationError) as e:
            raise ParseException() from e

    @staticmethod
    def __format(request: Request, wstl_obj: Dict[str, Any], link_callback: Callable[[int, Link], None]=None) -> Dict[str, Any]:
        """
        Formats a run-time WeSTL document as a Collection+JSON document.

        :param request: the HTTP request.
        :param wstl_obj: dict with run-time WeSTL JSON.
        :param coll_url: the URL of the collection.
        :param link_callback: a callable that will be called whenever a link is created. The first
        parameter contains the index of the item, or None if the link is global. The second parameter
        contains the link as a heaserver.service.representor.Link object.
        :return: a Collection+JSON dict.
        """
        wstl = wstl_obj['wstl']
        collection: Dict[str, Any] = {}
        collection['version'] = '1.0'
        collection['href'] = wstl.get('hea', {}).get('href', '#')

        content = _get_content(wstl)
        if content:
            collection['content'] = content

        items, tvars = _get_items(request, wstl, link_callback=link_callback)
        if items:
            collection.setdefault('items', []).extend(items)
        links = _get_links(wstl.get('actions', []), tvars, link_callback=link_callback)
        if links:
            collection.setdefault('links', []).extend(links)
        if 'template' not in collection:
            template = _get_template(wstl.get('actions', []), tvars)
            if template:
                collection['template'] = template

        queries = _get_queries(wstl.get('actions', []))
        if queries:
            collection.setdefault('queries', []).extend(queries)

        if 'error' in wstl:
            collection['error'] = _get_error(wstl['error'])

        return {'collection': collection}


def to_nvpjson(cj_template: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Converts a Collection+JSON template dict into a nvpjson object dict.

    :param cj_template: a dict
    :return: nvpjson
    :raises jsonschemavalidator.ValidationError if invalid Collection+JSON was passed in.
    """
    jsonschemavalidator.CJ_TEMPLATE_SCHEMA_VALIDATOR.validate(cj_template)
    data = cj_template['template'].get('data', [])
    result: Dict[str, Any] = {}
    triplets = []
    for d in data:
        nm = d['name']
        val = d.get('value', None)
        section = d.get('section', None)
        index = d.get('index', None)
        if section is not None and index is not None:
            triplets.append((section, index, nm, val))
        elif section is not None:
            result.setdefault(section, {})[nm] = val
        else:
            result[nm] = val
    if triplets:
        triplets.sort(key=operator.itemgetter(0, 1))
        for nm, val in groupby(triplets, operator.itemgetter(0)):  # by section
            result[nm] = [dict(x[2:] for x in e) for _, e in groupby(val, operator.itemgetter(1))]  # by index
    return result


def _get_content(obj):
    return obj.get('content', {})


def _get_links(actions: List[Dict[str, Any]], tvars: Dict[str, Any]=None, link_callback: Callable[[int, Link], None]=None):
    """
    Get top-level links.
    :param actions: iterator of actions.
    :return:
    """
    rtn = []
    for i, link in enumerate(actions):
        if link['type'] == 'safe' \
            and 'app' in link['target'] \
                and 'cj' in link['target'] \
                    and ('inputs' not in link or not link['inputs']):
            url = uritemplate.expand(link['href'], tvars)
            l = {
                'href': url,
                'rel': ' '.join(link['rel']) or '',
                'prompt': link.get('prompt', '')
            }
            rtn.append(l)
            if link_callback:
                link_callback(i, Link(href=url, rel=link['rel'], prompt=link.get('prompt')))
    return rtn


def _get_items(request: Request, wstl_obj: Dict[str, Any], link_callback: Callable[[int, Link], None]=None) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rtn = []
    tvars = {}
    data_len = len(wstl_obj.get('data', []))
    coll = wstl_obj.get('data', [])
    logger = logging.getLogger(__package__)
    logger.debug('%d item(s)', data_len)
    for temp in coll:
        item: Dict[str, Any] = {}
        data: List[Dict[str, Any]] = []
        type_str: Optional[str] = temp.get('type', None)
        if type_str:
            type_: Optional[Type[root.HEAObject]] = root.type_for_name(type_str)
        else:
            type_ = None
        local_tvars = {}
        for k, v in temp.items():
            if is_heaobject_dict(v) and len(v) > 0:
                for kprime, vprime in v.items():
                    if kprime not in ('meta', 'type'):
                        data.append({
                            'section': k,
                            'name': kprime,
                            'value': vprime,
                            'prompt': type_.get_prompt(kprime) if type_ else None,
                            'display': type_.is_displayed(kprime) if type_ else None
                        })
                        if data_len == 1:
                            tvars[f'{k}.{kprime}'] = vprime
                        local_tvars[f'{k}.{kprime}'] = vprime
                if data_len == 1:
                    tvars[f'{k}'] = v
                local_tvars[f'{k}'] = v
            elif is_heaobject_dict_list(v) and len(v) > 0:
                v__ = False
                v__prime = False
                if len(v) == 0:
                    v__ = True
                else:
                    for i, v_ in enumerate(v):
                        if isinstance(v_, dict):
                            v__prime = True
                            for kprime, vprime in v_.items():
                                if kprime != 'meta' and kprime != 'type':
                                    data.append({
                                        'section': k,
                                        'index': i,
                                        'name': kprime,
                                        'value': vprime,
                                        'prompt': type_.get_prompt(kprime) if type_ else None,
                                        'display': type_.is_displayed(kprime) if type_ else None
                                    })
                                    if data_len == 1:
                                        tvars[f'{k}.{kprime}.{i}'] = vprime
                                    local_tvars[f'{k}.{kprime}.{i}'] = vprime
                        else:
                            v__ = True
                if v__ and v__prime:
                    raise FormatException('List may not have a mixture of values and objects')
                if v__:
                    data.append({
                        'name': k,
                        'value': v,
                        'prompt': type_.get_prompt(k) if type_ else None,
                        'display': type_.is_displayed(k) if type_ else None
                    })
                if data_len == 1:
                    tvars[f'{k}'] = v
                local_tvars[f'{k}'] = v
            elif is_primitive(v) or is_primitive_list(v):
                if k != 'meta' and k != 'type':
                    data.append({
                        'name': k,
                        'value': v,
                        'prompt': type_.get_prompt(k) if type_ else None,
                        'display': type_.is_displayed(k) if type_ else None
                    })
                    if data_len == 1:
                        tvars[k] = v
                    local_tvars[k] = v
            else:
                raise ValueError(f'Primitive property {k}={v} of type {type(v)} is not allowed; allowed types are {", ".join(str(s) for s in root.PRIMITIVE_ATTRIBUTE_TYPES)}')
        item['data'] = data
        local_tvars.update(request.match_info)
        logger.debug('local_tvars=%s', local_tvars)

        link = _get_item_link(wstl_obj['actions'], link_callback=link_callback)
        if link:
            if isinstance(link['rel'], list):
                item['rel'] = ' '.join(link['rel'])
            else:
                item['rel'] = link['rel']
            if 'href' in link:
                item['href'] = uritemplate.expand(link['href'], local_tvars)

        item['links'] = _get_item_links(wstl_obj['actions'], local_tvars, link_callback=link_callback)

        rtn.append(item)
    tvars.update(request.match_info)
    logger.debug('tvars=%s', tvars)
    return rtn, tvars


def _get_queries(actions: List[Dict[str, Any]]):
    rtn = []
    for action in actions:
        if 'inputs' in action and action['type'] == 'safe' and \
                _is_in_target('list', action) and _is_in_target('cj', action):
            q = {'rel': ' '.join(action['rel']), 'href': action['href'], 'prompt': action.get('prompt', ''), 'data': []}
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
            rtn.append(q)
    return rtn


def _get_template(actions: List[Dict[str, Any]], tvars: Dict[str, Any]):
    rtn = {}
    for action in actions:
        if _is_in_target('cj-template', action):
            is_add = _is_in_target('add', action)

            rtn['prompt'] = action.get('prompt', action['name'])
            rtn['rel'] = ' '.join(action['rel'])

            rtn['data'] = []
            for d in action['inputs']:
                nm = d['name']
                if is_add:
                    value_ = d.get('value', None)
                elif 'section' in d:
                    value_ = tvars.get(f'{d["section"]}')
                else:
                    value_ = tvars.get(nm, None)
                if is_heaobject_dict_list(value_) and len(value_) > 0:
                    if 'section' not in d:
                        data_ = {
                            'name': d['name'],
                            'value': value_,
                            'prompt': d.get('prompt', nm),
                            'required': d.get('required', False),
                            'readOnly': d.get('readOnly', False),
                            'pattern': d.get('pattern', '')
                        }
                        rtn['data'].append(data_)
                    else:
                        for i, v in enumerate(value_):
                            data_ = {
                                'section': d['section'],
                                'index': i,
                                'name': d['name'],
                                'value': v[d['name']],
                                'prompt': d.get('prompt', nm),
                                'required': d.get('required', False),
                                'readOnly': d.get('readOnly', False),
                                'pattern': d.get('pattern', '')
                            }
                            rtn['data'].append(data_)
                elif is_heaobject_dict(value_) and len(value_) > 0:
                    data_ = {
                        'section': d['section'],
                        'name': d['name'],
                        'value': value_[d['name']],
                        'prompt': d.get('prompt', nm),
                        'required': d.get('required', False),
                        'readOnly': d.get('readOnly', False),
                        'pattern': d.get('pattern', '')
                    }
                    rtn['data'].append(data_)
                elif is_primitive(value_) or is_primitive_list(value_):
                    data_ = {
                        'name': nm,
                        'value': value_,
                        'prompt': d.get('prompt', nm),
                        'required': d.get('required', False),
                        'readOnly': d.get('readOnly', False),
                        'pattern': d.get('pattern', '')
                    }
                    rtn['data'].append(data_)
                else:
                    raise ValueError(value_)
            break
    return rtn


def _get_item_links(actions: List[Dict[str, Any]], tvars: Dict[str, Any], link_callback: Callable[[int, Link], None]=None):
    coll = []
    for i, action in enumerate(actions):
        target = action['target']
        if 'item' in target and 'read' in target and 'cj' in target:
            href = uritemplate.expand(action['href'], tvars)
            if link_callback:
                link_callback(i, Link(href=href, rel=action['rel'], prompt=action['prompt']))
            coll.append({
                'prompt': action['prompt'],
                'rel': ' '.join(action['rel']),
                'href': href
            })
    return coll


def _get_item_link(actions: List[Dict[str, Any]], link_callback: Callable[[int, Link], None]=None):
    rtn = {}
    for i, action in enumerate(actions):
        target = action['target']
        if 'item' in target and 'href' in target and 'cj' in target:
            rtn['rel'] = ' '.join(action['rel'])
            rtn['href'] = action['href']
            if link_callback:
                link_callback(i, Link(href=action['href'], rel=action['rel']))
            break
    return rtn


def _get_error(obj):
    return {'title': 'Error', 'message': obj.message or '', 'code': obj.code or '', 'url': obj.url or ''}


def _is_in_target(str_: str, action: Dict[str, Any]):
    return str_ in action['target'].split(' ')
