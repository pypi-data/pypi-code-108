from http import HTTPStatus

from flask.views import MethodView
from flask_smorest import Blueprint

from change_event_service.modules.rest.business import create_change_event, get_change_event, delete_change_event, \
    filter_change_events
from change_event_service.modules.rest.schemas import ChangeEventSchema, BaseResponseSchema, \
    ChangeEventFilterRequestSchema, ChangeEventResponseSchema, ChangeEventListResponseSchema

change_event = Blueprint('change_event', 'change_event', url_prefix='/api/v1/change_event',
                         description='Change Event API')


@change_event.route('/')
class ChangeEventCollection(MethodView):
    @change_event.arguments(ChangeEventSchema, location='json')
    @change_event.response(status_code=HTTPStatus.CREATED, schema=BaseResponseSchema)
    @change_event.alt_response(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, schema=BaseResponseSchema, success=False)
    @change_event.alt_response(status_code=HTTPStatus.BAD_REQUEST, schema=BaseResponseSchema, success=False)
    def post(self, args):
        """Yeni change event eklemek için kullanılır."""
        return create_change_event(args)


@change_event.route('/<int:change_event_id>')
class ChangeEventRecordCollection(MethodView):
    @change_event.response(status_code=HTTPStatus.OK, schema=ChangeEventResponseSchema)
    @change_event.alt_response(status_code=HTTPStatus.NOT_FOUND, schema=BaseResponseSchema, success=False)
    @change_event.alt_response(status_code=HTTPStatus.BAD_REQUEST, schema=BaseResponseSchema, success=False)
    def get(self, change_event_id):
        """Verilen id'li change event kaydını getirir."""
        return get_change_event(change_event_id)

    @change_event.response(status_code=HTTPStatus.OK, schema=BaseResponseSchema)
    @change_event.alt_response(status_code=HTTPStatus.NOT_FOUND, schema=BaseResponseSchema, success=False)
    @change_event.alt_response(status_code=HTTPStatus.BAD_REQUEST, schema=BaseResponseSchema, success=False)
    def delete(self, change_event_id):
        """Verilen id'li change event kaydını siler."""
        return delete_change_event(change_event_id)


@change_event.route('/filter')
class ChangeEventFilterCollection(MethodView):
    @change_event.arguments(ChangeEventFilterRequestSchema, location='json')
    @change_event.paginate()
    @change_event.response(status_code=HTTPStatus.OK, schema=ChangeEventListResponseSchema)
    @change_event.alt_response(status_code=HTTPStatus.BAD_REQUEST, schema=BaseResponseSchema, success=False)
    def post(self, args, pagination_parameters):
        """Verilen filtrelere göre change eventleri getirir."""
        return filter_change_events(args, pagination_parameters)
