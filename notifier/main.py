from threading import Thread

from common.app_logger import create_app_logger
from common.db_models import create_db_session
from common.redis_queue import create_redis_queue
from notifier.event_updates import subscriber_notifier
from notifier.upcoming_events import notify_upcoming_events


def main():
    logger_ = create_app_logger('notifier')
    logger_.info('Notifier is starting..')
    redis_queue = create_redis_queue()
    db_ = create_db_session()

    Thread(target=notify_upcoming_events, args=(db_, 30, logger_,)).start()
    Thread(target=subscriber_notifier, args=(redis_queue, db_, logger_,)).start()


if __name__ == '__main__':
    main()
