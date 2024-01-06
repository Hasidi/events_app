import logging
import os
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import scoped_session

from common.db_models import EventSubscriber
from common.redis_queue import RedisQueue


events_update_file = os.environ['EVENTS_UPDATE_FILE']


def handle_event_update(queue: RedisQueue, db: scoped_session, logger: logging.Logger) -> Optional[str]:
    event_id = queue.get()
    try:
        subscribers = db.query(EventSubscriber).filter_by(event_id=event_id).all()
        for subscriber in subscribers:
            logger.info(f'Hi {subscriber.user_id}, event was updated: {event_id}')
        return event_id if subscribers else None
    except Exception as e:
        logging.error(f'Failed to notify on event change {event_id}: {e}')


def subscriber_notifier(queue: RedisQueue, db: scoped_session, logger: logging.Logger):
    while True:
        event_id = handle_event_update(queue, db, logger)
        if event_id:
            with open(events_update_file, 'a') as file:
                file.write(f'{datetime.now().isoformat()}: Found subscribers for event update {event_id}\n')
