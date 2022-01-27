from flask import Flask
from flask_apscheduler import APScheduler
from flask_smorest import Api
from pyctuator.health.db_health_provider import DbHealthProvider
from pyctuator.pyctuator import Pyctuator

from change_event_service.database import db
from change_event_service.modules.job import consume_change_events
from change_event_service.modules.job.utils import JobHealthProvider
from change_event_service.modules.rest.views import change_event
from change_event_service.utils.settings import apply_settings

app = Flask(__name__)

apply_settings(app)

db.init_app(app)
db.create_all(app=app)

actuator = Pyctuator(
    app,
    app_name='change-event-service',
    app_description='Change Event Service',
    app_url=f"htttp://{app.config.get('ACTUATOR_BASE_URI').rstrip('actuator')}",
    pyctuator_endpoint_url=f"{app.config.get('ACTUATOR_BASE_URI')}",
    registration_url=None
)

db_engine = db.get_engine(app)
actuator.register_health_provider(DbHealthProvider(db_engine))
actuator.register_health_provider(JobHealthProvider())

api = Api(app)
Api.DEFAULT_ERROR_RESPONSE_NAME = None
api.register_blueprint(change_event)

scheduler = APScheduler()

scheduler.init_app(app)
scheduler.add_job(
    id='consume_change_events',
    func=consume_change_events,
    args=[scheduler.app],
)
scheduler.start()
