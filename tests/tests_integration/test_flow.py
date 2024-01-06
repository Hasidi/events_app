import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import pytest
import requests


server_url = os.environ['SERVICE_URL']
events_update_file_path = f"notifier/{os.environ['EVENTS_UPDATE_FILE']}"

events_url = f'{server_url}/events'
subscribe_url = f'{server_url}/subscribe'


data = {}
events_update_path = Path(events_update_file_path)


@pytest.fixture(autouse=True, scope='package')
def entry():
    sleep(3)
    if events_update_path.exists():
        events_update_path.unlink()
    body = {
        "events": []
    }
    response = requests.delete(f'{server_url}/admin/events', json=body)
    response.raise_for_status(), f'events were not deleted permanently'


def test__create_events():
    now = datetime.now()
    events = [
        {"name": "e1", "date": (now + timedelta(days=2)).isoformat(), "location": "some location_1", "participants_num": 170},
        {"name": "e2", "date": (now + timedelta(minutes=30)).isoformat(), "location": "some location_2", "participants_num": 50},
        {"name": "e3", "date": (now + timedelta(days=-7)).isoformat(), "location": "some location_4", "participants_num": 250},
        {"name": "e4", "date": (now + timedelta(minutes=35)).isoformat(), "location": "some location_5", "participants_num": 120}
    ]
    response = requests.post(events_url, json={'events': events})
    assert response.status_code == 201, response.json()


def test__get_events():
    response = requests.get(events_url)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 4
    event_id = events[0]['id']
    response = requests.get(f'{events_url}/{event_id}')
    assert response.status_code == 200
    assert response.json()['id'] == event_id
    data['event_id'] = event_id


def test__subscribe_users():
    response = requests.post(f'{subscribe_url}/{data["event_id"]}')
    assert response.status_code == 201, f'subscriber to event {data["event_id"]} was not created'
    requests.post(f'{subscribe_url}/{data["event_id"]}')
    assert response.status_code == 201, f'subscriber to event {data["event_id"]} was not created'


def test__put_event():
    response = requests.put(f'{events_url}/{data["event_id"]}',
                            json={"location": "update_location_1", "participants_num": 170})
    assert response.status_code == 200, response.json()
    sleep(2)
    assert events_update_path.exists()


def test__delete_event():
    response = requests.delete(f'{events_url}/{data["event_id"]}')
    assert response.status_code == 200, f'event {data["event_id"]} was not deleted'
    sleep(2)
    n_lines = events_update_path.read_text().count('\n') + 1
    assert n_lines, f'num of lines is {n_lines} != 2'

    response = requests.get(events_url)
    assert response.status_code == 200
    events = response.json()
    assert len(events) == 3
