from execredis import ExecRedisClient


class RedisHandler:
    def __init__(self, host=None, db=0, cluster=False, **kwargs):
        self.redis = ExecRedisClient(host, db, cluster, **kwargs)

    def get_keys(self):
        return self.redis.keys()


redis_client = RedisHandler(**{'host': '0.0.0.0', 'db': 0})


if __name__ == '__main__':
    print(redis_client.get_keys())
