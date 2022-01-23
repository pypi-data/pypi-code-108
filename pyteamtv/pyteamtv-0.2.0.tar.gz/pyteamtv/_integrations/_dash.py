from datetime import timedelta
from typing import Optional, Callable

from flask import request, session, has_request_context, g
from flask_session import Session

from .app import _get_current_app, App


def init_app(app, app_id: str = None) -> Callable[[], Optional[App]]:
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_SAMESITE'] = "None"
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_PATH'] = "/"

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

    # The maximum number of items the session stores
    # before it starts deleting some, default 500
    app.config['SESSION_FILE_THRESHOLD'] = 100

    sess = Session()
    sess.init_app(app)

    def get_current_app() -> Optional[App]:
        if not has_request_context():
            return None

        if 'teamtv_app' not in g:
            return None

        return g.teamtv_app

    @app.before_request
    def reset_app():
        g.teamtv_app = _get_current_app(
            app_id=app_id,
            session=session,
            token=request.args.get('token')
        )

    return get_current_app


