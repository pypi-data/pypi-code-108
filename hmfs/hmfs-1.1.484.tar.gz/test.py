import asyncio
from hamunafs.client import Client
from hamunafs.utils.redisutil import XRedis
from hamunafs.utils.nsqmanager import MQManager


redis = XRedis('cache.ai.hamuna.club', '1987yang', 6379, db=2)
mq = MQManager('kafka.ai.hamuna.club', 34150)

client = Client('backend.ai.hamuna.club', redis, mq, async_mq_mode=False, init_redis=False)

ret, e = asyncio.get_event_loop().run_until_complete(client.put_async('/mnt/aeb1fc58-ba15-4787-84dc-3703f264dd93/Project/Data/jilin_cow_det/cow_yibiao/0aac39f4-f263-11eb-9119-c39b4e498dbc.jpg', 'test', 'test3.jpg', file_ttl=7))
# if ret:
ret, e = asyncio.get_event_loop().run_until_complete(client.get_async('./test1.jpg', e, force_copy=True))