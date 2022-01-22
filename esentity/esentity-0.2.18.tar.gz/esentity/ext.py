#coding: utf-8
import jinja2
import html
from esentity.models import Page
from flask import current_app
from flask_login import current_user
from loguru import logger
from json import dumps


class HtmlExtension(jinja2.ext.Extension):
    tags = set(['html'])

    def __init__(self, environment):
        super(HtmlExtension, self).__init__(environment)

    def _render(self, caller):
        rv = caller()
        return html.unescape(rv)

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = parser.parse_statements(['name:endhtml'], drop_needle=True)
        args = []

        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)


class LicencesExtension(jinja2.ext.Extension):
    tags = set(['licences'])

    def __init__(self, environment):
        super(LicencesExtension, self).__init__(environment)

    def _render(self, caller):
        pages, _ = Page.get(
            category='collection',
            is_active=True,
            is_searchable=True,
            is_redirect=False,  
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['title', 'path', 'alt_title'],
            collection_mode='CasinoLicence',
            _count=100,
            _sort=[
                {'alt_title.keyword': {'order': 'asc'}}
            ]
        )
        t = current_app.jinja_env.get_template('_table-licences.html')
        s = t.render(pages=pages)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []

        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)


class SoftwaresExtension(jinja2.ext.Extension):
    tags = set(['softwares'])

    def __init__(self, environment):
        super(SoftwaresExtension, self).__init__(environment)

    def _render(self, caller):
        pages, _ = Page.get(
            category='collection',
            is_active=True,
            is_searchable=True,
            is_redirect=False,  
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['title', 'path', 'alt_title', 'custom_text', 'logo'],
            collection_mode='CasinoSoftware',
            _count=100,
            _sort=[
                {'alt_title.keyword': {'order': 'asc'}}
            ]
        )
        pages = {item.alt_title: item for item in pages}

        # v2 (with aggs)

        filter_list =  [ 
            {"term": {"is_active": True}},
            {"term": {"is_draft": False}},
            {"term": {"is_sandbox": False}},
            {"term": {"is_searchable": True}},
            {"term": {"is_redirect": False}},
            {"term": {"category.keyword": 'provider'}},
            {"term": {"locale.keyword": current_app.config['BABEL_DEFAULT_LOCALE']}},
        ]

        _aggs = {
            "software": {
                "terms": {
                    "field": "software.keyword",
                    "size": 500,
                    "order": {"_key": "asc"}
                },
                "aggs": {
                    "casinos": {
                        "top_hits": {
                            "sort": [
                                {
                                    "rating": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "_source": {
                                "includes": ["title", "path", "alt_title", "rating"]
                            },
                            "size": 3
                        }
                    }                
                }
            }
        }

        q = {
            "query": {
                "bool": {
                    "must": filter_list,
                }
            },
            "aggs": _aggs,
            "size": 0,
            "_source": False,
        }

        resp = current_app.es.search(index=Page._table(), body=q, request_timeout=60, ignore=[400, 404])

        if 'status' in resp and resp['status'] in [400, 404]:
            return ''

        t = current_app.jinja_env.get_template('_table-simple.html')
        s = t.render(pages=pages, items=resp['aggregations']['software']['buckets'])

        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []

        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)

class CountriesExtension(jinja2.ext.Extension):
    tags = set(['countries'])

    def __init__(self, environment):
        super(CountriesExtension, self).__init__(environment)

    def _render(self, caller):
        pages, _ = Page.get(
            category='collection',
            is_active=True,
            is_searchable=True,
            is_redirect=False,  
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['title', 'path', 'alt_title'],
            collection_mode='CasinoCountry',
            _count=100,
            _sort=[
                {'alt_title.keyword': {'order': 'asc'}}
            ]
        )
        t = current_app.jinja_env.get_template('_table-countries.html')
        s = t.render(pages=pages)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []

        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)        


class BankingExtension(jinja2.ext.Extension):
    tags = set(['banking'])

    def __init__(self, environment):
        super(BankingExtension, self).__init__(environment)

    def _render(self, caller):
        pages, _ = Page.get(
            category='collection',
            is_active=True,
            is_searchable=True,
            is_redirect=False,  
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['title', 'path', 'alt_title', 'custom_text', 'logo'],
            collection_mode='CasinoBanking',
            _count=100,
            _sort=[
                {'alt_title.keyword': {'order': 'asc'}}
            ]
        )
        pages = {item.alt_title: item for item in pages}

        # v2 (with aggs)

        filter_list =  [ 
            {"term": {"is_active": True}},
            {"term": {"is_draft": False}},
            {"term": {"is_sandbox": False}},
            {"term": {"is_searchable": True}},
            {"term": {"is_redirect": False}},
            {"term": {"category.keyword": 'provider'}},
            {"term": {"locale.keyword": current_app.config['BABEL_DEFAULT_LOCALE']}},
        ]

        _aggs = {
            "deposits": {
                "terms": {
                    "field": "deposits.keyword",
                    "size": 500,
                    "order": {"_key": "asc"}
                },
                "aggs": {
                    "casinos": {
                        "top_hits": {
                            "sort": [
                                {
                                    "rating": {
                                        "order": "desc"
                                    }
                                }
                            ],
                            "_source": {
                                "includes": ["title", "path", "alt_title", "rating"]
                            },
                            "size": 3
                        }
                    }                
                }
            }
        }

        q = {
            "query": {
                "bool": {
                    "must": filter_list,
                }
            },
            "aggs": _aggs,
            "size": 0,
            "_source": False,
        }

        resp = current_app.es.search(index=Page._table(), body=q, request_timeout=60, ignore=[400, 404])

        if 'status' in resp and resp['status'] in [400, 404]:
            return ''

        t = current_app.jinja_env.get_template('_table-simple.html')
        s = t.render(pages=pages, items=resp['aggregations']['deposits']['buckets'])

        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []

        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)  


