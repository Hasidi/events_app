from os import environ

from server.app import create_app
from server.blueprints.admin_blueprint import admin_blueprint
from server.blueprints.events_blueprint import events_blueprint
from server.blueprints.subscribers_blueprint import subscribe_blueprint


if __name__ == '__main__':
    app = create_app()
    app.register(events_blueprint, subscribe_blueprint, admin_blueprint)
    app.flask_app.run(host='0.0.0.0', port=5000, debug=bool(environ.get('DEBUG', False)))
