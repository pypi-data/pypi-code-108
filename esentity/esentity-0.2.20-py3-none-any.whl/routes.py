#coding: utf-8
import json
from flask import request, redirect, abort, current_app, make_response
from datetime import datetime
from flask_login import current_user
import random
import hashlib
import shortuuid
import ipaddress
import base64
import codecs
from loguru import logger 
from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode, urlunparse
from esentity.tasks import tdscampaign_hit
from esentity.models import BaseEntity


def tds_stream(alias):
    logger.info(f'Process stream: {alias}')

    uri = urlparse(request.url)
    qs = parse_qs(uri.query)

    key = uri._replace(query='', fragment='').geturl()
    campaign = current_app.redis.hget('tds_channels', key)

    logger.info(f'Get campaign by key ({key}): {campaign}')

    if campaign:
        campaign = json.loads(campaign)
        # logger.info(f'Campaign found: {campaign}')

        if campaign['is_active']:
            subid = None
            if qs:
                subid = qs.get('subid', [None]).pop()  
                logger.info(f'subid found: {subid}')

            click_id = shortuuid.ShortUUID().random(length=12)
            logger.info(f'click_id generated: {click_id}')

            ua = current_user.user_agent

            # generate by settings: ip, ip + ua, ip + ua + cookies
            is_uniq = True
            uniq_key = ':'.join([
                current_user.ip,
                ua.ua_string
            ])
            hashed_uniq_key = hashlib.md5(uniq_key.encode()).hexdigest()

            ts = int(datetime.utcnow().timestamp())
            ttl = current_app.redis.hget(f"tds_uniq_{alias}", uniq_key)
            if ttl:
                if ts - int(ttl) < campaign['ttl']:
                    is_uniq = False
                else:
                    current_app.redis.hset(f"tds_uniq_{alias}", uniq_key, ts)
                    is_uniq = True
            else:
                current_app.redis.hset(f"tds_uniq_{alias}", uniq_key, ts)
            logger.info(f'uniq: {is_uniq}')

            logger.info(f'referrer: {request.referrer}')

            # '2001:db8::' or 
            ip_obj = ipaddress.ip_address(current_user.ip)
            is_ipv6 = ip_obj.version == 6
            logger.info(f'is_ipv6: {is_ipv6}')

            is_bot = ua.is_bot

            # check is_bot by IP and UA from tds settings
            if not is_bot and not is_ipv6:
                is_bot = current_app.redis.sismember('tds_bots_ip', int(ip_obj))
                if is_bot:
                    logger.info(f'is_bot by ip blocklist: {int(ip_obj)}')

            if not is_bot:
                is_bot = current_app.redis.sismember('tds_bots_ua', str(ua))
                if is_bot:
                    logger.info(f'is_bot by ua blocklist: {str(ua)}')

            logger.info(f'UA found: {ua}, is_bot: {is_bot}, is_mobile: {ua.is_mobile}')


            def process_stream(_s):
                url = None

                if _s['action'] == 'campaign':
                    if 'campaign' in _s:
                        url = current_app.redis.hget('tds_channels_url', _s['campaign']).decode('utf-8')
                        params = {'subid': click_id}
                        url_parts = list(urlparse(url))
                        _q = dict(parse_qsl(url_parts[4]))
                        _q.update(params)
                        url_parts[4] = urlencode(_q)
                        url = urlunparse(url_parts)
                        logger.info(f'URL updated: {url}')
                else:
                    url = _s.get('url')

                if url:
                    snippets = {
                        'cid': click_id,
                        'subid': subid
                    }
                    for k, v in snippets.items():
                        snip = '{' + k + '}'
                        if snip in url:
                            url = url.replace(snip, v)

                # send task to create activity
                _doc = {
                    'createdon': datetime.utcnow(),
                    'stream': _s['id'],
                    'stream_name': _s['name'],
                    'campaign_name': campaign['name'],
                    'campaign_alias': campaign['alias'],
                    'campaign_id': campaign['id'],
                    'click_id': click_id,
                    'ip': current_user.ip,
                    'country_iso': current_user.location_iso.upper(),
                    'ua': str(ua),
                    'is_bot': is_bot,
                    'is_uniq': is_uniq,
                    'action': _s['action'],
                    'url': url if _s['action'] in ['http', 'campaign', 'js'] else None,
                    'subid': subid,
                    'fingerprint': hashed_uniq_key
                }
                tdscampaign_hit.apply_async(args=[_doc])

                if _s['action'] in ['http', 'campaign']:
                    if url:
                        logger.info(f'Redirect to: {url}')
                        response = make_response(redirect(url), 302)
                        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                        response.headers['Pragma'] = 'no-cache'
                        return response
                    else:
                        abort(404)
                elif _s['action'] == '404':
                    abort(404)
                elif _s['action'] == 'html':
                    return _s.get('html'), 200
                elif _s['action'] == 'js':
                    if url:
                        def _c(s):
                            return codecs.encode(base64.b64encode(s.encode()).decode(), 'rot_13')
                        _res = '<script>const {4}=function(s,i){{return s.replace(/[a-zA-Z]/g,function(c){{return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+i)?c:c-26)}});}};setTimeout(function(){{window[atob({4}("{0}",13))][atob({4}("{1}",13))]=atob({4}("{2}",13));}},{3});</script>'.format(_c('location'), _c('href'), _c(url), random.randint(1, 10), '_' + BaseEntity.get_urlsafe_string(4))
                        return _res, 200
                    else:
                        abort(404)
                # elif _s['action'] == 'meta':
                #     return _s.get('html'), 200
                # elif _s['action'] == 'curl':
                #     return _s.get('html'), 200
                # elif _s['action'] == 'remote':
                #     return _s.get('html'), 200                


            if campaign['is_split']:
                _w = tuple([int(item['weight']) for item in campaign['streams'] if item.get('is_active') and item.get('weight')])
                logger.info(f'w: {_w}')
                if _w:
                    stream = random.choices([item for item in campaign['streams'] if item.get('is_active') and item.get('weight')], weights=_w)

                    if len(stream):
                        _res = process_stream(stream[0])
                        if _res:
                            return _res
                abort(404)
            else:
                for stream in campaign['streams']:
                    if stream.get('is_active', False):
                        logger.info(f'Process stream: {stream["id"]}')
                        process = []

                        if stream.get('is_default'):
                            process.append(True)
                        else:
                            if stream.get('is_bot'):
                                process.append(is_bot)

                            if 'geo' in stream and len(stream['geo']):
                                rule_geo = current_user.location_iso.upper() in stream.get('geo', [])
                                process.append(rule_geo)

                            if stream.get('is_unique'):
                                process.append(is_uniq)

                            if stream.get('is_mobile'):
                                process.append(ua.is_mobile)

                            if stream.get('is_empty_referrer'):
                                process.append(request.referrer == None)

                            if stream.get('is_ipv6'):
                                process.append(is_ipv6)
                            else:
                                if stream.get('ip'):
                                    try:
                                        ip_obj = ipaddress.ip_address(stream['ip'])
                                        logger.info(f'ip_address found: {ip_obj}')
                                        process.append(ip_obj == ipaddress.ip_address(current_user.ip)) 
                                    except ValueError:
                                        try:
                                            network = ipaddress.ip_network(stream['ip'])
                                            logger.info(f'ip_network found: {network}, hosts: {network.num_addresses}')
                                            # logger.info(f'ip_network hosts: {list(network)}')

                                            in_network = ipaddress.ip_address(current_user.ip) in network
                                            logger.info(f'in_network: {in_network}')

                                            process.append(in_network) 
                                        except ValueError:
                                            logger.info(f"Invalid ip value: {stream.get('ip')}")
                                            process.append(False)

                            if stream.get('ua'):
                                process.append(stream['ua'].lower() in ua.ua_string.lower()) 

                            if stream.get('subid'):
                                process.append(stream['subid'] == subid) 

                        logger.info(f'Process rules: {process}')

                        if False not in process:
                            _res = process_stream(stream)
                            if _res:
                                return _res

                        if stream.get('is_default'):
                            break
        
    abort(404)