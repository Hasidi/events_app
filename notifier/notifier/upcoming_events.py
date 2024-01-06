import logging
import os
from datetime import datetime, timedelta
from time import sleep
from typing import List

from common.db_models import Event


upcoming_events_file = os.environ['UPCOMING_EVENTS_FILE']


def send_upcoming_events(db, minute_interval: int, logger: logging.Logger) -> List[str]:
    up = datetime.now() + timedelta(minutes=minute_interval+1)
    down = datetime.now() + timedelta(minutes=minute_interval-1)
    try:
        events = db.query(Event).filter(Event.date >= down, Event.date <= up).all()
        for e in events:
            logger.info(f'Event is about to start: {e.id}')
        return [str(e.id) for e in events]
    except Exception as e:
        logging.error(f'Failed to notify on upcoming events: {e}')



def notify_upcoming_events(db, minute_interval: int, logger: logging.Logger):
    while True:
        events = send_upcoming_events(db, minute_interval, logger)
        if events:
            with open(upcoming_events_file, 'a') as file:
                file.write(f'{datetime.now().isoformat()}: Upcoming events {events}\n')
        sleep(60)
