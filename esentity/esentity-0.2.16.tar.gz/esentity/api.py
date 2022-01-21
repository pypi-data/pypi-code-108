#coding: utf-8
from flask import request, url_for, session
from flask import current_app
from flask_restful import Resource
from flask_login import current_user, login_required
from flask_uploads import UploadNotAllowed
import os
import hashlib
import pycountry 
from datetime import date, datetime
from slugify import slugify 
from loguru import logger
from werkzeug.routing import BuildError
from functools import wraps
from json import dumps, loads
from utils import geo_context
from PIL import Image
from resizeimage import resizeimage
from esentity.models import BaseEntity, ElasticEntity
from esentity.models import Page, Actor, Activity, TdsCampaign, TdsDomain, TdsHit, CasinoCommit
from esentity.models import AuthModel, SignupModel, UserModel, ManagerModel, CasinoModel, CasinoProxyModel, DomainModel, CampaignModel  
from esentity.tasks import send_email, send_notify, tdscampaign_clear, tdscampaign_bots
from pydantic import ValidationError
from email_validator import validate_email, EmailNotValidError # TODO remove it


def su_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view


def zone_required(zone):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if zone not in current_user.zones:
                return current_app.login_manager.unauthorized()
            return f(*args, **kwargs)
        return wrapper
    return decorator


def get_page_url(obj):
    url = None

    kw = {
        'alias': obj['alias']
    }
    if current_app.config.get('CORE_PREFIX'):
        kw['lang_code'] = obj['locale']

    if obj['category'] == 'slot':
        url = url_for('{0}slot'.format(current_app.config.get('CORE_PREFIX', '')), **kw)
    elif obj['category'] == 'provider':
        url = url_for('{0}casino'.format(current_app.config.get('CORE_PREFIX', '')), **kw)
    else:
        url = url_for('{0}path'.format(current_app.config.get('CORE_PREFIX', '')), **kw)

    return url


def get_tags(item):
    _tags = []
    if item.category == 'provider':
        _tags.append({'title': 'Casino', 'class': 'casino'})
        if item.is_draft:
            _tags.append({'title': 'Draft', 'class': 'draft'})
        if item.owner:
            actors, found = Actor.get(_id=item.owner)
            if found == 1:
                actor = actors.pop()
                _tags.append({'title': actor.username, 'class': 'owner'})

    elif item.category == 'slot':
        _tags.append({'title': 'Slot', 'class': 'slot'})
    elif item.category == 'collection':
        _tags.append({'title': 'Collection', 'class': 'collection'})

    if not item.is_active:
        _tags.append({'title': 'Not Active', 'class': 'is-disabled'})
    if not item.is_searchable:
        _tags.append({'title': 'Not Searchable', 'class': 'not-searchable'})
    if item.is_redirect:
        _tags.append({'title': 'Redirect', 'class': 'is-redirected'})

    _tags.append({'title': item.locale.upper(), 'class': 'locale'})

    return _tags


def process_casino(item, actors={}, check_commit=False):
    _doc = item['_source']
    _doc['id'] = item['_id']
    _doc['path'] = f"https://{current_app.config['DOMAIN']}{_doc['path']}"
    if _doc.get('owner') and len(actors.keys()):
        _doc['owner'] = {'id': _doc['owner'], 'username': actors.get(_doc['owner'])}

    if check_commit and _doc['status'] in ['draft', 'published']:
        _, found = CasinoCommit.get(
            source_id=_doc['id'],
            actor_id=current_user.id
        )
        if found:
            _doc['status'] = 'unpublished_changes'

    return _doc


def get_timerange(timeframe, custom):
    # today
    start = "now/d"
    end = start

    if timeframe == 'Custom':
        _custom = custom.split(' to ')
        if len(_custom) == 1:
            start = f'{_custom[0]}||/d' 
            end = start
        elif (len(_custom) == 2):
            start = f'{_custom[0]}||/d' 
            end = f'{_custom[1]}||/d' 
    elif timeframe == "Yesterday":
        start = "now-1d/d"
        end = start
    elif timeframe == "Last 24 hours":
        start = "now-24h/m"
        end = "now/m"
    elif timeframe == "Last 7 days":
        start = "now-6d/d"
        end = "now/d"
    elif timeframe == "This Month":
        start = "now/M"
        end = start
    elif timeframe == "Prev Month":
        start = "now-1M/M"
        end = start

    return start, end


class ApiPing(Resource):
    def get(self):
        return {'ok': True, 'pong': True}


