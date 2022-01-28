#coding:utf-8
from flask import current_app, url_for, request
from flask_login import AnonymousUserMixin, current_user
from pydantic.types import constr
from user_agents import parse
from blinker import Signal
from datetime import datetime, date
from slugify import slugify 
from loguru import logger
from json import dumps, loads
from urllib.parse import unquote
import random
import string
import dateutil.parser
import hashlib
import pycountry
import os
import hashlib
import shortuuid
from pydantic import BaseModel, validator, EmailStr, conint, conlist, HttpUrl
from typing import Optional, List
from cryptography.fernet import Fernet


class UndefinedEntityAttribute(Exception):
    pass


class DateTimeField(list):
    pass


class BaseEntity(object):
    _schemas = {}
    _doc = {}
    _id = None

    def _validate(self, doc):
        res = dict()

        # remove not schema attrs
        for k, v in doc.items():
            if k in self._schemas.keys():
                res[k] = v

        doc = res

        for k in self._schemas.keys():
            v = doc.get(k)
            try:
                res[k] = self.__class__.format_attribute(v, self._schemas[k])
            except Exception as e:
                logger.error('Attribute ({0}): {1}'.format(k, str(e)))
                raise e

        return res

    def __init__(self, doc, _id):
        self._doc = self._validate(doc)
        self._id = _id

    def __repr__(self):
        return self._id

    def __getattr__(self, item):
        if item in self._schemas.keys():
            return self._doc.get(item, '')
        elif item in ['__html__']:
            raise AttributeError
        elif item in ['__func__', '__self__']:
            pass
        else:
            raise UndefinedEntityAttribute(item)

    def __setattr__(self, item, value):
        if item in self._schemas.keys():
            self._doc[item] = value
        else:
            self.__dict__[item] = value

    def to_dict(self):
        return self._doc

    # CLASS METHODS
    @classmethod
    def get_random_string(cls, _len):
        return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(_len)) 

    @classmethod
    def get_urlsafe_string(cls, _len):
        return shortuuid.ShortUUID().random(length=_len)

    @classmethod
    def format_attribute(cls, v, t):
        res = None

        if t == str:
            if isinstance(v, list):
                res = ", ".join(v)
            else:
                res = str(v).strip() if v else ''
        elif t == DateTimeField:
            if v:
                if isinstance(v, (date, datetime)):
                    res = v
                else:
                    res = dateutil.parser.isoparse(v)
        elif t == bool:
            res = bool(v)
        elif t == int:
            res = int(v) if v or v == 0 else None
        elif t == float:
            res = float(v) if v or v == 0 else None
        elif t == list:
            if v:
                v = v if type(v) == list else v.split(',')
                res = [item.strip() if type(item) in [str] else item for item in v]
            else:
                res = list()
        elif t == dict:
            if type(v) == dict:
                res = v
            else:
                res = dict()

        return res    


