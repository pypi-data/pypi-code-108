""" Pipeline APIs
"""
import logging

from celery.canvas import _chain
from celery_dyrygent.workflows import Workflow
from flask import jsonify, request
from flask.views import MethodView
from rho_web.smorest import Blueprint
from rho_web.response import abort
from marshmallow import Schema, fields
from marshmallow.exceptions import ValidationError
from sermos.constants import API_DOC_RESPONSES, API_DOC_PARAMS, API_PATH_V1
from sermos.flask.decorators import require_accesskey
from sermos.flask.api.utils import chain_helper
from sermos.utils.task_utils import PipelineResult
from sermos.utils.config_utils import retrieve_latest_pipeline_config
from sermos.pipeline_config_schema import BasePipelineSchema, PipelineSchemaV1

logger = logging.getLogger(__name__)
bp = Blueprint('pipelines', __name__, url_prefix=API_PATH_V1 + '/pipelines')


class InvokePipelineSchema(Schema):
    """ Incoming schema for invoking a pipeline
    """
    chain_payload = fields.Raw(
        description='Payload contains whatever arguments the pipeline expects '
        'to be passed to each node in the graph.',
        example={
            'document_id': '123',
            'send_alert': True
        },
        required=False)


class InvokePipelineResponseSchema(Schema):
    execution_id = fields.String()
    pipeline_id = fields.String()
    status = fields.String()


class GetPipelineResultResponseSchema(Schema):
    execution_id = fields.String()
    result = fields.Raw()
    result_ttl = fields.Integer()
    results = fields.Raw()
    status = fields.String()
    status_message = fields.String()


@bp.route('/')
class Pipelines(MethodView):
    """ Operations against all pipelines.
    """
    @require_accesskey
    @bp.doc(responses=API_DOC_RESPONSES,
            parameters=[API_DOC_PARAMS['accesskey']],
            tags=['Pipelines'])
    def get(self):
        """ Retrieve list of available pipelines.
        """
        access_key = request.headers.get('accesskey')
        pipeline_config_api_resp = retrieve_latest_pipeline_config(
            access_key=access_key)

        if pipeline_config_api_resp is None:
            abort(404)

        try:
            pipelines = []
            for p in pipeline_config_api_resp:
                PipelineSchema = \
                    BasePipelineSchema.get_by_version(p['schemaVersion'])
                pipeline_config = PipelineSchema().load(p)
                pipelines.append(pipeline_config)
        except ValidationError as e:
            msg = f"Invalid pipeline configuration: {e}"
            return jsonify({'message': msg}), 202

        return jsonify(pipelines)


@bp.route('/<string:pipeline_id>')
class PipelineInfo(MethodView):
    """ Operations against a single pipeline
    """
    @require_accesskey
    @bp.doc(responses=API_DOC_RESPONSES,
            parameters=[
                API_DOC_PARAMS['accesskey'], {
                    'in': 'path',
                    'name': 'pipeline_id',
                    'description':
                    'pipeline_id for which to retrieve metrics.',
                    'type': 'string',
                    'example': 'my_pipeline',
                    'required': True
                }
            ],
            tags=['Pipelines'])
    def get(self, pipeline_id: str):
        """ Retrieve details about a specific pipeline.
        """
        access_key = request.headers.get('accesskey')
        pipeline_config_api_resp = retrieve_latest_pipeline_config(
            pipeline_id=pipeline_id, access_key=access_key)

        if pipeline_config_api_resp is None:
            abort(404)

        try:
            pipeline_config = PipelineSchemaV1().load(pipeline_config_api_resp)
        except ValidationError as e:
            msg = f"Invalid pipeline configuration: {e}"
            return jsonify({'message': msg}), 202

        return jsonify(pipeline_config)


@bp.route('/invoke/<string:pipeline_id>')
class PipelineInvoke(MethodView):
    """ Operations involed with pipeline invocation
    """
    @require_accesskey
    @bp.doc(responses=API_DOC_RESPONSES,
            parameters=[
                API_DOC_PARAMS['accesskey'], {
                    'in': 'path',
                    'name': 'pipeline_id',
                    'description':
                    'pipeline_id for which to retrieve metrics.',
                    'type': 'string',
                    'example': 'my_pipeline',
                    'required': True
                }
            ],
            tags=['Pipelines'])
    @bp.arguments(InvokePipelineSchema)
    @bp.response(InvokePipelineResponseSchema)
    def post(self, payload: dict, pipeline_id: str):
        """ Invoke a pipeline by it's ID; optionally provide pipeline arguments.
        """

        access_key = request.headers.get('accesskey')
        pipeline_config = retrieve_latest_pipeline_config(
            pipeline_id=pipeline_id, access_key=access_key)

        if pipeline_config is None:
            return abort(404)

        retval = {'pipeline_id': pipeline_id, 'status': ''}
        try:
            # TODO - ideally we can validate the payload *at this stage*
            # before the chain is ever invoked so we can handle issues
            # without kicking off work.
            payload = payload['chain_payload']\
                if 'chain_payload' in payload else {}

            gen = chain_helper(pipeline_id=pipeline_id,
                               access_key=access_key,
                               chain_payload=payload)

            if gen.chain is None:
                abort(400, message=gen.loading_message)

            chain: _chain = gen.chain
            wf: Workflow = Workflow()
            wf.add_celery_canvas(chain)
            wf.apply_async()
            retval['status'] = 'success'
            retval['execution_id'] = gen.execution_id
            # Initialize the cached result
            pr = PipelineResult(gen.execution_id, status='pending')
            pr.save()

        except Exception as e:
            msg = "Failed to invoke pipeline ... {}".format(pipeline_id)
            logger.error(msg)
            logger.exception(f"{e}")
            abort(500, message=msg)

        return jsonify(retval)


results_responses = API_DOC_RESPONSES.copy()
results_responses[202] = {
    'code': 202,
    'description': 'Pipeline is still running. Try again later.'
}
results_responses[204] = {
    'code': 204,
    'description': 'The execution results have expired. Re-run pipeline.'
}


@bp.route('/results/<string:execution_id>')
class PipelineResults(MethodView):
    """ Operations with respect to pipeline results
    """
    @require_accesskey
    @bp.doc(responses=results_responses,
            parameters=[
                API_DOC_PARAMS['accesskey'], {
                    'in': 'path',
                    'name': 'execution_id',
                    'description':
                    'execution_id for which to retrieve results',
                    'type': 'string',
                    'example': '4c595cca-9bf1-4150-8c34-6b43faf276c8',
                    'required': True
                }
            ],
            tags=['Pipelines'])
    @bp.response(GetPipelineResultResponseSchema)
    def get(self, execution_id: str):
        """ Retrieve results of a pipeline's execution based on execution_id

            NOTE: Cached results expire after a time window so are not available
            forever.

            TODO: Need to add response marshalling/schema here.
        """
        try:
            pr = PipelineResult(execution_id)
            pr.load()
            retval = pr.to_dict()
            if pr.status == 'unavailable':
                retval['status_message'] = 'Results expired. Re-run pipeline.'
                return retval, 204

            if pr.status == 'pending':
                retval['status_message'] = 'Results pending. Check again soon.'
                return retval, 202

            else:
                retval['status_message'] = 'Results available.'
                return retval, 200

        except Exception as e:
            msg = "Failed to retrieve results for execution id: {}".format(
                execution_id)
            logger.error(msg)
            logger.exception(f"{e}")
            abort(500, message=msg)
