from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from pyopencell.client import Client
from pyopencell.exceptions import PyOpenCellAPIException
import base64


class UserController(http.Controller):

    @http.route(
        ['/web/binary/download_invoice'], auth='user',
        methods=['GET'], website=False
    )
    @serialize_exception
    def download_invoice(self, invoice_number, **kw):
        try:
            invoice_response = Client().get(
                "/invoice", invoiceNumber=invoice_number, includePdf=True
            )
        except PyOpenCellAPIException:
            return request.not_found()
        invoice_base64 = invoice_response["invoice"]["pdf"]
        filecontent = base64.b64decode(invoice_base64)
        if not filecontent:
            return request.not_found()
        else:
            filename = "{}.pdf".format(invoice_number)
            return request.make_response(filecontent, [
                ('Content-Type', 'application/octet-stream'),
                ('Content-Disposition', content_disposition(filename))
            ])