class ElasticEntity(BaseEntity):
    on_ready = Signal()
    on_pre_put = Signal()
    on_put = Signal()
    on_delete = Signal()

    @classmethod
    def generate_id(cls, *args):
        return hashlib.sha224(":".join([str(item) for item in args]).encode('utf-8')).hexdigest()

    @classmethod
    def _table(cls):
        return "{0}.v1".format(cls.__name__.lower())

    @classmethod
    def get(cls, _id=None, _count=10, _offset=0, _sort=[], _process=True, _source=None, _exclude=[], _all=False, _random=False, _range=None, **kwargs):
        if _id:
            resp = current_app.es.get(index=cls._table(), id=_id, ignore=[400, 404])
            logger.debug(u'GET: {0}'.format(resp))
            if resp.get('found'):
                doc = resp['_source']
                if doc:
                    obj = cls(doc, _id)
                    cls.on_ready.send(obj)
                    return [obj], 1
        elif not _id:
            def pre_field(k, v):
                return k if isinstance(v, bool) else '{0}.keyword'.format(k)
            must = [{"terms" if isinstance(v, list) else "term": {pre_field(k, v): v}} for k, v in kwargs.items()]

            if _range:
                _f, _s, _e, _tz = _range
                must.append({"range": {_f: {"gte": _s, "lte": _e, "time_zone": _tz}}})

            qbool = {
                "must": must
            }

            if _exclude:
                qbool['must_not'] = [
                    {'ids': {'values': _exclude}}
                ]

            if _random:
                def get_func():
                    flist = []
                    flist.append({
                        "random_score": {
                            "field": "_seq_no"
                        }
                    })
                    return flist

                q = {
                    "query": {
                        "function_score": {
                            "query": {
                                "bool": qbool
                            },
                            "boost": 1,
                            "boost_mode": "multiply",
                            "functions": get_func()
                        }
                    },
                    "size": _count,
                    "sort" : _sort,
                }
            else:
                q = {
                    "query": {
                        "bool": qbool
                    },
                    "size": _count,
                    "from": _offset,
                    "sort" : _sort,
                }
                
            if _source:
                q['_source'] = _source

            res = []
            found = 0

            if _all:
                _sid = None

                while True:
                    if _sid:
                        resp = current_app.es.scroll(scroll_id=_sid, scroll='20m') 
                    else:
                        resp = current_app.es.search(index=cls._table(), body=q, request_timeout=60, scroll='20m', ignore=[400, 404])

                    _sid = resp.get('_scroll_id')
                    if _sid is None or len(resp['hits']['hits']) == 0:
                        break

                    res += cls.process(resp['hits']['hits']) if _process else cls.format_source(resp['hits']['hits'])
                    found = resp['hits']['total']['value']
            else:
                resp = current_app.es.search(index=cls._table(), body=q, request_timeout=60, ignore=[400, 404])
                # logger.debug(u'RESPONSE: {0}'.format(resp))

                if 'status' in resp and resp['status'] in [400, 404]:
                    return [], 0

                logger.debug(u'RESPONSE took: {0}'.format(resp['took']))

                res = cls.process(resp['hits']['hits']) if _process else cls.format_source(resp['hits']['hits'])
                found = resp['hits']['total']['value']
            return res, found
        return [], 0

    @classmethod
    def process(cls, data):
        logger.debug(u'START process result')
        res = []
        for item in data:
            obj = cls(item['_source'], item['_id'])
            cls.on_ready.send(obj)
            res.append(obj)
        logger.debug(u'END process result')
        return res

    @classmethod
    def format_source(cls, data):
        res = []
        for item in data:
            for k, v in cls._schemas.items():
                if k in item['_source'] and item['_source'][k]:
                    if v == DateTimeField:
                        item['_source'][k] = f"{item['_source'][k]}Z"
            res.append(item)
        return res

    @classmethod
    def put(cls, _id, doc, _refresh=True, _signal=True):
        obj = cls(doc, _id)
        cls.on_pre_put.send(obj)
        resp = current_app.es.update(index=cls._table(), id=obj._id, body={'doc': obj.to_dict(), 'doc_as_upsert': True}, refresh=_refresh, retry_on_conflict=3)
        logger.debug(u'PUT: {0}'.format(resp))
        if _signal:
            cls.on_put.send(obj, response=resp)
        return resp, obj

    @classmethod
    def delete(cls, _id, _refresh=True, _signal=True):
        resp = current_app.es.delete(index=cls._table(), id=_id, refresh=_refresh, ignore=[404])
        if _signal:
            cls.on_delete.send(response=resp)
        return resp

    # @classmethod
    # def process_response(cls, _items):
    #     return [dict(item.to_dict(), **dict(_id=item._id)) for item in _items]


