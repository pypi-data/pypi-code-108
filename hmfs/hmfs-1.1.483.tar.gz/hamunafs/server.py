from threading import local
import traceback
from function_scheduling_distributed_framework import fsdf_background_scheduler, task_deco, patch_frame_config, get_publisher, BrokerEnum
from function_scheduling_distributed_framework.consumers.base_consumer import ExceptionForRequeue
from hamunafs.utils.cachemanager import CacheManager
from hamunafs.utils.minio import MinioAgent
from hamunafs.client import Client

import asyncio
import time
import os
import argparse
from hamunafs.utils.mqtt import MQTTClient

from hamunafs.utils.nsqmanager import MQManager
from hamunafs.sqlite import DB

def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='raspbian')
    parser.add_argument('--port', type=str, default='9000')
    parser.add_argument('--acs-key', type=str, default='hmcz')
    parser.add_argument('--acs-secret', type=str, default='hmcz1234')
    parser.add_argument('--location', type=str, default='brick1')
    parser.add_argument('--root-path', type=str, default='../hmfs_data')
    parser.add_argument('--api-host', type=str, default='backend.ai.hamuna.club')
    parser.add_argument('--broker-host', type=str, default='kafka.ai.hamuna.club')
    parser.add_argument('--broker-port', type=int, default=34150)
    parser.add_argument('--broker-http-port', type=int, default=34151)
    parser.add_argument('--redis-host', type=str, default='cache.ai.hamuna.club')
    parser.add_argument('--redis-port', type=int, default=6379)
    parser.add_argument('--redis-pass', type=str, default='1987yang')
    parser.add_argument('--redis-db', type=int, default=2)
    parser.add_argument('--mqtt-host', type=str, default='kafka.ai.hamuna.club')
    parser.add_argument('--mqtt-port', type=int, default=1883)
    parser.add_argument('--mqtt-user', type=str, default='opush')
    parser.add_argument('--mqtt-pass', type=str, default='innovation')

    opt = parser.parse_args()
    return opt

opt = get_opts()

root_path = opt.root_path

cache_path = os.path.join(root_path, 'cache')
db_path = os.path.join(root_path, 'db')

os.makedirs(cache_path, exist_ok=True)
os.makedirs(db_path, exist_ok=True)

# init sqlite
sqlite_db = DB(os.path.join(db_path, 'data.sqlite3'), is_relative=False)

sqlite_db.create_table('ttl_files', ["id integer PRIMARY KEY", "bucket text NOT NULL", "bucket_name text NOT NULL", "expired integer"])

broker_cfg = {
    'host': opt.broker_host,
    'port': opt.broker_port,
    'http_port': opt.broker_http_port
}

def on_mqtt_message(client, userdata, msg):
    if msg.topic == 'fs_backend_update':
        client.update()
    
minio = MinioAgent('{}:{}'.format(opt.host, opt.port), opt.acs_key, opt.acs_secret, secure=False, location=opt.location)

cache_engine = CacheManager(opt.redis_host, opt.redis_pass, opt.redis_port, opt.redis_db, local_cache=None)

mqtt_client = MQTTClient('fs_server', opt.mqtt_user, opt.mqtt_pass).connect(opt.mqtt_host, opt.mqtt_port)
mqtt_client.subscribe('fs_backend_update', 2)
mqtt_client.register_on_message_handler(on_mqtt_message)

patch_frame_config(
    NSQD_TCP_ADDRESSES=['{}:{}'.format(
        broker_cfg['host'], broker_cfg['port'])],
    NSQD_HTTP_CLIENT_HOST=broker_cfg['host'],
    NSQD_HTTP_CLIENT_PORT=broker_cfg['http_port']
)

hmfs_client = Client.get_client(opt.api_host, cache_engine.client, None)

