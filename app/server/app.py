import dataclasses
from http import HTTPStatus

from flask import Flask, Blueprint

from common.app_logger import create_app_logger
from common.redis_queue import create_redis_queue


@dataclasses.dataclass(frozen=True)
class EventsApp:
    flask_app: Flask

    def register(self, *blueprints: Blueprint):
        from common.db_models import create_db_session

        session = create_db_session()
        redis_queue = create_redis_queue()
        for blueprint in blueprints:
            self.flask_app.register_blueprint(blueprint, session=session, redis_queue=redis_queue)


def create_app() -> EventsApp:
    from sqlalchemy.exc import IntegrityError

    logger = create_app_logger('server')
    app = Flask(__name__)

    @app.errorhandler(ValueError)
    def handle_bad_request(error):
        return {'error': str(error)}, HTTPStatus.BAD_REQUEST

    @app.errorhandler(IntegrityError)
    def handle_db_integrity_error(err):
        return str(err.orig), HTTPStatus.BAD_REQUEST

    @app.errorhandler(Exception)
    def handle_unhandled_exception(err):
        logger.error(str(err))
        return 'Internal Error, please try again later', HTTPStatus.INTERNAL_SERVER_ERROR

    return EventsApp(app)
