from flask import request
from sqlalchemy import sql

from common.db_models import Event
from server.blueprints import AppBlueprint
from server.models.models import AdminEventDeleteRequest

admin_blueprint = AppBlueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.delete('/events')
def bulk_delete():
    req = AdminEventDeleteRequest.parse_raw(request.data)
    db = admin_blueprint.db_session
    q = sql.delete(Event)
    if req.events:
        events_id = [e_id for e_id in req.events]
        q = q.where(Event.id.in_(events_id))
    result = db.execute(q)
    if result.rowcount > 0:
        db.commit()
        return {'message': f'events were deleted permanently', "number": result.rowcount}
    return {}