@task_deco('fs_put', function_timeout=60, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
async def file_transfer_put(url, bucket, bucket_name, ttl):
    key = 'file_transfer_put_{}_{}'.format(bucket, bucket_name)
    if await cache_engine.get_cache_async(key, return_obj=False) is not None:
        return
    
    with cache_engine.lock(key, ttl=30) as lock:
        if lock:
            try:
                if await cache_engine.get_cache_async(key, return_obj=False) is not None:
                    return
                
                file_path = os.path.join(cache_path, '{}_{}'.format(bucket, bucket_name))
                print('downloading file from cloud....')
                ret, e = await hmfs_client.get_from_cloud_async(file_path, url)

                if ret:
                    print('cloud downloaded. start uploading...')
                    ret, e = minio.upload_file(e, bucket, bucket_name)
                    if ret:
                        cache_engine.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                            'ret': True, 
                            'url': url
                        }, expired=60)
                        print('upload success!!')
                        
                        if ttl != -1:
                            expired_time = time.time() + ttl * 24 * 60 * 60
                            sqlite_db.iud('insert into ttl_files(bucket, bucket_name, expired) values (?, ?, ?)', (bucket, bucket_name, expired_time))
                        
                    else:
                        cache_engine.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                            'ret': False,
                            'err': e
                        }, expired=60)
                else:
                    print('cloud download failed -> ' + e)
                    cache_engine.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                        'ret': False,
                        'err': '文件中转错误'
                    }, expired=60)
                cache_engine.cache(key, 1, expired=60)
                print('ok')
            except Exception as e:
                cache_engine.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                        'ret': False,
                        'err': str(e)
                    }, expired=60)
        else:
            cache_engine.cache('tmp_file_{}_{}'.format(bucket, bucket_name), {
                        'ret': False,
                        'err': '锁超时'
                    }, expired=60)


@task_deco('fs_get', function_timeout=60, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
async def file_transfer_get(bucket, bucket_name, refresh='no'):
    try:
        task_id = 'tmp_file_{}_{}'.format(bucket, bucket_name)
        if refresh == 'no':
            remote_state = await cache_engine.get_cache_async(task_id)
            if remote_state is not None:
                ret = remote_state['ret']
                if ret:
                    print('remote has record->{}, ignored.'.format(task_id))
                    return

        with cache_engine.lock(task_id) as lock:
            remote_state = await cache_engine.get_cache_async(task_id)
            if remote_state is not None:
                ret = remote_state['ret']
                if ret:
                    print('remote has record->{}, ignored.'.format(task_id))
                    return

            file_path = os.path.join(cache_path, '{}_{}'.format(bucket, bucket_name))
            if not os.path.isfile(file_path):
                ret, e = minio.download_file(file_path, bucket, bucket_name)
                if ret:
                    file_path = e
                else:
                    cache_engine.cache(task_id, {
                        'ret': False, 
                        'err': e.message
                    }, expired=60)
                    return

            ret, e = hmfs_client.put_to_cloud(file_path, bucket, bucket_name)
            if ret:
                cache_engine.cache(task_id, {
                    'ret': True,
                    'url': e
                }, expired=60 * 60 * 24 * 1)
                print('upload success!!')
            else:
                cache_engine.cache(task_id, {
                    'ret': False, 
                    'err': e
                }, expired=60)
    except Exception as e:
        traceback.print_exc()
    

# @task_deco('file_transfer_del', function_timeout=60, concurrent_mode=4, broker_kind=BrokerEnum.NSQ)
# async def file_transfer_del(bucket, bucket_name):
#     key = 'del_file_{}_{}'.format(bucket, bucket_name)
#     if await cache_engine.get_cache_async(key, return_obj=False) is not None:
#         return
    
#     with cache_engine.lock(key, ttl=30) as lock:
#         if lock:
#             if await cache_engine.get_cache_async(key, return_obj=False) is not None:
#                 return
#             file_path = os.path.join(cache_path, '{}_{}'.format(bucket, bucket_name))
#             if not os.path.isfile(file_path):
#                 ret, e = minio.delete(bucket, bucket_name)
                
#             print('ok')
            
async def ttl_cleanup():
    rows = sqlite_db.select('select id, bucket, bucket_name from ttl_files where expired >= ?', (time.time(),))
    affected_records = 0
    if rows is not None:
        for r in rows:
            bucket, bucket_name = r['bucket'], r['bucket_name']
            ret, e = minio.delete(bucket, bucket_name, 0)
            if ret:
                affected_records += 1
                print('removing file id: {} from db...'.format(r['id']))
                sqlite_db.iud('delete from ttl_files where id={};'.format(r['id']))
            else:
                print(e)
            
    return affected_records
    
async def extra_tasks():
    while True:
        try:
            affected_records = await ttl_cleanup()
            if affected_records > 0:
                print('data cleaned')
        except:
            traceback.print_exc()
        finally:
            await asyncio.sleep(30)

def run():
    file_transfer_get.consume()
    file_transfer_put.consume()
    # # file_transfer_del.consume()

    # asyncio.get_event_loop().run_until_complete(file_transfer_put('qiniu://tmp_file_test/test.jpg', 'test', 'test.jpg', -1))
    
    loop = asyncio.new_event_loop()
    loop.run_until_complete(extra_tasks())
    