class Page(ElasticEntity):
    on_put = Signal()

    _schemas = {     
        'project': str, 
        'suggest': str, # search_as_you_type
        'path': str,                                                                                                                
        'category': str,
        'locale': str,
        'locale_available': list, # for lang version
        'source_chain': list,
        'api_source': str,
        'alias': str,
        'title': str,
        'alt_title': str,
        'publishedon': DateTimeField,
        'updatedon': DateTimeField,
        'is_active': bool,
        'is_redirect': bool,
        'redirect': str,
        'redirect_geo': list,
        'is_searchable': bool,
        'meta_title': str,
        'meta_description': str,
        'meta_image': str,
        'breadcrumbs': list,
        'views_count': int,
        'activity_count': int,
        'authors': str,
        'template': str,
        'parent': str,
        'order': int,
        'overview': str,
        'content': str,
        'custom_text': str,
        'has_toc': bool,
        'attachs': list,
        'software': list,
        'rating': int,
        'boost': float,
        'rank': int,
        'default_currency': str,
        'faq': list,
        'is_commented': bool,
        'comments': list,
        'is_amp': bool,

        'tags': list, # for page: news, category
        'cover': str, # for page: collection, provider, page

        'screen': str,
        'themes': list,
        'releasedon': DateTimeField,
        'volatility': list,
        'rtp': float,
        'slot_pros': list,
        'slot_cons': list,
        'slot_features': list,
        'layout': list,
        'lines': int,
        'is_coins': bool,
        'min_bet': float,
        'max_bet': float,
        'max_win': int,
        'is_jackpot': bool,
        'jackpot': float,
        'is_freeplay': bool,
        'freeplay_url': str,
        'related': list,
        'preferred': list,

        'intro': str,
        'is_new': bool,
        'is_featured': bool,
        'is_sponsored': bool,
        'owner': str,
        'status': str, # status approve: draft, in review, published (manager editor mode)
        'is_draft': bool,
        'is_sandbox': bool,
        'user_rating': float,
        'games_count': int,
        'operator': str,
        'establishedon': DateTimeField,
        'affiliate': str,
        'affiliate_contact': str,
        'affiliate_email': str,
        'affiliate_ref': str,
        'website': str,
        'ref_link_geo': list,
        'ref_link': str,
        'ref_link_tc': str,
        'theme_color': str,
        'logo': str,
        'logo_white': str,
        'logo_small': str,
        'services': list,
        'games': list,
        'provider_tags': list,
        'provider_pros': list,
        'provider_cons': list,
        'licences': list,
        'licences_info': list,
        'languages': list,
        'support_languages': list,
        'support_livechat': bool,
        'support_email': str,
        'support_phone': str,
        'support_worktime': str,
        'currencies': list,
        'deposits': list,
        'withdrawal': list,
        'min_deposit': int,
        'min_withdrawal': int,
        'cashiers_limits': list,
        'games_limits': list,
        'withdrawal_time': list,
        'withdrawal_limits': list,
        'withdrawal_monthly': int,
        'withdrawal_weekend': bool,
        'kyc_deposit': bool,
        'kyc_withdrawal': bool,
        'welcome_package': str,
        'welcome_package_geo': list,
        'welcome_package_max_bonus': int,
        'welcome_package_match': int,
        'welcome_package_note': str,
        'welcome_package_wager': int,
        'wager_type': str,
        'welcome_package_fs': int,
        'welcome_package_min_dep': int,
        'no_deposit_fs': int,
        'no_deposit_note': str,
        'cashback': int,
        'promotions': list,
        'geo_blacklist': str,
        'geo_whitelist': str,
        'geo_priority': list,
        'geo': list,
        'external_id': str,
        'rank_alexa': int,
        'applications': list,
        'applications_review': str,

        'collection': list,
        'collection_category': str,
        'collection_mode': str,
        'collection_is_current_geo': bool,
        'collection_is_readonly': bool,
        'collection_is_static': bool,
        'collection_is_recommends': bool,
        'collection_paging': str,
        'collection_cpp': int,
        'collection_sort': str,
        'collection_sort_direction': str,
        'collection_column_title': str
    }

    @classmethod
    def _table(cls):
        return "{0}_page.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))

    @classmethod
    def process_country(cls, _clist):
        _c = []
        _m = []
        if len(_clist):
            for item in _clist:
                item = item.strip()
                if item:
                    _cn = None
                    if len(item) == 2:
                        _cn = pycountry.countries.get(alpha_2=item.upper())
                    else:
                        _cn = pycountry.countries.get(name=item)
                    if not _cn:
                        try:
                            _found = pycountry.countries.search_fuzzy(item)
                            if len(_found) == 1:
                                _cn = _found[0]
                            else:
                                _m.append({'term': item, 'options': [{'name': c.name, 'iso': c.alpha_2} for c in _found]})
                        except LookupError:
                            _m.append({'term': item, 'options': []})
                    if _cn:
                        _c.append(_cn.name)
        return _c, _m
                
    @classmethod
    def get_countries(cls, w, b):
        geo_wl = w.split(",")
        geo_bl = b.split(",")

        _countries_wl, _m1 = cls.process_country(geo_wl)
        _countries_bl, _m2 = cls.process_country(geo_bl)
                    
        if len(_countries_wl) == 0:
            _countries_wl = [_cn.name for _cn in pycountry.countries]

        _countries = list(set(_countries_wl) - set(_countries_bl))
        _countries.sort()
        _messages = {'w': _m1, 'b': _m2}

        return _countries, _messages, len(_m1 + _m2) > 0
    
    @classmethod
    def get_options(cls):
        _cnt = 500

        aggs = {
            "tags": {
                "terms": {
                    "field": "tags.keyword",
                    "size": _cnt
                }
            },
            "software": {
                "terms": {
                    "field": "software.keyword",
                    "size": _cnt
                }
            },
            "currencies": {
                "terms": {
                    "field": "currencies.keyword",
                    "size": _cnt
                }
            },
            "games": {
                "terms": {
                    "field": "games.keyword",
                    "size": _cnt
                }
            },
            "provider_tags": {
                "terms": {
                    "field": "provider_tags.keyword",
                    "size": _cnt
                }
            },
            "provider_pros": {
                "terms": {
                    "field": "provider_pros.keyword",
                    "size": _cnt
                }
            },
            "provider_cons": {
                "terms": {
                    "field": "provider_cons.keyword",
                    "size": _cnt
                }
            },
            "licences": {
                "terms": {
                    "field": "licences.keyword",
                    "size": _cnt
                }
            },
            "languages": {
                "terms": {
                    "field": "languages.keyword",
                    "size": _cnt
                }
            },
            "support_languages": {
                "terms": {
                    "field": "support_languages.keyword",
                    "size": _cnt
                }
            },
            "deposits": {
                "terms": {
                    "field": "deposits.keyword",
                    "size": _cnt
                }
            },
            "withdrawal": {
                "terms": {
                    "field": "withdrawal.keyword",
                    "size": _cnt
                }
            },
            # slot
            "themes": {
                "terms": {
                    "field": "themes.keyword",
                    "size": _cnt
                }
            },
            "slot_pros": {
                "terms": {
                    "field": "slot_pros.keyword",
                    "size": _cnt
                }
            },
            "slot_cons": {
                "terms": {
                    "field": "slot_cons.keyword",
                    "size": _cnt
                }
            },
            "slot_features": {
                "terms": {
                    "field": "slot_features.keyword",
                    "size": _cnt
                }
            },
            "layout": {
                "terms": {
                    "field": "layout.keyword",
                    "size": _cnt
                }
            },
            "authors": {
                "terms": {
                    "field": "authors.keyword",
                    "size": _cnt
                }
            },
        }        

        q = {
            "query": {
                "match_all": {}
            },
            "size": 0,
            "aggs": aggs
        }

        resp = current_app.es.search(index=cls._table(), body=q, request_timeout=60, ignore=[400, 404])

        aggs = {}
        if 'status' in resp and resp['status'] in [400, 404]:
            pass
        else:
            aggs = resp.get('aggregations', [])            

        def process(items, key):
            if key in items:
                return [item['key'].strip() for item in items[key]['buckets'] if item['key'].strip()]
            return []

        opts = {
            'authors': process(aggs, 'authors'),
            'custom_templates': [],
            'currency': process(aggs, 'currencies'),
            'provider_tags': process(aggs, 'provider_tags'),
            'provider_pros': process(aggs, 'provider_pros'),
            'provider_cons': process(aggs, 'provider_cons'),
            'software': process(aggs, 'software'),
            'licences': process(aggs, 'licences'),
            'languages': list(set(process(aggs, 'languages') + process(aggs, 'support_languages'))),
            'payment_methods': list(set(process(aggs, 'deposits') + process(aggs, 'withdrawal'))),
            'games': process(aggs, 'games'),

            'themes': process(aggs, 'themes'),
            'slot_pros': process(aggs, 'slot_pros'),
            'slot_cons': process(aggs, 'slot_cons'),
            'slot_features': process(aggs, 'slot_features'),
            'layout': process(aggs, 'layout'),

            'tags': process(aggs, 'tags'),

            'countries': [{'iso': item.alpha_2, 'country': item.name} for item in pycountry.countries],
            'countries_name': [item.name for item in pycountry.countries],
            'services': ['casino', 'poker', 'betting', 'lotto', 'bingo'],
            'status': ['published', 'draft', 'on_review'],
            'category': ['provider', 'slot', 'page', 'collection'],
            'collection_category': ['provider', 'slot'],
            'wager_types': ['xb', 'x(d+b)'],
            'volatility': ['Low', 'Medium', 'High'],
            'media_presets': [
                'origin', 
                'square_w50', 
                'slogo_w150', 
                'logo_w250', 
                'cover_w300', 
                'cover_w300_h200', 
                'content_w700',
                'meta_w1200_h630'
            ],
            'media_rename': ['none', 'entity', 'hash'],
            'promo_types': ['Welcome Bonus', '1st Deposit Bonus', '2nd Deposit Bonus', '3rd Deposit Bonus', '4th Deposit Bonus', 'No Deposit', 'Cashback', 'Freespins'],
            'promo_tags': ['Exclusive'],
            'apps': ['google_play', 'app_store'],
            'times': ['ewallets', 'cards', 'bank', 'cryptocurrency'],
            'limits': ['transaction', 'day', 'week', 'month'],
            'game_types': ['slots', 'roulette', 'blackjack'],
            'locale': [],
            'bgcolor': [],
            'collection_mode': [], # 'Best', 'New', 'Software'
            'collection_params': [
                'software:select:software', 
                'geo:select:countries_name',
                'deposits:select:payment_methods', 
                'withdrawal:select:payment_methods', 
                'services:select:services', 
                'games:select:games', 
                'licences:select:licences', 
                'provider_tags:select:provider_tags', 
                'languages:select:languages', 
                'currencies:select:currency',
                'operator:str', 
                'affiliate:str', 
                'is_searchable:bool',
                'is_new:bool',
                'is_featured:bool',
                'is_sponsored:bool',
                'withdrawal_weekend:bool',
                'kyc_deposit:bool',
                'kyc_withdrawal:bool',
                'themes:select:themes',
                'slot_features:select:slot_features',
                'is_jackpot:bool',
            ],
            'collection_sort': ['Func_1', 'Func_2', 'Rate', 'Rank', 'Views', 'Activity', 'Alexa', 'Adding', 'AZ', 'Launched', 'RTP', 'MaxWin', 'Jackpot', 'Min.Deposit'],
            'collection_sort_direction': ['Desc', 'Asc'],
            'collection_paging': ['FirstPage', 'Paging'],
        }
        
        return opts

    @property
    def software_key(self):
        if self.category == 'slot' and self.software:
            return slugify(self.software[0], separator='').lower()
        return None

    @classmethod
    def query(cls, query, is_full=False, locale='en', category=[], in_locale=None, count=10):
        if not query:
            return []

        must = [
            {"multi_match" : {
                "query": query, 
                "type": "bool_prefix",
                "fields": [
                    "suggest",
                    "suggest._2gram",
                    "suggest._3gram",
                    "alias"
                ] 
            }}
        ]
        if not is_full:
            must += [
                {"term": {"is_active": True}},
                {"term": {"is_searchable": True}},
                {"term": {"is_redirect": False}},
                {"term": {"is_draft": False}},
                {"term": {"is_sandbox": False}},
            ]
            if locale:
                must.append({"term": {"locale.keyword": locale}})
            if category:
                must.append({"terms": {"category.keyword": category}})
            if in_locale:
                must.append({"term": {"locale_available.keyword": in_locale}})

        q = {
            "query": {
                "bool": {
                    "must": must
                }
            },
            "size": count
        }

        resp = current_app.es.search(index=cls._table(), body=q, request_timeout=60, ignore=[404])

        for item in resp['hits']['hits']:
            obj = cls(item['_source'], item['_id'])
            cls.on_ready.send(obj)
            yield obj

    @property
    def visit_url(self):
        return url_for('{0}visit'.format(current_app.config.get('CORE_PREFIX', '')), alias=self.external_id or self.alias)

    @property
    def acceptable(self):
        if self.category == 'provider':
            return self.ref_link and self.accept_geo
        return True

    @property
    def accept_geo(self):
        if self.category == 'provider':
            return current_user.country_full in self.geo
        return True

    @property
    def activity_str(self):
        return self.activity_count or 0

    @classmethod
    def provider_by_context(cls, country, _exclude=[], _count=12, _page=1, _source=["title", "alias", "logo"], _aggs={}, _sorting=None, _locale='en', **params):
        filter_list =  [ 
            {"term": {"is_active": True}},
            {"term": {"is_draft": False}},
            {"term": {"is_sandbox": False}},
            {"term": {"category.keyword": 'provider'}},
        ]
        if _locale:
            filter_list.append({"term": {"locale.keyword": _locale}})            
        if country:
            filter_list.append({"term": {"geo.keyword": country}})            
        for key, value in params.items():
            if key not in ['sorting', 'cpp', 'query', 'is_grid', 'is_geo']:
                if isinstance(value, bool):
                    filter_list.append({"term": {key: value}})
                elif isinstance(value, list):
                    if value:
                        filter_list.append({"terms": {
                            "{0}.keyword".format(key): value,
                        }})
                else:                
                    filter_list.append({"term": {"{0}.keyword".format(key): value}})
            if key == 'query':
                if value:
                    filter_list.append(
                        {"multi_match" : {
                            "query": value, 
                            "type": "bool_prefix",
                            "fields": [
                                "suggest",
                                "suggest._2gram",
                                "suggest._3gram"
                            ] 
                        }})

        def get_func():
            flist = list()

            flist.append({
                "field_value_factor": {
                    "field": "rating",
                    "factor": 1,
                    "missing": 0
                },
                "weight": 2
            })

            flist.append({
                "field_value_factor": {
                    "field": "boost",
                    "factor": 1,
                    "missing": 1
                },
                "weight": 1
            })

            if country:
                flist.append({
                    "filter": {
                        "bool": {
                            "must": {
                                "term": {
                                    "geo_priority.keyword": country
                                }
                            }
                        }
                    },
                    "weight": 2
                })

            flist.append({
                "filter": {
                    "term": {
                        "is_sponsored": True
                    }
                },
                "weight": 3
            })

            return flist

        qbool = {
            "must": filter_list,
            "must_not": {'ids': {'values': _exclude}}
        }

        q = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": qbool
                    },
                    "boost": 1,
                    "boost_mode": "multiply",
                    "functions": get_func()
                }
            },
            "from": (_page - 1)*_count,
            "size": _count,
            "_source": _source,
        }

        _hash = None
        if _aggs:
            q["aggs"] = _aggs
            _hash = hashlib.md5(dumps(q).encode()).hexdigest()

        if _sorting:
            q["sort"] = _sorting

        resp = current_app.es.search(index=cls._table(), body=q, request_timeout=60, ignore=[400, 404])
        # logger.debug(u'RESPONSE: {0}'.format(resp))

        if 'status' in resp and resp['status'] in [400, 404]:
            if _aggs:
                return [], 0, {}, _hash
            else:
                return [], 0

        def process_aggs(_a):
            _res = {}
            for k, v in _a.items():
                _res[k] = [{'item': i['key'], 'count': i['doc_count']} for i in v['buckets']]
            return _res

        logger.debug(u'RESPONSE provider_by_context took: {0}'.format(resp['took']))
        if _aggs:
            return cls.process(resp['hits']['hits']), resp['hits']['total']['value'], process_aggs(resp['aggregations']), _hash
        else:
            return cls.process(resp['hits']['hits']), resp['hits']['total']['value']


