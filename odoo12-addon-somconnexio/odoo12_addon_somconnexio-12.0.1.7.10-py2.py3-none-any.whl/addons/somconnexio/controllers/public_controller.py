import logging

from odoo import http
from odoo.http import Root
from odoo.http import request
from odoo.addons.base_rest.http import HttpRestRequest
from odoo.addons.somconnexio.services import (
    contract_contract_service, contract_iban_change_service,
    contract_one_shot_service, contract_change_tariff_service
)
from odoo.addons.base_rest.controllers.main import RestController

_logger = logging.getLogger(__name__)
emc_process_method = RestController._process_method


def _process_method(self, service_name, method_name, *args, **kwargs):
    _logger.debug("args: {}, kwargs: {}".format(args, kwargs))
    return emc_process_method(
        self, service_name, method_name, *args, **kwargs
    )


RestController._process_method = _process_method


class UserPublicController(http.Controller):

    @http.route(['/public-api/contract'], auth='public',
                methods=['POST'], csrf=False)
    def create_contract(self, **kwargs):
        service = contract_contract_service.ContractService(request.env)
        data = request.params
        response = service.create(**data)
        return request.make_json_response(response)

    @http.route(['/public-api/contract-iban-change'], auth='public',
                methods=['POST'], csrf=False)
    def run_contract_iban_change(self, **kwargs):
        service = contract_iban_change_service.ContractIbanChangeService(request.env)
        data = request.params
        response = service.run_from_api(**data)
        return request.make_json_response(response)

    @http.route(['/public-api/contract-count'], auth='public',
                methods=['GET'], csrf=False)
    def count_contract(self):
        service = contract_contract_service.ContractService(request.env)
        response = service.count()
        return request.make_json_response(response)

    @http.route(['/public-api/add-one-shot'], auth='public',
                methods=['POST'], csrf=False)
    def run_add_contract_one_shot(self, **kwargs):
        service = contract_one_shot_service.ContractOneShotAdditionService(request.env)
        data = request.params
        response = service.run_from_api(**data)
        return request.make_json_response(response)

    @http.route(['/public-api/change-tariff'], auth='public',
                methods=['POST'], csrf=False)
    def run_change_contract_tariff(self, **kwargs):
        service = contract_change_tariff_service.ContractChangeTariffService(
            request.env)
        data = request.params
        response = service.run_from_api(**data)
        return request.make_json_response(response)


ori_get_request = Root.get_request


def get_request(self, httprequest):
    if (httprequest.path.startswith('/public-api/contract') or
            httprequest.path.startswith('/public-api/add-one-shot') or
            httprequest.path.startswith('/public-api/change-tariff')):
        return HttpRestRequest(httprequest)
    return ori_get_request(self, httprequest)


Root.get_request = get_request
