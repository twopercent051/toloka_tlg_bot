import redis
import json

from create_bot import config, logger

r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)


class RedisConnector:
    r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)

    @classmethod
    def redis_start(cls):
        cls.r.set('keywords', json.dumps(list()))
        logger.info('Redis connected OKK')

    @classmethod
    async def update_kw_list(cls, kw_list: list):
        cls.r.set('keywords', json.dumps(kw_list))

    @classmethod
    async def get_kw_list(cls):
        response = cls.r.get('keywords')
        if response is None:
            return None
        response = cls.r.get('keywords').decode('utf=8')
        kw_list = json.loads(response)
        return kw_list