class Guest(AnonymousUserMixin):
    @property
    def is_admin(self):
        return False

    @property
    def user_agent(self):
        return parse(request.user_agent.string)

    @property
    def ip(self):
        return request.remote_addr

    @property
    def location_iso(self):
        if self.user_agent.is_bot:
            return 'gb'
        else:
            return request.headers.get('X-Geo-Country', 'gb').lower()

    @property
    def location(self):
        _cn = pycountry.countries.get(alpha_2=self.location_iso.upper())
        return _cn.name if _cn else 'United Kingdom'

    @property
    def country(self):
        return request.cookies.get('iso', self.location_iso)

    @property
    def country_full(self):
        return unquote(request.cookies.get('country', self.location))

    @property
    def timezone(self):
        return 'Europe/London'

    @property
    def client_id(self):
        return ".".join(request.cookies.get("_ga", "").split(".")[-2:])

    def __repr__(self):
        return str(self.user_agent)


class Actor(ElasticEntity, Guest):
    on_put = Signal()

    _schemas = {
        'id': str,
        'project': str,
        'username': str,
        'password': str,
        'last_auth': DateTimeField,
        'last_country': str,
        'actor_is_active': bool,
        'actor_is_admin': bool,
        'zones': list,
        'ip': str,
        'ua': str,
        'cid': str,
        'sign_date': DateTimeField,
        'skype': str,
        'comment': str,
    }
    
    @classmethod
    def _table(cls):
        return "{0}_actor.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))

    @property
    def is_authenticated(self):
        return True

    @property
    def is_admin(self):
        return self.actor_is_admin

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def __repr__(self):
        return self._doc.get('username')        


