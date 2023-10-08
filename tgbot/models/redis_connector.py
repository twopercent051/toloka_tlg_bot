from typing import Optional, Union, Literal

import redis
import json

from create_bot import config, logger


class RedisConnector:
    """black_list repost_texts repost_messages"""

    r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)

    @classmethod
    def get_list(cls, redis_db_name: Literal["black_list", "repost_texts", "repost_messages"]) -> Optional[list]:
        response = cls.r.get(redis_db_name)
        if response is None:
            return None
        return json.loads(response.decode("utf=8"))

    @classmethod
    def redis_start(cls):
        for db_name in ["black_list", "repost_texts", "repost_chats"]:
            if cls.get_list(redis_db_name=db_name) is None:
                cls.r.set(db_name, json.dumps(list()))
        logger.info("Redis connected OKK")

    @classmethod
    def add_item(cls, redis_db_name: Literal["black_list", "repost_texts", "repost_messages"], item: Union[str, dict]):
        result = cls.get_list(redis_db_name=redis_db_name)
        result.append(item)
        cls.r.set(redis_db_name, json.dumps(result))

    @classmethod
    def delete_item(cls,
                    redis_db_name: Literal["black_list", "repost_texts", "repost_messages"],
                    item: Union[str, dict]):
        result = cls.get_list(redis_db_name=redis_db_name)
        result = list(filter(lambda x: x != item, result))
        cls.r.set(redis_db_name, json.dumps(result))
