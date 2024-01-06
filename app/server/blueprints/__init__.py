from flask import Blueprint
from sqlalchemy.orm import Session

from common.redis_queue import RedisQueue


class AppBlueprint(Blueprint):
    db_session: Session
    redis_queue: RedisQueue

    def register(self, app, options) -> None:
        self.db_session = options['session']
        self.redis_queue = options['redis_queue']
        super().register(app, options)