class Activity(ElasticEntity):
    on_put = Signal()

    _schemas = {
        'createdon': DateTimeField,
        'project': str,
        'ip': str,
        'country': str,
        'country_iso': str,
        'ua': str,
        'is_bot': bool,
        'cid': str,
        'activity': str,
        'name': str,
        'casino': str,

        'subject': str,
        'contacts': str,
        'message': str,

        'email': str,

        'rate': int,
        'casino_id': str,
        'pros': str,
        'cons': str,

        'url': str,
        'landing': str,
    }
        
    @classmethod
    def _table(cls):
        return "{0}_activity.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))


class TdsHit(ElasticEntity):
    on_put = Signal()

    _schemas = {
        'createdon': DateTimeField,
        'stream': str,
        'stream_name': str,
        'campaign_name': str,
        'campaign_alias': str,
        'campaign_id': str,
        'click_id': str,
        'ip': str,
        'country': str,
        'country_iso': str,
        'ua': str,
        'is_bot': bool,
        'is_uniq': bool,
        'action': str,
        'url': str,
        'subid': str,
        'fingerprint': str,
    }
        
    @classmethod
    def _table(cls):
        return "{0}_tds_hits.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))

    @classmethod
    def aggs(cls, _field, _range=None, _cnt=500):

        def get_subaggs(_a={}):
            _b = {
                "fingerprint": {
                    "cardinality": {
                        "field": "fingerprint.keyword"
                    }
                },
                "is_bot": {
                    "terms": {
                        "field": "is_bot",
                    }
                }
            }
            if _a:
                _b = dict(_b, **_a)
            return _b

        if _field in ['createdon']:
            aggs = {
                _field: {
                    "date_histogram": {
                        "field": _field,
                        "calendar_interval": "1d"
                    },
                    "aggs": get_subaggs()
                },
            }        
        elif _field in ['country']:
            aggs = {
                _field: {
                    "terms": {
                        "field": f"{_field}.keyword",
                        "size": _cnt
                    },
                    "aggs": get_subaggs({
                        "country_iso": {
                            "terms": {
                                "field": "country_iso.keyword"
                            },
                        }
                    })
                },
            }        
        elif _field in ['campaign_id']:
            aggs = {
                _field: {
                    "terms": {
                        "field": f"{_field}.keyword",
                        "size": _cnt
                    },
                    "aggs": get_subaggs({
                        "campaign_name": {
                            "terms": {
                                "field": "campaign_name.keyword"
                            },
                        }
                    })
                },
            }        
        elif _field in ['stream_key']:
            aggs = {
                _field: {
                    "terms": {
                        "field": 'stream.keyword',
                        "size": _cnt
                    },
                    "aggs": get_subaggs({
                        "campaign_name": {
                            "terms": {
                                "field": "campaign_name.keyword"
                            },
                        },
                        "stream_name": {
                            "terms": {
                                "field": "stream_name.keyword"
                            },
                        },
                    })
                },
            }        
        else:
            aggs = {
                _field: {
                    "terms": {
                        "field": f"{_field}.keyword",
                        "size": _cnt
                    },
                    "aggs": get_subaggs()
                },
            }        

        must = []

        if _range:
            _f, _s, _e, _tz = _range
            must.append({"range": {_f: {"gte": _s, "lte": _e, "time_zone": _tz}}})

        q = {
            "query": {
                "bool": {
                    "must": must
                }
            },
            "size": 0,
            "aggs": aggs
        }

        resp = current_app.es.search(index=cls._table(), body=q, request_timeout=60, ignore=[400, 404])
        logger.info(f'Response: {resp}')

        aggs = {}
        if 'status' in resp and resp['status'] in [400, 404]:
            pass
        else:
            aggs = resp.get('aggregations', [])            

        logger.info(f'Aggs found: {aggs}')

        def get_uc(item):
            return item['fingerprint']['value']

        def get_bots(item):
            _v = [item['doc_count'] for item in item['is_bot']['buckets'] if item['key_as_string'] == 'true']
            return _v.pop() if _v else 0

        def process(items, key):
            if key in items:
                if key == 'createdon':
                    return [{'term': item['key_as_string'].strip(), 'hits': item['doc_count'], 'uc': get_uc(item), 'bots': get_bots(item)} for item in items[key]['buckets']]
                elif key == 'country':
                    return [{'term': item['key'].strip(), 'country_iso': item['country_iso']['buckets'][0]['key'].lower(), 'hits': item['doc_count'], 'uc': get_uc(item), 'bots': get_bots(item)} for item in items[key]['buckets']]
                elif key in ['campaign_id']:
                    return [{'term': ', '.join([k['key'] for k in item['campaign_name']['buckets']]), 'hits': item['doc_count'], 'uc': get_uc(item), 'bots': get_bots(item)} for item in items[key]['buckets']]
                elif key in ['stream_key']:
                    return [{'term': item['key'].strip() + ' | Name: ' + ', '.join([k['key'] for k in item['stream_name']['buckets']]) + ' | Campaign: ' + ', '.join([k['key'] for k in item['campaign_name']['buckets']]), 'hits': item['doc_count'], 'uc': get_uc(item), 'bots': get_bots(item)} for item in items[key]['buckets']]
                else:
                    return [{'term': item['key'].strip(), 'hits': item['doc_count'], 'uc': get_uc(item), 'bots': get_bots(item)} for item in items[key]['buckets']]
            return []

        return process(aggs, _field), 0 #resp['hits']['total']['value']


