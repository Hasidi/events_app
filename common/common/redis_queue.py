from typing import Any, List

import redis


class RedisQueue:
    @staticmethod
    def get_queue_name(name: str):
        return f'queue:{name}'

    def __init__(self, queue_name: str, redis_con: redis.Redis):
        self.db = redis_con
        self.q_name = self.get_queue_name(queue_name)

    def qsize(self) -> int:
        return self.db.llen(self.q_name)

    def empty(self) -> bool:
        return self.qsize() == 0

    def put(self, item: List[str]) -> int:
        return self.db.rpush(self.q_name, *item)

    def get(self, timeout: int = 0) -> Any:
        item = self.db.blpop(self.q_name, timeout=timeout)
        if item:
            item = item[1]
        return item


def create_redis_queue() -> RedisQueue:
    import os

    queue_name = os.environ['NOTIFICATION_QUEUE']
    redis_url = os.environ['REDIS_URL']
    redis_con = redis.from_url(redis_url, decode_responses=True)
    return RedisQueue(queue_name, redis_con)