class RatingExtension(jinja2.ext.Extension):
    tags = set(['rating'])

    def __init__(self, environment):
        super(RatingExtension, self).__init__(environment)

    def _render(self, args, caller=None):
        logger.info('Args: {0}'.format(args))

        default = ['casino', True, 10]
        args = args[:2] + default[len(args):] + args[2:]

        service = args[0]
        has_filters = args[1]
        count = int(args[2])

        tags = args[3:]
        logger.info('Tags: {0}'.format(tags))

        _afields = ['software', 'licences', 'deposits', 'withdrawal', 'games']
        _aggs = {
            item: {
                "terms": {
                    "field": "{0}.keyword".format(item),
                    "size": 500,
                    "order": {"_key": "asc"}
                }
            } for item in _afields
        }

        # args: service
        pages, found, aggs, id = Page.provider_by_context(
            is_searchable=True,
            is_redirect=False,
            country=current_user.country_full,
            services=service,
            provider_tags=tags,
            _source = [
                "title", 
                "alias", 
                "logo", 
                "logo_white",
                "logo_small",
                "external_id", 
                "theme_color", 
                "welcome_package", 
                "welcome_package_note",
                "provider_pros",
                "services",
                "welcome_package_max_bonus",
                "welcome_package_fs",
                "default_currency",
                "rating",
                "rank",
                "user_rating",
                "is_sponsored",
                "website",
                "provider_pros",
                "licences",
                "ref_link",
                "geo",
            ] + _afields, 
            _count=count,
            _aggs = _aggs
        )
        if id and has_filters:
            _c = dumps(aggs)
            current_app.redis.hset('aggs', id, _c)
            logger.info('Cache aggs {0}: {1}'.format(id, len(_c)))

        deposits_primary = ['Visa', 'Trustly', 'PayPal', 'Skrill', 'Neteller']

        t = current_app.jinja_env.get_template('_rating.html')
        s = t.render(
            pages=pages, 
            has_filters=has_filters, 
            found=found, 
            service=service, 
            id=id, 
            count=count,
            tags=tags,
            deposits_primary=deposits_primary,
        )
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
            parser.stream.skip_if('comma')

        return jinja2.nodes.CallBlock(self.call_method("_render", args=[jinja2.nodes.List(args)]), [], [], []).set_lineno(lineno)          


class SlotsExtension(jinja2.ext.Extension):
    tags = set(['slots'])

    def __init__(self, environment):
        super(SlotsExtension, self).__init__(environment)

    def _render(self, caller):
        slots, found = Page.get(
            category='slot', 
            is_active=True, 
            is_searchable=True, 
            is_redirect=False, 
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['alias', 'title', 'cover', 'software'], 
            _count=500,
            _sort=[
                {'title.keyword': {'order': 'asc'}}
            ]
        )
        t = current_app.jinja_env.get_template('_slots.html')
        s = t.render(slots=slots, found=found)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []

        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)         


class TopSlotsExtension(jinja2.ext.Extension):
    tags = set(['top_slots'])

    def __init__(self, environment):
        super(TopSlotsExtension, self).__init__(environment)

    def _render(self, args, caller=None):
        logger.info('Top Slots IN Args: {0}'.format(args))

        default = ['NetEnt', 8, 4, False]
        args = args[:4] + default[len(args):] + args[4:]

        logger.info('Top Slots OUT Args: {0}'.format(args))

        provider = args[0]
        count = int(args[1])
        in_row = int(args[2])
        random = bool(args[3])

        # args: service
        slots, found = Page.get(
            is_active=True, 
            is_searchable=True, 
            is_redirect=False,
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=True, 
            _count=count,
            _random=random,
            category='slot',
            software=provider, 
        )

        t = current_app.jinja_env.get_template('_slots_list.html')
        s = t.render(
            slots=slots,
            in_row=in_row,
        )
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
            parser.stream.skip_if('comma')

        return jinja2.nodes.CallBlock(self.call_method("_render", args=[jinja2.nodes.List(args)]), [], [], []).set_lineno(lineno)          