class TdsDomain(ElasticEntity):
    on_put = Signal()

    _schemas = {
        'createdon': DateTimeField,
        'domain': str,
        'endpoint': str,
        'is_https': bool,
    }
        
    @classmethod
    def _table(cls):
        return "{0}_tds_domain.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))


class TdsCampaign(ElasticEntity):
    on_put = Signal()

    _schemas = {
        'createdon': DateTimeField,
        'updatedon': DateTimeField,
        'name': str,
        'domain': str,
        'alias': str,
        'groups': list,
        'ttl': int,
        'is_split': bool,
        'is_active': bool,
        'is_archive': bool,
        'notes': str,
        'streams': list,
    }
        
    @classmethod
    def _table(cls):
        return "{0}_tds_campaign.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))


# pydantic models

class UserModel(BaseModel):
    login: EmailStr

    @validator('login', allow_reuse=True)
    def fn_not_empty(cls, v):
        assert v != '', 'Required field'
        return v


class ManagerModel(BaseModel):
    login: EmailStr
    skype: str = ...

    @validator('login', 'skype', allow_reuse=True)
    def fn_not_empty(cls, v):
        assert v != '', 'Required field'
        return v


class SignupModel(BaseModel):
    login: EmailStr
    skype: str = ...
    invite_code: Optional[str] = None

    @validator('login', 'skype', allow_reuse=True)
    def fn_not_empty(cls, v):
        assert v != '', 'Required field'
        return v


