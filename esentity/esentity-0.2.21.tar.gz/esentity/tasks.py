#coding: utf-8
from flask import current_app
import os
from datetime import datetime, timedelta
from json import dumps
import requests
from loguru import logger 
from notifiers import get_notifier
import pycountry 
from emoji import emojize
from esentity.models import TdsCampaign, TdsHit, Page
import time
import ipaddress
from celery import shared_task


@shared_task
def add_vote(id, activity):
    logger.info('Add Vote: {0}'.format(activity))

    objs, total = Page.get(_id=activity['casino_id'])
    if total == 1:
        obj = objs.pop()
        if obj.is_active and not obj.is_redirect:
            _res = []
            _found = False
            _update = True

            for item in obj.comments:
                if 'hash' in item and item['hash'] == id:
                    if not item['is_disable']:
                        item['publishedon'] = activity['createdon'] 
                        item['rate'] = activity['rate'] 
                    else:
                        logger.info('Vote found: {0}, but is_disable'.format(item['hash']))
                        _update = False
                    _found = True
                _res.append(item)
            
            if not _found:
                _res.insert(0, {
                    'is_disable': False,
                    'publishedon': activity['createdon'],
                    'ip': activity['ip'],
                    'country': activity['country_iso'],
                    'rate': activity['rate'],
                    'hash': id
                })                

            if _update:
                obj.comments = _res
                resp, obj = Page.put(obj._id, obj.to_dict(), _signal=False)
                logger.info('Update casino [{1}]: {0}'.format(resp, obj.title))


@shared_task
def send_notify(msg):
    n = get_notifier('telegram')
    for cid in current_app.config['TELEGRAM_RECIPIENTS']:
        res = n.notify(
            message=f"[{current_app.config['TELEGRAM_PREFIX_MESSAGE']}] {emojize(msg, use_aliases=True)}", 
            token=current_app.config['TELEGRAM_TOKEN'], 
            chat_id=cid,
            disable_web_page_preview=True,
            disable_notification=True,
        )
        logger.info('Notify response: {0}'.format(res))


@shared_task
def send_email(template, to, subject, tv):
    send_res = requests.post(
        current_app.config['MAILGUN_ENDPOINT'],
        auth=("api", current_app.config['MAILGUN_TOKEN']),
        data={"from": current_app.config['MAILGUN_FROM'],
            "to": to,
            "subject": subject,
            "template": template,
            "h:X-Mailgun-Variables": dumps(tv)})
    logger.info('Email ({1}) send: {0}'.format(send_res.json(), template))


@shared_task
def tdscampaign_bots(data, section):

    def process_item(v, k):
        current_app.redis.sadd(f'tds_bots_{k}', v)

    for item in data:
        s = item
        if not '#' in s:
            if section == 'ip':
                if '-' in s:
                    min, max = s.split('-')
                    min = ipaddress.ip_address(min)
                    max = ipaddress.ip_address(max)
                    if min.version == 4 and max.version == 4 and min < max:
                        i = 0
                        while min <= max:
                            _v = ipaddress.ip_address(min) + i
                            logger.info(f'ip_address found: {_v}')
                            process_item(int(_v), 'ip')
                            i += 1
                else:
                    try:
                        ip_obj = ipaddress.ip_address(s)
                        if ip_obj.version == 4:
                            logger.info(f'ip_address found: {ip_obj}')
                            process_item(int(ip_obj), 'ip')
                    except ValueError:
                        try:
                            network = ipaddress.ip_network(s)
                            logger.info(f'ip_network found: {network}, hosts: {network.num_addresses}')

                            for _ip in network:
                                if _ip.version == 4:
                                    logger.info(f'ip_address found: {_ip}')
                                    process_item(int(_ip), 'ip')

                        except ValueError:
                            pass
            elif section == 'ua':
                logger.info(f'ua found: {s}')
                process_item(s, 'ua')


