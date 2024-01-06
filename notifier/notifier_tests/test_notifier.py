import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock

from sqlalchemy import delete

from common.db_models import create_db_session, Event

from notifier.upcoming_events import send_upcoming_events


class TestNotifier(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.db = create_db_session()

    def test_upcoming_events(self):
        minutes = 30

        events1 = [Event(name=f'n{i}', date=datetime.now() + timedelta(minutes=minutes + i)) for i in range(1, 4)]
        events2 = [Event(name=f'nn{i}', date=datetime.now() - timedelta(minutes=minutes + i)) for i in range(1, 4)]
        events = events1 + events2
        try:
            self.db.bulk_save_objects(events)
            self.db.commit()
            res = send_upcoming_events(self.db, minutes, Mock())
            self.assertEqual(len(res), 1)
        finally:
            statement = delete(Event).where(Event.name.in_([e.name for e in events]))
            res = self.db.execute(statement)
            self.db.commit()
            self.assertEqual(res.rowcount, len(events), "num of records were not deleted")


if __name__ == '__main__':
    unittest.main()