class SignupModelInvite(SignupModel):
    invite_code: str = ...

    @validator('invite_code', allow_reuse=True)
    def fn_invite_code(cls, v):
        assert v != '', 'Required field'
        if v == current_app.config['DASHBOARD_INVITE']:
            return v

        try:
            f = Fernet(current_app.config['FERNET_KEY'])
            _obj = f.decrypt(v.encode())
            _token = loads(_obj)
            if isinstance(_token, dict):
                _ts = datetime.timestamp(datetime.utcnow())
                if _ts > _token['expired']:
                    logger.info(f'Token expired: {_token}, now: {_ts}')
                    assert False, 'Invite Expired'
                else:
                    logger.info(f'Token valid: {_token}')
                    return v
        except Exception as e:
            logger.error(f'Exception encrypt token: {e}')

        assert False, 'Invite Expired'


class AuthModel(BaseModel):
    login: EmailStr
    password: str = ...

    @validator('login', 'password', allow_reuse=True)
    def fn_not_empty(cls, v):
        assert v != '', 'Required field'
        return v


class CasinoModel(BaseModel):
    @validator('*', pre=True, allow_reuse=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    @validator('year', pre=True, allow_reuse=True)
    def year_validator(cls, v):
        if v:
            s = str(v)
            if s.isdigit() and (int(s) < 1990 or int(s) > datetime.utcnow().year):
                raise ValueError('Incorrect value')
        return v        

    title: str = ...
    website: HttpUrl = ...
    languages: List[str] = []
    services: List[str] = []
    year: Optional[int]
    support_languages: List[str] = []
    support_livechat: bool = False
    support_email: Optional[EmailStr] = None
    support_phone: Optional[str] = None
    attachs: List[dict] = []
    logo: Optional[str] = None
    logo_small: Optional[str] = None
    licences: List[str] = []
    games: List[str] = []
    games_count: Optional[int]
    software: List[str] = []
    currencies: conlist(str, min_items=1)
    default_currency: str
    deposits: List[str] = []
    min_deposit: int
    kyc_deposit: bool = False
    withdrawal: List[str] = []
    min_withdrawal: int
    withdrawal_monthly: Optional[int] = None
    kyc_withdrawal: bool = False
    welcome_package_max_bonus: Optional[int] = None
    welcome_package_match: Optional[int] = None
    welcome_package_fs: Optional[int] = None
    welcome_package: constr(max_length=50)
    welcome_package_note: Optional[constr(max_length=500)] = None
    welcome_package_wager: Optional[int] = None
    cashback: Optional[int] = None
    geo_whitelist: Optional[str] = None
    geo_blacklist: Optional[str] = None
    geo: List[str] = []
    content: Optional[str] = None


class CasinoProxyModel(CasinoModel):
    website: Optional[str] = None
    default_currency: Optional[str] = None
    min_deposit: Optional[int] = None
    min_withdrawal: Optional[int] = None
    welcome_package: Optional[str] = None
    welcome_package_note: Optional[str] = None


class DomainModel(BaseModel):
    @validator('*', pre=True, allow_reuse=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    domain: str = ...
    endpoint: str = ...
    is_https: bool = False


class CampaignModel(BaseModel):
    @validator('*', pre=True, allow_reuse=True)
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v

    name: str = ...
    domain: str = ...
    alias: str = ...
    groups: Optional[List[str]] = []
    ttl: int
    is_split: bool = False
    is_active: bool = False
    is_archive: bool = False
    notes: Optional[str] = None
    streams: conlist(dict, min_items=1)


class ActivityTicketModel(BaseModel):
    subject: str = ...
    contacts: str = ...
    name: str = ...
    message: str = ...

    @validator('subject', 'contacts', 'name', 'message', allow_reuse=True)
    def not_empty(cls, v):
        assert v != '', 'Required field'
        return v


class ActivitySubscribeModel(BaseModel):
    email: EmailStr
    is_agree: bool = False

    @validator('is_agree', pre=True, always=True, allow_reuse=True)
    def check_agree(cls, v):
        assert v == True, 'You must accept our terms'
        return v   


class ActivityFeedbackModel(BaseModel):
    rate: conint(ge=1, le=5)
    casino: str = ...
    casino_id: str = ...
    name: Optional[str]
    pros: Optional[str]
    cons: Optional[str]                


class CasinoCommit(ElasticEntity):
    on_put = Signal()

    _schemas = {
        'updatedon': DateTimeField,
        'source_id': str,
        'actor_id': str,
        'casino': str,
        ###
        'title': str,
        'website': str,
        'languages': list,
        'services': list,
        'year': int,
        'support_languages': list,
        'support_livechat': bool,
        'support_email': str,
        'support_phone': str,
        'attachs': list,
        'logo': str,
        'logo_small': str,
        'licences': list,
        'games': list,
        'games_count': int,
        'software': list,
        'currencies': list,
        'default_currency': str,
        'deposits': list,
        'min_deposit': int,
        'kyc_deposit': bool,
        'withdrawal': list,
        'min_withdrawal': int,
        'withdrawal_monthly': int,
        'kyc_withdrawal': bool,
        'welcome_package_max_bonus': int,
        'welcome_package_match': int,
        'welcome_package_fs': int,
        'welcome_package': str,
        'welcome_package_note': str,
        'welcome_package_wager': int,
        'cashback': int,
        'geo_whitelist': str,
        'geo_blacklist': str,
        'geo': list,
        'content': str,
    }
        
    @classmethod
    def _table(cls):
        return "{0}_casino_commit.{1}".format(os.environ.get('PROJECT', 'project'), os.environ.get('VERSION', 'v1'))