@shared_task
def tdscampaign_setup(id, campaign):
    logger.info('Setup TDS campaign: {0}'.format(campaign['name']))
    key = '{0}{1}'.format(campaign['domain'], campaign['alias'])
    current_app.redis.hset('tds_channels_url', id, key)

    if campaign['is_active']:
        campaign['id'] = id
        current_app.redis.hset('tds_channels', key, dumps(campaign))
        logger.info('Add campaign')
    else:
        current_app.redis.hdel('tds_channels', key)
        logger.info('Remove campaign')


@shared_task
def tdscampaign_clear(id):
    logger.info('Clear campaign stats: {0}'.format(id))
    campaigns, total = TdsCampaign.get(_id=id)
    if total == 1:
        campaign = campaigns.pop()
        if not campaign.is_active:
            hits, total = TdsHit.get(
                campaign_id=campaign._id,
                _process=False, 
                _source=False, 
                _all=True,
            )
            logger.info(f'Hits for remove: {total}')
            for item in hits:
                resp = TdsHit.delete(item['_id'], _refresh=False)
                logger.info(f'Hit removed: {resp}')

            current_app.redis.delete(f"tds_uniq_{campaign.alias}")
            logger.info(f'Uniq stack for {campaign.alias} removed')
        else:
            logger.warning(f'Campaign {campaign.name} is active, only disabled may by cleared')


@shared_task
def tdscampaign_hit(_doc):
    logger.info(f'Process TDS click: {_doc}')

    _cn = pycountry.countries.get(alpha_2=_doc['country_iso'])
    _doc['country'] = _cn.name if _cn else 'United Kingdom'

    resp, _ = TdsHit.put(TdsHit.generate_id(_doc['ip'], _doc['click_id']), _doc, _refresh=False, _signal=False)
    logger.info(f'Hit response: {resp}')

    _a = ''
    if _doc['action'] == '404':
        _a = ', 404'
    elif _doc['action'] in ['http', 'campaign', 'js']:
        _a = f", url: {_doc['url']}"

    msg = f"Hit: {_doc['campaign_name']} | {_doc['stream_name']} [{_doc['click_id']}], IP: {_doc['ip']} [{_doc['country_iso'].upper()}], is_bot: {_doc['is_bot']}{_a}"
    send_notify.apply_async(args=[msg])


@shared_task
def backup(indices, prefix):
    host = '{0}:{1}'.format(os.environ.get('ES', 'localhost'), 9200)
    logger.info('Process Snapshot Elasticsearch: {0}'.format(host))

    snap = f"{prefix}{datetime.utcnow().strftime('%Y-%m-%d')}"
    logger.info('Snap: {0}'.format(snap))

    snap_url = 'http://{0}/_snapshot/backup/{1}'.format(host, snap)

    r = requests.get(snap_url)
    if r.status_code == 200:
        r = requests.delete(snap_url)        
        logger.info('Snapshot {0} already exist, remove it: {1}'.format(snap, r.json()))

    if indices:
        r = requests.put(snap_url, json={'indices': indices})
        logger.info('Snapshot create: {0}, response: {1}'.format(r.status_code, r.json()))

        if r.status_code == 200:
            while True:
                time.sleep(5)
                r = requests.get(snap_url)
                res = r.json()

                for item in res['snapshots']:
                    if item['snapshot'] == snap:
                        if item['state'] == 'SUCCESS':
                            logger.info('Snapshot created: {0}'.format(res))

                            wl = [snap] + ['{1}{0}'.format((datetime.utcnow()-timedelta(days=i)).strftime('%Y-%m-%d'), prefix) for i in [1, 2, 3, 4, 5]]
                            logger.info('Actual Snaps: {0}'.format(wl))

                            snaps_url = 'http://{0}/_snapshot/backup/_all'.format(host)
                            r = requests.get(snaps_url)
                            if r.status_code == 200:
                                res = r.json()
                                for item in res['snapshots']:
                                    if prefix in item['snapshot'] and item['snapshot'] not in wl:
                                        snap_url = 'http://{0}/_snapshot/backup/{1}'.format(host, item['snapshot'])
                                        r = requests.delete(snap_url)        
                                        logger.info('Remove old snapshot: {0}'.format(item['snapshot']))
                            return
                        else:
                            logger.info('Snapshot {0} status: {1}'.format(snap, item['state']))
                        break
