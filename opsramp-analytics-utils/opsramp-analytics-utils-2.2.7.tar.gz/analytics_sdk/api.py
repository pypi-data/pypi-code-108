from flask import request

from .mixins import generic_list_view, generic_detail_view
from .models import Session, Analysis, AnalysisRun, AnalysisExport, AnalysisSend
from .utilities import (
    get_jwt_token, run_scheduled_send, generate_pdf, login_required,
    get_msp_id, get_user_id, call_get_requests, BASE_API_URL
)


#@login_required
def analysis_list_view():
    filter_fields = ['app_id']
    extra_params = {'tenant_id': get_msp_id()}
    return generic_list_view(Analysis, filter_fields, extra_params=extra_params)


#@login_required
def analysis_detail_view(id):
    return generic_detail_view(Analysis, id)


#@login_required
def analysis_run_list_view():
    filter_fields = ['analysis_id']
    extra_params = {'triggered_by_id': get_user_id()}
    return generic_list_view(AnalysisRun, filter_fields, extra_params=extra_params)


#@login_required
def analysis_run_detail_view(id):
    return generic_detail_view(AnalysisRun, id)


#@login_required
def analysis_export_create_view():
    resp = generic_list_view(AnalysisExport)

    with Session() as session:
        entity = session.query(AnalysisExport).filter_by(id=resp['id']).first()

    pdf_info = generate_pdf(entity.run)
    with Session.begin() as session:
        entity.url = pdf_info['Location']
        resp['url'] = pdf_info['Location']

    return resp


#@login_required
def analysis_export_detail_view(id):
    return generic_detail_view(AnalysisExport, id)


#@login_required
def analysis_send_list_view(func_compute):
    filter_fields = ['analysis_id']
    extra_params = {'jwt_token': get_jwt_token()}
    resp = generic_list_view(AnalysisSend, filter_fields, extra_params=extra_params)

    if request.method == 'POST':
        with Session() as session:
            entity = session.query(AnalysisSend).filter_by(id=resp['id']).first()

        if entity.is_active and not entity.is_ran and not entity.schedule:  # send now
            run_scheduled_send(entity, func_compute)

    return resp


#@login_required
def compute_view(func_compute):
    params = request.get_json()
    analysis = Analysis(
        id=params.get('analysis_id'),
        params=params
    )
    user_id = get_user_id()
    run = analysis.run(func_compute, user_id)

    resp = {
        'analysis': analysis.id,
        'analysis-run': run.id
    }

    return resp


#@login_required
def oap_get_users():
    org_id = get_msp_id()
    url = f'{BASE_API_URL}/api/v2/tenants/{org_id}/users/minimal'
    resp = call_get_requests(url, verify=False).json()

    return {
        'results': resp,
        'count': len(resp)
    }
