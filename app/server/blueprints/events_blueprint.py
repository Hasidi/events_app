import uuid
from http import HTTPStatus

import sqlalchemy as sql
from flask import request
from sqlalchemy.orm.exc import StaleDataError

from common.db_models import Event
from server.blueprints import AppBlueprint
from server.models.models import CreateEventsRequest, EventModel, EventDeleteRequest, GetEventsRequest, \
    EventUpdateRequest, SingleEventUpdateRequest, validate_uuid

events_blueprint = AppBlueprint('events', __name__, url_prefix='/events')


@events_blueprint.post('/')
def insert_events():
    events_req = CreateEventsRequest.parse_raw(request.data)

    db = events_blueprint.db_session
    new_events = [Event(id=uuid.uuid4(), **e.dict()) for e in events_req.events]
    db.bulk_save_objects(new_events)
    db.commit()
    return {'new_events': [e.id for e in new_events]}, HTTPStatus.CREATED


@events_blueprint.get('/<event_id>')
def get_event_by_name(event_id: str):
    validate_uuid(event_id)
    db = events_blueprint.db_session
    res = db.query(Event).filter_by(id=event_id, deleted=False).first()
    if not res:
        return {}
    return EventModel.from_orm(res).dict()


@events_blueprint.get('/')
def get_events():
    req = GetEventsRequest.parse_obj(request.args.to_dict())

    db = events_blueprint.db_session
    query = db.query(Event)
    if req.dict(exclude_none=True):
        query = db.query(Event)
        if req.name:
            query = query.filter(Event.name.like(f'%{req.name}%'))
        if req.location:
            query = query.filter(Event.location.like(f'%{req.location}%'))
        if req.participants_num:
            query = query.filter(Event.participants_num >= req.participants_num)
        if req.sort_by:
            query = query.order_by(sql.desc(getattr(Event, req.sort_by)))
    db_result = query.filter_by(deleted=False).all()
    events = [EventModel.from_orm(e).dict() for e in db_result]
    return events


# UPDATE / DELETE

@events_blueprint.put('/<event_id>')
def update_event(event_id: str):
    validate_uuid(event_id)
    req = SingleEventUpdateRequest.parse_raw(request.data)
    db = events_blueprint.db_session
    q = sql.update(Event).where(Event.id == event_id).values(**req.dict(exclude_none=True))
    result = db.execute(q)
    if result.rowcount > 0:
        db.commit()
        events_blueprint.redis_queue.put([event_id])
        return {'message': f'event {event_id} was updated successfully'}
    return {}, HTTPStatus.NOT_FOUND


@events_blueprint.put('/')
def update_events():
    req = EventUpdateRequest.parse_raw(request.data)

    db = events_blueprint.db_session
    try:
        db.execute(sql.update(Event), [r.dict(exclude_none=True) for r in req.updates])
        db.commit()
        events_blueprint.redis_queue.put([r.id for r in req.updates])
        return {'message': 'Events were updated successfully', 'number': len(req.updates)}
    except StaleDataError:
        return {'message:': 'Some event does not exist'}, HTTPStatus.BAD_REQUEST


@events_blueprint.delete('/<event_id>')
def delete_event(event_id: str):
    validate_uuid(event_id)
    db = events_blueprint.db_session
    q = sql.update(Event).where(Event.id == event_id).values(deleted=True)
    result = db.execute(q)
    if result.rowcount > 0:
        db.commit()
        events_blueprint.redis_queue.put([event_id])
        return {'message': f'event {event_id} was deleted.'}
    return {}, HTTPStatus.NOT_FOUND


@events_blueprint.delete('/')
def bulk_delete():
    req = EventDeleteRequest.parse_raw(request.data)
    if not req.events:
        return {}
    db = events_blueprint.db_session
    events_id = [e_id for e_id in req.events]
    q = sql.update(Event).where(Event.id.in_(events_id)).values(deleted=True)
    result = db.execute(q)
    if result.rowcount > 0:
        db.commit()
        events_blueprint.redis_queue.put(events_id)
        return {'message': f'events were deleted', "number": result.rowcount}
    return {}, HTTPStatus.NOT_FOUND
