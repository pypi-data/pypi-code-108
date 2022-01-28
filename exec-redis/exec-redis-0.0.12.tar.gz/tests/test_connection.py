from execredis import ExecRedisClient


class RedisHandler:
    def __init__(self, host=None, db=0, cluster=False, **kwargs):
        self.redis = ExecRedisClient(host, db, cluster, **kwargs)

    def get_keys(self):
        return self.redis.keys()


if __name__ == '__main__':
    redis_client = RedisHandler(**{'host': '0.0.0.0', 'db': 0})
    print(redis_client.get_keys())
