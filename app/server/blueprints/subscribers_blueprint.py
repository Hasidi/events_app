import uuid
from http import HTTPStatus

from common.db_models import EventSubscriber
from server.blueprints import AppBlueprint

subscribe_blueprint = AppBlueprint('subscribe', __name__, url_prefix='/subscribe')


@subscribe_blueprint.post('/<event_id>')
def subscribe_to_event(event_id: str):
    db = subscribe_blueprint.db_session

    # user_id should be determined by our auth system, from header information.
    # im using random value as there is no implementation for authentication and user
    user_id = uuid.uuid4()

    event_subscriber = EventSubscriber(user_id=user_id, event_id=event_id)
    db.add(event_subscriber)
    db.commit()
    return {'message': f'subscription was created successfully'}, HTTPStatus.CREATED