class ApiResourceSlug(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSlug: {0}'.format(data))
    
        _attrs = {'alias': slugify(data.get('title'))}

        return {'ok': True, 'attrs': _attrs}


class ApiResourceGet(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceGet: {0}'.format(data))

        if data:
            objs, total = Page.get(_id=data['key'])
            if total == 1:
                obj = objs.pop()
                doc = obj.to_dict()
                doc['updatedon'] = datetime.utcnow()
                resp = {
                    'ok': True,
                    'resource': doc,
                }
                return resp
        else:
            resp = {
                'ok': True,
                'resource': {
                    'alias': Page.get_random_string(10).lower(),
                    'category': 'page',
                    'is_active': True,
                    'is_searchable': True,
                    'publishedon': datetime.utcnow().date(),
                    'updatedon': datetime.utcnow(),
                    'order': 0,
                    'locale': 'en'
                },
            }
            return resp
        return {'ok': False}


class ApiResourceSearch(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSearch: {0}'.format(data))

        objs, total = Page.get(path=data['key'], locale=data.get('locale', 'en'))
        if total:
            obj = objs.pop()


            data = [{
                'key': obj._id, 
                'title': obj.title or obj.path, 
                'url': get_page_url(obj.to_dict())
            }]
            resp = {
                'ok': True,
                'found': data, 
                'resource_key': data[0],
            }
        else:
            resp = {
                'ok': True,
                'found': [], 
                'resource_key': None
            }
        return resp


class ApiResourceSearchPage(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSearchPage: {0}'.format(data))

        objs = [{
            'key': item._id, 
            'title': item.title or item.path, 
            'url': get_page_url(item.to_dict()),
            'tags': get_tags(item)
        } for item in Page.query(data['query'], True)]
        return {'ok': True, 'items': objs}


class ApiResourceGeo(Resource):
    @login_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceGeo: {0}'.format(data))

        _c, _e, _v = Page.get_countries(data.get('w', '') or '', data.get('b', '') or '')
        if _v:
            _c = []

        return {'ok': True, 'countries': _c, 'errors': _e, 'valid': not _v}


class ApiResourceUpload(Resource):
    @login_required
    def post(self):
        logger.info(u'Data ApiResourceUpload: {0}'.format(request.form))

        _e = None
        try:
            resp = {}
            file = request.files['file']
            basename = slugify(u'.'.join(file.filename.split('.')[:-1])).lower() + '.'

            rename = request.form['rename']
            if rename in ['entity']:
                basename = slugify(request.form['title'] or basename).lower() + '.'
            if rename in ['hash']:
                basename = hashlib.md5(file.read()).hexdigest() + '.'
                file.seek(0)
            
            filename = current_app.images.save(file, None, basename)
            resp['origin'] = current_app.images.url(filename)

            path = current_app.images.path(filename)
            image = Image.open(path) 
            image = image.convert('RGBA')            
            w, h = image.size

            _w = None
            _h = None

            preset = request.form['preset'].split('_')
            for item in preset:
                if 'w' in item:
                    _w = int(item.replace('w', ''))
                elif 'h' in item:
                    _h = int(item.replace('h', ''))

            if len(preset) > 1:
                tfname = '{0}.' + preset[0] + '.png'
                filename = '.'.join(filename.split('.')[:-1])

                if _w and _h:
                    if w > _w and h > _h: 
                        image = resizeimage.resize_cover(image, [_w, _h])
                else:
                    if w > _w:
                        image = resizeimage.resize_width(image, _w)

                png = current_app.images.path(tfname.format(filename))
                image.save(png, 'PNG')
                resp['png'] = current_app.images.url(tfname.format(filename))

                image.save("{0}.webp".format(png), 'WEBP')
                resp['webp'] = "{0}.webp".format(resp['png'])
            else:
                image.save("{0}.webp".format(path), 'WEBP')
                resp['webp'] = "{0}.webp".format(resp['origin'])

            resp['ok'] = True
            return resp
        except UploadNotAllowed:
            _e = 'Not allowed'
        return {'ok': False, 'error': _e}


class ApiResourceSave(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSave: {0}'.format(data))

        _errors = dict()
        entity = data['entity']

        # to cerberus
        if not entity.get('alias'):
            if entity.get('title'):
                entity['alias'] = entity['title']
            else:
                _errors['alias'] = ['Mandatory field']

        if not _errors:
            if entity['category'] in ['slot', 'provider']:
                entity['alias'] = slugify(entity['alias'].strip()).lower()

            resource_key = data['key']

            try:
                path = get_page_url(entity)
            except BuildError:
                _errors['category'] = ['Endpoint not found']

            if not _errors:
                if current_app.config.get('CORE_PREFIX'):
                    path = path.replace('/{0}'.format(entity['locale']), '')

                _, total = Page.get(path=path, locale=entity['locale'])

                if total > 0 and (not resource_key or (resource_key and resource_key.get('key') != _.pop()._id)):
                    _errors['alias'] = ['Page already exist: {0}'.format(path)]
                else:
                    if not resource_key:
                        _id = Page.generate_id(path, entity['locale'])
                    else:
                        _id = resource_key.get('key')

                    entity['path'] = path
                    entity['suggest'] = entity.get('title', '')
                    entity['project'] = os.environ.get('PROJECT', 'app')

                    # TODO fix errors data
                    if entity['category'] not in ['provider']:
                        entity['geo'] = []
                        
                    resp, obj = Page.put(_id, entity)
                    return {'ok': True}

        return {'ok': False, 'errors': _errors}


class ApiResourceHistory(Resource):
    @login_required
    @su_required
    def post(self):
        history, _ = Page.get(_count=20, _sort=[{"updatedon": {"order": "desc"}}])
        objs = [{
            'key': item._id, 
            'title': item.title or item.path, 
            'url': get_page_url(item.to_dict()),
            'tags': get_tags(item)
        } for item in history]
        return {'ok': True, 'history': objs}


class ApiResourceAPISearch(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceAPISearch: {0}'.format(data))
        return {'ok': True, 'items': []}


class ApiResourceImportPush(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceImportPush: {0}'.format(data))

        _attrs = {}

        entity = data['entity']
        raw = entity.get('raw')
        if raw:
            _data = [item.strip() for item in raw.split('\n')]
            if len(_data) == 1:
                _data = _data[0].split(';')
                if entity.get('category') == 'slot' and len(_data) == 11:
                    _attrs = {
                        'title': _data[0],
                        'software': [_data[1]],
                        'releasedon': date(int(_data[2]), 1, 1) if _data[2].isdigit() and len(_data[2]) == 4 else _data[2],
                        'layout': _data[3],
                        'lines': _data[4],
                        'volatility': _data[5],
                        'rtp': _data[6],
                        'default_currency': _data[7],
                        'min_bet': _data[8],
                        'max_bet': _data[9],
                        'alias': '',
                        'raw': 'Complete!'
                    }

        return {'ok': True, 'attrs': _attrs}


class ApiSearch(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiSearch: {0}'.format(data))

        _afields = ['software', 'licences', 'deposits', 'withdrawal', 'games']
        payload = data['payload']
        _n = payload
        for k, v in payload.items():
            if k in _afields and isinstance(v, list):
                _a = []
                for item in v:
                    _a.append(item['item'] if isinstance(item, dict) else item)
                _n[k] = _a
        data['payload'] = _n
        logger.info(u'Processed Data ApiSearch: {0}'.format(data))

        _res = None
        _found = None

        # _aggs_primary = {}

        ## experiment
        _cached = current_app.redis.hget('aggs', data['hash'])
        _aggs_primary = loads(_cached) if _cached else {}
        ## experiment

        if data.get('is_init'):
            # _cached = current_app.redis.hget('aggs', data['hash'])
            # _aggs_primary = loads(_cached) if _cached else {}

            ## experiment
            current_app.redis.hset('aggs_history', data['hash'] + '123', _cached)
            ## experiment
        else:
            _aggs = {
                item: {
                    "terms": {
                        "field": "{0}.keyword".format(item),
                        "size": 500,
                        "order": {"_key": "asc"}
                    }
                } for item in _afields
            }

            payload = data['payload']
            logger.info(u'Filters for search: {0}'.format(payload))

            _sorting = None
            if 'sorting' in payload:
                if payload['sorting'] == 'Rating Highest first':
                    _sorting = [{'rating': {'order': 'desc'}}]
                elif payload['sorting'] == 'Newest sites first':
                    _sorting = [{'establishedon': {'order': 'desc'}}]
                elif payload['sorting'] == 'Oldest sites first':
                    _sorting = [{'establishedon': {'order': 'asc'}}]
                elif payload['sorting'] == 'Most traffic first':
                    _sorting = [{'rank_alexa': {'order': 'asc'}}]
                elif payload['sorting'] == 'Last added':
                    _sorting = [{'publishedon': {'order': 'desc'}}]
                elif payload['sorting'] == 'Sort A-Z':
                    _sorting = [{'title.keyword': {'order': 'asc'}}]

            # args: service
            pages, _found, _aggs_primary_filtered, id = Page.provider_by_context(
                is_searchable=True,
                is_redirect=False,
                country=current_user.country_full if payload.get('is_geo', True) else None,
                services=data['category'],
                provider_tags=data['tags'],
                **payload,
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
                    "category",
                ] + _afields, 
                _count=int(payload.get('cpp', 10)),
                _page=int(data.get('page', 1)),
                _aggs = _aggs,
                _sorting = _sorting
            )

            ## experiment
            def to_dict(items):
                return {item['item']: item['count'] for item in items}

            _cached_prev = current_app.redis.hget('aggs_history', data['hash'] + '123')
            _aggs_prev = loads(_cached_prev) if _cached_prev else {}

            _aggs_diff = {}
            for k, v in _aggs_primary.items():
                _diff = []
                prev = to_dict(_aggs_prev.get(k, []))
                current = to_dict(_aggs_primary_filtered[k])
                for j in v:
                    _name = j['item']
                    if len(payload[k]):
                        if _name in payload[k]:
                            _diff.append({'item': _name, 'count': ''})
                        else:
                            _cnt = j['count']
                            if _name in current:
                                _cnt = _cnt - current[_name]
                            else:
                                if _name in prev:
                                    _cnt = prev[_name]
                                else:
                                    _cnt = 0
                            _diff.append({'item': _name, 'count': '+{0}'.format(_cnt)})
                    else:
                        _diff.append({'item': _name, 'count': current.get(_name, 0)})
                _aggs_diff[k] = _diff

            _aggs_primary = _aggs_diff
            if _found > 0:
                current_app.redis.hset('aggs_history', data['hash'] + '123', dumps(_aggs_primary_filtered))
            ## experiment

            # _aggs_primary = _aggs_primary_filtered

            _template = '_rating-grid.html' if payload.get('is_grid', False) else '_rating-rows.html'
            t = current_app.jinja_env.get_template(_template)
            deposits_primary, langs_primary, currency_primary = geo_context(current_user.country_full)
            _res = t.render(pages=pages, deposits_primary=deposits_primary)
            
        _aggs_secondary = {
            'sorting': [
                'Legal in my region', 
                'Rating Highest first', 
                'Newest sites first',
                'Oldest sites first',
                'Most traffic first',
                'Last added',
                'Sort A-Z',
            ],
            'cpp': [10, 25, 50, 100, 200],
        }
        _aggs = dict(_aggs_primary, **_aggs_secondary)

        return {
            'ok': True, 
            'aggs': _aggs,
            'found': _found,
            'data': _res
        }
    

class ApiGeo(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiGeo: {0}'.format(data))

        _c = []

        if 'query' in data:
            try:
                res = pycountry.countries.search_fuzzy(data['query'])
                _c = [{'iso': item.alpha_2.lower(), 'country': item.name} for item in res]
            except Exception as e:
                logger.warning('Pycountry exception: {0}'.format(e))
        else:
            _c = [{'iso': item.alpha_2.lower(), 'country': item.name} for item in pycountry.countries]

        return {
            'ok': True, 
            'countries': _c,
        }


class ApiAuthLogin(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAuth: {0}'.format(data))

        _errors = {}

        try:
            obj = AuthModel(**data)

            objs, found = Actor.get(username=obj.login.lower(), actor_is_active=True)
            if found == 1:
                actor = objs.pop()
                if hashlib.sha256(obj.password.encode()).hexdigest() == actor.password:
                    if actor.actor_is_active:
                        _doc = actor.to_dict()
                        _doc['last_auth'] = datetime.utcnow()
                        _doc['last_country'] = current_user.location_iso
                        _doc['ip'] = request.remote_addr
                        _doc['ua'] = str(request.user_agent)
                        # _doc['zones'] = ['admin']
                        # _doc['actor_is_admin'] = True
                        resp, obj = Actor.put(actor._id, _doc)

                        session['actor'] = obj.to_dict()

                        msg = ':man: Auth success: {0}, IP: {1} [{2}]'.format(obj.username, current_user.ip, current_user.location_iso.upper())
                        send_notify.apply_async(args=[msg])

                        return {'ok': True, 'user': obj.to_dict()}
                    else:
                        _errors['login'] = 'Account is lock'
                else:
                    _errors['password'] = 'Incorrect password'
            else:
                _errors['login'] = 'Account not found'

            msg = ':lock: Auth error: {0}, IP: {1} [{2}]'.format(obj.login, current_user.ip, current_user.location_iso.upper())
            send_notify.apply_async(args=[msg])

        except ValidationError as e:
            logger.warning('ApiAuth validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}, 401


class ApiAuthLogout(Resource):
    @login_required
    def get(self):
        if 'actor' in session:
            del session['actor']
            logger.info('ApiLogout complete')
            return {'ok': True}

        return {'ok': False}
            

class ApiAuthSignup(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAuthSignup: {0}'.format(data))

        _errors = {}

        try:
            obj = SignupModel(**data)

            try:
                validate_email(obj.login)

                objs, found = Actor.get(username=obj.login.lower())
                if found == 0:
                    password = Actor.get_random_string(8)
                    logger.info('{0} new password: {1}'.format(obj.login.lower(), password))

                    _id = Actor.generate_id(obj.login.lower(), request.remote_addr, datetime.utcnow().isoformat())
                    _doc = {
                        'id': _id,
                        'username': obj.login.lower(),
                        'password': hashlib.sha256(password.encode()).hexdigest(),
                        'actor_is_active': True,
                        'actor_is_admin': False,
                        'zones': current_app.config.get('DASHBOARD_DEFAULT_ZONES') or [],
                        'ip': request.remote_addr,
                        'ua': str(request.user_agent),
                        'sign_date': datetime.utcnow(),
                        'skype': obj.skype
                    }
                    resp, actor = Actor.put(_id, _doc)

                    tv = {"password": password, "login": actor.username}
                    send_email.apply_async(args=['sign', actor.username, 'Welcome on board', tv])

                    msg = ':id: Signup: {0}, IP: {1} [{2}]'.format(actor.username, current_user.ip, current_user.location_iso.upper())
                    send_notify.apply_async(args=[msg])

                    if len(obj.invite_code) == 56:
                        objs, total = Page.get(_id=obj.invite_code)
                        if total == 1:
                            casino = objs.pop()
                            if casino.category == 'provider':
                                casino.owner = actor._id
                                resp, casino = Page.put(casino._id, casino.to_dict())

                                msg = ':id: Casino {0} attached to {1}'.format(casino.title, actor.username)
                                send_notify.apply_async(args=[msg])

                    return {'ok': True}
                else:
                    _errors['login'] = 'Account already exist'

            except EmailNotValidError as e:
                _errors['login'] = 'E-mail is not valid'

        except ValidationError as e:
            logger.warning('ApiAuthSignup validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}     


class ApiAuthReset(Resource):
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAuthReset: {0}'.format(data))

        _errors = {}

        try:
            obj = UserModel(**data)

            try:
                validate_email(obj.login)

                objs, found = Actor.get(username=obj.login.lower())
                if found == 1:
                    password = Actor.get_random_string(8)
                    logger.info('{0} update password: {1}'.format(obj.login.lower(), password))

                    actor = objs.pop()
                    _doc = actor.to_dict()
                    _doc['password'] = hashlib.sha256(password.encode()).hexdigest()
                    resp, obj = Actor.put(actor._id, _doc)

                    tv = {"password": password}
                    send_email.apply_async(args=['reset', obj.username, 'Reset Password', tv])

                    msg = ':man: Reset password: {0}, IP: {1} [{2}]'.format(obj.username, current_user.ip, current_user.location_iso.upper())
                    send_notify.apply_async(args=[msg])

                    return {'ok': True}
                else:
                    _errors['login'] = 'Account not found'

            except EmailNotValidError as e:
                _errors['login'] = 'E-mail is not valid'
        except ValidationError as e:
            logger.warning('ApiAuthReset validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}     


class ApiAuthActor(Resource):
    @login_required
    def get(self):
        _doc = current_user.to_dict()
        _doc.pop('comment', None)
        _doc.pop('password', None)
        _doc.pop('project', None)
        return {'ok': True, 'user': _doc}


class ApiManagerUpdate(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerUpdate: {0}'.format(data))

        _errors = {}

        try:
            obj = ManagerModel(**data)

            _doc = current_user.to_dict()
            _doc['skype'] = obj.skype

            email_updated = False

            try:
                if current_user.username != obj.login.lower():
                    validate_email(obj.login)

                    objs, found = Actor.get(username=obj.login.lower())
                    if found == 0:
                        logger.info('{0} update e-mail: {1}'.format(current_user.username, obj.login.lower()))

                        password = Actor.get_random_string(8)
                        logger.info('{0} update password: {1}'.format(obj.login.lower(), password))

                        _doc['username'] = obj.login.lower()
                        _doc['password'] = hashlib.sha256(password.encode()).hexdigest()

                        # send email with password to new address
                        tv = {"password": password, "login": obj.login.lower()}
                        send_email.apply_async(args=['update', obj.login.lower(), 'You have updated your login', tv])

                        email_updated = True
                    else:
                        _errors['login'] = 'E-mail already used'

            except EmailNotValidError as e:
                _errors['login'] = 'E-mail is not valid'

            if not _errors:
                resp, obj = Actor.put(current_user._id, _doc)
                session['actor'] = obj.to_dict()

                return {'ok': True, 'updated': email_updated, 'email': obj.username}

        except ValidationError as e:
            logger.warning('ApiManagerUpdate validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}   


class ApiAdminUsers(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsers: {0}'.format(data))

        _sort = [{'username.keyword': {'order': 'asc'}}]
        if data['sorting'] in ['last_auth', 'sign_date']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        users, total = Actor.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'id', 
                'username', 
                'last_auth', 
                'last_country',
                'actor_is_active', 
                'actor_is_admin', 
                'ip', 
                'sign_date', 
                'skype', 
                'comment', 
                'zones'
            ]
        )

        def process_user(item):
            _doc = item['_source']
            return _doc

        return {'ok': True, 'users': [process_user(item) for item in users], 'total': total}


class ApiAdminUsersGet(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsersGet: {0}'.format(data))

        actors, found = Actor.get(_id=data['id'])
        if found == 1:
            actor = actors.pop()

            _sort = [{'updatedon': {'order': 'desc'}}]
            casinos, total = Page.get(
                owner=actor.id,
                category='provider',
                is_redirect=False, 
                locale='en',
                _all=True,
                _process=False,
                _sort=_sort,
                _source=[
                    'id', 
                    'updatedon',
                    'publishedon',
                    'title',
                    'path',
                    'is_active', 
                    'is_searchable', 
                    'is_draft', 
                    'status'
                ]
            )

            return {
                'ok': True, 
                'actor': {
                    'id': actor.id,
                    'username': actor.username,
                    'actor_is_active': actor.actor_is_active,
                    'actor_is_admin': actor.actor_is_admin,
                    'skype': actor.skype,
                    'comment': actor.comment,
                    'zones': actor.zones,
                },
                'casinos': [process_casino(item) for item in casinos],
                'zones': [
                    'manager',
                    'admin',
                    'content',
                    'tds',
                    'bots',
                    'tools',
                ],
                'total': total                
            }

        return {'ok': False}


class ApiAdminUsersUpdate(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsersUpdate: {0}'.format(data))

        actors, found = Actor.get(_id=data['id'])
        if found == 1:
            actor = actors.pop()

            raw = data['actor']
            actor.username = raw['username']
            actor.actor_is_active = raw['actor_is_active']
            actor.skype = raw['skype']
            actor.comment = raw['comment']

            # only SU
            if current_user.actor_is_admin:
                actor.actor_is_admin = raw['actor_is_admin']
                actor.zones = sorted(raw['zones'])

            Actor.put(actor._id, actor.to_dict())
            return {'ok': True}

        return {'ok': False}


class ApiAdminUsersRemove(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminUsersRemove: {0}'.format(data))

        actors, found = Actor.get(_id=data['id'])
        if found == 1:
            actor = actors.pop()

            # not admin and only disabled
            if not actor.actor_is_admin and not actor.actor_is_active:
                # check related entities (owner casino)
                casinos, found = Page.get(
                    category='provider',
                    owner=actor._id
                )
                for item in casinos:
                    item.owner = None
                    Page.put(item._id, item.to_dict(), _signal=False)
                    logger.info(f'Owner removed: {item.title}')

                Actor.delete(actor._id)
                return {'ok': True}

        return {'ok': False}


class ApiContentCasinos(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentCasinos: {0}'.format(data))

        kwargs = {}
        if data['table'] == 'requests':
            kwargs = {'is_draft': True, 'status': 'on_review'}
        elif data['table'] == 'drafts':
            kwargs = {'is_draft': True, 'status': 'draft'}
        elif data['table'] == 'casinos':
            kwargs = {'is_draft': False}

        _sort = [{'updatedon': {'order': 'desc'}}]
        if data['sorting'] in ['title', 'casino']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['publishedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        if data['table'] == 'commits':
            commits, _ = CasinoCommit.get(_all=True, _process=False, _sort=_sort)

            _res = []
            for item in commits:
                casinos, found = Page.get(_id=item['_source']['source_id'])
                if found == 1:
                    casino = casinos.pop()
                    _casino = casino.to_dict()
                    _casino['updatedon'] = item['_source']['updatedon']

                    obj_casino = CasinoProxyModel(**_casino)
                    obj_casino_attrs = obj_casino.dict()
                    if casino.establishedon:
                        obj_casino_attrs['year'] = casino.establishedon.year

                    obj_commit = CasinoModel(**item['_source'])
                    obj_commit_attrs = obj_commit.dict()

                    _fields = []
                    for k, v in obj_commit_attrs.items():
                        if k in obj_casino_attrs:
                            if v != obj_casino_attrs[k]:
                                _fields.append({
                                    'attr': k,
                                    'casino':  obj_casino_attrs[k],
                                    'commit': v
                                })

                    _doc = {
                        '_id': casino._id,
                        '_source': _casino,
                    }
                    _doc['_source']['commit'] = _fields
                    _doc['_source']['commit_id'] = item['_id']
                    _doc['_source']['casino_id'] = casino._id
                    _res.append(_doc)

            casinos = _res
        else:
            casinos, _ = Page.get(
                category='provider',
                **kwargs,
                locale='en',
                _all=True,
                _process=False,
                _sort=_sort,
                _source=[
                    'id', 
                    'updatedon',
                    'publishedon',
                    'title',
                    'path',
                    'is_active', 
                    'is_searchable', 
                    'is_redirect',
                    'is_sponsored',
                    'redirect',
                    'is_draft', 
                    'status',
                    'owner',
                    'ref_link',
                    'website',
                    'provider_tags',
                ]
            )

        owners = [item['_source'].get('owner') for item in casinos if item['_source'].get('owner')]
        actors, _ = Actor.get(id=owners)
        actors = {item.id: item.username for item in actors}
        logger.info('Actors found: {0}'.format(actors))

        return {
            'ok': True,
            'items': [process_casino(item, actors) for item in casinos],
        }


class ApiContentPages(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentPages: {0}'.format(data))

        _sort = [{'updatedon': {'order': 'desc'}}]
        if data['sorting'] in ['title', 'category']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['publishedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        pages, _ = Page.get(
            category=['page', 'collection'],
            locale='en',
            _all=True,
            _process=False,
            _sort=_sort,
            _source=[
                'id', 
                'updatedon',
                'publishedon',
                'title',
                'path',
                'is_active', 
                'is_searchable', 
                'is_redirect',
                'redirect',
                'category',
                'meta_title',
                'collection_mode'
            ]
        )

        def process_page(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            _doc['path'] = f"https://{current_app.config['DOMAIN']}{_doc['path']}"
            return _doc

        return {
            'ok': True,
            'items': [process_page(item) for item in pages],
        }


class ApiContentSlots(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentSlots: {0}'.format(data))

        _sort = [{'updatedon': {'order': 'desc'}}]
        if data['sorting'] in ['title', 'software']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['publishedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        pages, _ = Page.get(
            category=['slot'],
            locale='en',
            _all=True,
            _process=False,
            _sort=_sort,
            _source=[
                'id', 
                'updatedon',
                'publishedon',
                'title',
                'path',
                'is_active', 
                'is_searchable', 
                'is_redirect',
                'redirect',
                'software',
                'meta_title',
            ]
        )

        def process_page(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            _doc['path'] = f"https://{current_app.config['DOMAIN']}{_doc['path']}"
            return _doc

        return {
            'ok': True,
            'items': [process_page(item) for item in pages],
        }


class ApiContentTickets(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminTickets: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['contacts', 'subject']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        users, total = Activity.get(
            activity='ticket',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'subject', 
                'contacts',
                'name',
                'message',
                'ip', 
                'country', 
                'cid'
            ]
        )

        def process_ticket(_doc, _id):
            _doc['message'] = '<br />'.join(_doc['message'].split('\n'))   
            _doc['id'] = _id      
            return _doc

        return {'ok': True, 'tickets': [process_ticket(item.to_dict(), item._id) for item in users], 'total': total}


class ApiContentFeedback(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminFeedback: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['casino']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        users, total = Activity.get(
            activity='feedback',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'name',
                'ip', 
                'country', 
                'cid',
                'casino',
                'rate',
                'casino_id',
                'pros',
                'cons',
            ]
        )

        def process_feedback(_doc, _id):
            _doc['pros'] = '<br />'.join(_doc['pros'].split('\n'))   
            _doc['cons'] = '<br />'.join(_doc['cons'].split('\n'))   
            _doc['id'] = _id       
            return _doc

        return {'ok': True, 'feedback': [process_feedback(item.to_dict(), item._id) for item in users], 'total': total}


class ApiContentSubscribers(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminSubscribers: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['email', 'ip']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        users, total = Activity.get(
            activity='subscribe',
            _all=True,
            _sort=_sort,
            _source=[
                'id', 
                'createdon', 
                'email',
                'ip', 
                'country', 
                'cid',
            ]
        )

        def process_subscriber(_doc, _id):
            _doc['id'] = _id   
            return _doc

        return {'ok': True, 'subscribers': [process_subscriber(item.to_dict(), item._id) for item in users], 'total': total}


class ApiAdminActivity(Resource):
    @login_required
    @zone_required(zone='admin')
    def post(self):
        _d = request.get_json()
        logger.info(u'Data ApiAdminActivity: {0}'.format(_d))

        data = _d['payload']

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['country', 'ip', 'casino', 'ua']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['createdon_asc']:
            _sort = [{'createdon': {'order': 'asc'}}]

        cpp = int(data['cpp'])
        start, end = get_timerange(data['range'], data['custom_range'])

        items, total = Activity.get(
            activity='click',
            _sort=_sort,
            _process=False,
            _count=cpp,
            _offset=int(_d['offset'])*cpp,
            _range=('createdon', start, end),
            _source=[
                'id', 
                'createdon', 
                'ip', 
                'country', 
                'country_iso',
                'cid',
                'ua',
                'is_bot',
                'casino',
                'url',
                'landing',
            ]
        )

        def process_activity(item):
            _doc = item['_source']
            _doc['id'] = item['_id']      
            return _doc

        return {'ok': True, 'items': [process_activity(item) for item in items], 'total': total}


class ApiContentActivityRemove(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiAdminActivityRemove: {0}'.format(data))

        activities, found = Activity.get(_id=data['id'])
        if found == 1:
            activity = activities.pop()
            Activity.delete(activity._id)
            return {'ok': True}

        return {'ok': False}


class ApiContentCommit(Resource):
    @login_required
    @zone_required(zone='content')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiContentCommit: {0}'.format(data))

        commits, commits_found = CasinoCommit.get(_id=data['commit_id'])
        casinos, casinos_found = Page.get(_id=data['casino_id'])

        if commits_found and casinos_found:
            commit = commits.pop()
            casino = casinos.pop()

            if data['action'] == 'reject':
                resp = CasinoCommit.delete(commit._id)
                logger.info(f'Commit for {commit.casino} rejected: {resp}')
                
                casino.status = 'published'
                resp, _ = Page.put(casino._id, casino.to_dict())
                logger.info(f'Casino status updated: {resp}')

                return {'ok': True, 'rejected': True}
            elif data['action'] == 'accept':
                _commit = commit.to_dict()
                _casino = casino.to_dict()
                if 'attr' in data:
                    _attr = data['attr']
                    if _attr in _commit:
                        if _attr == 'year':
                            if _commit[_attr]:
                                _casino['establishedon'] = datetime(year=int(_commit[_attr]), month=1, day=1)
                        else:
                            _casino[_attr] = _commit[_attr]
                        resp, _ = Page.put(casino._id, _casino)
                        logger.info(f'Casino attr {_attr} updated: {resp}')
                else:
                    # accept all
                    if _commit['year']:
                        _commit['establishedon'] = datetime(year=int(_commit['year']), month=1, day=1)

                    _casino.update(_commit)
                    _casino['status'] = 'published'

                    resp, _ = Page.put(casino._id, _casino)
                    logger.info(f'Casino attrs and status updated: {resp}')

                    resp = CasinoCommit.delete(commit._id)
                    logger.info(f'Commit for {commit.casino} accepted: {resp}')

                    return {'ok': True, 'accepted': True}

            return {'ok': True}

        return {'ok': False}, 404


class ApiManagerCasinos(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinos: {0}'.format(data))

        _sort = [{'publishedon': {'order': 'desc'}}]
        if data['sorting'] in ['title']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['updatedon']:
            _sort = [{data['sorting']: {'order': 'desc'}}]

        casinos, total = Page.get(
            owner=current_user.id,
            category='provider',
            is_redirect=False, 
            locale='en',
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'id', 
                'publishedon',
                'updatedon', 
                'title',
                'path',
                'is_active', 
                'is_draft', 
                'status'
            ]
        )

        return {'ok': True, 'casinos': [process_casino(item, {}, True) for item in casinos], 'total': total}


class ApiManagerActivity(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        _d = request.get_json()
        logger.info(u'Data ApiManagerActivity: {0}'.format(_d))

        data = _d['payload']

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['country', 'ip', 'casino', 'ua']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
        elif data['sorting'] in ['createdon_asc']:
            _sort = [{'createdon': {'order': 'asc'}}]

        cpp = int(data['cpp'])
        start, end = get_timerange(data['range'], data['custom_range'])

        casinos, total = Page.get(
            owner=current_user.id,
            category='provider',
            is_redirect=False, 
            locale='en',
            _all=True,
            _source=[
                'id', 
                'publishedon',
                'updatedon', 
                'title',
                'path',
                'is_active', 
                'is_draft', 
            ]
        )

        casino_list = [item.title for item in casinos]
        logger.info('Casinos: {0}'.format(casino_list))

        users, total = Activity.get(
            activity='click',
            casino=casino_list,
            is_bot=False,
            _sort=_sort,
            _process=False,
            _count=cpp,
            _offset=int(_d['offset'])*cpp,
            _range=('createdon', start, end),
            _source=[
                'id', 
                'createdon', 
                'ip', 
                'country', 
                'country_iso',
                'ua',
                'is_bot',
                'casino',
            ]
        )

        def process_activity(item):
            _doc = item['_source']
            _doc['id'] = item['_id']         
            return _doc

        return {'ok': True, 'items': [process_activity(item) for item in users], 'total': total}


class ApiManagerCasinosGet(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinosGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            casinos, found = Page.get(_id=data['id'])
            if found == 1:
                casino = casinos.pop()
                if casino.owner == current_user.id and casino.status in ['draft', 'published']:
                    _attrs = casino.to_dict()

                    if casino.establishedon:
                        _attrs['year'] = casino.establishedon.year

                    if casino.status == 'published':
                        commits, found = CasinoCommit.get(
                            source_id=casino._id,
                            actor_id=current_user.id
                        )
                        if found == 1:
                            commit = commits.pop()
                            _attrs.update(commit.to_dict())
                            logger.info(f'Data from commit {commit._id} loaded')

                    obj = CasinoProxyModel(**_attrs)
                    _doc = obj.dict()
                    logger.info(u'Casino found: {0}'.format(_doc))
                else:
                    return {'ok': False}, 401
            else:
                return {'ok': False}, 404

        support = current_app.config['DASHBOARD_SUPPORT']

        options = Page.get_options()
        wl = [
            'services',
            'languages', 
            'payment_methods',
            'software',
            'currency',
            'games',
            'licences',
            'countries_name'
        ]
        _res = {}
        for k, v in options.items():
            if k in wl:
                _res[k] = sorted(v)

        return {'ok': True, 'support': support, 'options': _res, 'casino': _doc}


class ApiManagerCasinosSave(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinosSave: {0}'.format(data))

        _errors = {}
        try:
            obj = CasinoModel(**data['payload'])
            _doc = obj.dict()

            if _doc['year']:
                _doc['establishedon'] = datetime(year=int(_doc['year']), month=1, day=1)

            if 'id' in data:
                casinos, found = Page.get(_id=data['id'])
                if found == 1:
                    casino = casinos.pop()
                    if casino.owner == current_user.id and casino.status in ['draft', 'published']:
                        if casino.status and casino.status == 'draft':
                            _attrs = casino.to_dict()
                            _attrs.update(_doc)

                            _attrs['suggest'] = _doc['title']
                            _attrs['alt_title'] = _doc['title']
                            _attrs['updatedon'] = datetime.utcnow()

                            logger.info(f'Doc for update casino: {_attrs}')
                            resp, obj = Page.put(casino._id, _attrs)
                        elif casino.status == 'published':
                            commits, found = CasinoCommit.get(
                                source_id=casino._id,
                                actor_id=current_user.id
                            )
                            if found == 1:
                                commit = commits.pop()
                                _attrs = commit.to_dict()
                                _attrs.update(_doc)

                                _attrs['updatedon'] = datetime.utcnow()
                                _doc['casino'] = casino.title

                                resp, obj = CasinoCommit.put(commit._id, _attrs)
                                logger.info(f'Commit updated: {resp}')
                            elif found == 0:
                                _doc['updatedon'] = datetime.utcnow()
                                _doc['source_id'] = casino._id
                                _doc['actor_id'] = current_user.id
                                _doc['casino'] = casino.title

                                resp, obj = CasinoCommit.put(CasinoCommit.generate_id([casino._id, current_user.id]), _doc)
                                logger.info(f'Commit created: {resp}')
                    else:
                        return {'ok': False}, 401
                else:
                    return {'ok': False}, 404

            else:
                alias = Page.get_random_string(10).lower()
                _meta = {
                    'category': 'provider',
                    'locale': 'en',
                    'is_active': False,
                    'is_searchable': False,
                    'is_draft': True,
                    'alias': alias,
                    'suggest': _doc['title'],
                    'alt_title': _doc['title'],
                    'publishedon': datetime.utcnow().date(),
                    'updatedon': datetime.utcnow(),
                    'owner': current_user.id,
                    'status': 'draft',
                    'theme_color': '#6B8794',
                }

                _doc.update(_meta)
                _doc['path'] = get_page_url(_doc)

                logger.info(f'Doc for create casino: {_doc}')
                resp, obj = Page.put(Page.generate_id(_doc['path'], _doc['locale']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiManagerCasinosSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'type_error.none.not_allowed': 'Required field',
                'value_error.list.min_items': 'Required field',
                'type_error.integer': 'Not a valid integer',
                'value_error.url.scheme': 'Not a valid URL',
                'value_error.email': 'Not a valid e-mail',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiManagerCasinosPublish(Resource):
    @login_required
    @zone_required(zone='manager')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiManagerCasinosPublish: {0}'.format(data))

        if 'id' in data:
            casinos, found = Page.get(_id=data['id'])
            if found == 1:
                casino = casinos.pop()
                if casino.owner == current_user.id:
                    _doc = casino.to_dict()
                    _doc['status'] = 'on_review'
                    _doc['updatedon'] = datetime.utcnow()
                    resp, obj = Page.put(casino._id, _doc)
                    return {'ok': True}
                else:
                    return {'ok': False}, 401

        return {'ok': False}, 404


class ApiTdsDomains(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsDomains: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['domain']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        domains, _ = TdsDomain.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'domain', 
                'endpoint', 
                'createdon',
                'is_https'
            ]
        )

        def process_domain(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            return _doc

        return {'ok': True, 'items': [process_domain(item) for item in domains]}


class ApiTdsDomainsGet(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsDomainsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            domains, found = TdsDomain.get(_id=data['id'])
            if found == 1:
                domain = domains.pop()
                _attrs = domain.to_dict()
                obj = DomainModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Domain found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404

        return {'ok': True, 'options': {}, 'domain': _doc}


class ApiTdsDomainsSave(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsDomainsSave: {0}'.format(data))

        _errors = {}
        try:
            obj = DomainModel(**data['payload'])
            _doc = obj.dict()

            if 'id' in data:
                domains, found = TdsDomain.get(_id=data['id'])
                if found == 1:
                    domain = domains.pop()

                    _attrs = domain.to_dict()
                    _attrs.update(_doc)

                    logger.info(f'Doc for update domain: {_attrs}')
                    resp, obj = TdsDomain.put(domain._id, _attrs)
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                }

                _doc.update(_meta)

                logger.info(f'Doc for create domain: {_doc}')
                resp, obj = TdsDomain.put(Page.generate_id(_doc['domain'], _doc['endpoint']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTdsDomainsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiTdsStats(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        _d = request.get_json()
        logger.info(u'Data ApiTdsStats: {0}'.format(_d))

        data = _d['payload']

        cpp = int(data['cpp'])
        start, end = get_timerange(data['range'], data['custom_range'])

        items = []
        total = 0
        aggs_name = None

        if data['mode'] == 'Clicks':
            _sort = [{'createdon': {'order': 'desc'}}]

            if data['sorting'] in ['click_id', 'ip', 'country', 'ua', 'campaign_name', 'stream_name']:
                _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]
            elif data['sorting'] in ['createdon_asc']:
                _sort = [{'createdon': {'order': 'asc'}}]

            items, total = TdsHit.get(
                _sort=_sort,
                _process=False,
                _count=cpp,
                _offset=int(_d['offset'])*cpp,
                _range=('createdon', start, end),
                _source=[
                    'createdon',
                    'stream',
                    'stream_name',
                    'campaign_name',
                    'campaign_alias',
                    'click_id',
                    'ip',
                    'country',
                    'country_iso',
                    'ua',
                    'is_bot',
                    'is_uniq',
                    'action',
                    'url',
                    'subid',
                ]
            )

            def process_hit(item):
                _doc = item['_source']
                _doc['id'] = item['_id']    
                _doc['country_iso'] = _doc['country_iso'].lower()     
                return _doc

            items = [process_hit(item) for item in items]
        else:
            field = None
            if data['mode'] == 'By Day':
                aggs_name = 'Days'
                field = 'createdon'
            elif data['mode'] == 'By Campaign':
                aggs_name = 'Campaigns'
                field = 'campaign_id'
            elif data['mode'] == 'By Stream':
                aggs_name = 'Streams'
                field = 'stream'
            elif data['mode'] == 'By Geo':
                aggs_name = 'Countries'
                field = 'country'
            elif data['mode'] == 'By Link':
                aggs_name = 'Links'
                field = 'url'
            elif data['mode'] == 'By User-Agent':
                aggs_name = 'User-Agents'
                field = 'ua'
            elif data['mode'] == 'By IP':
                aggs_name = 'IP'
                field = 'ip'
            elif data['mode'] == 'By Sub-ID':
                aggs_name = 'Sub-ID'
                field = 'subid'
            elif data['mode'] == 'By Action':
                aggs_name = 'Actions'
                field = 'action'

            if field:
                items, total = TdsHit.aggs(field, _range=('createdon', start, end))

        return {'ok': True, 'items': items, 'total': total, 'aggs_name': aggs_name}


class ApiTdsCampaigns(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaigns: {0}'.format(data))

        _sort = [{'createdon': {'order': 'desc'}}]
        if data['sorting'] in ['name', 'alias']:
            _sort = [{'{0}.keyword'.format(data['sorting']): {'order': 'asc'}}]

        campaigns, _ = TdsCampaign.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'name', 
                'alias',
                'createdon',
                'updatedon',
                'is_active',
                'is_split',
                'groups',
                'domain',
                'streams',
            ]
        )

        start, end = get_timerange(data['payload']['range'], data['payload']['custom_range'])
        stats, _ = TdsHit.aggs('stream', _range=('createdon', start, end))
        stats = {item['term']: {'hits': item['hits'], 'uc': item['uc']} for item in stats}

        def process_campaign(item):
            _doc = item['_source']
            _doc['id'] = item['_id']
            _doc['url'] = '{0}{1}'.format(_doc['domain'], _doc['alias'])
            return _doc

        return {'ok': True, 'items': [process_campaign(item) for item in campaigns], 'stats': stats}


class ApiTdsCampaignsGet(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsGet: {0}'.format(data))

        _doc = {}
        if data and 'id' in data:
            campaigns, found = TdsCampaign.get(_id=data['id'])
            if found == 1:
                campaign = campaigns.pop()
                _attrs = campaign.to_dict()
                obj = CampaignModel(**_attrs)
                _doc = obj.dict()
                logger.info(u'Campaign found: {0}'.format(_doc))
            else:
                return {'ok': False}, 404
        else:
            _doc['alias'] = BaseEntity.get_urlsafe_string(6)
            _doc['groups'] = []
            _doc['ttl'] = 86400

        domains, _ = TdsDomain.get(
            _all=True,
            _process=False,
            _source=[
                'domain', 
                'endpoint',
                'is_https',
            ]
        )

        campaigns, _ = TdsCampaign.get(
            _all=True,
            _process=False,
            _source=[
                'name', 
                'groups',
            ]
        )

        def process_campaign(_doc):
            return {
                'id': _doc['_id'],
                'name': _doc['_source']['name']
            }

        _groups = []
        for item in campaigns:
            _groups += item['_source'].get('groups', [])

        _opts = {
            'countries': [{'iso': item.alpha_2, 'country': item.name} for item in pycountry.countries],
            'domains': ['{2}://{0}{1}'.format(item['_source']['domain'], item['_source']['endpoint'], 'https' if item['_source']['is_https'] else 'http') for item in domains],
            'campaigns': [process_campaign(item) for item in campaigns if not data or (data and data.get('id') != item['_id'])],
            'groups': sorted(list(set(_groups))),
            'actions': [
                {'key': '404', 'value': '404 NotFound'},
                {'key': 'http', 'value': 'HTTP Redirect'},
                {'key': 'js', 'value': 'JS Redirect'},
                {'key': 'meta', 'value': 'Meta Redirect'},
                {'key': 'curl', 'value': 'cURL'},
                {'key': 'remote', 'value': 'Remote URL'},
                {'key': 'campaign', 'value': 'Send to Campaign'},
                {'key': 'html', 'value': 'Show as HTML'},
            ]
        }

        return {'ok': True, 'options': _opts, 'campaign': _doc}


class ApiTdsCampaignsSave(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsSave: {0}'.format(data))

        _errors = {}
        try:
            obj = CampaignModel(**data['payload'])
            _doc = obj.dict()

            def process_streams(_s):
                # check all streams
                _res = []
                for stream in _s:
                    if 'id' not in stream:
                        stream['id'] = BaseEntity.get_urlsafe_string(6)
                    if stream.get('is_default'):
                        stream['position'] = None
                        stream['is_bot'] = False
                        stream['advanced_mode'] = False
                        stream['is_unique'] = False
                        stream['is_mobile'] = False
                        stream['is_empty_referrer'] = False
                        stream['is_ipv6'] = False
                        stream['geo'] = []
                        stream['ip'] = None
                        stream['ua'] = None
                        stream['subid'] = None
                    if stream.get('is_bot'):
                        stream['advanced_mode'] = False
                        stream['is_unique'] = False
                        stream['is_mobile'] = False
                        stream['is_empty_referrer'] = False
                        stream['is_ipv6'] = False
                        stream['geo'] = []
                        stream['ip'] = None
                        stream['ua'] = None
                        stream['subid'] = None

                    if stream['action'] in ['http', 'js', 'meta', 'curl', 'remote']:
                        stream['campaign'] = None
                        stream['html'] = None
                    elif stream['action'] in ['404']:
                        stream['url'] = None
                        stream['campaign'] = None
                        stream['html'] = None
                    elif stream['action'] in ['campaign']:
                        stream['url'] = None
                        stream['html'] = None
                    elif stream['action'] in ['html']:
                        stream['url'] = None
                        stream['campaign'] = None

                    _res.append(stream)
                return sorted(_res, key = lambda i: int(i.get('position') or 1000))

            if 'id' in data:
                campaigns, found = TdsCampaign.get(_id=data['id'])
                if found == 1:
                    campaign = campaigns.pop()

                    _attrs = campaign.to_dict()
                    _attrs.update(_doc)

                    _attrs['streams'] = process_streams(_attrs['streams'])
                    _attrs['updatedon'] = datetime.utcnow()

                    logger.info(f'Doc for update campaign: {_attrs}')
                    resp, obj = TdsCampaign.put(campaign._id, _attrs)
                else:
                    return {'ok': False}, 404

            else:
                _meta = {
                    'createdon': datetime.utcnow(),
                    'updatedon': datetime.utcnow(),
                }

                _doc.update(_meta)
                _doc['streams'] = process_streams(_doc['streams'])

                logger.info(f'Doc for create campaign: {_doc}')
                resp, obj = TdsCampaign.put(Page.generate_id(_doc['alias'], _doc['domain']), _doc)

            return {'ok': True}

        except ValidationError as e:
            logger.warning('ApiTdsCampaignsSave validation: {0}'.format(e.json()))
            _error_options = {
                'value_error.missing': 'Required field',
                'value_error.list.min_items': 'Required field',
                'type_error.none.not_allowed': 'Required field',
                'type_error.integer': 'Not a valid integer',
            }
            _errors = {item['loc'][0]: _error_options.get(item['type'], item['msg']) for item in loads(e.json())}

        return {'ok': False, 'errors': _errors}


class ApiTdsCampaignsClone(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsClone: {0}'.format(data))

        if 'id' in data:
            campaigns, found = TdsCampaign.get(_id=data['id'])
            if found == 1:
                campaign = campaigns.pop()

                _doc = campaign.to_dict()

                # check all streams
                _res = []
                for stream in _doc['streams']:
                    stream['id'] = BaseEntity.get_urlsafe_string(6)
                    _res.append(stream)

                _doc['streams'] = _res
                _doc['alias'] = BaseEntity.get_urlsafe_string(6)
                _doc['name'] = '{0} [{1}]'.format(campaign.name, _doc['alias'])
                _doc['createdon'] = datetime.utcnow()
                _doc['updatedon'] = datetime.utcnow()

                logger.info(f'Doc for clone campaign: {_doc}')
                TdsCampaign.put(ElasticEntity.generate_id(_doc['alias'], _doc['domain']), _doc)

                return {'ok': True}

        return {'ok': False}, 404


class ApiTdsCampaignsClear(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsClear: {0}'.format(data))

        if 'id' in data:
            campaigns, found = TdsCampaign.get(_id=data['id'])
            if found == 1:
                campaign = campaigns.pop()
                if campaign.is_active:
                    return {'ok': False}
                else:
                    tdscampaign_clear.apply_async(args=[campaign._id])
                    return {'ok': True}

        return {'ok': False}, 404


class ApiTdsCampaignsToggle(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignsToggle: {0}'.format(data))

        campaigns, found = TdsCampaign.get(_id=data['campaign'])
        if found == 1:
            campaign = campaigns.pop()

            _c = None
            _s = None
            _status = False

            if 'stream' in data:
                _s = data['stream']

                _res = []
                for stream in campaign.streams:
                    if stream['id'] == _s:
                        _status = not stream.get('is_active', False)
                        stream['is_active'] = _status                        
                    _res.append(stream)

                campaign.streams = _res
                TdsCampaign.put(campaign._id, campaign.to_dict())
            else:
                _status = not campaign.is_active
                campaign.is_active = _status
                TdsCampaign.put(campaign._id, campaign.to_dict())
                _c = campaign.alias

            return {'ok': True, 'status': _status, 'campaign': _c, 'stream': _s}

        return {'ok': False}, 404


class ApiTdsBotsUpload(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        logger.info(u'Data ApiTdsBotsUpload: {0}'.format(request.form))
        file = request.files['file']
        data = [item.strip().decode() for item in file.readlines()]
        tdscampaign_bots.apply_async(args=[data, request.form['section']])
        return {'ok': True}


class ApiTdsSettings(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsBots: {0}'.format(data))
        ip_count = current_app.redis.scard(f'tds_bots_ip')
        ua_count = current_app.redis.scard(f'tds_bots_ua')

        _sort = [{'createdon': {'order': 'desc'}}]
        campaigns, _ = TdsCampaign.get(
            _all=True,
            _sort=_sort,
            _process=False,
            _source=[
                'name', 
                'alias',
            ]
        )

        def process_uniq(s):
            _doc = s['_source']
            _doc['id'] = s['_id']
            _doc['count'] = current_app.redis.hlen(f'tds_uniq_{_doc["alias"]}')
            return _doc

        uniq = [process_uniq(item) for item in campaigns]

        return {'ok': True, 'ip_count': ip_count, 'ua_count': ua_count, 'uniq': uniq}


class ApiTdsBotsClear(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsBotsClear: {0}'.format(data))
        current_app.redis.delete(f'tds_bots_{data["section"]}')
        return {'ok': True}


class ApiTdsCampaignUniqClear(Resource):
    @login_required
    @zone_required(zone='tds')
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiTdsCampaignUniqClear: {0}'.format(data))

        campaigns, total = TdsCampaign.get(_id=data['id'])
        if total == 1:
            campaign = campaigns.pop()
            current_app.redis.delete(f"tds_uniq_{campaign.alias}")
            return {'ok': True}

        return {'ok': False}


class ApiResourceSignupLink(Resource):
    @login_required
    @su_required
    def post(self):
        data = request.get_json()
        logger.info(u'Data ApiResourceSignupLink: {0}'.format(data))

        url = f"https://{current_app.config['DASHBOARD_DOMAIN']}/signup?invite=" + data['key']

        return {'ok': True, 'url': url}