class GuideExtension(jinja2.ext.Extension):
    tags = set(['guides'])

    def __init__(self, environment):
        super(GuideExtension, self).__init__(environment)

    def _render(self, args, caller=None):
        logger.info('Guide args: {0}'.format(args))

        guides, found = Page.get(
            is_active=True, 
            is_searchable=True, 
            is_redirect=False, 
            tags=args[0],
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['path', 'title'], 
            _count=500,
            _sort=[
                {'publishedon': {'order': 'desc'}}
            ]
        )
        t = current_app.jinja_env.get_template('_table-guides.html')
        s = t.render(pages=guides, found=found)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
            parser.stream.skip_if('comma')

        return jinja2.nodes.CallBlock(self.call_method("_render", args=[jinja2.nodes.List(args)]), [], [], []).set_lineno(lineno)          


class TopCasinosExtension(jinja2.ext.Extension):
    tags = set(['top_casinos'])

    def __init__(self, environment):
        super(TopCasinosExtension, self).__init__(environment)

    def _render(self, caller=None):
        top, found = Page.provider_by_context(
            country=current_user.country_full,
            is_searchable=True,
            is_redirect=False,
            _source = [
                "title", 
                "alias", 
                "logo", 
                "logo_white",
                "logo_small",
                "external_id", 
                "theme_color", 
                "welcome_package", 
                "welcome_package_note",
                "provider_pros",
                "services",
                "welcome_package_max_bonus",
                "welcome_package_fs",
                "default_currency",
                "rating",
                "rank",
                "user_rating",
                "is_sponsored",
                "website",
                "provider_pros",
                "licences",
                "ref_link",
                "geo",
            ], 
            _count=3
        )    
        t = current_app.jinja_env.get_template('_top-casinos.html')
        s = t.render(top=top, found=found)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []
        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)


class CasinoAppsExtension(jinja2.ext.Extension):
    tags = set(['casino_apps'])

    def __init__(self, environment):
        super(CasinoAppsExtension, self).__init__(environment)

    def _render(self, args, caller=None):
        logger.info('CasinoApps IN Args: {0}'.format(args))

        default = [True]
        args = args[:len(default)-1] + default[len(args):] + args[len(default)-1:] # TODO (-1 ??)

        logger.info('CasinoApps OUT Args: {0}'.format(args))

        t = current_app.jinja_env.get_template('_ext-casino-apps.html')
        s = t.render()
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
            parser.stream.skip_if('comma')

        return jinja2.nodes.CallBlock(self.call_method("_render", args=[jinja2.nodes.List(args)]), [], [], []).set_lineno(lineno)          


class SlotPlayExtension(jinja2.ext.Extension):
    tags = set(['slot_play'])

    def __init__(self, environment):
        super(SlotPlayExtension, self).__init__(environment)

    def _render(self, args, caller=None):
        logger.info('SlotPlay IN Args: {0}'.format(args))

        title = args[0]
        alias = args[1]
        screen = args[2]

        t = current_app.jinja_env.get_template('_ext-slot-play.html')
        s = t.render(screen=screen, alias=alias, title=title)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
            parser.stream.skip_if('comma')

        return jinja2.nodes.CallBlock(self.call_method("_render", args=[jinja2.nodes.List(args)]), [], [], []).set_lineno(lineno)          


class AuthorExtension(jinja2.ext.Extension):
    tags = set(['author_badge'])

    def __init__(self, environment):
        super(AuthorExtension, self).__init__(environment)

    def _render(self, args, caller=None):
        logger.info('Author IN Args: {0}'.format(args))

        author = args[0]

        t = current_app.jinja_env.get_template('_ext-author.html')
        s = t.render(author=author)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = []
        while parser.stream.current.type != 'block_end':
            args.append(parser.parse_expression())
            parser.stream.skip_if('comma')

        return jinja2.nodes.CallBlock(self.call_method("_render", args=[jinja2.nodes.List(args)]), [], [], []).set_lineno(lineno)          


class TopAlexaExtension(jinja2.ext.Extension):
    tags = set(['top_alexa'])

    def __init__(self, environment):
        super(TopAlexaExtension, self).__init__(environment)

    def _render(self, caller=None):
        pages, _ = Page.get(
            category='provider',
            is_active=True,
            is_searchable=True,
            is_redirect=False,  
            locale=current_app.config['BABEL_DEFAULT_LOCALE'], 
            _source=['title', 'path', 'alt_title', 'rank_alexa'],
            _count=30,
            _sort=[
                {'rank_alexa': {'order': 'asc'}}
            ]
        )
   
        t = current_app.jinja_env.get_template('_top-alexa.html')
        s = t.render(pages=pages)
        return s

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        body = ''
        args = []
        return jinja2.nodes.CallBlock(self.call_method("_render", args), [], [], body).set_lineno(lineno)
